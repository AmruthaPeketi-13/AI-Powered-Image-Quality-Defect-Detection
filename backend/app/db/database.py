"""SQLAlchemy database setup — SQLite for local dev, PostgreSQL for production.

The database backend is selected via the DATABASE_URL environment variable
(pydantic settings field `database_url`). Examples:
  - Local:      sqlite:///./data/results.db  (default)
  - Supabase:   postgresql://user:pass@host:port/dbname
"""
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker  # declarative_base moved to orm in SA 2.0

from app.config import settings


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


def init_db():
    """Create all tables on startup."""
    Base.metadata.create_all(bind=engine)
