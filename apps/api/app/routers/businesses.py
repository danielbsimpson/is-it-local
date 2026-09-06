"""Business read/search/detail endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories import business_repository
from app.schemas.business import BusinessRead
from app.schemas.classification import ClassificationEnum, ClassificationRead
from app.schemas.detail import BusinessDetail
from app.schemas.source import SourceRead

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.get("/search", response_model=list[BusinessRead])
def search_businesses(
    db: Annotated[Session, Depends(get_db)],
    name: Annotated[str | None, Query(description="Partial, case-insensitive name match.")] = None,
    lat: Annotated[
        float | None, Query(ge=-90, le=90, description="Latitude of the search center.")
    ] = None,
    lon: Annotated[
        float | None, Query(ge=-180, le=180, description="Longitude of the search center.")
    ] = None,
    radius_m: Annotated[float, Query(gt=0, description="Search radius in meters.")] = 1000,
) -> list[BusinessRead]:
    if (lat is None) != (lon is None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="lat and lon must be provided together.",
        )
    businesses = business_repository.search(db, name=name, lat=lat, lon=lon, radius_m=radius_m)
    return [BusinessRead.from_orm_business(b) for b in businesses]


@router.get("/{business_id}", response_model=BusinessDetail)
def get_business(business_id: UUID, db: Annotated[Session, Depends(get_db)]) -> BusinessDetail:
    business = business_repository.get_by_id(db, business_id)
    if business is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found.")

    latest = business_repository.latest_classification(db, business_id)
    classification: ClassificationRead | None = None
    sources: list[SourceRead] = []
    if latest is not None:
        classification = ClassificationRead(
            classification=ClassificationEnum(latest.classification),
            confidence=latest.confidence,
            updated_at=latest.updated_at,
            source_ids=[s.id for s in latest.sources],
        )
        sources = [SourceRead.model_validate(s) for s in latest.sources]

    return BusinessDetail(
        business=BusinessRead.from_orm_business(business),
        classification=classification,
        sources=sources,
    )
