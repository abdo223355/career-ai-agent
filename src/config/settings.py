"""
src/config/settings.py
======================
Centralised application configuration.

All values are loaded from environment variables (via a .env file).
Required secrets are validated at import time so the application fails
fast with a clear error message rather than at the point of first use.

Usage
-----
    from src.config.settings import settings

    print(settings.MODEL_NAME)
    print(settings.VECTOR_DB_PATH)
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env — must happen before any os.getenv() call.
# override=False means real environment variables always win over .env values,
# which is the correct behaviour in CI/CD and container deployments.
# ---------------------------------------------------------------------------
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_ENV_FILE, override=False)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _require(key: str) -> str:
    """
    Return the value of an environment variable.

    Raises
    ------
    EnvironmentError
        If the variable is absent or empty, with a clear message telling the
        developer exactly which key is missing and where to set it.
    """
    value = os.getenv(key, "").strip()
    if not value:
        raise EnvironmentError(
            f"\n\n[config] Required environment variable '{key}' is missing or empty.\n"
            f"  → Copy .env.example to .env and set a real value for {key}.\n"
        )
    return value


def _optional(key: str, default: str = "") -> str:
    """Return an optional environment variable, falling back to *default*."""
    return os.getenv(key, default).strip()


def _bool(key: str, default: bool = False) -> bool:
    """Parse a boolean environment variable (true/1/yes → True)."""
    raw = os.getenv(key, str(default)).strip().lower()
    return raw in {"true", "1", "yes"}


def _int(key: str, default: int) -> int:
    """Parse an integer environment variable, falling back to *default*."""
    raw = os.getenv(key, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(
            f"[config] Environment variable '{key}' must be an integer, got: {raw!r}"
        ) from exc


def _float(key: str, default: float) -> float:
    """Parse a float environment variable, falling back to *default*."""
    raw = os.getenv(key, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(
            f"[config] Environment variable '{key}' must be a float, got: {raw!r}"
        ) from exc


# ---------------------------------------------------------------------------
# Settings dataclass (plain Python — no Pydantic dependency required)
# ---------------------------------------------------------------------------

class _Settings:
    """
    Immutable-by-convention configuration object.

    Attribute names intentionally match the environment variable names
    so that the mapping is obvious at a glance.
    """

    # ── Secrets ──────────────────────────────────────────────────────────────
    # Validated at import time — the app will not start without these.
    OPENROUTER_API_KEY: str = _require("OPENROUTER_API_KEY")

    # LangSmith is optional: if tracing is disabled the key is not required.
    LANGSMITH_TRACING: bool = _bool("LANGSMITH_TRACING", default=False)
    LANGSMITH_API_KEY: str = (
        _require("LANGSMITH_API_KEY") if _bool("LANGSMITH_TRACING", default=False) else ""
    )
    LANGSMITH_PROJECT: str = _optional("LANGSMITH_PROJECT", default="career-ai-agent")

    # ── Application ───────────────────────────────────────────────────────────
    APP_ENV: str = _optional("APP_ENV", default="development")
    APP_LOG_LEVEL: str = _optional("APP_LOG_LEVEL", default="INFO")

    # ── LLM ───────────────────────────────────────────────────────────────────
    MODEL_NAME: str = _optional("MODEL_NAME", default="openai/gpt-4o-mini")
    TEMPERATURE: float = _float("TEMPERATURE", default=0.0)

    # ── Embeddings ────────────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = _optional(
        "EMBEDDING_MODEL",
        default="sentence-transformers/all-MiniLM-L6-v2",
    )

    # ── RAG pipeline ─────────────────────────────────────────────────────────
    TOP_K: int = _int("TOP_K", default=5)
    CHUNK_SIZE: int = _int("CHUNK_SIZE", default=1000)
    CHUNK_OVERLAP: int = _int("CHUNK_OVERLAP", default=200)

    # ── Vector store ─────────────────────────────────────────────────────────
    VECTOR_DB_PATH: Path = Path(_optional("VECTOR_DB_PATH", default="storage/vector_db"))
    CHROMA_COLLECTION_NAME: str = _optional(
        "CHROMA_COLLECTION_NAME", default="career_documents"
    )

    # ── Relational database ───────────────────────────────────────────────────
    DATABASE_URL: str = _optional(
        "DATABASE_URL", default="sqlite:///storage/career_ai_agent.db"
    )

    # ── MCP server ────────────────────────────────────────────────────────────
    MCP_SERVER_HOST: str = _optional("MCP_SERVER_HOST", default="localhost")
    MCP_SERVER_PORT: int = _int("MCP_SERVER_PORT", default=8080)

    # ── Derived helpers ───────────────────────────────────────────────────────

    @property
    def is_production(self) -> bool:
        """True when running in a production environment."""
        return self.APP_ENV.lower() == "production"

    @property
    def is_development(self) -> bool:
        """True when running in a development environment."""
        return self.APP_ENV.lower() == "development"

    def __repr__(self) -> str:
        """
        Safe repr — secrets are redacted so this is safe to log.
        """
        return (
            f"Settings("
            f"APP_ENV={self.APP_ENV!r}, "
            f"MODEL_NAME={self.MODEL_NAME!r}, "
            f"EMBEDDING_MODEL={self.EMBEDDING_MODEL!r}, "
            f"TOP_K={self.TOP_K}, "
            f"CHUNK_SIZE={self.CHUNK_SIZE}, "
            f"CHUNK_OVERLAP={self.CHUNK_OVERLAP}, "
            f"TEMPERATURE={self.TEMPERATURE}, "
            f"VECTOR_DB_PATH={self.VECTOR_DB_PATH!r}, "
            f"LANGSMITH_TRACING={self.LANGSMITH_TRACING}"
            f")"
        )


# ---------------------------------------------------------------------------
# Public singleton — import this throughout the codebase.
#
#     from src.config.settings import settings
#
# ---------------------------------------------------------------------------
settings = _Settings()
