from langgraph.graph import StateGraph, START, END
from src.agent.state import SupervisorState
from src.agent.registry import AGENT_REGISTRY, NODE_FUNCTION_REGISTRY
from src.agent.supervisor import supervisor_node, supervisor_router
from src.agent.cache_nodes import (
    normalize_question_node,
    cache_lookup_node,
    save_cache_node,
    cache_router,
)

builder = StateGraph(SupervisorState)

# ── Cache pipeline nodes ──────────────────────────────────────────────────────
builder.add_node("normalize_question_node", normalize_question_node)
builder.add_node("cache_lookup_node", cache_lookup_node)
builder.add_node("save_cache_node", save_cache_node)

# ── Executive Supervisor Node ─────────────────────────────────────────────────
builder.add_node("supervisor_node", supervisor_node)

# ── Specialized Worker Nodes (via registry) ───────────────────────────────────
for node_name, node_func in NODE_FUNCTION_REGISTRY.items():
    builder.add_node(node_name, node_func)

# ── Entry point: normalize first, then check cache ────────────────────────────
builder.add_edge(START, "normalize_question_node")
builder.add_edge("normalize_question_node", "cache_lookup_node")

# ── Cache conditional edge ────────────────────────────────────────────────────
# HIT  → final_response_node (skip LLM worker pipeline)
# MISS → supervisor_node     (full multi-agent execution)
builder.add_conditional_edges(
    "cache_lookup_node",
    cache_router,
    {
        "cache_hit":  "final_response_node",
        "cache_miss": "supervisor_node",
    },
)

# ── Supervisor dynamic routing edges ─────────────────────────────────────────
builder.add_conditional_edges(
    "supervisor_node",
    supervisor_router,
    {
        "upload_cv_node":      "upload_cv_node",
        "resume_parsing_node": "resume_parsing_node",
        "skill_extraction_node": "skill_extraction_node",
        "learning_roadmap_node": "learning_roadmap_node",
        "interview_coach_node":  "interview_coach_node",
        "salary_advisor_node":   "salary_advisor_node",
        "job_matching_node":     "job_matching_node",
        "project_recommender_node": "project_recommender_node",
        "final_response_node":   "final_response_node",
    },
)

# ── upload_cv_node feeds back to supervisor (pending analysis) ────────────────
builder.add_edge("upload_cv_node", "supervisor_node")

# ── Worker nodes return to supervisor for verification loop ───────────────────
builder.add_edge("resume_parsing_node",    "supervisor_node")
builder.add_edge("skill_extraction_node",  "supervisor_node")
builder.add_edge("learning_roadmap_node",  "supervisor_node")
builder.add_edge("interview_coach_node",   "supervisor_node")
builder.add_edge("salary_advisor_node",    "supervisor_node")
builder.add_edge("job_matching_node",      "supervisor_node")
builder.add_edge("project_recommender_node", "supervisor_node")

# ── final_response_node → save_cache_node → END ───────────────────────────────
builder.add_edge("final_response_node", "save_cache_node")
builder.add_edge("save_cache_node", END)

# Compiled production multi-agent graph
graph = builder.compile()
