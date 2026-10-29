"""FastAPI application entry point.

Run (from the backend/ folder):
    uvicorn app.main:app --reload
Docs:
    http://localhost:8000/docs   (Swagger UI)
    http://localhost:8000/redoc  (ReDoc)
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from .config import settings
from .database import Base, engine
from .routers import dashboard, listings

log = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create listing_master if it does not exist yet (no-op when schema.sql ran).
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as exc:
        log.error("Database not reachable at startup: %s", exc.orig)
    yield
    engine.dispose()


app = FastAPI(
    title="Business Listings API",
    description="Stores scraped business listings in MySQL and serves aggregated "
                "counts for the React dashboard.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(OperationalError)
async def database_unavailable(request: Request, exc: OperationalError):
    """MySQL down / wrong credentials -> clean 503 instead of a 500 stack trace."""
    log.error("Database error on %s: %s", request.url.path, exc.orig)
    return JSONResponse(status_code=503, content={"detail": "Database unavailable"})


app.include_router(listings.router)
app.include_router(dashboard.router)


@app.get("/api/health", tags=["Health"], summary="API and database health check")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
