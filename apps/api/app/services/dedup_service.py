"""Cross-provider de-duplication of business records.

Records from different providers that describe the same physical business are merged
into a single canonical :class:`Business`. Two records are considered duplicates when
their normalized names match and they lie within ``DEDUP_RADIUS_M`` meters of each
other (via PostGIS ``ST_DWithin`` on the geography column).
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import cast, func, select, update
from sqlalchemy.orm import Session

from app.models.business import Business
from app.models.classification import OwnershipClassification
from app.models.source import Source

DEDUP_RADIUS_M = 50.0

# Lower value wins when choosing the canonical record to keep.
_PROVIDER_PRIORITY = {"openstreetmap": 0, "overture": 1}

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _normalize_name(name: str) -> str:
    return _NON_ALNUM.sub(" ", name.lower()).strip()


def _canonical_order(business: Business) -> tuple[int, datetime, str]:
    provider = business.provider or ""
    return (_PROVIDER_PRIORITY.get(provider, 99), business.created_at, str(business.id))


def deduplicate(db: Session, *, radius_m: float = DEDUP_RADIUS_M) -> int:
    """Merge duplicate businesses and return the number of records merged away."""
    businesses = list(db.scalars(select(Business).order_by(Business.created_at, Business.id)).all())

    groups: dict[str, list[Business]] = defaultdict(list)
    for business in businesses:
        groups[_normalize_name(business.name)].append(business)

    merged = 0
    for group in groups.values():
        if len(group) < 2:
            continue
        group.sort(key=_canonical_order)
        canonical = group[0]
        for duplicate in group[1:]:
            # Cast to Geography so ST_Distance returns meters rather than planar degrees.
            distance = db.scalar(
                select(
                    func.ST_Distance(
                        cast(canonical.location, Geography),
                        cast(duplicate.location, Geography),
                    )
                )
            )
            if distance is not None and distance <= radius_m:
                _merge(db, canonical, duplicate)
                merged += 1
    return merged


def _merge(db: Session, canonical: Business, duplicate: Business) -> None:
    db.execute(
        update(Source).where(Source.business_id == duplicate.id).values(business_id=canonical.id)
    )
    db.execute(
        update(OwnershipClassification)
        .where(OwnershipClassification.business_id == duplicate.id)
        .values(business_id=canonical.id)
    )

    for attr in ("address", "categories", "contact", "brand", "parent_company"):
        if getattr(canonical, attr) is None and getattr(duplicate, attr) is not None:
            setattr(canonical, attr, getattr(duplicate, attr))

    # Detach reassigned children so the delete-orphan cascade does not remove them.
    db.expire(duplicate, ["sources", "classifications"])
    db.delete(duplicate)
    db.flush()
