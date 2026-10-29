"""ORM model for the ``listing_master`` table (mirrors database/schema.sql)."""
from datetime import datetime

from sqlalchemy import CHAR, DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Listing(Base):
    __tablename__ = "listing_master"
    __table_args__ = (
        Index("idx_city", "city"),
        Index("idx_category", "category"),
        Index("idx_source", "source"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(String(500))
    phone: Mapped[str | None] = mapped_column(String(30))
    source: Mapped[str] = mapped_column(String(50))
    listing_hash: Mapped[str] = mapped_column(CHAR(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<Listing {self.id} {self.business_name!r} ({self.city})>"
