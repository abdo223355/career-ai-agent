# Architecture Analysis

This document outlines the complete architectural implementation extracted exactly from the project source code.

## 1. All Graphs

- **Graph Name**: `builder` (compiled to `graph`)
- **File Path**: `src/agent/graph.py`
- **Purpose**: Orchestrates the multi-agent system including the response caching pipeline, executive supervisor routing, and specialized worker execution.
- **Entry Point**: `START` -> `normalize_question_node`
- **End Point**: `save_cache_node` -> `END`

---

## 2. All Nodes

### `normalize_question_node`
- **Python Function Name**: `normalize_question_node`
- **File Path**: `src/agent/cache_nodes.py`
- **Purpose**: Normalizes the user message and computes a SHA-256 hash for cache lookup.
- **Inputs from State**: `user_message`
- **Outputs to State**: `normalized_question`, `question_hash`, `cache_hit`, `active_node`
- **Graph Belonging**: `builder`

### `cache_lookup_node`
- **Python Function Name**: `cache_lookup_node`
- **File Path**: `src/agent/cache_nodes.py`
- **Purpose**: Searches the persistent response cache. Fast-paths to final response if hit.
- **Inputs from State**: `question_hash`, `experience_level`, `cv_bytes`
- **Outputs to State**: `cache_hit`, `final_response`, `worker_executed_this_turn`, `latest_worker_output`, `active_node`
- **Graph Belonging**: `builder`

### `save_cache_node`
- **Python Function Name**: `save_cache_node`
- **File Path**: `src/agent/cache_nodes.py`
- **Purpose**: Persists the final LLM response to the SQLite response cache if it wasn't a hit or CV upload.
- **Inputs from State**: `cache_hit`, `final_response`, `question_hash`, `normalized_question`, `experience_level`, `active_node`, `cv_bytes`
- **Outputs to State**: `active_node`
- **Graph Belonging**: `builder`

### `supervisor_node`
- **Python Function Name**: `supervisor_node`
- **File Path**: `src/agent/supervisor.py`
- **Purpose**: Analyzes state, detects user language, evaluates fast-paths (small talk, CV upload), or uses an LLM to route to the appropriate worker agent.
- **Inputs from State**: `user_message`, `extracted_skills`, `career_goal`, `uploaded_cv`, `cv_text`, `analysis_status`, `roadmap`, `interview_feedback`, `planner_output`, `messages`, `worker_executed_this_turn`, `detected_language`, `preferred_language`, `target_market`
- **Outputs to State**: `active_node`, `next_agent`, `routing_reason`, `planner_output`, `detected_language`, `response_language`, `preferred_language`, `worker_executed_this_turn`, `analysis_status`
- **Graph Belonging**: `builder`

### `upload_cv_node`
- **Python Function Name**: `upload_cv_node`
- **File Path**: `src/agent/nodes.py`
- **Purpose**: Accepts raw file bytes, validates format, extracts plain text (PDF/DOCX), and populates graph state without calling LLM.
- **Inputs from State**: `cv_bytes`, `cv_filename`
- **Outputs to State**: `cv_text`, `cv_filename`, `cv_upload_timestamp`, `cv_metadata`, `analysis_status`, `uploaded_cv`, `cv_bytes` (cleared to None), `active_node`
- **Graph Belonging**: `builder`

### `resume_parsing_node`
- **Python Function Name**: `resume_parsing_node`
- **File Path**: `src/agent/nodes.py`
- **Purpose**: Uses LLM to parse resume text and extract technical skills.
- **Inputs from State**: `uploaded_cv`, `user_message`, `detected_language`, `experience_level`
- **Outputs to State**: `uploaded_cv`, `extracted_skills`, `skills`, `interview_feedback`, `latest_worker_output`, `worker_executed_this_turn`, `active_node`, `detected_language`
- **Graph Belonging**: `builder`

### `skill_extraction_node`
- **Python Function Name**: `skill_extraction_node`
- **File Path**: `src/agent/nodes.py`
- **Purpose**: Analyzes competencies and skill gaps.
- **Inputs from State**: `extracted_skills`, `user_message`, `detected_language`, `experience_level`
- **Outputs to State**: `interview_feedback`, `latest_worker_output`, `worker_executed_this_turn`, `active_node`, `detected_language`
- **Graph Belonging**: `builder`

