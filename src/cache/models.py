"""
src/cache/models.py
===================
SQLAlchemy ORM model for the response cache table.

Schema
------
    id                  Auto-incrementing primary key
    question_hash       SHA-256 of the normalized question (indexed)
    normalized_question Human-readable normalized form for debugging
    response            The full LLM response text
    response_type       Category tag: "general" | "roadmap" | "interview" | "salary" | "skill_gap"
    experience_level    "Internship" | "Junior" | "Mid Level" | "Senior"
    created_at          ISO 8601 UTC timestamp of first cache write
    updated_at          ISO 8601 UTC timestamp of last cache hit or update
    usage_count         Number of times this entry has been served from cache
"""

from __future__ import annotations

import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ResponseCacheEntry(Base):
    """Maps to the `response_cache` table in SQLite."""

    __tablename__ = "response_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_hash = Column(String(64), nullable=False, index=True)
    normalized_question = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    response_type = Column(String(50), nullable=False, default="general")
    experience_level = Column(String(20), nullable=False, default="Senior")
    created_at = Column(
        DateTime(timezone=False),
        nullable=False,
        default=datetime.datetime.utcnow,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=False),
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
    usage_count = Column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return (
            f"ResponseCacheEntry(id={self.id}, hash={self.question_hash[:8]}..., "
            f"level={self.experience_level!r}, hits={self.usage_count})"
        )
