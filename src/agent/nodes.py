import io
import time
import datetime
import functools
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from src.models.llm import llm
from src.agent.language import get_language_prompt_instruction, detect_language
from src.config.constants import DEFAULT_EXPERIENCE_LEVEL


# Removed _get_cached_retriever since components are now cached in retriever.py


# ── Experience Level Context Helper ───────────────────────────────────────────
def _get_experience_context(level: str) -> str:
    """
    Returns level-specific guidance inserted into every relevant prompt.
    Maps the experience level into actionable instructions for the LLM.
    """
    contexts = {
        "Internship": (
            "EXPERIENCE CONTEXT: Target candidate is an INTERN / student.\n"
            "- Focus on foundational concepts, learning resources, and entry-level projects.\n"
            "- Recommend internship-appropriate stipend ranges (not full-time salaries).\n"
            "- Suggest beginner-friendly technologies, tutorials, and hands-on projects.\n"
            "- Interview questions should target CS fundamentals, not advanced system design.\n"
            "- Roadmap should be structured for someone with minimal work experience."
        ),
        "Junior": (
            "EXPERIENCE CONTEXT: Target candidate is a JUNIOR developer (0-2 years experience).\n"
            "- Focus on solidifying core skills and best practices.\n"
            "- Recommend entry-level to junior salary ranges.\n"
            "- Interview questions should cover fundamentals + simple problem solving.\n"
            "- Roadmap should build from basics toward producing independent deliverables.\n"
            "- Emphasize mentorship, code review, and team collaboration skills."
        ),
        "Mid Level": (
            "EXPERIENCE CONTEXT: Target candidate is a MID-LEVEL engineer (2-5 years experience).\n"
            "- Focus on deepening technical expertise and cross-team contributions.\n"
            "- Recommend mid-level market salary ranges and equity considerations.\n"
            "- Interview questions should include system design basics + leadership scenarios.\n"
            "- Roadmap should include specialization paths and architecture exposure.\n"
            "- Emphasize ownership of features, code quality, and mentoring juniors."
        ),
        "Senior": (
            "EXPERIENCE CONTEXT: Target candidate is a SENIOR engineer (5+ years experience).\n"
            "- Focus on advanced architecture, leadership, and strategic technical decisions.\n"
            "- Recommend senior-level compensation benchmarks including equity and bonuses.\n"
            "- Interview questions should include complex system design, distributed systems, and leadership.\n"
            "- Roadmap should target principal/staff-level skills and technical influence.\n"
            "- Emphasize technical vision, cross-org impact, and team multiplier behaviors."
        ),
    }
    return contexts.get(level, contexts["Senior"])


