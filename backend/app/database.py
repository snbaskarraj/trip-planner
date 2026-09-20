import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


def _database_url() -> str:
    # Prefer the process env so a Render dashboard value cannot be ignored.
    url = (os.environ.get("DATABASE_URL") or settings.database_url).strip()
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def _require_postgres_on_render(url: str) -> None:
    """Render sets RENDER=true. Refuse the SQLite default so writes cannot
    silently miss trip-planner-db.
    """
    if os.environ.get("RENDER") and url.startswith("sqlite"):
        raise RuntimeError(
            "DATABASE_URL is SQLite on Render. On the web service "
            "(trip-planner-2-3t88), set DATABASE_URL to the Internal "
            "Database URL from trip-planner-db, then redeploy."
        )


_resolved_url = _database_url()
_require_postgres_on_render(_resolved_url)

connect_args = {}
if _resolved_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(_resolved_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
