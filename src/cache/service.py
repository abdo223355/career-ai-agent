"""
src/cache/service.py
====================
High-level response cache service used by LangGraph cache nodes.

Wraps the SQLAlchemy session and provides three operations:
    lookup  — exact match by (question_hash, experience_level)
    save    — upsert a new or updated cache entry
    stats   — aggregate usage statistics for monitoring/sidebar display

Thread safety
-------------
Each method opens its own session and closes it immediately, which is
safe for Streamlit's multi-threaded execution model.
"""

from __future__ import annotations

import datetime
import logging
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError

from src.cache.database import SessionLocal, init_cache_db
from src.cache.models import ResponseCacheEntry

logger = logging.getLogger(__name__)


class ResponseCacheService:
    """
    Application-level service for reading from and writing to the
    persistent LLM response cache.

    Usage
    -----
        service = ResponseCacheService()

        # Before LLM call
        cached = service.lookup("abc123", "Senior")
        if cached:
            return cached   # skip LLM

        # After LLM call
        service.save("abc123", "what is langgraph", response, "general", "Senior")
    """

    def __init__(self) -> None:
        # Ensure the table exists on first instantiation
        try:
            init_cache_db()
        except Exception as exc:
            logger.warning("[Cache] Could not initialise cache DB: %s", exc)

    # ── Lookup ────────────────────────────────────────────────────────────────

    def lookup(
        self,
        question_hash: str,
        experience_level: str = "Senior",
    ) -> Optional[str]:
        """
        Look up a cached response by (question_hash, experience_level).

        On a hit, increments usage_count and updates updated_at.

        Parameters
        ----------
        question_hash:
            SHA-256 hex digest produced by :func:`~src.cache.normalizer.hash_question`.
        experience_level:
            The candidate's current experience level setting.

        Returns
        -------
        str | None
            The cached response text, or None if no entry exists.
        """
        try:
            with SessionLocal() as session:
                entry: Optional[ResponseCacheEntry] = (
                    session.query(ResponseCacheEntry)
                    .filter_by(
                        question_hash=question_hash,
                        experience_level=experience_level,
                    )
                    .first()
                )

                if entry is None:
                    logger.debug("[Cache] MISS  hash=%s level=%s", question_hash[:8], experience_level)
                    return None

                # Increment hit counter
                entry.usage_count += 1
                entry.updated_at = datetime.datetime.utcnow()
                session.commit()

                logger.info(
                    "[Cache] HIT   hash=%s level=%s hits=%d",
                    question_hash[:8],
                    experience_level,
                    entry.usage_count,
                )
                return entry.response

        except SQLAlchemyError as exc:
            logger.error("[Cache] lookup error: %s", exc)
            return None

    # ── Save ──────────────────────────────────────────────────────────────────

    def save(
        self,
        question_hash: str,
        normalized_question: str,
        response: str,
        response_type: str = "general",
        experience_level: str = "Senior",
    ) -> bool:
        """
        Persist or update a cache entry for future reuse.

        If an entry with the same (question_hash, experience_level) already
        exists, the response text is updated and updated_at is refreshed.
        Otherwise a new entry is created.

        Parameters
        ----------
        question_hash:
            SHA-256 hex digest of the normalized question.
        normalized_question:
            Human-readable normalized form (for debugging).
        response:
            The full LLM response text to cache.
        response_type:
            Category tag ("general" | "roadmap" | "interview" | "salary" | "skill_gap").
        experience_level:
            The candidate's experience level at time of generation.

        Returns
        -------
        bool
            True on success, False on database error.
        """
        if not response or not response.strip():
            logger.debug("[Cache] Skipping save — empty response.")
            return False

        try:
            with SessionLocal() as session:
                existing: Optional[ResponseCacheEntry] = (
                    session.query(ResponseCacheEntry)
                    .filter_by(
                        question_hash=question_hash,
                        experience_level=experience_level,
                    )
                    .first()
                )

                if existing:
                    existing.response = response
                    existing.response_type = response_type
                    existing.updated_at = datetime.datetime.utcnow()
                    logger.debug("[Cache] UPDATED hash=%s level=%s", question_hash[:8], experience_level)
                else:
                    entry = ResponseCacheEntry(
                        question_hash=question_hash,
                        normalized_question=normalized_question,
                        response=response,
                        response_type=response_type,
                        experience_level=experience_level,
                        usage_count=0,
                    )
                    session.add(entry)
                    logger.info("[Cache] SAVED  hash=%s level=%s", question_hash[:8], experience_level)

                session.commit()
                return True

        except SQLAlchemyError as exc:
            logger.error("[Cache] save error: %s", exc)
            return False

    # ── Stats ─────────────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """
        Return aggregate cache statistics for sidebar display.

        Returns
        -------
        dict with keys:
            total_entries  — number of unique cached questions
            total_hits     — sum of all usage_count values
            top_level      — most-cached experience level
        """
        try:
            with SessionLocal() as session:
                total_entries = session.query(ResponseCacheEntry).count()
                total_hits_row = session.query(
                    ResponseCacheEntry.usage_count
                ).all()
                total_hits = sum(r[0] for r in total_hits_row) if total_hits_row else 0

                # Most common experience level
                from sqlalchemy import func
                top_row = (
                    session.query(
                        ResponseCacheEntry.experience_level,
                        func.count(ResponseCacheEntry.id).label("cnt"),
                    )
                    .group_by(ResponseCacheEntry.experience_level)
                    .order_by(func.count(ResponseCacheEntry.id).desc())
                    .first()
                )
                top_level = top_row[0] if top_row else "—"

                return {
                    "total_entries": total_entries,
                    "total_hits": total_hits,
                    "top_level": top_level,
                }
        except SQLAlchemyError as exc:
            logger.error("[Cache] stats error: %s", exc)
            return {"total_entries": 0, "total_hits": 0, "top_level": "—"}
