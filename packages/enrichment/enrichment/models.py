"""Data-transfer objects shared across the enrichment pipeline."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator

CLASSIFICATIONS: tuple[str, ...] = (
    "family_owned",
    "locally_owned",
    "independent",
    "franchise",
    "corporate_owned",
    "unknown",
)


class BusinessRef(BaseModel):
    """The subset of a business needed to research and classify ownership."""

    id: uuid.UUID
    name: str
    address: dict | None = None
    categories: list[str] | None = None
    brand: str | None = None
    parent_company: str | None = None


class SourceCandidate(BaseModel):
    """A piece of web evidence retrieved for a business."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    provider: str = "searxng"
    url: str
    snippet: str | None = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ClassificationResult(BaseModel):
    """The outcome of classifying a business's ownership."""

    classification: str
    confidence: float = Field(ge=0.0, le=1.0)
    cited_source_ids: list[uuid.UUID] = Field(default_factory=list)

    @field_validator("classification")
    @classmethod
    def _known_classification(cls, value: str) -> str:
        if value not in CLASSIFICATIONS:
            raise ValueError(f"classification must be one of {CLASSIFICATIONS}")
        return value
