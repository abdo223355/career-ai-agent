import re
import time
import logging
from pydantic import BaseModel, Field
from src.agent.types import AgentType
from src.agent.state import SupervisorState
from src.agent.registry import AGENT_REGISTRY
from src.prompts.supervisor import supervisor_prompt
from src.models.llm import llm

# Configure detailed debug logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

from src.agent.language import detect_conversation_language

# ── Fast-path: patterns that never need an LLM routing call ──────────────────
_SMALLTALK_PATTERNS = re.compile(
    r"^\s*("
    r"hi+|hello+|hey+|howdy|greetings|good (morning|afternoon|evening|day)|what'?s up|sup|yo|hola"
    r"|مرحبا+|اهلاً+|أهلاً+|السلام عليكم|صباح الخير|مساء الخير|كيف حالك|ازيك|ازيكوا|من انت|ماذا تفعل"
    r"|who are you|what are you|what can you do|introduce yourself"
    r"|[0-9]+\s*[\+\-\*/]\s*[0-9]+"   # math expressions
    r"|tell me a joke|joke|lol|haha|thanks|thank you|ok|okay|cool|great|bye|goodbye|شكرا|شكراً|تسلم|تمام|ماشى|ماشي|مع السلامة"
    r")\s*[\?!.]*\s*$",
    re.IGNORECASE
)

class SupervisorRoute(BaseModel):
    """
    Type-safe Pydantic structured output model for Supervisor routing decisions.
    """
    next_agent: AgentType = Field(description="The next specialized Worker Agent to execute, or FINISH.")
    reasoning: str = Field(description="Engineering rationale for the routing decision.")

# Supervisor LCEL Chain bound to the single shared production LLM instance
supervisor_chain = supervisor_prompt | llm.with_structured_output(SupervisorRoute)

