"""Data-access layer for :class:`Business` records."""

from __future__ import annotations

import uuid

from geoalchemy2 import Geography
from sqlalchemy import cast, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.business import Business
from app.models.classification import OwnershipClassification


def get_by_id(db: Session, business_id: uuid.UUID) -> Business | None:
    return db.get(Business, business_id)


def latest_classification(db: Session, business_id: uuid.UUID) -> OwnershipClassification | None:
    stmt = (
        select(OwnershipClassification)
        .where(OwnershipClassification.business_id == business_id)
        .order_by(OwnershipClassification.updated_at.desc())
        .options(selectinload(OwnershipClassification.sources))
        .limit(1)
    )
    return db.scalars(stmt).first()


def search(
    db: Session,
    *,
    name: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    radius_m: float = 1000.0,
    limit: int = 100,
) -> list[Business]:
    stmt = select(Business)
    if name:
        stmt = stmt.where(Business.name.ilike(f"%{name}%"))
    if lat is not None and lon is not None:
        point = cast(func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326), Geography)
        stmt = stmt.where(func.ST_DWithin(Business.location, point, radius_m))
    return list(db.scalars(stmt.limit(limit)).all())


def upsert_by_provider_identity(
    db: Session,
    *,
    provider: str,
    provider_place_id: str,
    name: str,
    lat: float,
    lon: float,
    address: dict | None = None,
    categories: list[str] | None = None,
    contact: dict | None = None,
    brand: str | None = None,
    parent_company: str | None = None,
) -> Business:
    """Insert or update a business identified by ``(provider, provider_place_id)``.

    Idempotent: re-running with the same identity updates the existing row rather
    than creating a duplicate.
    """
    point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
    existing = db.scalars(
        select(Business).where(
            Business.provider == provider,
            Business.provider_place_id == provider_place_id,
        )
    ).first()

    if existing is not None:
        existing.name = name
        existing.location = point
        existing.address = address
        existing.categories = categories
        existing.contact = contact
        existing.brand = brand
        existing.parent_company = parent_company
        db.flush()
        return existing

    business = Business(
        provider=provider,
        provider_place_id=provider_place_id,
        name=name,
        location=point,
        address=address,
        categories=categories,
        contact=contact,
        brand=brand,
        parent_company=parent_company,
    )
    db.add(business)
    db.flush()
    return business
