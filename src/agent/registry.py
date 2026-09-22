from typing import Dict, Callable
from src.agent.types import AgentType
from src.agent.nodes import (
    upload_cv_node,
    resume_parsing_node,
    skill_extraction_node,
    learning_roadmap_node,
    interview_coach_node,
    salary_advisor_node,
    job_matching_node,
    project_recommender_node,
    final_response_node
)

# Central Agent Registry mapping AgentType Enums to registered node targets
AGENT_REGISTRY: Dict[AgentType, str] = {
    AgentType.CV_UPLOADER: "upload_cv_node",
    AgentType.CV_REVIEWER: "resume_parsing_node",
    AgentType.SKILLS_ANALYZER: "skill_extraction_node",
    AgentType.ROADMAP_GENERATOR: "learning_roadmap_node",
    AgentType.INTERVIEW_COACH: "interview_coach_node",
    AgentType.SALARY_ADVISOR: "salary_advisor_node",
    AgentType.JOB_MATCHER: "job_matching_node",
    AgentType.PROJECT_RECOMMENDER: "project_recommender_node",
    AgentType.FINISH: "final_response_node"
}

# Mapping of Node Names to executable Node Functions
NODE_FUNCTION_REGISTRY: Dict[str, Callable] = {
    "upload_cv_node": upload_cv_node,
    "resume_parsing_node": resume_parsing_node,
    "skill_extraction_node": skill_extraction_node,
    "learning_roadmap_node": learning_roadmap_node,
    "interview_coach_node": interview_coach_node,
    "salary_advisor_node": salary_advisor_node,
    "job_matching_node": job_matching_node,
    "project_recommender_node": project_recommender_node,
    "final_response_node": final_response_node
}