# ─────────────────────────────────────────────────────────────────────────────
# NEW: upload_cv_node — File Parsing Entry Point (no LLM calls here)
# ─────────────────────────────────────────────────────────────────────────────
def upload_cv_node(state: dict) -> dict:
    """
    CV Upload Node: Accepts raw file bytes from state, validates format,
    extracts plain text from PDF or DOCX, and populates graph state.
    Does NOT call the LLM — pure file processing only.
    Feeds uploaded_cv so existing resume_parsing_node works unchanged.
    """
    cv_bytes: bytes = state.get("cv_bytes")
    cv_filename: str = state.get("cv_filename", "unknown_file")

    print(f"[DEBUG - upload_cv_node]: Processing file '{cv_filename}' ({len(cv_bytes or b'')} bytes)")

    if not cv_bytes:
        print("[DEBUG - upload_cv_node]: No file bytes found in state — skipping.")
        return {
            "analysis_status": "error",
            "active_node": "upload_cv_node"
        }

    ext = cv_filename.lower().rsplit(".", 1)[-1] if "." in cv_filename else ""
    extracted_text = ""
    metadata: dict = {
        "filename": cv_filename,
        "file_size_bytes": len(cv_bytes),
        "format": ext.upper()
    }

    try:
        if ext == "pdf":
            # ── PDF extraction via pypdf ─────────────────────────────────────
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(cv_bytes))
            pages_text = []
            for page in reader.pages:
                page_txt = page.extract_text() or ""
                pages_text.append(page_txt)
            extracted_text = "\n".join(pages_text).strip()
            metadata["page_count"] = len(reader.pages)

        elif ext in ("docx", "doc"):
            # ── DOCX extraction via python-docx ─────────────────────────────
            import docx
            document = docx.Document(io.BytesIO(cv_bytes))
            paragraphs = [para.text for para in document.paragraphs if para.text.strip()]
            extracted_text = "\n".join(paragraphs).strip()
            metadata["paragraph_count"] = len(paragraphs)

        elif ext == "txt":
            # ── Plain text fallback ──────────────────────────────────────────
            extracted_text = cv_bytes.decode("utf-8", errors="ignore").strip()

        else:
            print(f"[DEBUG - upload_cv_node]: Unsupported file format '{ext}'")
            return {
                "analysis_status": "error",
                "active_node": "upload_cv_node",
                "cv_filename": cv_filename,
                "cv_metadata": metadata
            }

    except Exception as e:
        print(f"[ERROR - upload_cv_node]: Text extraction failed: {e}")
        return {
            "analysis_status": "error",
            "active_node": "upload_cv_node",
            "cv_filename": cv_filename,
            "cv_metadata": metadata
        }

    if not extracted_text:
        print("[DEBUG - upload_cv_node]: Extracted text is empty.")
        return {
            "analysis_status": "error",
            "cv_filename": cv_filename,
            "cv_metadata": metadata,
            "active_node": "upload_cv_node"
        }

    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    print(f"[DEBUG - upload_cv_node]: Successfully extracted {len(extracted_text)} chars from '{cv_filename}'")

    return {
        # ── New CV pipeline fields ───────────────────────────────────────────
        "cv_text": extracted_text,
        "cv_filename": cv_filename,
        "cv_upload_timestamp": timestamp,
        "cv_metadata": metadata,
        "analysis_status": "pending",   # Supervisor will see "pending" → force CV_Reviewer
        # ── Feed legacy field so resume_parsing_node works unchanged ─────────
        "uploaded_cv": extracted_text,
        # ── Clear raw bytes after extraction (memory hygiene) ────────────────
        "cv_bytes": None,
        "active_node": "upload_cv_node"
    }


def resume_parsing_node(state: dict) -> dict:
    """
    CV Reviewer Agent Node: Uses LLM to parse resume text and extract technical skills.
    Respects state language ('ar' or 'en') and experience_level.
    """
    t0 = time.perf_counter()
    cv = state.get("uploaded_cv") or state.get("user_message", "")
    lang = state.get("detected_language") or detect_language(cv)
    lang_instruction = get_language_prompt_instruction(lang)
    experience_level = state.get("experience_level") or DEFAULT_EXPERIENCE_LEVEL
    exp_context = _get_experience_context(experience_level)
    print(f"[DEBUG] resume_parsing_node: processing {len(cv)} chars | lang='{lang}' | level='{experience_level}'")

    prompt = (
        f"Parse the following resume/text and extract a bulleted list of key technical skills, "
        f"programming languages, and tools. Consider the candidate is at {experience_level} level.\n\n"
        f"{cv[:3000]}"
    )
    t_llm = time.perf_counter()
    sys_msg = f"You are an expert ATS CV Reviewer.\n{exp_context}{lang_instruction}"
    response = llm.invoke([SystemMessage(content=sys_msg), HumanMessage(content=prompt)])
    print(f"[TIMING] resume_parsing_node LLM: {(time.perf_counter()-t_llm)*1000:.1f} ms | Total: {(time.perf_counter()-t0)*1000:.1f} ms")

    content = response.content
    extracted = [line.strip("-•* ").strip() for line in content.split("\n") if line.strip().startswith(("-", "•", "*", "1", "2", "3", "4", "5"))]
    if not extracted:
        extracted = ["Python", "Software Engineering"]

    return {
        "uploaded_cv": cv,
        "extracted_skills": extracted,
        "skills": extracted,
        "interview_feedback": content,
        "latest_worker_output": content,
        "worker_executed_this_turn": True,
        "active_node": "resume_parsing_node",
        "detected_language": lang
    }

