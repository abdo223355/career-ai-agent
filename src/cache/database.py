"""
src/cache/database.py
=====================
SQLAlchemy engine, session factory, and database initialisation for the
response cache.

The cache database is intentionally separate from the LangGraph memory
checkpointer database (career_agent_production.db) to avoid schema conflicts
and allow independent lifecycle management.

Usage
-----
    from src.cache.database import init_cache_db, SessionLocal

    init_cache_db()                # creates table if not exists (idempotent)
    with SessionLocal() as session:
        ...
"""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.cache.models import Base


def _resolve_db_path() -> str:
    """
    Resolves the absolute path to the cache SQLite database.

    Priority:
      1. CACHE_DB_PATH environment variable (absolute or relative to CWD)
      2. Default: storage/response_cache.db relative to the project root
    """
    env_path = os.environ.get("CACHE_DB_PATH", "").strip()
    if env_path:
        db_path = Path(env_path)
    else:
        # Project root is two levels above this file (src/cache/database.py)
        project_root = Path(__file__).resolve().parents[2]
        db_path = project_root / "storage" / "response_cache.db"

    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return str(db_path)


# ── Engine — check_same_thread=False needed for Streamlit's threading model ──
_DB_URL = f"sqlite:///{_resolve_db_path()}"
engine = create_engine(
    _DB_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# ── Session factory ───────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def init_cache_db() -> None:
    """
    Creates the response_cache table if it does not already exist.
    Safe to call multiple times (idempotent).
    """
    Base.metadata.create_all(bind=engine)
    print(f"[Cache] Database initialised at: {_DB_URL}")
