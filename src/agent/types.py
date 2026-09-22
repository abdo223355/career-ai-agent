from enum import Enum

class AgentType(str, Enum):
    """
    Centralized Enum defining all authorized Agent Types in the Career AI Agent system.
    Eliminates hardcoded routing strings across nodes, prompts, and graph edges.
    """
    CV_REVIEWER = "CV_Reviewer"
    SKILLS_ANALYZER = "Skills_Analyzer"
    ROADMAP_GENERATOR = "Roadmap_Generator"
    INTERVIEW_COACH = "Interview_Coach"
    SALARY_ADVISOR = "Salary_Advisor"
    CV_UPLOADER = "CV_Uploader"
    JOB_MATCHER = "Job_Matcher"
    PROJECT_RECOMMENDER = "Project_Recommender"
    FINISH = "FINISH"
