"""Ownership classification ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.source import Source

CLASSIFICATION_VALUES = (
    "family_owned",
    "locally_owned",
    "independent",
    "franchise",
    "corporate_owned",
    "unknown",
)


class OwnershipClassification(Base):
    __tablename__ = "ownership_classifications"
    __table_args__ = (
        CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="ck_classification_confidence_range",
        ),
        CheckConstraint(
            "classification IN ("
            "'family_owned','locally_owned','independent',"
            "'franchise','corporate_owned','unknown')",
            name="ck_classification_value",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    classification: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    business: Mapped[Business] = relationship(back_populates="classifications")
    sources: Mapped[list[Source]] = relationship(back_populates="classification")
