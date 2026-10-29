"""Pydantic models: validate incoming JSON and shape outgoing JSON."""
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
Label = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
SourceName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]

MAX_BULK_SIZE = 5000


# ---------------------------------------------------------------- listings
class ListingBase(BaseModel):
    business_name: Name
    category: Label
    city: Label
    address: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=30)
    source: SourceName

    @field_validator("address", "phone", mode="before")
    @classmethod
    def blank_to_none(cls, value):
        """Treat "" or "   " the same as a missing value."""
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ListingCreate(ListingBase):
    model_config = ConfigDict(json_schema_extra={"example": {
        "business_name": "Apollo Pharmacy",
        "category": "Pharmacy",
        "city": "Bengaluru",
        "address": "12, 100 Feet Road, Indiranagar, Bengaluru, 560038",
        "phone": "+918022223333",
        "source": "OpenStreetMap",
    }})


class ListingOut(ListingBase):
    model_config = ConfigDict(from_attributes=True)  # build from ORM objects

    id: int
    created_at: datetime


class BulkInsertRequest(BaseModel):
    listings: list[ListingCreate] = Field(min_length=1, max_length=MAX_BULK_SIZE)


class BulkInsertResponse(BaseModel):
    received: int
    inserted: int
    duplicates_skipped: int


class PaginatedListings(BaseModel):
    total: int
    page: int
    page_size: int
    pages: int
    items: list[ListingOut]


# --------------------------------------------------------------- dashboard
class CountItem(BaseModel):
    label: str
    count: int


class CountResponse(BaseModel):
    dimension: str
    total: int
    items: list[CountItem]


class SummaryResponse(BaseModel):
    total_listings: int
    cities: int
    categories: int
    sources: int
    with_phone: int
