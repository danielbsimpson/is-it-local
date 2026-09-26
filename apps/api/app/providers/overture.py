"""Overture Maps place provider reading local open place data.

Overture distributes places as GeoParquet, but for the local-first PoC this provider
reads a local file of Overture place features (a GeoJSON ``FeatureCollection`` or a
newline-delimited JSON file of features) so ingestion needs no cloud access.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

from app.providers.base import BoundingBox, NormalizedPlace, PlaceProvider

PROVIDER_NAME = "overture"


class OvertureProvider(PlaceProvider):
    """Fetch places from a local Overture place-data export."""

    def __init__(self, data_path: str | Path):
        self._data_path = Path(data_path)

    @property
    def name(self) -> str:
        return PROVIDER_NAME

    def fetch_places(self, bbox: BoundingBox) -> list[NormalizedPlace]:
        if not self._data_path.exists():
            raise FileNotFoundError(f"Overture data file not found: {self._data_path}")

        places: list[NormalizedPlace] = []
        for feature in self._iter_features():
            place = self._to_place(feature)
            if place is None:
                continue
            if not _within(bbox, place.lat, place.lon):
                continue
            places.append(place)
        return places

    def _iter_features(self) -> Iterator[dict]:
        text = self._data_path.read_text(encoding="utf-8").strip()
        if not text:
            return
        first = text.lstrip()[0]
        if first == "{":
            document = json.loads(text)
            if document.get("type") == "FeatureCollection":
                yield from document.get("features", [])
                return
            yield document
            return
        for line in text.splitlines():
            line = line.strip()
            if line:
                yield json.loads(line)

    def _to_place(self, feature: dict) -> NormalizedPlace | None:
        geometry = feature.get("geometry") or {}
        coords = geometry.get("coordinates")
        if not coords or len(coords) < 2:
            return None
        lon, lat = float(coords[0]), float(coords[1])

        props = feature.get("properties") or {}
        name = _primary_name(props)
        if not name:
            return None

        place_id = feature.get("id") or props.get("id")
        if not place_id:
            return None

        return NormalizedPlace(
            provider=PROVIDER_NAME,
            provider_place_id=str(place_id),
            name=name,
            lat=lat,
            lon=lon,
            address=_address(props),
            categories=_categories(props),
            contact=_contact(props),
            brand=_brand(props),
        )


def _within(bbox: BoundingBox, lat: float, lon: float) -> bool:
    return bbox.min_lat <= lat <= bbox.max_lat and bbox.min_lon <= lon <= bbox.max_lon


def _primary_name(props: dict) -> str | None:
    names = props.get("names")
    if isinstance(names, dict):
        return names.get("primary")
    if isinstance(names, str):
        return names
    return None


def _categories(props: dict) -> list[str] | None:
    categories = props.get("categories")
    if not isinstance(categories, dict):
        return None
    values: list[str] = []
    primary = categories.get("primary") or categories.get("main")
    if primary:
        values.append(str(primary))
    for alt in categories.get("alternate") or []:
        values.append(str(alt))
    return values or None


def _address(props: dict) -> dict | None:
    addresses = props.get("addresses")
    if not isinstance(addresses, list) or not addresses:
        return None
    first = addresses[0]
    if not isinstance(first, dict):
        return None
    mapping = {
        "freeform": "street",
        "locality": "city",
        "region": "region",
        "postcode": "postal_code",
        "country": "country",
    }
    result = {key: first[tag] for tag, key in mapping.items() if first.get(tag)}
    return result or None


def _contact(props: dict) -> dict | None:
    result: dict[str, str] = {}
    phones = props.get("phones")
    if isinstance(phones, list) and phones:
        result["phone"] = str(phones[0])
    websites = props.get("websites")
    if isinstance(websites, list) and websites:
        result["website"] = str(websites[0])
    return result or None


def _brand(props: dict) -> str | None:
    brand = props.get("brand")
    if isinstance(brand, dict):
        names = brand.get("names")
        if isinstance(names, dict):
            return names.get("primary")
    if isinstance(brand, str):
        return brand
    return None
