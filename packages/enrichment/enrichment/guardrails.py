"""Guardrails for the local services: rate limiting, retries, and response caching.

These keep the local llama.cpp and SearXNG instances from being overwhelmed. There is
no external spend to guard in the PoC — the goal is stability under batch enrichment.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

T = TypeVar("T")


class RateLimiter:
    """A thread-safe token-bucket rate limiter measured in operations per minute."""

    def __init__(
        self,
        rate_per_min: int,
        *,
        sleep: Callable[[float], None] = time.sleep,
        monotonic: Callable[[], float] = time.monotonic,
    ):
        if rate_per_min <= 0:
            raise ValueError("rate_per_min must be positive")
        self._capacity = float(rate_per_min)
        self._tokens = float(rate_per_min)
        self._refill_per_sec = rate_per_min / 60.0
        self._monotonic = monotonic
        self._updated = monotonic()
        self._sleep = sleep
        self._lock = threading.Lock()

    def acquire(self) -> None:
        """Block until a token is available, then consume one."""
        while True:
            with self._lock:
                now = self._monotonic()
                elapsed = now - self._updated
                self._tokens = min(self._capacity, self._tokens + elapsed * self._refill_per_sec)
                self._updated = now
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
                wait = (1.0 - self._tokens) / self._refill_per_sec
            self._sleep(wait)


class DiskCache:
    """A minimal JSON on-disk cache keyed by an arbitrary string."""

    def __init__(self, directory: str | Path):
        self._directory = Path(directory)
        self._directory.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self._directory / f"{digest}.json"

    def get(self, key: str) -> Any | None:
        path = self._path(key)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def set(self, key: str, value: Any) -> None:
        self._path(key).write_text(json.dumps(value), encoding="utf-8")


def with_retries(
    func: Callable[..., T],
    *,
    attempts: int = 3,
    exceptions: type[Exception] | tuple[type[Exception], ...] = Exception,
) -> Callable[..., T]:
    """Wrap ``func`` with exponential-backoff retries via tenacity."""
    decorator = retry(
        reraise=True,
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=0.5, max=8),
        retry=retry_if_exception_type(exceptions),
    )
    return decorator(func)
