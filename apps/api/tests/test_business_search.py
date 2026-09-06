"""Business search endpoint tests."""

from fastapi.testclient import TestClient
from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from app.models import Business


def _add_business(session: Session, name: str, lon: float, lat: float, place_id: str) -> Business:
    business = Business(
        name=name,
        location=WKTElement(f"POINT({lon} {lat})", srid=4326),
        provider="openstreetmap",
        provider_place_id=place_id,
    )
    session.add(business)
    session.flush()
    return business


def test_search_by_name(client: TestClient, db_session: Session) -> None:
    _add_business(db_session, "Corner Bakery", -122.42, 37.77, "node/1")
    _add_business(db_session, "City Hardware", -122.42, 37.77, "node/2")

    response = client.get("/businesses/search", params={"name": "bakery"})

    assert response.status_code == 200
    names = [b["name"] for b in response.json()]
    assert names == ["Corner Bakery"]


def test_search_by_location_radius(client: TestClient, db_session: Session) -> None:
    _add_business(db_session, "Near Cafe", -122.4194, 37.7749, "node/1")
    _add_business(db_session, "Far Cafe", -73.9857, 40.7484, "node/2")

    response = client.get(
        "/businesses/search",
        params={"lat": 37.7749, "lon": -122.4194, "radius_m": 500},
    )

    assert response.status_code == 200
    names = [b["name"] for b in response.json()]
    assert names == ["Near Cafe"]


def test_search_requires_lat_and_lon_together(client: TestClient) -> None:
    response = client.get("/businesses/search", params={"lat": 37.7749})
    assert response.status_code == 422
