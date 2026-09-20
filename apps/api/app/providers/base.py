"""Shared interface and data types for place providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, field_validator


class BoundingBox(BaseModel):
    """A geographic bounding box in WGS84 (EPSG:4326) degrees."""

    min_lat: float = Field(ge=-90.0, le=90.0)
    min_lon: float = Field(ge=-180.0, le=180.0)
    max_lat: float = Field(ge=-90.0, le=90.0)
    max_lon: float = Field(ge=-180.0, le=180.0)

    @field_validator("max_lat")
    @classmethod
    def _lat_ordered(cls, value: float, info) -> float:
        min_lat = info.data.get("min_lat")
        if min_lat is not None and value < min_lat:
            raise ValueError("max_lat must be greater than or equal to min_lat")
        return value

    @field_validator("max_lon")
    @classmethod
    def _lon_ordered(cls, value: float, info) -> float:
        min_lon = info.data.get("min_lon")
        if min_lon is not None and value < min_lon:
            raise ValueError("max_lon must be greater than or equal to min_lon")
        return value

    @classmethod
    def parse(cls, value: str) -> BoundingBox:
        """Parse a ``min_lat,min_lon,max_lat,max_lon`` string (south,west,north,east)."""
        parts = [p.strip() for p in value.split(",")]
        if len(parts) != 4:
            raise ValueError(
                "bbox must have four comma-separated values: min_lat,min_lon,max_lat,max_lon"
            )
        min_lat, min_lon, max_lat, max_lon = (float(p) for p in parts)
        return cls(min_lat=min_lat, min_lon=min_lon, max_lat=max_lat, max_lon=max_lon)


class NormalizedPlace(BaseModel):
    """A provider-agnostic representation of a business/place."""

    provider: str
    provider_place_id: str
    name: str
    lat: float = Field(ge=-90.0, le=90.0)
    lon: float = Field(ge=-180.0, le=180.0)
    address: dict | None = None
    categories: list[str] | None = None
    contact: dict | None = None
    brand: str | None = None
    parent_company: str | None = None


class PlaceProvider(ABC):
    """Abstract interface every place data provider must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable provider identifier persisted on ``Business.provider``."""

    @abstractmethod
    def fetch_places(self, bbox: BoundingBox) -> list[NormalizedPlace]:
        """Return the normalized places found within ``bbox``."""
