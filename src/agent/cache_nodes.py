"""
src/agent/cache_nodes.py
========================
LangGraph nodes for the intelligent response cache pipeline.

Graph integration
-----------------
These three nodes wrap the cache lookup/save operations as first-class
LangGraph nodes so every workflow automatically benefits from caching
without modifying individual worker nodes.

    START
      → normalize_question_node      (normalise + hash user_message)
      → cache_lookup_node            (check DB)
      → conditional_edge
            cache HIT  → final_response_node → END
            cache MISS → supervisor_node → ... → final_response_node
                                             → save_cache_node → END

CV-upload turns are automatically excluded from caching because
cache_lookup_node detects an incoming file (cv_bytes present) and
sets cache_hit=False, forwarding directly to the supervisor.
"""

from __future__ import annotations

import logging
import functools
from typing import Optional

from src.cache.normalizer import normalize_question, hash_question
from src.config.constants import DEFAULT_EXPERIENCE_LEVEL

logger = logging.getLogger(__name__)


# ── Lazy singleton cache service ─────────────────────────────────────────────
@functools.lru_cache(maxsize=1)
def _get_cache_service():
    """Returns a single shared ResponseCacheService instance per process."""
    from src.cache.service import ResponseCacheService
    return ResponseCacheService()


# ─────────────────────────────────────────────────────────────────────────────
# Node 1: normalize_question_node
# ─────────────────────────────────────────────────────────────────────────────
def normalize_question_node(state: dict) -> dict:
    """
    Cache Pipeline Node 1: Normalizes the user message and computes its hash.

    Sets:
        normalized_question  — lowercase, whitespace-collapsed, punctuation-stripped
        question_hash        — SHA-256 hex of normalized_question
        cache_hit            — reset to False at the start of each turn

    This node runs before every graph invocation so the hash is always
    available to cache_lookup_node and save_cache_node.
    """
    user_msg: str = state.get("user_message", "")
    normalized = normalize_question(user_msg)
    q_hash = hash_question(normalized) if normalized else ""

    logger.debug(
        "[normalize_question_node] raw=%r  normalized=%r  hash=%s",
        user_msg[:60],
        normalized[:60],
        q_hash[:8],
    )

    return {
        "normalized_question": normalized,
        "question_hash": q_hash,
        "cache_hit": False,          # reset every turn
        "active_node": "normalize_question_node",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 2: cache_lookup_node
# ─────────────────────────────────────────────────────────────────────────────
def cache_lookup_node(state: dict) -> dict:
    """
    Cache Pipeline Node 2: Searches the persistent response cache.

    Exclusions (no cache lookup performed):
        - CV file is being uploaded (cv_bytes present) — document-specific,
          must never be cached
        - question_hash is empty (normalization produced nothing)

    On CACHE HIT:
        Sets final_response + cache_hit=True + worker_executed_this_turn=True
        so the supervisor fast-paths directly to final_response_node, which
        synthesises the cached text without calling the LLM.

    On CACHE MISS:
        Returns cache_hit=False — graph continues to supervisor_node.
    """
    q_hash: Optional[str] = state.get("question_hash", "")
    experience_level: str = state.get("experience_level") or DEFAULT_EXPERIENCE_LEVEL

    # ── Exclusion: CV upload in progress ────────────────────────────────────
    if state.get("cv_bytes"):
        logger.debug("[cache_lookup_node] CV upload detected — skipping cache.")
        return {
            "cache_hit": False,
            "active_node": "cache_lookup_node",
        }

    # ── Exclusion: empty hash (e.g., empty message) ──────────────────────────
    if not q_hash:
        logger.debug("[cache_lookup_node] Empty hash — skipping cache.")
        return {
            "cache_hit": False,
            "active_node": "cache_lookup_node",
        }

    # ── Cache lookup ─────────────────────────────────────────────────────────
    try:
        service = _get_cache_service()
        cached_response: Optional[str] = service.lookup(
            question_hash=q_hash,
            experience_level=experience_level,
        )
    except Exception as exc:
        logger.warning("[cache_lookup_node] Lookup failed (non-fatal): %s", exc)
        cached_response = None

    if cached_response:
        logger.info(
            "[cache_lookup_node] HIT  hash=%s level=%s",
            q_hash[:8],
            experience_level,
        )
        return {
            "cache_hit": True,
            "final_response": cached_response,
            # Mark worker as done so supervisor routes to final_response_node
            "worker_executed_this_turn": True,
            "latest_worker_output": cached_response,
            "active_node": "cache_lookup_node",
        }

    logger.debug("[cache_lookup_node] MISS hash=%s level=%s", q_hash[:8], experience_level)
    return {
        "cache_hit": False,
        "active_node": "cache_lookup_node",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Node 3: save_cache_node
# ─────────────────────────────────────────────────────────────────────────────
def save_cache_node(state: dict) -> dict:
    """
    Cache Pipeline Node 3: Persists the final LLM response to the cache.

    Only saves when:
        - cache_hit is False (don't re-save a response served from cache)
        - final_response is non-empty
        - question_hash is non-empty
        - The turn was NOT a CV-upload turn (cv_bytes absent)

    The response_type is inferred from the active_node that generated the
    response, providing useful categorisation for future analytics.
    """
    cache_hit: bool = state.get("cache_hit", False)
    final_response: str = state.get("final_response", "")
    q_hash: Optional[str] = state.get("question_hash", "")
    normalized_q: str = state.get("normalized_question", "")
    experience_level: str = state.get("experience_level") or DEFAULT_EXPERIENCE_LEVEL
    active_node: str = state.get("active_node", "final_response_node")

    # ── Conditions that prevent saving ───────────────────────────────────────
    if cache_hit:
        logger.debug("[save_cache_node] Already a cache hit — not re-saving.")
        return {"active_node": "save_cache_node"}

    if not final_response or not q_hash:
        logger.debug("[save_cache_node] Missing response or hash — skipping save.")
        return {"active_node": "save_cache_node"}

    if state.get("cv_bytes"):
        logger.debug("[save_cache_node] CV upload turn — skipping save.")
        return {"active_node": "save_cache_node"}

    # ── Infer response_type from last active node ─────────────────────────────
    _type_map = {
        "learning_roadmap_node": "roadmap",
        "interview_coach_node": "interview",
        "salary_advisor_node": "salary",
        "skill_extraction_node": "skill_gap",
        "resume_parsing_node": "cv_review",
        "job_recommendation_node": "job_recommendation",
    }
    response_type = _type_map.get(active_node, "general")

    # ── Persist ───────────────────────────────────────────────────────────────
    try:
        service = _get_cache_service()
        service.save(
            question_hash=q_hash,
            normalized_question=normalized_q,
            response=final_response,
            response_type=response_type,
            experience_level=experience_level,
        )
        logger.info(
            "[save_cache_node] SAVED hash=%s type=%s level=%s",
            q_hash[:8],
            response_type,
            experience_level,
        )
    except Exception as exc:
        logger.warning("[save_cache_node] Save failed (non-fatal): %s", exc)

    return {"active_node": "save_cache_node"}


# ── Conditional edge function ─────────────────────────────────────────────────
def cache_router(state: dict) -> str:
    """
    Conditional edge after cache_lookup_node.

    Returns
    -------
    "cache_hit"   if a cached response was found (→ final_response_node)
    "cache_miss"  if no cached response (→ supervisor_node)
    """
    if state.get("cache_hit"):
        logger.debug("[cache_router] Routing to final_response_node (cache hit)")
        return "cache_hit"
    logger.debug("[cache_router] Routing to supervisor_node (cache miss)")
    return "cache_miss"
