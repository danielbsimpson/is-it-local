"""Community submission ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CommunitySubmission(Base):
    __tablename__ = "community_submissions"
    __table_args__ = (
        CheckConstraint(
            "proposed_classification IN ("
            "'family_owned','locally_owned','independent',"
            "'franchise','corporate_owned','unknown')",
            name="ck_submission_classification_value",
        ),
        CheckConstraint(
            "status IN ('pending','approved','rejected')",
            name="ck_submission_status_value",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    proposed_classification: Mapped[str] = mapped_column(String, nullable=False)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, server_default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
