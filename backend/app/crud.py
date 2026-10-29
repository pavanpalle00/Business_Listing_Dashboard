"""Database operations (the "service layer").

Routers stay thin: they parse the HTTP request, call a function from here and
return the result. All SQL lives in this module.
"""
import hashlib
import math
import re
from collections.abc import Sequence

from sqlalchemy import func, insert, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from . import schemas
from .models import Listing

# Columns the dashboard is allowed to group by (whitelist -> no SQL injection)
GROUPABLE = {"city": Listing.city, "category": Listing.category, "source": Listing.source}
HASH_LOOKUP_CHUNK = 1000


def compute_listing_hash(name: str, city: str, address: str | None) -> str:
    """SHA-256 of the normalised identity of a listing.

    "Cafe  Coffee Day", "cafe coffee day" and "Cafe-Coffee-Day" all produce
    the same hash, so the same business is never stored twice.
    """
    norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
    key = f"{norm(name)}|{norm(city)}|{norm(address)}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


# ------------------------------------------------------------------ writes
def bulk_insert_listings(db: Session, listings: Sequence[schemas.ListingCreate]) -> schemas.BulkInsertResponse:
    # 1. hash every row and drop duplicates *inside* the request
    unique_rows: dict[str, dict] = {}
    for item in listings:
        row = item.model_dump()
        row["listing_hash"] = compute_listing_hash(row["business_name"], row["city"], row["address"])
        unique_rows.setdefault(row["listing_hash"], row)

    # 2. find hashes that already exist in MySQL (chunked IN (...) queries)
    hashes = list(unique_rows)
    existing: set[str] = set()
    for start in range(0, len(hashes), HASH_LOOKUP_CHUNK):
        chunk = hashes[start:start + HASH_LOOKUP_CHUNK]
        existing.update(db.scalars(select(Listing.listing_hash).where(Listing.listing_hash.in_(chunk))))

    # 3. one multi-row INSERT for everything that is new, in a single transaction
    new_rows = [row for h, row in unique_rows.items() if h not in existing]
    if new_rows:
        db.execute(insert(Listing), new_rows)
    db.commit()

    return schemas.BulkInsertResponse(
        received=len(listings),
        inserted=len(new_rows),
        duplicates_skipped=len(listings) - len(new_rows),
    )


# ------------------------------------------------------------------- reads
def _apply_filters(stmt: Select, city: str | None, category: str | None, source: str | None) -> Select:
    if city:
        stmt = stmt.where(Listing.city == city)
    if category:
        stmt = stmt.where(Listing.category == category)
    if source:
        stmt = stmt.where(Listing.source == source)
    return stmt


def count_by(db: Session, dimension: str, *, limit: int | None = None,
             city: str | None = None, category: str | None = None,
             source: str | None = None) -> schemas.CountResponse:
    """SELECT <dimension>, COUNT(*) ... GROUP BY <dimension> ORDER BY count DESC."""
    column = GROUPABLE[dimension]
    count = func.count(Listing.id).label("count")
    stmt = _apply_filters(select(column, count), city, category, source)
    stmt = stmt.group_by(column).order_by(count.desc(), column.asc())

    rows = db.execute(stmt).all()
    total = sum(row.count for row in rows)
    if limit:
        rows = rows[:limit]
    return schemas.CountResponse(
        dimension=dimension,
        total=total,
        items=[schemas.CountItem(label=label, count=n) for label, n in rows],
    )


def get_summary(db: Session, city: str | None = None, category: str | None = None,
                source: str | None = None) -> schemas.SummaryResponse:
    stmt = select(
        func.count(Listing.id),
        func.count(func.distinct(Listing.city)),
        func.count(func.distinct(Listing.category)),
        func.count(func.distinct(Listing.source)),
        func.count(Listing.phone),  # COUNT(col) ignores NULLs
    )
    total, cities, categories, sources, with_phone = db.execute(
        _apply_filters(stmt, city, category, source)
    ).one()
    return schemas.SummaryResponse(total_listings=total, cities=cities, categories=categories,
                                   sources=sources, with_phone=with_phone)


def list_listings(db: Session, *, page: int, page_size: int, city: str | None = None,
                  category: str | None = None, source: str | None = None,
                  search: str | None = None) -> schemas.PaginatedListings:
    stmt = _apply_filters(select(Listing), city, category, source)
    if search:
        stmt = stmt.where(Listing.business_name.like(f"%{search}%"))  # bound param, not string SQL

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.scalars(
        stmt.order_by(Listing.business_name, Listing.id).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return schemas.PaginatedListings(
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
        items=[schemas.ListingOut.model_validate(item) for item in items],
    )
