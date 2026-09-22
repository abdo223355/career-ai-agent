from typing_extensions import TypedDict, Annotated
from typing import List, Dict, Optional, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from src.agent.types import AgentType

class CareerState(TypedDict):
    """
    Base shared state schema for the Career AI Agent.
    """
    messages: Annotated[list[AnyMessage], add_messages]
    user_message: str
    active_node: str
    # ── legacy CV field (kept for backward compat with existing nodes) ──────
    uploaded_cv: Optional[str]
    extracted_skills: List[str]
    career_goal: Optional[str]
    planner_output: Optional[str]
    roadmap: Optional[Dict[str, Any]]
    recommended_courses: List[Dict[str, str]]
    interview_feedback: Optional[str]
    retrieved_documents: List[Any]
    retrieved_jobs: List[Dict[str, Any]]
    final_response: str
    # ── CV upload pipeline fields ────────────────────────────────────────────
    cv_bytes: Optional[bytes]            # raw file bytes from UI (cleared after parsing)
    cv_filename: Optional[str]           # original uploaded filename
    cv_text: Optional[str]              # full extracted plain text from PDF/DOCX
    cv_upload_timestamp: Optional[str]  # ISO 8601 upload timestamp
    cv_metadata: Optional[Dict[str, Any]]  # page_count, file_size, format, etc.
    skills: List[str]                   # alias-friendly mirror of extracted_skills
    resume_summary: Optional[str]       # short LLM-generated CV summary
    analysis_status: Optional[str]      # "pending" | "complete" | "error"
    # ── per-turn execution tracking ──────────────────────────────────────────
    latest_worker_output: Optional[str]
    worker_executed_this_turn: Optional[bool]
    # ── Multilingual & Language Detection fields ────────────────────────────
    preferred_language: Optional[str]   # "ar" | "en"
    response_language: Optional[str]    # "ar" | "en"
    detected_language: Optional[str]    # "ar" | "en"
    # ── Experience Level ─────────────────────────────────────────────────────
    experience_level: Optional[str]     # "Internship" | "Junior" | "Mid Level" | "Senior"
    # ── Intelligent Response Cache ───────────────────────────────────────────
    cache_hit: Optional[bool]           # True if response served from cache
    normalized_question: Optional[str]  # normalized form of user_message
    question_hash: Optional[str]        # SHA-256 of normalized_question


class SupervisorState(CareerState, total=False):
    """
    Extended state schema for Multi-Agent Orchestration.
    Extends CareerState without breaking previous notebook contracts.
    """
    next_agent: Optional[AgentType]
    routing_reason: Optional[str]

__all__ = ["CareerState", "SupervisorState"]
