"""/api/listings - write scraped data and browse raw rows."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/listings", tags=["Listings"])

DB = Annotated[Session, Depends(get_db)]


@router.post(
    "/bulk",
    response_model=schemas.BulkInsertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk insert scraped listings",
)
def bulk_insert(payload: schemas.BulkInsertRequest, db: DB):
    """Insert up to 5,000 listings in one request.

    Every row is validated by Pydantic first; if any row is invalid the whole
    request is rejected with **422** and nothing is written. Rows that already
    exist (same name + city + address) are skipped and reported in
    `duplicates_skipped`, which makes the endpoint safe to call repeatedly.
    """
    return crud.bulk_insert_listings(db, payload.listings)


@router.get("", response_model=schemas.PaginatedListings, summary="Browse listings")
def list_listings(
    db: DB,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    city: str | None = None,
    category: str | None = None,
    source: str | None = None,
    search: Annotated[str | None, Query(max_length=100, description="Part of the business name")] = None,
):
    return crud.list_listings(db, page=page, page_size=page_size, city=city,
                              category=category, source=source, search=search)
