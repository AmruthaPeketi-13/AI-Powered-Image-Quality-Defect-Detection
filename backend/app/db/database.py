"""SQLAlchemy database setup — SQLite for local dev, PostgreSQL for production.

The database backend is selected via the DATABASE_URL environment variable
(pydantic settings field `database_url`). Examples:
  - Local:      sqlite:///./data/results.db  (default)
  - Supabase:   postgresql://user:pass@host:port/dbname
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker  # declarative_base moved to orm in SA 2.0

from app.config import settings


def _engine_kwargs(url: str) -> dict:
    """Return per-dialect engine kwargs (SQLite needs check_same_thread=False)."""
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}


engine = create_engine(settings.database_url, **_engine_kwargs(settings.database_url))
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
