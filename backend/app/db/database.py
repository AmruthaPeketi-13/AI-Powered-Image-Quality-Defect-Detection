"""SQLAlchemy database setup — SQLite for local dev, PostgreSQL for production.

The database backend is selected via the DATABASE_URL environment variable
(pydantic settings field `database_url`). Examples:
  - Local:      sqlite:///./data/results.db  (default)
  - Supabase:   postgresql://user:pass@host:port/dbname
"""
import logging
import time

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker  # declarative_base moved to orm in SA 2.0

from app.config import settings

logger = logging.getLogger("uvicorn.error")


def _engine_url(url: str) -> str:
    """Normalise postgres:// -> postgresql:// so SQLAlchemy recognises it."""
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://"):]
    return url


def _engine_kwargs(url: str) -> dict:
    """Return per-dialect engine kwargs.

    - SQLite needs check_same_thread=False.
    - Supabase (like most managed Postgres) requires SSL.
    """
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}

    url = _engine_url(url)
    if url.startswith("postgresql"):
        # Validate the URL early so a malformed connection string fails with a
        # clear message at startup instead of a cryptic socket error.
        parsed = make_url(url)
        if not parsed.host:
            raise ValueError(
                f"Invalid DATABASE_URL: host is missing. Got: {url!r}. "
                "Use the full Supabase URI from Project Settings -> Database "
                "-> Connection string -> URI."
            )
        # Supabase requires SSL for external connections.
        return {"connect_args": {"sslmode": "require"}}

    return {}


engine = create_engine(_engine_url(settings.database_url), **_engine_kwargs(settings.database_url))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(retries=5, delay=3.0):
    """Create all tables on startup.

    Connection attempts are retried so a transient network blip during a cold
    start (common with managed Postgres like Supabase) does not crash the app.
    """
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            _log_connection()
            return
        except Exception as exc:  # noqa: BLE001 - connection errors are retried
            last_exc = exc
            logger.warning(
                "DB init attempt %d/%d failed: %s", attempt, retries, exc
            )
            if attempt < retries:
                time.sleep(delay)
    raise last_exc


def _log_connection():
    """Log the resolved DB host for easy debugging (never logs the password)."""
    url = _engine_url(settings.database_url)
    if url.startswith("postgresql"):
        try:
            parsed = make_url(url)
            logger.info(
                "Connected to Postgres host=%s port=%s user=%s",
                parsed.host or "(no host)",
                parsed.port,
                parsed.username,
            )
        except Exception:  # noqa: BLE001
            logger.info("Connected to Postgres (host detail unavailable)")
    else:
        logger.info("Using local SQLite database")
