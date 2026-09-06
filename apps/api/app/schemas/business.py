"""Business response schema and ORM adapter."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from geoalchemy2.shape import to_shape
from pydantic import BaseModel

from app.schemas.common import Address, Contact, GeoPoint

if TYPE_CHECKING:
    from app.models.business import Business


class BusinessRead(BaseModel):
    id: UUID
    name: str
    location: GeoPoint
    address: Address | None = None
    categories: list[str] | None = None
    contact: Contact | None = None
    brand: str | None = None
    parent_company: str | None = None

    @classmethod
    def from_orm_business(cls, business: Business) -> BusinessRead:
        point = to_shape(business.location)
        return cls(
            id=business.id,
            name=business.name,
            location=GeoPoint(coordinates=(point.x, point.y)),
            address=Address(**business.address) if business.address else None,
            categories=business.categories,
            contact=Contact(**business.contact) if business.contact else None,
            brand=business.brand,
            parent_company=business.parent_company,
        )
