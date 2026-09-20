"""Persistence for enrichment results.

The pipeline writes directly to the database for batch efficiency, but does so through
the :class:`EnrichmentRepository` protocol so the storage backend can be swapped (e.g.
for an API client) and mocked in tests.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy import Engine, text
from sqlalchemy.orm import Session

from enrichment.models import BusinessRef, ClassificationResult, SourceCandidate


class EnrichmentRepository(Protocol):
    """Storage operations the enrichment pipeline depends on."""

    def iter_unclassified(self, limit: int) -> list[BusinessRef]:
        """Return up to ``limit`` businesses that have no ownership classification."""

    def persist(
        self,
        business_id: uuid.UUID,
        result: ClassificationResult,
        sources: list[SourceCandidate],
    ) -> None:
        """Persist one classification and its cited sources for ``business_id``."""


class SqlAlchemyEnrichmentRepository:
    """A :class:`EnrichmentRepository` backed by the shared PostgreSQL database."""

    def __init__(self, engine: Engine):
        self._engine = engine

    def iter_unclassified(self, limit: int) -> list[BusinessRef]:
        stmt = text(
            """
            SELECT b.id, b.name, b.address, b.categories, b.brand, b.parent_company
            FROM businesses b
            LEFT JOIN ownership_classifications c ON c.business_id = b.id
            WHERE c.id IS NULL
            ORDER BY b.created_at
            LIMIT :limit
            """
        )
        with Session(self._engine) as session:
            rows = session.execute(stmt, {"limit": limit}).mappings().all()
        return [
            BusinessRef(
                id=row["id"],
                name=row["name"],
                address=row["address"],
                categories=list(row["categories"]) if row["categories"] is not None else None,
                brand=row["brand"],
                parent_company=row["parent_company"],
            )
            for row in rows
        ]

    def persist(
        self,
        business_id: uuid.UUID,
        result: ClassificationResult,
        sources: list[SourceCandidate],
    ) -> None:
        classification_id = uuid.uuid4()
        cited = {str(sid) for sid in result.cited_source_ids}
        now = datetime.now(UTC)

        with Session(self._engine) as session:
            session.execute(
                text(
                    """
                    INSERT INTO ownership_classifications
                        (id, business_id, classification, confidence, updated_at)
                    VALUES (:id, :business_id, :classification, :confidence, :updated_at)
                    """
                ),
                {
                    "id": classification_id,
                    "business_id": business_id,
                    "classification": result.classification,
                    "confidence": result.confidence,
                    "updated_at": now,
                },
            )
            for source in sources:
                linked = classification_id if str(source.id) in cited else None
                session.execute(
                    text(
                        """
                        INSERT INTO sources
                            (id, business_id, classification_id, provider, url,
                             retrieved_at, snippet)
                        VALUES (:id, :business_id, :classification_id, :provider, :url,
                                :retrieved_at, :snippet)
                        """
                    ),
                    {
                        "id": source.id,
                        "business_id": business_id,
                        "classification_id": linked,
                        "provider": source.provider,
                        "url": source.url,
                        "retrieved_at": source.retrieved_at,
                        "snippet": source.snippet,
                    },
                )
            session.commit()
