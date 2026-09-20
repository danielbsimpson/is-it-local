"""OpenStreetMap place provider using the Overpass API."""

from __future__ import annotations

import httpx

from app.providers.base import BoundingBox, NormalizedPlace, PlaceProvider

PROVIDER_NAME = "openstreetmap"

_ADDRESS_TAGS = {
    "addr:housenumber": "house_number",
    "addr:street": "street",
    "addr:city": "city",
    "addr:state": "state",
    "addr:postcode": "postcode",
    "addr:country": "country",
}
_CONTACT_TAGS = {
    "phone": "phone",
    "contact:phone": "phone",
    "website": "website",
    "contact:website": "website",
    "email": "email",
    "contact:email": "email",
}


class OpenStreetMapProvider(PlaceProvider):
    """Fetch named shops and amenities from the Overpass API."""

    def __init__(
        self, overpass_url: str, *, client: httpx.Client | None = None, timeout: float = 60.0
    ):
        self._overpass_url = overpass_url
        self._client = client
        self._timeout = timeout

    @property
    def name(self) -> str:
        return PROVIDER_NAME

    def _build_query(self, bbox: BoundingBox) -> str:
        bounds = f"{bbox.min_lat},{bbox.min_lon},{bbox.max_lat},{bbox.max_lon}"
        return (
            "[out:json][timeout:60];"
            "("
            f'node["name"]["shop"]({bounds});'
            f'way["name"]["shop"]({bounds});'
            f'node["name"]["amenity"]({bounds});'
            f'way["name"]["amenity"]({bounds});'
            ");"
            "out center tags;"
        )

    def fetch_places(self, bbox: BoundingBox) -> list[NormalizedPlace]:
        query = self._build_query(bbox)
        if self._client is not None:
            response = self._client.post(self._overpass_url, data={"data": query})
            response.raise_for_status()
            payload = response.json()
        else:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(self._overpass_url, data={"data": query})
                response.raise_for_status()
                payload = response.json()

        places: list[NormalizedPlace] = []
        for element in payload.get("elements", []):
            place = self._to_place(element)
            if place is not None:
                places.append(place)
        return places

    def _to_place(self, element: dict) -> NormalizedPlace | None:
        tags = element.get("tags") or {}
        name = tags.get("name")
        if not name:
            return None

        lat, lon = self._coordinates(element)
        if lat is None or lon is None:
            return None

        element_type = element.get("type")
        element_id = element.get("id")
        if element_type is None or element_id is None:
            return None

        return NormalizedPlace(
            provider=PROVIDER_NAME,
            provider_place_id=f"{element_type}/{element_id}",
            name=name,
            lat=lat,
            lon=lon,
            address=self._extract(tags, _ADDRESS_TAGS),
            categories=self._categories(tags),
            contact=self._extract(tags, _CONTACT_TAGS),
            brand=tags.get("brand"),
        )

    @staticmethod
    def _coordinates(element: dict) -> tuple[float | None, float | None]:
        if "lat" in element and "lon" in element:
            return element["lat"], element["lon"]
        center = element.get("center")
        if center:
            return center.get("lat"), center.get("lon")
        return None, None

    @staticmethod
    def _extract(tags: dict, mapping: dict[str, str]) -> dict | None:
        result: dict[str, str] = {}
        for tag, key in mapping.items():
            if tag in tags and key not in result:
                result[key] = tags[tag]
        return result or None

    @staticmethod
    def _categories(tags: dict) -> list[str] | None:
        values = [tags[key] for key in ("shop", "amenity", "cuisine") if tags.get(key)]
        categories = [v for value in values for v in str(value).split(";")]
        return categories or None
