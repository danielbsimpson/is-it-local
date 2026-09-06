"""Ownership classification schemas."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class ClassificationEnum(StrEnum):
    family_owned = "family_owned"
    locally_owned = "locally_owned"
    independent = "independent"
    franchise = "franchise"
    corporate_owned = "corporate_owned"
    unknown = "unknown"


class ClassificationRead(BaseModel):
    classification: ClassificationEnum
    confidence: float = Field(ge=0.0, le=1.0)
    updated_at: datetime
    source_ids: list[UUID] = Field(default_factory=list)
