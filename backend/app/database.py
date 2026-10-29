"""SQLAlchemy engine, session factory and the FastAPI ``get_db`` dependency."""
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import settings

url = settings.database_url

if str(url).startswith("sqlite"):
    # Used only by the test-suite: one shared in-memory database.
    engine = create_engine(url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
else:
    engine = create_engine(
        url,
        pool_pre_ping=True,   # transparently replace connections MySQL has closed
        pool_recycle=3600,    # recycle before MySQL's wait_timeout kicks in
        pool_size=5,
        max_overflow=10,
    )

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Parent class of every ORM model."""


def get_db() -> Iterator[Session]:
    """Open one session per request and always close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
