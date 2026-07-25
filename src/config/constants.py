"""
src/config/constants.py
=======================
Design-time constants — values that are fixed regardless of environment.

Rule of thumb
-------------
- If a value could differ between dev and prod   → put it in settings.py
- If a value is hardcoded by design and never changes → put it here

Never import settings.py from this file (would create a circular dependency).
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Project root — useful for constructing absolute paths throughout the app.
# Resolves to the directory containing src/ (i.e. the repo root).
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Directory layout — absolute paths derived from PROJECT_ROOT.
# These mirror the physical structure and are used by scripts and the RAG
# pipeline to avoid hardcoded string paths scattered across the codebase.
# ---------------------------------------------------------------------------
DATA_DIR: Path = PROJECT_ROOT / "data"
STORAGE_DIR: Path = PROJECT_ROOT / "storage"
LOGS_DIR: Path = PROJECT_ROOT / "logs"
PROMPTS_DIR: Path = PROJECT_ROOT / "src" / "prompts"

# ---------------------------------------------------------------------------
# Prompt file names
# Keep filenames here so a rename only requires one change.
# ---------------------------------------------------------------------------
SYSTEM_PROMPT_FILE: str = "system_prompt.txt"
CV_PROMPT_FILE: str = "cv_prompt.txt"
INTERVIEW_PROMPT_FILE: str = "interview_prompt.txt"
ROADMAP_PROMPT_FILE: str = "roadmap_prompt.txt"

# ---------------------------------------------------------------------------
# ChromaDB
# ---------------------------------------------------------------------------
# Distance metric used when creating the collection.
CHROMA_DISTANCE_METRIC: str = "cosine"

# ---------------------------------------------------------------------------
# RAG pipeline limits
# Hard upper bounds that prevent runaway resource usage.
# ---------------------------------------------------------------------------
MAX_CHUNK_SIZE: int = 4_000      # characters — refuse chunks larger than this
MAX_CHUNK_OVERLAP: int = 800     # characters — overlap cannot exceed this
MAX_TOP_K: int = 20              # retrieved chunks — cap to avoid token overflow

# ---------------------------------------------------------------------------
# LLM output constraints
# ---------------------------------------------------------------------------
MAX_TOKENS: int = 2_048          # maximum tokens in a single LLM response

# ---------------------------------------------------------------------------
# Supported data-file extensions for the ingestion pipeline.
# Only files with these suffixes will be loaded from data/.
# ---------------------------------------------------------------------------
SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({".pdf", ".txt", ".md", ".docx"})
