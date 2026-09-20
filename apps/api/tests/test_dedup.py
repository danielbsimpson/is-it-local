"""De-duplication service tests."""

from __future__ import annotations

from datetime import UTC, datetime

from geoalchemy2.elements import WKTElement
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Business, OwnershipClassification, Source
from app.services import deduplicate


def _add_business(
    session: Session,
    *,
    name: str,
    lon: float,
    lat: float,
    provider: str,
    place_id: str,
    brand: str | None = None,
) -> Business:
    business = Business(
        name=name,
        location=WKTElement(f"POINT({lon} {lat})", srid=4326),
        provider=provider,
        provider_place_id=place_id,
        brand=brand,
    )
    session.add(business)
    session.flush()
    return business


def _count(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(Business)) or 0


def test_merges_nearby_same_name_across_providers(db_session: Session) -> None:
    _add_business(
        db_session,
        name="Corner Bakery",
        lon=-122.4194,
        lat=37.7749,
        provider="openstreetmap",
        place_id="node/1",
    )
    _add_business(
        db_session,
        name="corner  bakery",
        lon=-122.41941,
        lat=37.77491,
        provider="overture",
        place_id="ov-1",
        brand="Corner Bakery",
    )

    merged = deduplicate(db_session)

    assert merged == 1
    assert _count(db_session) == 1
    canonical = db_session.scalars(select(Business)).one()
    assert canonical.provider == "openstreetmap"
    # Missing fields are backfilled from the merged duplicate.
    assert canonical.brand == "Corner Bakery"


def test_keeps_distant_same_name_records(db_session: Session) -> None:
    _add_business(
        db_session,
        name="Joe's Coffee",
        lon=-122.4194,
        lat=37.7749,
        provider="openstreetmap",
        place_id="node/1",
    )
    _add_business(
        db_session,
        name="Joe's Coffee",
        lon=-73.9857,
        lat=40.7484,
        provider="openstreetmap",
        place_id="node/2",
    )

    merged = deduplicate(db_session)

    assert merged == 0
    assert _count(db_session) == 2


def test_reassigns_children_to_canonical(db_session: Session) -> None:
    canonical = _add_business(
        db_session,
        name="Book Nook",
        lon=-122.4194,
        lat=37.7749,
        provider="openstreetmap",
        place_id="node/1",
    )
    duplicate = _add_business(
        db_session,
        name="Book Nook",
        lon=-122.41942,
        lat=37.77492,
        provider="overture",
        place_id="ov-9",
    )
    classification = OwnershipClassification(
        business_id=duplicate.id, classification="independent", confidence=0.8
    )
    db_session.add(classification)
    db_session.flush()
    db_session.add(
        Source(
            business_id=duplicate.id,
            classification_id=classification.id,
            provider="searxng",
            url="https://example.com/book-nook",
            retrieved_at=datetime.now(UTC),
        )
    )
    db_session.flush()

    merged = deduplicate(db_session)

    assert merged == 1
    assert _count(db_session) == 1
    surviving_classification = db_session.scalars(select(OwnershipClassification)).one()
    surviving_source = db_session.scalars(select(Source)).one()
    assert surviving_classification.business_id == canonical.id
    assert surviving_source.business_id == canonical.id
