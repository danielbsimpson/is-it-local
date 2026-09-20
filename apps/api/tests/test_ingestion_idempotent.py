"""Ingestion idempotency tests using a stub provider (no network)."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Business
from app.providers.base import BoundingBox, NormalizedPlace, PlaceProvider
from app.services import ingest

_BBOX = BoundingBox(min_lat=37.70, min_lon=-122.52, max_lat=37.83, max_lon=-122.35)


class _StubProvider(PlaceProvider):
    def __init__(self, places: list[NormalizedPlace]):
        self._places = places

    @property
    def name(self) -> str:
        return "openstreetmap"

    def fetch_places(self, bbox: BoundingBox) -> list[NormalizedPlace]:
        return self._places


def _places() -> list[NormalizedPlace]:
    return [
        NormalizedPlace(
            provider="openstreetmap",
            provider_place_id="node/1",
            name="Corner Bakery",
            lat=37.7749,
            lon=-122.4194,
            categories=["bakery"],
        ),
        NormalizedPlace(
            provider="openstreetmap",
            provider_place_id="node/2",
            name="City Hardware",
            lat=37.7750,
            lon=-122.4195,
            categories=["hardware"],
        ),
    ]


def _count(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(Business)) or 0


def test_ingest_inserts_places(db_session: Session) -> None:
    count = ingest(db_session, _StubProvider(_places()), _BBOX)
    assert count == 2
    assert _count(db_session) == 2


def test_ingest_is_idempotent(db_session: Session) -> None:
    ingest(db_session, _StubProvider(_places()), _BBOX)
    ingest(db_session, _StubProvider(_places()), _BBOX)
    assert _count(db_session) == 2


def test_ingest_updates_existing_record(db_session: Session) -> None:
    ingest(db_session, _StubProvider(_places()), _BBOX)

    updated = _places()
    updated[0] = updated[0].model_copy(update={"name": "Corner Bakery & Cafe"})
    ingest(db_session, _StubProvider(updated), _BBOX)

    assert _count(db_session) == 2
    business = db_session.scalars(
        select(Business).where(Business.provider_place_id == "node/1")
    ).one()
    assert business.name == "Corner Bakery & Cafe"
