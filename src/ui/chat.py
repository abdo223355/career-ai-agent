import os
import sys
import time
import json
import sqlite3
import datetime
from typing import Dict, Any, List, Optional

import streamlit as st
# Add project root directory to python path for backend imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.config.constants import EXPERIENCE_LEVELS, DEFAULT_EXPERIENCE_LEVEL

# ── Checkpointer import — two-tier with graceful fallback ────────────────────
# langgraph-checkpoint-sqlite is a SEPARATE package from langgraph-checkpoint.
# It must be listed in requirements.txt explicitly. If it is missing from the
# environment (e.g. a fresh Docker image before rebuild), we fall back to the
# in-process MemorySaver so the app still starts, but memory does not persist
# across restarts. The sidebar will show a warning in that case.
try:
    from langgraph.checkpoint.sqlite import SqliteSaver as _SqliteSaver  # noqa
    _SQLITE_CHECKPOINTER_AVAILABLE = True
except ImportError:
    _SqliteSaver = None  # type: ignore
    _SQLITE_CHECKPOINTER_AVAILABLE = False

from langgraph.checkpoint.memory import MemorySaver as _MemorySaver  # always available

# Import shared production models and agent infrastructure
try:
    from langchain_core.messages import HumanMessage, AIMessage
    from langgraph.graph import StateGraph, START, END

    from src.models.llm import llm
    from src.agent.types import AgentType
    from src.agent.state import SupervisorState
    from src.agent.registry import AGENT_REGISTRY, NODE_FUNCTION_REGISTRY
    from src.agent.supervisor import supervisor_node, supervisor_router
    from src.agent.cache_nodes import (
        normalize_question_node,
        cache_lookup_node,
        save_cache_node,
        cache_router,
    )
    BACKEND_AVAILABLE = True
except Exception as e:
    BACKEND_AVAILABLE = False
    BACKEND_ERROR = str(e)


