"""Application settings, read from environment variables / backend/.env."""
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

# backend/.env -> os.environ (real environment variables win)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _split(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    mysql_host: str = os.getenv("MYSQL_HOST", "localhost")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_user: str = os.getenv("MYSQL_USER", "listings_user")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "listings_pass")
    mysql_database: str = os.getenv("MYSQL_DATABASE", "business_listings")
    # Optional full override, e.g. "sqlite+pysqlite:///:memory:" in tests
    database_url_override: str | None = os.getenv("DATABASE_URL")
    cors_origins: list[str] = field(default_factory=lambda: _split(
        os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    ))

    @property
    def database_url(self) -> str | URL:
        if self.database_url_override:
            return self.database_url_override
        # URL.create escapes special characters in the password safely
        return URL.create(
            "mysql+pymysql",
            username=self.mysql_user,
            password=self.mysql_password,
            host=self.mysql_host,
            port=self.mysql_port,
            database=self.mysql_database,
            query={"charset": "utf8mb4"},
        )


settings = Settings()
