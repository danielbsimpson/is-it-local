"""Idempotent ingestion of provider places into the business catalog."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.providers.base import BoundingBox, PlaceProvider
from app.repositories import business_repository


def ingest(db: Session, provider: PlaceProvider, bbox: BoundingBox) -> int:
    """Fetch places from ``provider`` within ``bbox`` and upsert them.

    Idempotent: existing businesses are matched by ``(provider, provider_place_id)``
    and updated in place, so re-running never creates duplicate rows.

    Returns the number of places processed.
    """
    places = provider.fetch_places(bbox)
    for place in places:
        business_repository.upsert_by_provider_identity(
            db,
            provider=place.provider,
            provider_place_id=place.provider_place_id,
            name=place.name,
            lat=place.lat,
            lon=place.lon,
            address=place.address,
            categories=place.categories,
            contact=place.contact,
            brand=place.brand,
            parent_company=place.parent_company,
        )
    return len(places)
