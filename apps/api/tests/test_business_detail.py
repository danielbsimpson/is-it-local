"""Business detail endpoint tests."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient
from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from app.models import Business, OwnershipClassification, Source


def _make_business(session: Session) -> Business:
    business = Business(
        name="Blue Bottle Coffee",
        location=WKTElement("POINT(-122.4194 37.7749)", srid=4326),
        categories=["coffee_shop"],
        provider="openstreetmap",
        provider_place_id="node/1",
    )
    session.add(business)
    session.flush()
    return business


def test_detail_returns_classification_and_sources(client: TestClient, db_session: Session) -> None:
    business = _make_business(db_session)
    classification = OwnershipClassification(
        business_id=business.id,
        classification="independent",
        confidence=0.82,
        updated_at=datetime.now(UTC),
    )
    db_session.add(classification)
    db_session.flush()
    source = Source(
        business_id=business.id,
        classification_id=classification.id,
        provider="searxng",
        url="https://example.com/about",
        retrieved_at=datetime.now(UTC),
        snippet="Family run since 1998.",
    )
    db_session.add(source)
    db_session.flush()

    response = client.get(f"/businesses/{business.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["business"]["name"] == "Blue Bottle Coffee"
    assert body["business"]["location"]["coordinates"] == [-122.4194, 37.7749]
    assert body["classification"]["classification"] == "independent"
    assert body["classification"]["confidence"] == 0.82
    assert len(body["sources"]) == 1
    assert body["sources"][0]["url"] == "https://example.com/about"


def test_detail_unknown_business_returns_404(client: TestClient) -> None:
    response = client.get("/businesses/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
