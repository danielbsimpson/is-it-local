"""Shared value-object schemas."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class Address(BaseModel):
    model_config = ConfigDict(extra="forbid")

    street: str | None = None
    city: str | None = None
    region: str | None = None
    postal_code: str | None = None
    country: str | None = None


class Contact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    phone: str | None = None
    website: str | None = None
    email: str | None = None


class GeoPoint(BaseModel):
    """GeoJSON Point (RFC 7946) with ``[longitude, latitude]`` coordinates."""

    type: Literal["Point"] = "Point"
    coordinates: tuple[float, float]