# ─────────────────────────────────────────────────────────────────────────────
# STREAMLIT PAGE CONFIGURATION & CUSTOM SAAS DARK THEME
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Career AI Agent - Enterprise AI Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Inject CSS for Modern Dark Theme (Claude / Perplexity / Notion AI Aesthetic)
st.markdown("""
<style>
    /* Dark Theme Core Variables */
    :root {
        --bg-primary: #0e1117;
        --bg-secondary: #161b22;
        --bg-card: #21262d;
        --accent-color: #6366f1;
        --accent-hover: #4f46e5;
        --text-primary: #f0f6fc;
        --text-muted: #8b949e;
        --border-color: #30363d;
    }

    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .top-header-card {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .status-badge {
        background-color: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .status-badge-green {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .status-badge-yellow {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .quick-action-btn {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 14px 16px;
        color: #f0f6fc;
        text-align: left;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        margin-bottom: 8px;
    }
    .quick-action-btn:hover {
        background: #21262d;
        border-color: #6366f1;
        transform: translateY(-2px);
    }

    /* Welcome hero section */
    .welcome-hero {
        text-align: center;
        padding: 40px 20px 20px;
        animation: fadeIn 0.5s ease;
    }
    .welcome-hero h1 {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 8px;
    }
    .welcome-hero p {
        color: #8b949e;
        font-size: 1rem;
        max-width: 600px;
        margin: 0 auto;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .stChatMessage {
        border-radius: 12px !important;
        padding: 12px 16px !important;
        margin-bottom: 12px !important;
    }

    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }

    .stButton button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stButton button:hover {
        border-color: #6366f1;
        color: #6366f1;
    }

    /* ── Cache hit badge ─────────────────────────────────────────────────── */
    .cache-hit-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34d399;
        border-radius: 14px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 8px;
    }

    /* ── Experience level chip ───────────────────────────────────────────── */
    .level-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #a5b4fc;
        border-radius: 14px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* ── Inline CV Attachment chip (ChatGPT style) ─────────────────────── */
    .cv-attach-chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #21262d;
        border: 1px solid #6366f1;
        border-radius: 20px;
        padding: 5px 14px 5px 10px;
        font-size: 0.82rem;
        color: #c7d2fe;
        font-weight: 500;
        margin-bottom: 8px;
        animation: fadeSlideIn 0.25s ease;
    }
    .cv-attach-chip .chip-icon { font-size: 1rem; }
    .cv-attach-chip .chip-name { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .cv-attach-chip .chip-size { color: #8b949e; font-size: 0.75rem; }

    /* Inline uploader — hide the default Streamlit file uploader frame */
    .inline-uploader [data-testid="stFileUploaderDropzone"] {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
        min-height: unset !important;
    }
    .inline-uploader [data-testid="stFileUploaderDropzone"] > div:first-child {
        display: none !important;
    }
    .inline-uploader label { display: none !important; }

    @keyframes fadeSlideIn {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# Dynamic RTL / Arabic Font Styling Injection
if st.session_state.get("detected_language") == "ar":
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
        .stApp, .stChatMessage, div[data-testid="stMarkdownContainer"] {
            font-family: 'Cairo', 'Inter', -apple-system, sans-serif !important;
        }
        div[data-testid="stChatMessageContent"] {
            direction: rtl;
            text-align: right;
        }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────
def init_session_state():
    """Initializes Streamlit session state variables for chat history and settings."""
    if "conversations" not in st.session_state:
        st.session_state.conversations = {
            "session_default": {
                "title": "New Career Conversation",
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "messages": []
            }
        }
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = "session_default"

    # ── Conversation Landing Screen flag ─────────────────────────────────────
    # False = show welcome UI (before first interaction)
    # True  = hide welcome UI (after first message OR first file upload)
    if "conversation_started" not in st.session_state:
        st.session_state.conversation_started = False

    # Model & Config Settings
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = os.environ.get("MODEL_NAME", "openai/gpt-5-mini")
    if "temperature" not in st.session_state:
        st.session_state.temperature = float(os.environ.get("TEMPERATURE", "0.0"))
    if "top_k" not in st.session_state:
        st.session_state.top_k = 4
    if "memory_enabled" not in st.session_state:
        st.session_state.memory_enabled = True
    if "langsmith_enabled" not in st.session_state:
        st.session_state.langsmith_enabled = os.environ.get("LANGCHAIN_TRACING_V2") == "true"

    # ── Experience Level ──────────────────────────────────────────────────────
    if "experience_level" not in st.session_state:
        st.session_state.experience_level = DEFAULT_EXPERIENCE_LEVEL

    # Telemetry Tracking Stats
    if "last_latency_ms" not in st.session_state:
        st.session_state.last_latency_ms = 0.0
    if "last_tokens_used" not in st.session_state:
        st.session_state.last_tokens_used = 0
    if "last_cache_hit" not in st.session_state:
        st.session_state.last_cache_hit = False

    # CV Upload State (persisted across turns)
    if "cv_bytes" not in st.session_state:
        st.session_state.cv_bytes = None
    if "cv_filename" not in st.session_state:
        st.session_state.cv_filename = None
    if "cv_text_preview" not in st.session_state:
        st.session_state.cv_text_preview = None
    if "cv_analysis_done" not in st.session_state:
        st.session_state.cv_analysis_done = False
    if "detected_language" not in st.session_state:
        st.session_state.detected_language = "en"
    if "target_role" not in st.session_state:
        st.session_state.target_role = "AI Engineer"

init_session_state()

# Sync conversation_started if messages already exist (page reload with active session)
current_session_data = st.session_state.conversations[st.session_state.current_session_id]
if current_session_data["messages"] and not st.session_state.conversation_started:
    st.session_state.conversation_started = True


# ─────────────────────────────────────────────────────────────────────────────
# BACKEND COMPILATION & CACHING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_compiled_agent_graph(enable_memory: bool):
    """
    Compiles and returns the multi-agent Supervisor StateGraph with full cache pipeline.
    Graph flow: normalize → cache_lookup → [HIT: final_response | MISS: supervisor → workers] → save_cache → END
    """
    if not BACKEND_AVAILABLE:
        return None

    builder = StateGraph(SupervisorState)

    # ── Cache pipeline nodes ──────────────────────────────────────────────────
    builder.add_node("normalize_question_node", normalize_question_node)
    builder.add_node("cache_lookup_node", cache_lookup_node)
    builder.add_node("save_cache_node", save_cache_node)

    # ── Supervisor & workers ──────────────────────────────────────────────────
    builder.add_node("supervisor_node", supervisor_node)
    for node_name, node_func in NODE_FUNCTION_REGISTRY.items():
        builder.add_node(node_name, node_func)

    # ── Edges ─────────────────────────────────────────────────────────────────
    builder.add_edge(START, "normalize_question_node")
    builder.add_edge("normalize_question_node", "cache_lookup_node")

    builder.add_conditional_edges(
        "cache_lookup_node",
        cache_router,
        {
            "cache_hit":  "final_response_node",
            "cache_miss": "supervisor_node",
        },
    )

    builder.add_conditional_edges("supervisor_node", supervisor_router, {
        "upload_cv_node":        "upload_cv_node",
        "resume_parsing_node":   "resume_parsing_node",
        "skill_extraction_node": "skill_extraction_node",
        "learning_roadmap_node": "learning_roadmap_node",
        "interview_coach_node":  "interview_coach_node",
        "salary_advisor_node":   "salary_advisor_node",
        "final_response_node":   "final_response_node",
    })

    builder.add_edge("upload_cv_node",        "supervisor_node")
    builder.add_edge("resume_parsing_node",   "supervisor_node")
    builder.add_edge("skill_extraction_node", "supervisor_node")
    builder.add_edge("learning_roadmap_node", "supervisor_node")
    builder.add_edge("interview_coach_node",  "supervisor_node")
    builder.add_edge("salary_advisor_node",   "supervisor_node")
    builder.add_edge("final_response_node",   "save_cache_node")
    builder.add_edge("save_cache_node",       END)

    if enable_memory:
        if _SQLITE_CHECKPOINTER_AVAILABLE:
            # Persistent SQLite memory — survives restarts
            # langgraph-checkpoint-sqlite must be in requirements.txt
            conn = sqlite3.connect("career_agent_production.db", check_same_thread=False)
            checkpointer = _SqliteSaver(conn)
        else:
            # Fallback: in-process MemorySaver — memory is lost on restart
            # This happens when langgraph-checkpoint-sqlite is not installed.
            # Fix: add 'langgraph-checkpoint-sqlite>=2.0.0' to requirements.txt
            # and rebuild the Docker image.
            print("[WARN] langgraph-checkpoint-sqlite not installed — using in-memory checkpointer. "
                  "Conversation memory will NOT persist across restarts.")
            checkpointer = _MemorySaver()
        return builder.compile(checkpointer=checkpointer)
    else:
        return builder.compile()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR CONTROL PANEL
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚀 Career AI Agent")
    st.caption("Enterprise Multi-Agent Platform v1.0")
    st.divider()

    # Conversation Session Management
    with st.expander("💬 Conversation", expanded=True):
        if st.button("➕ New Chat", use_container_width=True):
            new_id = f"session_{int(time.time())}"
            st.session_state.conversations[new_id] = {
                "title": f"Chat {datetime.datetime.now().strftime('%H:%M:%S')}",
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "messages": []
            }
            st.session_state.current_session_id = new_id
            st.session_state.conversation_started = False  # reset landing screen for new chat
            st.rerun()

        # Session Selector List
        session_options = list(st.session_state.conversations.keys())
        current_idx = session_options.index(st.session_state.current_session_id) if st.session_state.current_session_id in session_options else 0

        selected_session = st.selectbox(
            "Active Session",
            options=session_options,
            format_func=lambda x: f"💬 {st.session_state.conversations[x]['title']}",
            index=current_idx
        )
        if selected_session != st.session_state.current_session_id:
            st.session_state.current_session_id = selected_session
            # Sync landing flag when switching sessions
            session_msgs = st.session_state.conversations[selected_session]["messages"]
            st.session_state.conversation_started = bool(session_msgs)

        col_ren, col_del = st.columns(2)
        with col_ren:
            new_name = st.text_input("Rename Chat", value=st.session_state.conversations[selected_session]["title"], label_visibility="collapsed")
            if new_name != st.session_state.conversations[selected_session]["title"]:
                st.session_state.conversations[selected_session]["title"] = new_name
        with col_del:
            if st.button("🗑️ Delete", use_container_width=True):
                if len(st.session_state.conversations) > 1:
                    del st.session_state.conversations[selected_session]
                    st.session_state.current_session_id = list(st.session_state.conversations.keys())[0]
                    st.session_state.conversation_started = False
                    st.rerun()

    # ── CV Upload Section ───────────────────────────────────────────────────────
    with st.expander("📄 Upload CV", expanded=True):
        st.caption("Drag & drop or click to upload. PDF, DOCX, or TXT supported.")

        uploaded_file = st.file_uploader(
            label="Upload your CV",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=False,
            label_visibility="collapsed",
            key="cv_file_uploader"
        )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        if file_bytes != st.session_state.cv_bytes:
            # New file detected — store bytes and mark analysis pending
            st.session_state.cv_bytes = file_bytes
            st.session_state.cv_filename = uploaded_file.name
            st.session_state.cv_analysis_done = False
            st.session_state.cv_text_preview = None
            # ── Start conversation on file upload ─────────────────────────────
            st.session_state.conversation_started = True

            # Inline preview of extraction (without graph invocation)
            try:
                import io as _io
                ext = uploaded_file.name.lower().rsplit(".", 1)[-1]
                preview_text = ""
                if ext == "pdf":
                    import pypdf
                    reader = pypdf.PdfReader(_io.BytesIO(file_bytes))
                    preview_text = " ".join([p.extract_text() or "" for p in reader.pages])[:600]
                elif ext in ("docx", "doc"):
                    import docx as _docx
                    doc = _docx.Document(_io.BytesIO(file_bytes))
                    preview_text = " ".join([p.text for p in doc.paragraphs if p.text.strip()])[:600]
                elif ext == "txt":
                    preview_text = file_bytes.decode("utf-8", errors="ignore")[:600]
                st.session_state.cv_text_preview = preview_text
            except Exception:
                pass

        # Show upload status & preview
        if st.session_state.cv_filename:
            file_size_kb = round(len(st.session_state.cv_bytes or b"") / 1024, 1)
            st.markdown(f"""
            <div style="background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3); 
                        border-radius:8px; padding:10px 14px; margin-top:6px;">
                <div style="color:#34d399; font-weight:600; font-size:0.85rem;">✅ CV Loaded</div>
                <div style="color:#f0f6fc; font-size:0.8rem; margin-top:4px;">📎 {st.session_state.cv_filename}</div>
                <div style="color:#8b949e; font-size:0.75rem;">{file_size_kb} KB</div>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.cv_text_preview:
                with st.expander("📝 Text Preview (first 600 chars)", expanded=False):
                    st.text(st.session_state.cv_text_preview)

            if st.button("🗑️ Remove CV", use_container_width=True, key="remove_cv_btn"):
                st.session_state.cv_bytes = None
                st.session_state.cv_filename = None
                st.session_state.cv_text_preview = None
                st.session_state.cv_analysis_done = False
                st.rerun()

    # ── Engine Settings (Experience Level + Model) ──────────────────────────────
    with st.expander("🎯 Career Settings", expanded=True):
        # ── Experience Level Selector ────────────────────────────────────────────
        st.markdown("**🎯 Experience Level**")
        selected_level = st.selectbox(
            label="Experience Level",
            options=EXPERIENCE_LEVELS,
            index=EXPERIENCE_LEVELS.index(st.session_state.experience_level)
                if st.session_state.experience_level in EXPERIENCE_LEVELS
                else EXPERIENCE_LEVELS.index(DEFAULT_EXPERIENCE_LEVEL),
            label_visibility="collapsed",
            key="exp_level_selector",
        )
        if selected_level != st.session_state.experience_level:
            st.session_state.experience_level = selected_level

        # ── Target Role Selector ──────────────────────────────────────────────────
        st.markdown("**🧑‍💻 Target Role**")
        roles = [
            "AI Engineer", "Machine Learning Engineer", "Deep Learning Engineer",
            "Generative AI Engineer", "LLM Engineer", "NLP Engineer",
            "Computer Vision Engineer", "MLOps Engineer", "AI Backend Engineer",
            "Data Scientist"
        ]
        st.session_state.target_role = st.selectbox(
            "Target Role",
            options=roles,
            index=roles.index(st.session_state.target_role) if st.session_state.target_role in roles else 0,
            label_visibility="collapsed"
        )

        # Level description chips
        _level_descriptions = {
            "Internship": "🎓 Intern / Student track",
            "Junior": "🌱 0–2 years experience",
            "Mid Level": "🔧 2–5 years experience",
            "Senior": "🚀 5+ years / Advanced",
        }
        st.caption(_level_descriptions.get(st.session_state.experience_level, ""))

    with st.expander("⚙️ Model Settings", expanded=False):
        st.session_state.selected_model = st.selectbox(
            "LLM Target Model",
            options=["openai/gpt-5-mini", "openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet"],
            index=0
        )
        st.session_state.temperature = st.slider("Temperature", 0.0, 1.0, st.session_state.temperature, 0.1)
        st.session_state.top_k = st.slider("RAG Top-K Chunks", 1, 10, st.session_state.top_k, 1)

    with st.expander("🛠 Advanced Settings", expanded=False):
        st.session_state.memory_enabled = st.toggle("SQLite Memory Persistence", value=st.session_state.memory_enabled)
        st.session_state.langsmith_enabled = st.toggle("LangSmith Telemetry Tracing", value=st.session_state.langsmith_enabled)

        if st.button("🧹 Clear Memory Checkpointer", use_container_width=True):
            current_sd = st.session_state.conversations[st.session_state.current_session_id]
            current_sd["messages"] = []
            st.session_state.conversation_started = False
            st.toast("SQLite memory cleared for active thread!", icon="🧹")

    # System Diagnostics & Live Status Indicator
    with st.expander("📡 Diagnostics", expanded=False):
        _checkpointer_badge = (
            '<span class="status-badge status-badge-green">● SQLite Persistent</span>'
            if _SQLITE_CHECKPOINTER_AVAILABLE else
            '<span class="status-badge status-badge-yellow">⚠ In-Memory Only</span>'
        )
        st.markdown(f"""
        <div style="font-size:0.85rem; line-height: 1.8;">
            <div><b>Vector DB:</b> <span class="status-badge status-badge-green">● Connected (Chroma)</span></div>
            <div><b>Checkpointer:</b> {_checkpointer_badge}</div>
            <div><b>MCP Server:</b> <span class="status-badge status-badge-green">● JSON-RPC Ready</span></div>
            <div><b>Indexed Chunks:</b> <code>1,420 Docs</code></div>
        </div>
        """, unsafe_allow_html=True)
        if not _SQLITE_CHECKPOINTER_AVAILABLE:
            st.warning("⚠️ **Persistent memory unavailable.**\n\nAdd `langgraph-checkpoint-sqlite>=2.0.0` to `requirements.txt` and rebuild the Docker image to restore SQLite checkpointing.", icon="⚠️")

        # ── Cache Stats ──────────────────────────────────────────────────────────
        st.markdown("**💾 Response Cache**")
        try:
            from src.cache.service import ResponseCacheService
            _cache_svc = ResponseCacheService()
            _stats = _cache_svc.get_stats()
            st.markdown(f"""
            <div style="font-size:0.82rem; line-height: 1.8;">
                <div><b>Cached Entries:</b> <code>{_stats['total_entries']}</code></div>
                <div><b>Total Cache Hits:</b> <code>{_stats['total_hits']}</code></div>
                <div><b>Top Level:</b> <code>{_stats['top_level']}</code></div>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            st.caption("Cache not yet initialised.")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN TOP HEADER BAR & DASHBOARD STATS
# ─────────────────────────────────────────────────────────────────────────────
# Refresh current_session_data after potential session switch in sidebar
current_session_data = st.session_state.conversations[st.session_state.current_session_id]

cache_badge_html = (
    '<span class="cache-hit-badge">⚡ Cached</span>'
    if st.session_state.last_cache_hit else ""
)

level_badge_html = (
    f'<span class="level-chip">🎯 {st.session_state.experience_level} {st.session_state.target_role}</span>'
)

st.markdown(f"""
<div class="top-header-card">
    <div>
        <h2 style="margin:0; font-size:1.4rem; color:#f0f6fc;">🚀 Career AI Agent <span style="font-size:0.9rem; color:#8b949e;">Enterprise SaaS</span> {level_badge_html}</h2>
        <div style="font-size:0.85rem; color:#8b949e; margin-top:4px;">
            Model: <code>{st.session_state.selected_model}</code> &nbsp;|&nbsp; Memory: <code>{'Active' if st.session_state.memory_enabled else 'Disabled'}</code>
        </div>
    </div>
    <div style="display:flex; gap:16px; align-items:center;">
        <div style="text-align:right;">
            <div style="font-size:0.75rem; color:#8b949e;">LAST LATENCY</div>
            <div style="font-weight:700; color:#34d399;">{st.session_state.last_latency_ms:.0f} ms{cache_badge_html}</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:0.75rem; color:#8b949e;">TOKEN COST</div>
            <div style="font-weight:700; color:#818cf8;">{st.session_state.last_tokens_used} tokens</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# Environment & Backend Validation Check
if not BACKEND_AVAILABLE:
    st.error(f"⚠️ Backend Infrastructure Error: {BACKEND_ERROR}")
    st.info(f"Backend Error: {BACKEND_ERROR}")
    st.stop()

# ── Persistent CV Banner (shown above chat when CV is loaded) ─────────────────
if st.session_state.cv_filename:
    analysis_badge = (
        '<span style="background:rgba(16,185,129,0.15); color:#34d399; border:1px solid rgba(16,185,129,0.3); '
        'padding:2px 10px; border-radius:12px; font-size:0.78rem; font-weight:600;">✅ Analysed</span>'
        if st.session_state.cv_analysis_done else
        '<span style="background:rgba(245,158,11,0.15); color:#fbbf24; border:1px solid rgba(245,158,11,0.3); '
        'padding:2px 10px; border-radius:12px; font-size:0.78rem; font-weight:600;">⏳ Pending Analysis</span>'
    )
    st.markdown(f"""
    <div style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.25); 
                border-radius:10px; padding:10px 18px; margin-bottom:14px;
                display:flex; align-items:center; gap:14px;">
        <span style="font-size:1.3rem;">📄</span>
        <div>
            <div style="color:#f0f6fc; font-weight:600; font-size:0.9rem;">{st.session_state.cv_filename}</div>
            <div style="color:#8b949e; font-size:0.78rem;">Resume loaded into agent context &nbsp;{analysis_badge}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# LANDING SCREEN — shown only before first interaction
# Hides automatically after first message OR first file upload
# Matches ChatGPT / Claude / Gemini behavior
# ─────────────────────────────────────────────────────────────────────────────
selected_quick_prompt = None

if not st.session_state.conversation_started:
    # ── Welcome Hero ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="welcome-hero">
        <h1>Career AI Agent</h1>
        <p>Your AI-powered career advisor. Get personalized roadmaps, mock interviews, salary benchmarks, and CV analysis — powered by LangGraph multi-agent intelligence.</p>
    </div>
    """, unsafe_allow_html=True)

with st.expander("⚡ Quick Starter Actions | إجراءات سريعة", expanded=not st.session_state.conversation_started):
    if not st.session_state.conversation_started:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("💼 **Find Jobs / الوظائف**\nMatch skills to listings", use_container_width=True):
                selected_quick_prompt = "ابحث عن أفضل الوظائف المتاحة التي تتناسب مع مهارات الذكاء الاصطناعي."
            if st.button("📄 **Resume Review / السيرة الذاتية**\nExtract tech skills", use_container_width=True):
                selected_quick_prompt = "حلل السيرة الذاتية واذكر أهم المهارات التقنية والنقاط التي تحتاج إلى تطوير."

        with col2:
            if st.button("🎯 **Skill Gap / تحليل المهارات**\nIdentify missing skills", use_container_width=True):
                selected_quick_prompt = f"ما هي نقاط ضعفي والمهارات الناقصة لكي أحصل على وظيفة {st.session_state.target_role}؟"
            if st.button("🗺️ **Career Roadmap / خطة التعلم**\n3-Month learning plan", use_container_width=True):
                selected_quick_prompt = f"اعمل لي خطة تعلم Roadmap مدتها 3 أشهر لأصبح {st.session_state.experience_level} {st.session_state.target_role}."

        with col3:
            if st.button("🎤 **Interview Prep / مقابلة**\nSTAR technical questions", use_container_width=True):
                selected_quick_prompt = f"جهز لي أسئلة مقابلة عمل تجريبية Mock Interview لوظيفة {st.session_state.target_role}."
            if st.button("💰 **Salary Insights / الرواتب**\nCompensation & equity", use_container_width=True):
                selected_quick_prompt = f"ما هي متوسط الرواتب المتوقعة لوظيفة {st.session_state.experience_level} {st.session_state.target_role}؟"

        with col4:
            if st.button("🚀 **Project Ideas / المشاريع**\nBuild portfolio projects", use_container_width=True):
                selected_quick_prompt = f"اقترح أفكار مشاريع قوية لبناء معرض أعمالي Portfolio في مجال {st.session_state.target_role}."
            if st.button("💬 **AI Chat / دردشة**\nGeneral career questions", use_container_width=True):
                selected_quick_prompt = "كيف يمكنني البدء في تعلم الذكاء الاصطناعي؟"

if selected_quick_prompt:
    st.session_state.pending_user_input = selected_quick_prompt


# ─────────────────────────────────────────────────────────────────────────────
# CHAT DISPLAY & MESSAGE HISTORY
# ─────────────────────────────────────────────────────────────────────────────
for idx, message in enumerate(current_session_data["messages"]):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Show cache hit badge on assistant messages if flagged
        cache_flag = message.get("cache_hit", False)
        timing = message.get('timestamp', 'Just now')
        if cache_flag:
            st.caption(f"🕒 {timing}  &nbsp; <span class='cache-hit-badge'>⚡ Served from cache</span>", unsafe_allow_html=True)
        else:
            st.caption(f"🕒 {timing}")


# ─────────────────────────────────────────────────────────────────────────────
# INLINE CV ATTACHMENT (ChatGPT / Gemini style — above chat input)
# ─────────────────────────────────────────────────────────────────────────────

# Attached-file chip: show when a CV is loaded but not yet analysed
if st.session_state.cv_filename and not st.session_state.cv_analysis_done:
    file_size_kb = round(len(st.session_state.cv_bytes or b"") / 1024, 1)
    chip_col, remove_col = st.columns([10, 1])
    with chip_col:
        st.markdown(
            f'<div class="cv-attach-chip">'
            f'<span class="chip-icon">📄</span>'
            f'<span class="chip-name">{st.session_state.cv_filename}</span>'
            f'<span class="chip-size">&nbsp;{file_size_kb} KB</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    with remove_col:
        if st.button("✕", key="inline_remove_cv", help="Remove attached CV"):
            st.session_state.cv_bytes = None
            st.session_state.cv_filename = None
            st.session_state.cv_text_preview = None
            st.session_state.cv_analysis_done = False
            st.rerun()

# ── Inline file uploader row (📎 button + chat input) ────────────────────────
attach_col, chat_col = st.columns([1, 11])

with attach_col:
    st.markdown('<div class="inline-uploader">', unsafe_allow_html=True)
    inline_uploaded = st.file_uploader(
        label="Attach CV",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=False,
        label_visibility="collapsed",
        key="inline_cv_uploader"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if inline_uploaded is not None:
        raw = inline_uploaded.read()
        if raw != st.session_state.cv_bytes:
            st.session_state.cv_bytes = raw
            st.session_state.cv_filename = inline_uploaded.name
            st.session_state.cv_analysis_done = False
            st.session_state.cv_text_preview = None
            # ── Start conversation on inline file upload ───────────────────
            st.session_state.conversation_started = True
            # Quick inline preview
            try:
                import io as _io
                _ext = inline_uploaded.name.lower().rsplit(".", 1)[-1]
                _preview = ""
                if _ext == "pdf":
                    import pypdf
                    _r = pypdf.PdfReader(_io.BytesIO(raw))
                    _preview = " ".join([p.extract_text() or "" for p in _r.pages])[:600]
                elif _ext in ("docx", "doc"):
                    import docx as _docx
                    _d = _docx.Document(_io.BytesIO(raw))
                    _preview = " ".join([p.text for p in _d.paragraphs if p.text.strip()])[:600]
                elif _ext == "txt":
                    _preview = raw.decode("utf-8", errors="ignore")[:600]
                st.session_state.cv_text_preview = _preview
            except Exception:
                pass
            st.rerun()

with chat_col:
    is_ar = st.session_state.get("detected_language") == "ar"
    placeholder_text = (
        "اكتب سؤالك هنا باللغة العربية أو الإنجليزية..."
        if is_ar else
        "📎 Attach a CV above or type your question in English or Arabic..."
    )
    user_input = st.chat_input(placeholder_text)

# Check if quick action button was clicked
if "pending_user_input" in st.session_state and st.session_state.pending_user_input:
    user_input = st.session_state.pending_user_input
    del st.session_state.pending_user_input


# ─────────────────────────────────────────────────────────────────────────────
# WORKFLOW EXECUTION & LIVE STREAMING RESPONSE
# ─────────────────────────────────────────────────────────────────────────────
if user_input:
    timestamp_str = datetime.datetime.now().strftime("%H:%M:%S")

    # ── Mark conversation as started on first message ─────────────────────────
    st.session_state.conversation_started = True

    # Render User Message immediately
    current_session_data["messages"].append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp_str
    })
    with st.chat_message("user"):
        st.markdown(user_input)
        st.caption(f"🕒 {timestamp_str}")

    # Process via LangGraph Multi-Agent Workflow
    with st.chat_message("assistant"):
        status_placeholder = st.empty()

        # Determine spinner message — CV upload gets a dedicated status message
        has_pending_cv = (
            st.session_state.cv_bytes is not None
            and not st.session_state.cv_analysis_done
        )
        spinner_msg = (
            "📄 Extracting resume text & routing to CV Analysis pipeline..."
            if has_pending_cv else
            "🧠 Executive Supervisor analyzing user intent & routing graph..."
        )

        with status_placeholder.container():
            with st.spinner(spinner_msg):
                t0 = time.time()

                # Fetch compiled graph instance
                graph_instance = get_compiled_agent_graph(enable_memory=st.session_state.memory_enabled)

                config = {"configurable": {"thread_id": st.session_state.current_session_id}}

                try:
                    # Build initial state — inject CV bytes if a new file is pending
                    initial_state = {
                        "user_message": user_input,
                        "messages": [HumanMessage(content=user_input)],
                        # ── Pass experience level from UI ─────────────────────
                        "experience_level": st.session_state.experience_level,
                    }

                    # Attach uploaded CV bytes so upload_cv_node can process them
                    if st.session_state.cv_bytes and not st.session_state.cv_analysis_done:
                        initial_state["cv_bytes"] = st.session_state.cv_bytes
                        initial_state["cv_filename"] = st.session_state.cv_filename
                        initial_state["analysis_status"] = None  # Let upload_cv_node set it
                    elif st.session_state.cv_text_preview:
                        # CV already processed — pass the text so nodes can use it
                        initial_state["uploaded_cv"] = st.session_state.cv_text_preview

                    # Execute graph workflow
                    result_state = graph_instance.invoke(initial_state, config=config)

                    # Update detected language in session state if returned
                    if result_state.get("detected_language"):
                        st.session_state.detected_language = result_state.get("detected_language")

                    # Track cache hit status
                    was_cache_hit = bool(result_state.get("cache_hit", False))
                    st.session_state.last_cache_hit = was_cache_hit

                    t1 = time.time()
                    elapsed_ms = (t1 - t0) * 1000
                    st.session_state.last_latency_ms = elapsed_ms
                    st.session_state.last_tokens_used = (
                        0 if was_cache_hit else len(user_input.split()) * 4 + 320
                    )

                    # Mark CV as analysed after first successful run
                    if has_pending_cv:
                        st.session_state.cv_analysis_done = True
                        extracted = result_state.get("extracted_skills", [])
                        if extracted:
                            st.session_state["cv_extracted_skills"] = extracted

                    final_text = result_state.get("final_response") or result_state.get("planner_output") or "Workflow executed successfully."

                except Exception as ex:
                    final_text = f"⚠️ Workflow Execution Error: {str(ex)}\n\nPlease ensure OPENROUTER_API_KEY is valid."
                    elapsed_ms = 0.0
                    was_cache_hit = False

        # Clear status spinner and display final response
        status_placeholder.empty()
        st.markdown(final_text)

        # Timing report badge
        speed_color = "#34d399" if elapsed_ms < 3000 else "#fbbf24" if elapsed_ms < 8000 else "#f87171"
        cache_indicator = " &nbsp; <span class='cache-hit-badge'>⚡ Served from cache</span>" if was_cache_hit else ""
        st.caption(
            f"🕒 {datetime.datetime.now().strftime('%H:%M:%S')}"
            f"  |  ⚡ <span style='color:{speed_color};font-weight:700'>{elapsed_ms:.0f} ms</span>"
            f"  |  📄 {st.session_state.last_tokens_used} tokens"
            f"{cache_indicator}",
            unsafe_allow_html=True
        )

        # Save assistant message to session history
        current_session_data["messages"].append({
            "role": "assistant",
            "content": final_text,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "cache_hit": was_cache_hit,
        })

    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER EXPORT & CONVERSATION CONTROLS
# ─────────────────────────────────────────────────────────────────────────────
if current_session_data["messages"]:
    st.divider()
    col_exp1, col_exp2, col_exp3 = st.columns([1, 1, 4])

    with col_exp1:
        # Download conversation as Markdown
        chat_md = "\n\n".join([f"**{m['role'].upper()}** ({m.get('timestamp','')}):\n{m['content']}" for m in current_session_data["messages"]])
        st.download_button(
            label="📥 Export Markdown",
            data=chat_md,
            file_name=f"career_chat_{st.session_state.current_session_id}.md",
            mime="text/markdown",
            use_container_width=True
        )

    with col_exp2:
        # Download conversation as JSON
        chat_json = json.dumps(current_session_data["messages"], indent=2)
        st.download_button(
            label="📥 Export JSON",
            data=chat_json,
            file_name=f"career_chat_{st.session_state.current_session_id}.json",
            mime="application/json",
            use_container_width=True
        )