### `learning_roadmap_node`
- **Python Function Name**: `learning_roadmap_node`
- **File Path**: `src/agent/nodes.py`
- **Purpose**: Dynamically generates a 3-month structured roadmap based on skills and goal.
- **Inputs from State**: `career_goal`, `extracted_skills`, `user_message`, `detected_language`, `experience_level`
- **Outputs to State**: `interview_feedback`, `latest_worker_output`, `worker_executed_this_turn`, `planner_output`, `active_node`, `detected_language`
- **Graph Belonging**: `builder`

### `interview_coach_node`
- **Python Function Name**: `interview_coach_node`
- **File Path**: `src/agent/nodes.py`
- **Purpose**: Generates mock interview questions with STAR method feedback.
- **Inputs from State**: `career_goal`, `extracted_skills`, `user_message`, `detected_language`, `experience_level`
- **Outputs to State**: `interview_feedback`, `latest_worker_output`, `worker_executed_this_turn`, `active_node`, `detected_language`
- **Graph Belonging**: `builder`

### `salary_advisor_node`
- **Python Function Name**: `salary_advisor_node`
- **File Path**: `src/agent/nodes.py`
- **Purpose**: Generates market compensation benchmarks and negotiation strategies.
- **Inputs from State**: `career_goal`, `user_message`, `detected_language`, `experience_level`, `target_market`
- **Outputs to State**: `interview_feedback`, `latest_worker_output`, `worker_executed_this_turn`, `planner_output`, `active_node`, `detected_language`
- **Graph Belonging**: `builder`

### `job_matching_node`
- **Python Function Name**: `job_matching_node`
- **File Path**: `src/agent/nodes.py`
- **Purpose**: Compares CV skills against job requirements (using RAG) and calculates a match score.
- **Inputs from State**: `extracted_skills`, `user_message`, `detected_language`, `experience_level`, `target_market`
- **Outputs to State**: `interview_feedback`, `latest_worker_output`, `worker_executed_this_turn`, `active_node`, `detected_language`
- **Graph Belonging**: `builder`

### `project_recommender_node`
- **Python Function Name**: `project_recommender_node`
- **File Path**: `src/agent/nodes.py`
- **Purpose**: Recommends top portfolio projects using RAG context based on target career and skills.
- **Inputs from State**: `extracted_skills`, `career_goal`, `user_message`, `detected_language`, `experience_level`
- **Outputs to State**: `interview_feedback`, `latest_worker_output`, `worker_executed_this_turn`, `active_node`, `detected_language`
- **Graph Belonging**: `builder`

### `mcp_client_node`
- **Python Function Name**: `mcp_client_node`
- **File Path**: `src/agent/mcp_client_node.py`
- **Purpose**: Acts as an MCP Client connecting to an external server to load tools dynamically and fetch web content.
- **Inputs from State**: `user_query`, `language_preference`
- **Outputs to State**: `final_response`
- **Graph Belonging**: `builder`

### `final_response_node`
- **Python Function Name**: `final_response_node`
- **File Path**: `src/agent/nodes.py`
- **Purpose**: Synthesizes a clean, professional, and friendly final answer from the specialized worker agent output or directly for general queries.
- **Inputs from State**: `user_message`, `latest_worker_output`, `worker_executed_this_turn`, `cache_hit`, `final_response`, `detected_language`, `experience_level`, `messages`
- **Outputs to State**: `final_response`, `messages`, `worker_executed_this_turn`, `latest_worker_output`, `active_node`, `detected_language`, `cache_hit`
- **Graph Belonging**: `builder`

---

## 3. All Edges

- **START** -> `normalize_question_node` (Direct Edge)
- `normalize_question_node` -> `cache_lookup_node` (Direct Edge)
- `cache_lookup_node` -> **Conditional Edge** (`cache_router`)
  - **Routing Condition**: 
    - `cache_hit` (if `state.get("cache_hit")` is True) -> `final_response_node`
    - `cache_miss` (otherwise) -> `supervisor_node`
- `supervisor_node` -> **Conditional Edge** (`supervisor_router`)
  - **Routing Condition**: Evaluates `state.get("next_agent")` enum against `AGENT_REGISTRY`. Falls back to parsing `planner_output`.
    - `"upload_cv_node"` -> `upload_cv_node`
    - `"resume_parsing_node"` -> `resume_parsing_node`
    - `"skill_extraction_node"` -> `skill_extraction_node`
    - `"learning_roadmap_node"` -> `learning_roadmap_node`
    - `"interview_coach_node"` -> `interview_coach_node`
    - `"salary_advisor_node"` -> `salary_advisor_node`
    - `"job_matching_node"` -> `job_matching_node`
    - `"project_recommender_node"` -> `project_recommender_node`
    - `"mcp_client_node"` -> `mcp_client_node`
    - `"final_response_node"` -> `final_response_node` (AgentType.FINISH)
