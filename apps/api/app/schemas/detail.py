"""Composite business detail response schema."""

from pydantic import BaseModel

from app.schemas.business import BusinessRead
from app.schemas.classification import ClassificationRead
from app.schemas.source import SourceRead


class BusinessDetail(BaseModel):
    business: BusinessRead
    classification: ClassificationRead | None = None
    sources: list[SourceRead] = []
