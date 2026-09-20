"""Ownership-signal retrieval via a self-hosted SearXNG instance."""

from __future__ import annotations

import httpx

from enrichment.models import SourceCandidate


class SearxngSearchClient:
    """Query a self-hosted SearXNG instance and return candidate sources.

    Uses SearXNG's JSON output format (enabled in ``infra/searxng/settings.yml``).
    """

    def __init__(
        self,
        base_url: str,
        *,
        client: httpx.Client | None = None,
        timeout: float = 30.0,
    ):
        self._base_url = base_url.rstrip("/")
        self._client = client
        self._timeout = timeout

    def search(self, query: str, *, max_results: int = 5) -> list[SourceCandidate]:
        params = {"q": query, "format": "json"}
        if self._client is not None:
            response = self._client.get(f"{self._base_url}/search", params=params)
            response.raise_for_status()
            payload = response.json()
        else:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(f"{self._base_url}/search", params=params)
                response.raise_for_status()
                payload = response.json()

        candidates: list[SourceCandidate] = []
        for result in payload.get("results", [])[:max_results]:
            url = result.get("url")
            if not url:
                continue
            candidates.append(
                SourceCandidate(
                    provider="searxng",
                    url=url,
                    snippet=result.get("content") or result.get("title"),
                )
            )
        return candidates
