"""Tests for the LLM ownership classifier using a mocked chat client."""

from __future__ import annotations

import uuid
from types import SimpleNamespace

from enrichment.llm_classifier import classify
from enrichment.models import CLASSIFICATIONS, BusinessRef, SourceCandidate


class _FakeCompletions:
    def __init__(self, content: str):
        self._content = content
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        message = SimpleNamespace(content=self._content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class _FakeClient:
    def __init__(self, content: str):
        self.chat = SimpleNamespace(completions=_FakeCompletions(content))


def _business() -> BusinessRef:
    return BusinessRef(id=uuid.uuid4(), name="Corner Bakery", categories=["bakery"])


def test_classify_returns_valid_enum_and_confidence() -> None:
    source = SourceCandidate(url="https://example.com/a", snippet="Family owned since 1975.")
    content = (
        '{"classification": "family_owned", "confidence": 0.82, '
        f'"cited_source_ids": ["{source.id}"]}}'
    )
    client = _FakeClient(content)

    result = classify(_business(), [source], client=client, model="local-model")

    assert result.classification in CLASSIFICATIONS
    assert 0.0 <= result.confidence <= 1.0
    assert result.classification == "family_owned"
    assert result.cited_source_ids == [source.id]


def test_classify_filters_unknown_source_ids() -> None:
    source = SourceCandidate(url="https://example.com/a", snippet="Independent shop.")
    stray = uuid.uuid4()
    content = (
        f'{{"classification": "independent", "confidence": 0.6, "cited_source_ids": ["{stray}"]}}'
    )
    client = _FakeClient(content)

    result = classify(_business(), [source], client=client, model="local-model")

    assert result.cited_source_ids == []


def test_classify_coerces_invalid_classification_to_unknown() -> None:
    client = _FakeClient('{"classification": "megacorp", "confidence": 0.9}')

    result = classify(_business(), [], client=client, model="local-model")

    assert result.classification == "unknown"
    assert result.confidence <= 0.5


def test_classify_handles_non_json_response() -> None:
    client = _FakeClient("I could not determine ownership.")

    result = classify(_business(), [], client=client, model="local-model")

    assert result.classification == "unknown"
    assert result.confidence == 0.0


def test_classify_clamps_out_of_range_confidence() -> None:
    client = _FakeClient('{"classification": "corporate_owned", "confidence": 5}')

    result = classify(_business(), [], client=client, model="local-model")

    assert result.confidence == 1.0