def skill_extraction_node(state: dict) -> dict:
    """
    Skills Analyzer Agent Node: Uses LLM to analyze competencies and skill gaps.
    Respects state language ('ar' or 'en') and experience_level.
    """
    t0 = time.perf_counter()
    skills = state.get("extracted_skills", [])
    user_msg = state.get("user_message", "")
    lang = state.get("detected_language") or detect_language(user_msg)
    lang_instruction = get_language_prompt_instruction(lang)
    experience_level = state.get("experience_level") or DEFAULT_EXPERIENCE_LEVEL
    exp_context = _get_experience_context(experience_level)
    print(f"[DEBUG] skill_extraction_node: skills={skills[:5]} | lang='{lang}' | level='{experience_level}'")

    prompt = (
        f"Analyze these current skills: {skills}.\n"
        f"Query: '{user_msg}'.\n"
        f"Identify technical strengths and 3 key skill gaps for a {experience_level} AI/Data role. "
        f"Tailor your analysis specifically for the {experience_level} experience level."
    )
    t_llm = time.perf_counter()
    sys_msg = f"You are a Technical Skill Analyst.\n{exp_context}{lang_instruction}"
    response = llm.invoke([SystemMessage(content=sys_msg), HumanMessage(content=prompt)])
    print(f"[TIMING] skill_extraction_node LLM: {(time.perf_counter()-t_llm)*1000:.1f} ms | Total: {(time.perf_counter()-t0)*1000:.1f} ms")

    return {
        "interview_feedback": response.content,
        "latest_worker_output": response.content,
        "worker_executed_this_turn": True,
        "active_node": "skill_extraction_node",
        "detected_language": lang
    }

