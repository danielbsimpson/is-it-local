"""Orchestrates ownership enrichment: search, classify, and persist."""

from __future__ import annotations

from collections.abc import Callable

from enrichment.guardrails import RateLimiter
from enrichment.models import BusinessRef, ClassificationResult, SourceCandidate
from enrichment.repository import EnrichmentRepository
from enrichment.search_client import SearxngSearchClient

Classifier = Callable[[BusinessRef, list[SourceCandidate]], ClassificationResult]


def default_query(business: BusinessRef) -> str:
    parts = [business.name, "owner OR ownership OR parent company OR franchise"]
    if business.address and business.address.get("city"):
        parts.insert(1, str(business.address["city"]))
    return " ".join(parts)


class EnrichmentPipeline:
    """Enrich businesses lacking an ownership classification."""

    def __init__(
        self,
        *,
        repository: EnrichmentRepository,
        search_client: SearxngSearchClient,
        classifier: Classifier,
        rate_limiter: RateLimiter | None = None,
        max_results: int = 5,
        query_builder: Callable[[BusinessRef], str] = default_query,
    ):
        self._repository = repository
        self._search_client = search_client
        self._classifier = classifier
        self._rate_limiter = rate_limiter
        self._max_results = max_results
        self._query_builder = query_builder

    def enrich_business(self, business: BusinessRef) -> ClassificationResult:
        if self._rate_limiter is not None:
            self._rate_limiter.acquire()

        sources = self._search_client.search(
            self._query_builder(business), max_results=self._max_results
        )
        result = self._classifier(business, sources)

        cited_ids = set(result.cited_source_ids)
        cited = [source for source in sources if source.id in cited_ids]

        # REQ-007: a classification with confidence > 0 must cite at least one source.
        if result.confidence > 0.0 and not cited:
            if sources:
                cited = sources
                result = result.model_copy(
                    update={"cited_source_ids": [source.id for source in sources]}
                )
            else:
                result = result.model_copy(update={"classification": "unknown", "confidence": 0.0})

        self._repository.persist(business.id, result, cited)
        return result

    def run(self, limit: int) -> list[ClassificationResult]:
        businesses = self._repository.iter_unclassified(limit)
        return [self.enrich_business(business) for business in businesses]
