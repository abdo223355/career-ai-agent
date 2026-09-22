from src.agent.state import CareerState

def career_router(state: CareerState) -> str:
    # If raw file bytes are present → route to upload_cv_node first
    if state.get("cv_bytes"):
        return "upload_cv_node"
    output = (state.get("planner_output") or "").lower()
    if "job" in output:
        return "advanced_rag_retrieval_node"
    elif "roadmap" in output:
        return "learning_roadmap_node"
    else:
        return "final_response_node"
