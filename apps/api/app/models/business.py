"""Business ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from geoalchemy2 import Geography
from geoalchemy2.elements import WKBElement
from sqlalchemy import ARRAY, DateTime, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.classification import OwnershipClassification
    from app.models.source import Source


class Business(Base):
    __tablename__ = "businesses"
    __table_args__ = (
        UniqueConstraint("provider", "provider_place_id", name="uq_business_provider_identity"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    location: Mapped[WKBElement] = mapped_column(
        Geography(geometry_type="POINT", srid=4326, spatial_index=False), nullable=False
    )
    categories: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    contact: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    brand: Mapped[str | None] = mapped_column(String, nullable=True)
    parent_company: Mapped[str | None] = mapped_column(String, nullable=True)
    provider: Mapped[str | None] = mapped_column(String, nullable=True)
    provider_place_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    classifications: Mapped[list[OwnershipClassification]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    sources: Mapped[list[Source]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
