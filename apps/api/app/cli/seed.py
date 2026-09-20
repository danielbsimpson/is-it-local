"""Repeatable seed CLI: ingest provider places and de-duplicate.

Examples
--------
Seed from OpenStreetMap within a bounding box (south,west,north,east)::

    python -m app.cli.seed --provider openstreetmap --bbox 37.70,-122.52,37.83,-122.35

Seed from a local Overture export::

    python -m app.cli.seed --provider overture --bbox 37.70,-122.52,37.83,-122.35 \
        --overture-path ./data/overture-places.geojson
"""

from __future__ import annotations

import argparse
import sys

from app.config import settings
from app.db import SessionLocal
from app.providers.base import BoundingBox, PlaceProvider
from app.providers.openstreetmap import OpenStreetMapProvider
from app.providers.overture import OvertureProvider
from app.services import deduplicate, ingest


def _build_provider(name: str, args: argparse.Namespace) -> PlaceProvider:
    if name == "openstreetmap":
        return OpenStreetMapProvider(args.overpass_url or settings.overpass_url)
    if name == "overture":
        data_path = args.overture_path or settings.overture_data_path
        if not data_path:
            raise SystemExit("overture provider requires --overture-path or OVERTURE_DATA_PATH")
        return OvertureProvider(data_path)
    raise SystemExit(f"unknown provider: {name}")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed the business catalog from open place data.")
    parser.add_argument(
        "--provider",
        required=True,
        choices=["openstreetmap", "overture"],
        help="Place provider to ingest from.",
    )
    parser.add_argument(
        "--bbox",
        required=True,
        help="Bounding box as min_lat,min_lon,max_lat,max_lon (south,west,north,east).",
    )
    parser.add_argument("--overpass-url", default=None, help="Override the Overpass API URL.")
    parser.add_argument("--overture-path", default=None, help="Path to a local Overture export.")
    parser.add_argument(
        "--no-dedup",
        action="store_true",
        help="Skip cross-provider de-duplication after ingestion.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        bbox = BoundingBox.parse(args.bbox)
    except ValueError as exc:
        raise SystemExit(f"invalid --bbox: {exc}") from exc

    provider = _build_provider(args.provider, args)

    db = SessionLocal()
    try:
        count = ingest(db, provider, bbox)
        merged = 0 if args.no_dedup else deduplicate(db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(f"Ingested {count} place(s) from {provider.name}; merged {merged} duplicate(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