- `upload_cv_node` -> `supervisor_node` (Direct Edge)
- `resume_parsing_node` -> `supervisor_node` (Direct Edge)
- `skill_extraction_node` -> `supervisor_node` (Direct Edge)
- `learning_roadmap_node` -> `supervisor_node` (Direct Edge)
- `interview_coach_node` -> `supervisor_node` (Direct Edge)
- `salary_advisor_node` -> `supervisor_node` (Direct Edge)
- `job_matching_node` -> `supervisor_node` (Direct Edge)
- `project_recommender_node` -> `supervisor_node` (Direct Edge)
- `mcp_client_node` -> `supervisor_node` (Direct Edge)
- `final_response_node` -> `save_cache_node` (Direct Edge)
- `save_cache_node` -> **END** (Direct Edge)

---

## 4. Supervisor Architecture

- **Supervisor Node**: `supervisor_node` (`src/agent/supervisor.py`)
- **Worker Nodes**: `upload_cv_node`, `resume_parsing_node`, `skill_extraction_node`, `learning_roadmap_node`, `interview_coach_node`, `salary_advisor_node`, `job_matching_node`, `project_recommender_node`, `mcp_client_node`
- **Routing Execution**: 
  - Routing happens via an LLM structure output binding `SupervisorRoute(next_agent, reasoning)` for standard inputs.
  - Hardcoded "fast paths" bypass LLM routing for:
    - CV Uploads (pending analysis status forces routing to `CV_Reviewer`).
    - Smalltalk/Greetings/Math (regex pattern matching forces `FINISH`).
    - Completion Loop (if `worker_executed_this_turn` is True, forces `FINISH` to prevent loops).
- **State Variables used for Routing**:
  - `user_message`, `extracted_skills`, `career_goal`, `uploaded_cv` / `cv_text`, `analysis_status`, `roadmap`, `interview_feedback`, `planner_output`, `messages`, `worker_executed_this_turn`, `detected_language` / `preferred_language`, `target_market`

---

## 5. All Agents

### CV_Uploader
- **Node**: `upload_cv_node`
- **Responsibilities**: Accepts raw file bytes, validates format, extracts plain text (PDF/DOCX), clears bytes from memory.
- **LLM Used**: None (Pure Python parsing).
- **Prompt Location**: Not implemented.
- **Tools Used**: `pypdf`, `python-docx`
- **RAG**: No

### CV_Reviewer
- **Node**: `resume_parsing_node`
- **Responsibilities**: Parses resume text and extracts bulleted technical skills and tools.
- **LLM Used**: Shared `llm` (ChatOpenAI `openai/gpt-5-mini` via OpenRouter).
- **Prompt Location**: Embedded in `src/agent/nodes.py` (line 169).
- **Tools Used**: None
- **RAG**: No

### Skills_Analyzer
- **Node**: `skill_extraction_node`
- **Responsibilities**: Analyzes competencies and identifies 3 key skill gaps for a specific role and experience level.
- **LLM Used**: Shared `llm` (ChatOpenAI).
- **Prompt Location**: Embedded in `src/agent/nodes.py` (line 209).
- **Tools Used**: None
- **RAG**: No

### Roadmap_Generator
- **Node**: `learning_roadmap_node`
- **Responsibilities**: Dynamically generates a 3-month structured technical learning roadmap.
- **LLM Used**: Shared `llm` (ChatOpenAI).
- **Prompt Location**: Embedded in `src/agent/nodes.py` (line 371).
- **Tools Used**: None
- **RAG**: No

### Interview_Coach
- **Node**: `interview_coach_node`
- **Responsibilities**: Generates technical and behavioral mock interview questions with STAR method feedback.
- **LLM Used**: Shared `llm` (ChatOpenAI).
- **Prompt Location**: Embedded in `src/agent/nodes.py` (line 407).
- **Tools Used**: None
- **RAG**: No

### Salary_Advisor
- **Node**: `salary_advisor_node`
- **Responsibilities**: Provides market compensation benchmarks (Base, Equity, Bonus) and negotiation strategies targeted to specific markets.
- **LLM Used**: Shared `llm` (ChatOpenAI).
- **Prompt Location**: Embedded in `src/agent/nodes.py` (line 441).
- **Tools Used**: None
- **RAG**: No

