"""
src/cache
=========
Intelligent response cache package for the Career AI Agent.

Provides SQLite-backed persistent caching of LLM responses to reduce
token usage. The cache is keyed by (question_hash, experience_level)
so different experience levels always get separate cached entries.

Public API
----------
    from src.cache import ResponseCacheService, init_cache_db

    init_cache_db()
    service = ResponseCacheService()

    cached = service.lookup(question_hash="abc123", experience_level="Senior")
    if cached:
        return cached

    response = run_llm(...)
    service.save(
        question_hash="abc123",
        normalized_question="what is langgraph",
        response=response,
        response_type="general",
        experience_level="Senior",
    )
"""

from src.cache.database import init_cache_db
from src.cache.service import ResponseCacheService

__all__ = ["ResponseCacheService", "init_cache_db"]
