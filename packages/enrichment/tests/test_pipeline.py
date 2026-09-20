"""Tests for the enrichment pipeline using mocked search, classifier, and repository."""

from __future__ import annotations

import uuid

from enrichment.models import BusinessRef, ClassificationResult, SourceCandidate
from enrichment.pipeline import EnrichmentPipeline


class _FakeSearchClient:
    def __init__(self, sources: list[SourceCandidate]):
        self._sources = sources
        self.queries: list[str] = []

    def search(self, query: str, *, max_results: int = 5) -> list[SourceCandidate]:
        self.queries.append(query)
        return self._sources[:max_results]


class _FakeRepository:
    def __init__(self, businesses: list[BusinessRef] | None = None):
        self._businesses = businesses or []
        self.persisted: list[tuple[uuid.UUID, ClassificationResult, list[SourceCandidate]]] = []

    def iter_unclassified(self, limit: int) -> list[BusinessRef]:
        return self._businesses[:limit]

    def persist(self, business_id, result, sources) -> None:
        self.persisted.append((business_id, result, sources))


def _business() -> BusinessRef:
    return BusinessRef(id=uuid.uuid4(), name="Corner Bakery", categories=["bakery"])


def _pipeline(search_client, classifier, repository) -> EnrichmentPipeline:
    return EnrichmentPipeline(
        repository=repository,
        search_client=search_client,
        classifier=classifier,
    )


def test_persists_only_cited_sources() -> None:
    sources = [
        SourceCandidate(url="https://example.com/a", snippet="Family owned."),
        SourceCandidate(url="https://example.com/b", snippet="Unrelated."),
    ]
    business = _business()

    def classifier(_business, _sources):
        return ClassificationResult(
            classification="family_owned", confidence=0.9, cited_source_ids=[sources[0].id]
        )

    repository = _FakeRepository()
    pipeline = _pipeline(_FakeSearchClient(sources), classifier, repository)

    result = pipeline.enrich_business(business)

    assert result.classification == "family_owned"
    _, _, persisted_sources = repository.persisted[0]
    assert [s.id for s in persisted_sources] == [sources[0].id]


def test_confident_result_without_citations_promotes_all_sources() -> None:
    sources = [SourceCandidate(url="https://example.com/a", snippet="Evidence.")]
    business = _business()

    def classifier(_business, _sources):
        return ClassificationResult(classification="independent", confidence=0.7)

    repository = _FakeRepository()
    pipeline = _pipeline(_FakeSearchClient(sources), classifier, repository)

    result = pipeline.enrich_business(business)

    # REQ-007: confidence > 0 must cite at least one source.
    assert result.cited_source_ids == [sources[0].id]
    _, _, persisted_sources = repository.persisted[0]
    assert len(persisted_sources) == 1


def test_confident_result_without_any_sources_becomes_unknown() -> None:
    business = _business()

    def classifier(_business, _sources):
        return ClassificationResult(classification="franchise", confidence=0.8)

    repository = _FakeRepository()
    pipeline = _pipeline(_FakeSearchClient([]), classifier, repository)

    result = pipeline.enrich_business(business)

    assert result.classification == "unknown"
    assert result.confidence == 0.0
    _, persisted_result, persisted_sources = repository.persisted[0]
    assert persisted_sources == []
    assert persisted_result.confidence == 0.0


def test_run_enriches_all_unclassified() -> None:
    businesses = [_business(), _business()]
    sources = [SourceCandidate(url="https://example.com/a")]

    def classifier(_business, _sources):
        return ClassificationResult(
            classification="independent", confidence=0.6, cited_source_ids=[sources[0].id]
        )

    repository = _FakeRepository(businesses)
    pipeline = _pipeline(_FakeSearchClient(sources), classifier, repository)

    results = pipeline.run(limit=10)

    assert len(results) == 2
    assert len(repository.persisted) == 2