### Job_Matcher
- **Node**: `job_matching_node`
- **Responsibilities**: Compares extracted skills against retrieved job market data, calculates match score, and suggests missing skills.
- **LLM Used**: Shared `llm` (ChatOpenAI).
- **Prompt Location**: Embedded in `src/agent/nodes.py` (line 552).
- **Tools Used**: None
- **RAG**: Yes (Queries RAG via `get_advanced_retriever` with filter `document_types=["jobs"]`).

### Project_Recommender
- **Node**: `project_recommender_node`
- **Responsibilities**: Recommends top portfolio projects based on target career, skills, and experience level using retrieved contextual project ideas.
- **LLM Used**: Shared `llm` (ChatOpenAI).
- **Prompt Location**: Embedded in `src/agent/nodes.py` (line 593).
- **Tools Used**: None
- **RAG**: Yes (Queries RAG via `get_advanced_retriever` with filter `document_types=["projects"]`).

### External_Researcher
- **Node**: `mcp_client_node`
- **Responsibilities**: Connects to an external MCP server to fetch live data from web URLs.
- **LLM Used**: Shared `llm` (ChatOpenAI).
- **Prompt Location**: Embedded in `src/agent/mcp_client_node.py` (line 44).
- **Tools Used**: Dynamically bound tools (e.g., `fetch_web_content`).
- **RAG**: No (Live fetch).

### FINISH (Final Response Synthesizer)
- **Node**: `final_response_node`
- **Responsibilities**: Synthesizes specialized worker agent output into a clean, professional response. Handles small talk and cache hits.
- **LLM Used**: Shared `llm` (ChatOpenAI).
- **Prompt Location**: Embedded in `src/agent/nodes.py` (lines 493 and 501).
- **Tools Used**: None
- **RAG**: No

---

## 6. All Tools

- **Tool Name**: Dynamically loaded via MCP (e.g., `fetch_web_content`)
- **Python Function**: Extracted dynamically from MCP Client server configuration.
- **File Path**: `external_services/web_fetcher_mcp.py`
- **Purpose**: Allows the LLM to access live web scraping tools securely over stdio.
- **Calling Node**: `mcp_client_node`
- **Calling Agent**: `External_Researcher`
- **API type**: External Tool (via standard MCP protocol)
- **Input**: URLs to fetch.
- **Output**: Scraped/parsed text content.

---

## 7. All State Objects

### `CareerState` (Defined in `src/agent/state.py`)
- `messages`: `list[AnyMessage]`
- `user_message`: `str`
- `active_node`: `str`
- `uploaded_cv`: `Optional[str]`
- `extracted_skills`: `List[str]`
- `career_goal`: `Optional[str]`
- `planner_output`: `Optional[str]`
- `roadmap`: `Optional[Dict[str, Any]]`
- `recommended_courses`: `List[Dict[str, str]]`
- `interview_feedback`: `Optional[str]`
- `retrieved_documents`: `List[Any]`
- `retrieved_jobs`: `List[Dict[str, Any]]`
- `final_response`: `str`
- `cv_bytes`: `Optional[bytes]`
- `cv_filename`: `Optional[str]`
- `cv_text`: `Optional[str]`
- `cv_upload_timestamp`: `Optional[str]`
- `cv_metadata`: `Optional[Dict[str, Any]]`
- `skills`: `List[str]`
- `resume_summary`: `Optional[str]`
- `analysis_status`: `Optional[str]`
- `latest_worker_output`: `Optional[str]`
- `worker_executed_this_turn`: `Optional[bool]`
- `preferred_language`: `Optional[str]`
- `response_language`: `Optional[str]`
- `detected_language`: `Optional[str]`
- `experience_level`: `Optional[str]`
- `target_market`: `Optional[str]`
- `cache_hit`: `Optional[bool]`
- `normalized_question`: `Optional[str]`
- `question_hash`: `Optional[str]`

### `SupervisorState` (Extends `CareerState`)
- `next_agent`: `Optional[AgentType]`
- `routing_reason`: `Optional[str]`

---

## 8. All Checkpointers

- `SqliteSaver` (from `langgraph.checkpoint.sqlite`) - Primary persistent production saver.
- `MemorySaver` (from `langgraph.checkpoint.memory`) - Graceful fallback if SQLite is unavailable.

---

## 9. All Memory Implementations

