"""Provider address mapping must emit the canonical Address schema keys.

Regression: providers previously emitted ``state``/``postcode``/``house_number``,
which the ``Address`` schema (``extra="forbid"``) rejected, causing 500s on any
business that had an address.
"""

from __future__ import annotations

from app.providers.openstreetmap import OpenStreetMapProvider
from app.providers.overture import OvertureProvider
from app.schemas.common import Address

_OSM_ELEMENT = {
    "type": "node",
    "id": 1,
    "lat": 37.789,
    "lon": -122.408,
    "tags": {
        "name": "Starlite Room",
        "amenity": "nightclub",
        "addr:housenumber": "450",
        "addr:street": "Powell Street",
        "addr:city": "San Francisco",
        "addr:state": "CA",
        "addr:postcode": "94102",
    },
}

_OVERTURE_FEATURE = {
    "id": "overture-1",
    "geometry": {"type": "Point", "coordinates": [-122.408, 37.789]},
    "properties": {
        "names": {"primary": "Starlite Room"},
        "addresses": [
            {
                "freeform": "450 Powell Street",
                "locality": "San Francisco",
                "region": "CA",
                "postcode": "94102",
                "country": "US",
            }
        ],
    },
}


def test_openstreetmap_address_uses_canonical_keys() -> None:
    place = OpenStreetMapProvider("http://unused")._to_place(_OSM_ELEMENT)

    assert place is not None
    assert place.address == {
        "street": "450 Powell Street",
        "city": "San Francisco",
        "region": "CA",
        "postal_code": "94102",
    }
    # Must validate against the API contract that previously rejected these fields.
    Address(**place.address)


def test_overture_address_uses_canonical_keys() -> None:
    place = OvertureProvider("unused")._to_place(_OVERTURE_FEATURE)

    assert place is not None
    assert place.address == {
        "street": "450 Powell Street",
        "city": "San Francisco",
        "region": "CA",
        "postal_code": "94102",
        "country": "US",
    }
    Address(**place.address)
