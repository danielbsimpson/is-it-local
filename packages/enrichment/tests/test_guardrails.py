"""Tests for enrichment guardrails: rate limiting, caching, and retries."""

from __future__ import annotations

import pytest

from enrichment.guardrails import DiskCache, RateLimiter, with_retries


class _Clock:
    """A manual clock whose time only advances when ``sleep`` is called."""

    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def test_rate_limiter_allows_burst_up_to_capacity() -> None:
    clock = _Clock()
    limiter = RateLimiter(3, sleep=clock.sleep, monotonic=clock.monotonic)

    for _ in range(3):
        limiter.acquire()

    assert clock.sleeps == []


def test_rate_limiter_blocks_when_tokens_exhausted() -> None:
    clock = _Clock()
    limiter = RateLimiter(60, sleep=clock.sleep, monotonic=clock.monotonic)  # 1 token/sec

    for _ in range(60):
        limiter.acquire()
    limiter.acquire()  # 61st call must wait for a refill

    assert clock.sleeps
    assert sum(clock.sleeps) == pytest.approx(1.0, abs=0.01)


def test_rate_limiter_rejects_non_positive_rate() -> None:
    with pytest.raises(ValueError):
        RateLimiter(0)


def test_disk_cache_roundtrip(tmp_path) -> None:
    cache = DiskCache(tmp_path)

    assert cache.get("missing") is None
    cache.set("key", {"classification": "independent"})
    assert cache.get("key") == {"classification": "independent"}


def test_with_retries_retries_until_success() -> None:
    calls = {"n": 0}

    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("transient")
        return "ok"

    wrapped = with_retries(flaky, attempts=3, exceptions=ValueError)

    assert wrapped() == "ok"
    assert calls["n"] == 3


def test_with_retries_reraises_after_exhaustion() -> None:
    def always_fail() -> None:
        raise ValueError("boom")

    wrapped = with_retries(always_fail, attempts=2, exceptions=ValueError)

    with pytest.raises(ValueError):
        wrapped()