1. **Graph State Checkpointing**: LangGraph Checkpointer connected to `career_agent_production.db` (or in-memory) managed within `src/ui/chat.py` (session memory).
2. **Response Cache DB**: A separate SQLAlchemy-managed SQLite database (`storage/response_cache.db`) for semantic LLM caching, defined in `src/cache/database.py`.

---

## 10. All Vector Databases

- **VectorStore**: `Chroma` 
- **Directory**: `storage/vector_db` (or `../storage/vector_db` in notebooks).
- **Implementation**: Wrapped in `get_vectordb` inside `src/rag/retriever.py`.

---

## 11. All Embedding Models

- **Dense Embeddings**: `HuggingFaceEmbeddings` 
  - **Model**: `"sentence-transformers/all-MiniLM-L6-v2"` (`src/models/embeddings.py`)
- **Cross Encoder (Reranker)**: `HuggingFaceCrossEncoder`
  - **Model**: `"cross-encoder/ms-marco-MiniLM-L-6-v2"` (`src/rag/retriever.py`)

---

## 12. All LLM Models

- **Primary Chat Model**: `ChatOpenAI`
  - **Configuration**: `openai/gpt-5-mini` (default via `MODEL_NAME` env var), executing via OpenRouter API with `max_tokens=1024` and temperature `0.0`. (`src/models/llm.py`)

---

## 13. All Prompt Templates

- `src/prompts/supervisor.py`: Contains `SUPERVISOR_SYSTEM_PROMPT` structured output rules for the `Supervisor` agent.
- `src/prompts/cv_prompt.txt`: Standalone text prompt for CV processing (legacy/alternate).
- `src/prompts/interview_prompt.txt`: Standalone text prompt for interviews.
- `src/prompts/qa_prompt.py`: Standalone QA routing template.
- `src/prompts/roadmap_prompt.txt`: Standalone text template for roadmaps.
- `src/prompts/system_prompt.py`: General system instructions template.
- `src/prompts/system_prompt.txt`: Text version of system prompt.
- `src/prompts/contextualize_question_prompt.py`: Used for rewriting queries in context.
- **Embedded Prompts**: `src/agent/nodes.py` contains inline formatted F-strings for: `skill_extraction_node`, `resume_parsing_node`, `learning_roadmap_node`, `interview_coach_node`, `salary_advisor_node`, `job_matching_node`, `project_recommender_node`, `final_response_node`.
- **Embedded Experience Contexts**: `_get_experience_context` in `src/agent/nodes.py` injects dynamic instructions for Internship, Junior, Mid Level, and Senior levels.

---

## 14. Complete Request Flow from Streamlit to Final Response

1. **User Interaction**: User inputs a text message or uploads a CV file via Streamlit (`src/ui/chat.py`). 
2. **State Construction**: `chat.py` initializes the state dictionary containing `user_message`, `cv_bytes` (if file uploaded), `experience_level`, and `target_market`.
3. **Graph Execution (`graph.stream`)**: The `builder` StateGraph is invoked.
4. **Cache Normalization**: `START` flows to `normalize_question_node` to standardize the string and compute a SHA-256 hash.
5. **Cache Lookup**: `cache_lookup_node` queries the SQLite response DB. 
   - If a hit: updates state with cached `final_response`, sets `cache_hit=True`, and fast-paths.
   - If a file is attached or no hit: `cache_hit=False`.
6. **Executive Routing**: If cache miss, execution proceeds to `supervisor_node`. 
   - Checks fast-paths (CV uploads go to `CV_Reviewer`; small talk/math go to `FINISH`).
   - For career queries, it calls the LLM with `SupervisorRoute` schema to select `next_agent`.
7. **Worker Execution**: `supervisor_router` triggers the chosen worker (e.g., `learning_roadmap_node` or `job_matching_node`).
   - The worker executes its LLM chain (possibly invoking RAG or external tools via MCP).
   - Worker sets `latest_worker_output` and flags `worker_executed_this_turn = True`.
8. **Synthesis Fast-Path**: The state flows back to `supervisor_node`, which detects `worker_executed_this_turn` and deterministically routes to `final_response_node`.
9. **Final Synthesis**: `final_response_node` reads the worker output, formats it naturally considering user language and experience level, and produces `final_response`.
10. **Cache Saving**: `save_cache_node` persists the new response (if applicable) using `question_hash`.
11. **Display**: The graph hits `END`, returns state to `chat.py`, and Streamlit displays the newly synthesized `final_response` back to the user.