def career_goal_analysis_node(state: dict) -> dict:
    """
    Career Goal Analysis Node: Analyzes candidate career trajectory goals using LLM.
    Uses experience_level to suggest an appropriate target role.
    """
    msg = state.get("user_message", "")
    experience_level = state.get("experience_level") or DEFAULT_EXPERIENCE_LEVEL
    print(f"[DEBUG - NODE INVOCATION]: Running 'career_goal_analysis_node' | level='{experience_level}'")

    # Level-appropriate default goals if extraction fails
    _level_defaults = {
        "Internship": "Software Engineering Intern",
        "Junior": "Junior AI Engineer",
        "Mid Level": "AI Engineer",
        "Senior": "Senior AI Engineer",
    }
    default_goal = _level_defaults.get(experience_level, "Senior AI Engineer")

    prompt = (
        f"Extract the candidate's target career job title from this message: '{msg}'. "
        f"The candidate is at {experience_level} level. "
        f"Respond with ONLY the job title (e.g. {default_goal})."
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    goal = response.content.strip() or default_goal

    return {
        "career_goal": goal,
        "active_node": "career_goal_analysis_node"
    }

def advanced_rag_retrieval_node(state: dict) -> dict:
    """
    Advanced RAG Retrieval Node: Classifies the query intent to route to specific 
    document categories, then dynamically builds a filtered retriever.
    """
    t0 = time.perf_counter()
    query = state.get("user_message", "")
    
    # 1. Query Routing via LLM
    routing_prompt = f"""You are a query router for a Career AI Agent.
Analyze the following user query and determine which document categories are most likely to contain the answer.
Available categories: 
- interview
- skills
- career (for salary, negotiation)
- jobs (for job requirements)
- roadmap (for learning paths)
- courses (for recommended courses/learning)
- ats (for resume keywords and ATS optimization)
- faq (for common career questions)
- glossary (for technical AI definitions)
- projects (for portfolio ideas)
- technical (for git, docker, generic tech docs)
- resumes (for resume writing rules)

Output ONLY a comma-separated list of the relevant categories (e.g., 'interview, skills'). If none apply clearly, output 'all'.
User Query: {query}"""

    try:
        from src.models.llm import llm
        from langchain_core.messages import HumanMessage
        route_resp = llm.invoke([HumanMessage(content=routing_prompt)])
        raw_cats = route_resp.content.strip().lower()
        if "all" in raw_cats or not raw_cats:
            document_types = None
        else:
            valid_cats = ["interview", "skills", "career", "jobs", "roadmap", "courses", "ats", "faq", "glossary", "projects", "technical", "resumes"]
            document_types = [c.strip() for c in raw_cats.split(",") if c.strip() in valid_cats]
            if not document_types:
                document_types = None
    except Exception as e:
        print(f"[WARN] Query routing failed: {e}")
        document_types = None
        
    print(f"[DEBUG] advanced_rag_retrieval_node: query='{query[:60]}', routed to: {document_types}")
    
    try:
        from src.models.embeddings import get_embeddings
        from src.rag.retriever import get_advanced_retriever
        
        embeddings = get_embeddings()
        # Heavy components (DB, CrossEncoder) are LRU cached inside retriever.py
        retriever = get_advanced_retriever(embeddings, document_types=document_types)
        
        t_ret = time.perf_counter()
        docs = retriever.invoke(query)
        print(f"[TIMING] RAG retriever invoke: {(time.perf_counter()-t_ret)*1000:.1f} ms | Total RAG: {(time.perf_counter()-t0)*1000:.1f} ms")
        retrieved_content = [{"content": d.page_content, "metadata": d.metadata} for d in docs]
    except Exception as e:
        print(f"[WARN] RAG retriever failed: {e}")
        retrieved_content = [{"content": f"Relevant career documentation for: {query}"}]

    return {
        "retrieved_documents": retrieved_content,
        "active_node": "advanced_rag_retrieval_node"
    }

def job_recommendation_node(state: dict) -> dict:
    """
    Job Recommendation Node: Matches candidates to open engineering positions using LLM.
    Respects experience_level for appropriate job targeting.
    """
    goal = state.get("career_goal", "AI Engineer")
    skills = state.get("extracted_skills", [])
    lang = state.get("detected_language") or "en"
    lang_instruction = get_language_prompt_instruction(lang)
    experience_level = state.get("experience_level") or DEFAULT_EXPERIENCE_LEVEL
    exp_context = _get_experience_context(experience_level)
    print(f"[DEBUG - NODE INVOCATION]: Running 'job_recommendation_node' | lang='{lang}' | level='{experience_level}'")

    prompt = (
        f"Generate 3 realistic open remote job postings for a {experience_level} candidate "
        f"targeting role '{goal}' requiring skills {skills}. "
        f"Match the seniority level ({experience_level}) for each listing. "
        f"Include Company, Title, Level, and Location."
    )
    sys_msg = f"You are a Career Placement Specialist.\n{exp_context}{lang_instruction}"
    response = llm.invoke([SystemMessage(content=sys_msg), HumanMessage(content=prompt)])

    return {
        "interview_feedback": response.content,
        "latest_worker_output": response.content,
        "worker_executed_this_turn": True,
        "active_node": "job_recommendation_node",
        "detected_language": lang
    }

def learning_roadmap_node(state: dict) -> dict:
    """
    Learning Roadmap Agent Node: Dynamically generates a 3-month structured roadmap.
    Respects state language ('ar' or 'en') and experience_level.
    """
    t0 = time.perf_counter()
    goal = state.get("career_goal") or "AI Engineer"
    skills = state.get("extracted_skills", [])
    msg = state.get("user_message", "")
    lang = state.get("detected_language") or detect_language(msg)
    lang_instruction = get_language_prompt_instruction(lang)
    experience_level = state.get("experience_level") or DEFAULT_EXPERIENCE_LEVEL
    exp_context = _get_experience_context(experience_level)
    print(f"[DEBUG] learning_roadmap_node: goal='{goal}' | lang='{lang}' | level='{experience_level}'")

    prompt = (
        f"Create a detailed 3-month technical learning roadmap for a {experience_level} candidate "
        f"working toward becoming a {goal}.\n"
        f"Current skills: {skills}.\n"
        f"Query context: {msg}.\n"
        f"Structure the roadmap specifically for a {experience_level} — adjust depth, pace, and topics accordingly."
    )
    t_llm = time.perf_counter()
    sys_msg = f"You are a Technical Curriculum Architect.\n{exp_context}{lang_instruction}"
    response = llm.invoke([SystemMessage(content=sys_msg), HumanMessage(content=prompt)])
    print(f"[TIMING] learning_roadmap_node LLM: {(time.perf_counter()-t_llm)*1000:.1f} ms | Total: {(time.perf_counter()-t0)*1000:.1f} ms")

    return {
        "interview_feedback": response.content,
        "latest_worker_output": response.content,
        "worker_executed_this_turn": True,
        "planner_output": "roadmap_generated",
        "active_node": "learning_roadmap_node",
        "detected_language": lang
    }

def interview_coach_node(state: dict) -> dict:
    """
    Interview Coach Agent Node: Generates mock interview questions with STAR feedback.
    Respects state language ('ar' or 'en') and experience_level.
    """
    t0 = time.perf_counter()
    goal = state.get("career_goal") or "AI Engineer"
    skills = state.get("extracted_skills", [])
    msg = state.get("user_message", "")
    lang = state.get("detected_language") or detect_language(msg)
    lang_instruction = get_language_prompt_instruction(lang)
    experience_level = state.get("experience_level") or DEFAULT_EXPERIENCE_LEVEL
    exp_context = _get_experience_context(experience_level)
    print(f"[DEBUG] interview_coach_node: goal='{goal}' | lang='{lang}' | level='{experience_level}'")

    prompt = (
        f"Generate 3 technical & behavioral mock interview questions with STAR method guidance "
        f"for a {experience_level} candidate targeting role '{goal}' with skills {skills}.\n"
        f"Query: {msg}\n"
        f"Calibrate question difficulty and depth for {experience_level} level."
    )
    t_llm = time.perf_counter()
    sys_msg = f"You are a Technical Interview Coach.\n{exp_context}{lang_instruction}"
    response = llm.invoke([SystemMessage(content=sys_msg), HumanMessage(content=prompt)])
    print(f"[TIMING] interview_coach_node LLM: {(time.perf_counter()-t_llm)*1000:.1f} ms | Total: {(time.perf_counter()-t0)*1000:.1f} ms")

    return {
        "interview_feedback": response.content,
        "latest_worker_output": response.content,
        "worker_executed_this_turn": True,
        "active_node": "interview_coach_node",
        "detected_language": lang
    }

def salary_advisor_node(state: dict) -> dict:
    """
    Salary Advisor Agent Node: Generates market compensation benchmarks.
    Respects state language ('ar' or 'en') and experience_level.
    """
    t0 = time.perf_counter()
    goal = state.get("career_goal") or "AI Engineer"
    msg = state.get("user_message", "")
    lang = state.get("detected_language") or detect_language(msg)
    lang_instruction = get_language_prompt_instruction(lang)
    experience_level = state.get("experience_level") or DEFAULT_EXPERIENCE_LEVEL
    exp_context = _get_experience_context(experience_level)
    print(f"[DEBUG] salary_advisor_node: goal='{goal}' | lang='{lang}' | level='{experience_level}'")

    prompt = (
        f"Provide salary/compensation benchmarks (Base, Equity, Bonus) and negotiation strategies "
        f"for a {experience_level} candidate targeting role '{goal}'.\n"
        f"Query: {msg}\n"
        f"For Internship level, provide stipend ranges instead of full salaries. "
        f"For Junior/Mid Level/Senior, provide appropriate market ranges with progression context."
    )
    t_llm = time.perf_counter()
    sys_msg = f"You are an Executive Compensation & Salary Consultant.\n{exp_context}{lang_instruction}"
    response = llm.invoke([SystemMessage(content=sys_msg), HumanMessage(content=prompt)])
    print(f"[TIMING] salary_advisor_node LLM: {(time.perf_counter()-t_llm)*1000:.1f} ms | Total: {(time.perf_counter()-t0)*1000:.1f} ms")

    return {
        "interview_feedback": response.content,
        "latest_worker_output": response.content,
        "worker_executed_this_turn": True,
        "planner_output": "salary_info_generated",
        "active_node": "salary_advisor_node",
        "detected_language": lang
    }

def final_response_node(state: dict) -> dict:
    """
    Final Response Node: Synthesizes context-aware answer in detected language ('ar' or 'en').
    Keeps all technical terms in English. Respects experience_level in synthesis.
    """
    t0 = time.perf_counter()
    msg = state.get("user_message", "")
    latest_output = state.get("latest_worker_output")
    worker_ran = state.get("worker_executed_this_turn", False)
    cache_hit = state.get("cache_hit", False)
    lang = state.get("detected_language") or detect_language(msg)
    lang_instruction = get_language_prompt_instruction(lang)
    experience_level = state.get("experience_level") or DEFAULT_EXPERIENCE_LEVEL

    print(f"[DEBUG] final_response_node: worker_ran={worker_ran} | cache_hit={cache_hit} | lang='{lang}' | level='{experience_level}'")

    # If this is a cache hit, the response is already in final_response — return it as-is
    if cache_hit and state.get("final_response"):
        cached_resp = state["final_response"]
        print(f"[DEBUG] final_response_node: serving cached response directly")
        return {
            "final_response": cached_resp,
            "messages": [AIMessage(content=cached_resp)],
            "worker_executed_this_turn": False,
            "latest_worker_output": None,
            "active_node": "final_response_node",
            "detected_language": lang,
            "cache_hit": True,
        }

    if worker_ran and latest_output:
        system_prompt = (
            "You are the Career AI Agent assistant. Synthesize the specialized worker agent output "
            "into a clean, professional, and friendly response answering the candidate's query.\n"
            f"The candidate is at {experience_level} experience level — keep the tone and depth appropriate.\n"
            f"{lang_instruction}\n\n"
            f"Worker Output:\n{latest_output}"
        )
    else:
        system_prompt = (
            "You are the Career AI Agent assistant. Respond to the user's message directly, accurately, "
            "naturally, and helpfully. For general greetings (e.g. 'hi', 'hello', 'مرحبا', 'السلام عليكم'), "
            "greet the user warmly and briefly introduce yourself as the Career AI Agent ready to help with "
            "resumes, roadmaps, mock interviews, and salary benchmarks. For math or general questions answer them directly.\n"
            f"{lang_instruction}"
        )

    t_llm = time.perf_counter()
    # Construct message list: System Prompt + Full Conversation History
    # The history already includes the current user message (added by chat.py)
    llm_messages = [SystemMessage(content=system_prompt)] + state.get("messages", [])
    response = llm.invoke(llm_messages)
    llm_ms = (time.perf_counter() - t_llm) * 1000
    total_ms = (time.perf_counter() - t0) * 1000
    print(f"[TIMING] final_response_node LLM: {llm_ms:.1f} ms | Total: {total_ms:.1f} ms")

    res_content = response.content

    return {
        "final_response": res_content,
        "messages": [AIMessage(content=res_content)],
        "worker_executed_this_turn": False,
        "latest_worker_output": None,
        "active_node": "final_response_node",
        "detected_language": lang,
        "cache_hit": False,
    }

def job_matching_node(state: dict) -> dict:
    t0 = time.perf_counter()
    skills = state.get("extracted_skills", [])
    msg = state.get("user_message", "")
    lang = state.get("detected_language") or detect_language(msg)
    lang_instruction = get_language_prompt_instruction(lang)
    experience_level = state.get("experience_level") or DEFAULT_EXPERIENCE_LEVEL
    exp_context = _get_experience_context(experience_level)

    try:
        from src.models.embeddings import get_embeddings
        from src.rag.retriever import get_advanced_retriever
        
        embeddings = get_embeddings()
        retriever = get_advanced_retriever(embeddings, document_types=["jobs"])
        docs = retriever.invoke(msg)
        retrieved_content = [{"content": d.page_content, "metadata": d.metadata} for d in docs]
    except Exception as e:
        print(f"[WARN] RAG retriever failed: {e}")
        retrieved_content = []

    prompt = (
        f"Act as an expert Technical Recruiter.\n"
        f"Compare these extracted skills: {skills}\n"
        f"against the following retrieved job market data/requirements:\n{retrieved_content}\n\n"
        f"User Query: {msg}\n"
        f"Calculate a match score (e.g. 82%), list Strengths, list Missing Skills, and provide a clear Recommendation on whether they should apply or what they need to improve."
    )
    
    sys_msg = f"You are a Job Matching Specialist.\n{exp_context}{lang_instruction}"
    response = llm.invoke([SystemMessage(content=sys_msg), HumanMessage(content=prompt)])
    
    return {
        "interview_feedback": response.content,
        "latest_worker_output": response.content,
        "worker_executed_this_turn": True,
        "active_node": "job_matching_node",
        "detected_language": lang
    }

def project_recommender_node(state: dict) -> dict:
    t0 = time.perf_counter()
    skills = state.get("extracted_skills", [])
    goal = state.get("career_goal") or "AI Engineer"
    msg = state.get("user_message", "")
    lang = state.get("detected_language") or detect_language(msg)
    lang_instruction = get_language_prompt_instruction(lang)
    experience_level = state.get("experience_level") or DEFAULT_EXPERIENCE_LEVEL
    exp_context = _get_experience_context(experience_level)
    
    try:
        from src.models.embeddings import get_embeddings
        from src.rag.retriever import get_advanced_retriever
        
        embeddings = get_embeddings()
        retriever = get_advanced_retriever(embeddings, document_types=["projects"])
        docs = retriever.invoke(msg)
        retrieved_content = [{"content": d.page_content, "metadata": d.metadata} for d in docs]
    except Exception as e:
        print(f"[WARN] RAG retriever failed: {e}")
        retrieved_content = []

    prompt = (
        f"Act as a Technical Mentor. Recommend top portfolio projects based on:\n"
        f"- Target Career: {goal}\n"
        f"- Current Skills: {skills}\n"
        f"- Experience Level: {experience_level}\n"
        f"- Relevant retrieved project ideas: {retrieved_content}\n\n"
        f"User Query: {msg}\n"
        f"Provide a structured list of highly relevant, production-grade projects. Categorize them (e.g. Portfolio, Hackathon, Startup) if appropriate."
    )
    
    sys_msg = f"You are a Project Recommendation Advisor.\n{exp_context}{lang_instruction}"
    response = llm.invoke([SystemMessage(content=sys_msg), HumanMessage(content=prompt)])
    
    return {
        "interview_feedback": response.content,
        "latest_worker_output": response.content,
        "worker_executed_this_turn": True,
        "active_node": "project_recommender_node",
        "detected_language": lang
    }
