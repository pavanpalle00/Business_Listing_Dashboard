"""/api/dashboard - aggregated data for the charts.

Every endpoint accepts optional ``city`` / ``category`` / ``source`` filters,
so the dashboard can answer questions like "category counts in Mumbai only".
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

DB = Annotated[Session, Depends(get_db)]
Limit = Annotated[int | None, Query(ge=1, le=100, description="Return only the top N groups")]


@router.get("/summary", response_model=schemas.SummaryResponse, summary="Headline numbers")
def summary(db: DB, city: str | None = None, category: str | None = None, source: str | None = None):
    return crud.get_summary(db, city=city, category=category, source=source)


@router.get("/city-count", response_model=schemas.CountResponse, summary="City-wise business count")
def city_count(db: DB, limit: Limit = None, category: str | None = None, source: str | None = None):
    return crud.count_by(db, "city", limit=limit, category=category, source=source)


@router.get("/category-count", response_model=schemas.CountResponse, summary="Category-wise business count")
def category_count(db: DB, limit: Limit = None, city: str | None = None, source: str | None = None):
    return crud.count_by(db, "category", limit=limit, city=city, source=source)


@router.get("/source-count", response_model=schemas.CountResponse, summary="Source-wise business count")
def source_count(db: DB, limit: Limit = None, city: str | None = None, category: str | None = None):
    return crud.count_by(db, "source", limit=limit, city=city, category=category)