def supervisor_node(state: SupervisorState) -> dict:
    """
    Supervisor Node: Analyzes state, detects user language, and routes to the right agent.

    Fast-paths (no LLM call):
      1. CV just uploaded  → CV_Reviewer
      2. Small talk / math → FINISH directly
      3. Worker already ran this turn → FINISH (prevents infinite loops)
    Full LLM routing only for genuine first-time career queries.
    """
    t_start = time.perf_counter()
    user_msg   = state.get("user_message", "")
    skills     = state.get("extracted_skills", [])
    goal       = state.get("career_goal", "Software Engineer")
    cv         = state.get("uploaded_cv")
    cv_text    = state.get("cv_text")
    analysis_status = state.get("analysis_status")
    roadmap    = state.get("roadmap")
    feedback   = state.get("interview_feedback")
    planner_out = state.get("planner_output", "")
    messages   = state.get("messages", [])
    worker_ran = state.get("worker_executed_this_turn", False)

    # ── Language Detection ───────────────────────────────────────────────────
    current_lang = state.get("detected_language") or state.get("preferred_language")
    lang = detect_conversation_language(
        user_message=user_msg,
        cv_text=cv_text or cv,
        messages=messages,
        current_detected=current_lang
    )
    print(f"[DEBUG - LANGUAGE DETECTED]: '{lang}' for message: '{user_msg[:40]}'")

    lang_state_update = {
        "detected_language": lang,
        "response_language": lang,
        "preferred_language": lang
    }

    # ── Fast-path 1: CV just uploaded — no LLM call ───────────────────────────
    if analysis_status == "pending" and (cv_text or cv):
        elapsed = (time.perf_counter() - t_start) * 1000
        print(f"[TIMING] Supervisor (CV fast-path): {elapsed:.1f} ms  [0 LLM calls]")
        return {
            "active_node": "supervisor_node",
            "next_agent": AgentType.CV_REVIEWER,
            "routing_reason": "CV uploaded and pending analysis — deterministically routing to CV_Reviewer.",
            "planner_output": f"next={AgentType.CV_REVIEWER.value} | CV pending analysis",
            "analysis_status": "complete",
            **lang_state_update
        }

    # ── Fast-path 2: Small talk / greetings / math — no LLM call ─────────────
    if _SMALLTALK_PATTERNS.match(user_msg):
        elapsed = (time.perf_counter() - t_start) * 1000
        print(f"[TIMING] Supervisor (small-talk fast-path): {elapsed:.1f} ms  [0 LLM calls]")
        return {
            "active_node": "supervisor_node",
            "next_agent": AgentType.FINISH,
            "routing_reason": "Small-talk / greeting / math detected — routing directly to final response.",
            "planner_output": f"next={AgentType.FINISH.value} | small-talk fast-path",
            "worker_executed_this_turn": False,
            **lang_state_update
        }

    # ── Fast-path 3: Worker already ran this turn → go to FINISH ─────────────
    if worker_ran:
        elapsed = (time.perf_counter() - t_start) * 1000
        print(f"[TIMING] Supervisor (worker-done fast-path): {elapsed:.1f} ms  [0 LLM calls]")
        return {
            "active_node": "supervisor_node",
            "next_agent": AgentType.FINISH,
            "routing_reason": "Worker already executed this turn — routing to final response synthesis.",
            "planner_output": f"next={AgentType.FINISH.value} | worker completed",
            **lang_state_update
        }

    completed = []
    if cv or cv_text: completed.append("CV_Parsed")
    if skills:        completed.append("Skills_Extracted")
    if roadmap:       completed.append("Roadmap_Generated")
    if feedback:      completed.append("Interview_Feedback_Generated")
    if "salary" in planner_out.lower() or "salary" in str(feedback).lower():
        completed.append("Salary_Info_Generated")

    print(f"\n[DEBUG] SUPERVISOR: routing for '{user_msg[:60]}'")

    t_llm = time.perf_counter()
    route_decision: SupervisorRoute = supervisor_chain.invoke({
        "user_message":          user_msg,
        "extracted_skills":      skills,
        "career_goal":           goal,
        "completed_outputs":     ", ".join(completed) if completed else "None",
        "has_cv":                bool(cv or cv_text),
        "has_skills":            bool(skills),
        "has_roadmap":           bool(roadmap),
        "has_interview_feedback":bool(feedback),
        "messages":              messages
    })
    llm_ms   = (time.perf_counter() - t_llm) * 1000
    total_ms = (time.perf_counter() - t_start) * 1000
    print(f"[TIMING] Supervisor LLM: {llm_ms:.1f} ms | Total: {total_ms:.1f} ms")
    print(f"[DEBUG] SUPERVISOR ROUTE: Next='{route_decision.next_agent.value}' | {route_decision.reasoning}")

    return {
        "active_node":    "supervisor_node",
        "next_agent":     route_decision.next_agent,
        "routing_reason": route_decision.reasoning,
        "planner_output": f"next={route_decision.next_agent.value} | {route_decision.reasoning}",
        **lang_state_update
    }

def supervisor_router(state: SupervisorState) -> str:
    """
    Supervisor Dynamic Router: Resolves next_agent Enum via central AGENT_REGISTRY.
    No hardcoded string comparisons!
    """
    next_agent = state.get("next_agent")
    
    if isinstance(next_agent, AgentType) and next_agent in AGENT_REGISTRY:
        target = AGENT_REGISTRY[next_agent]
        print(f"[DEBUG - ROUTER INVOCATION]: Routing to node '{target}'")
        return target
    
    # Fallback lookup from planner_output if next_agent is string
    planner_out = state.get("planner_output", "")
    for agent_enum, target_node in AGENT_REGISTRY.items():
        if f"next={agent_enum.value}" in planner_out:
            print(f"[DEBUG - ROUTER FALLBACK]: Routing to node '{target_node}'")
            return target_node
            
    print(f"[DEBUG - ROUTER FINISH]: Routing to 'final_response_node'")
    return AGENT_REGISTRY[AgentType.FINISH]
