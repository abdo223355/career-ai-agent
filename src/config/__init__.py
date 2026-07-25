"""
src/config package
==================
Single import surface for all application configuration.

Usage anywhere in the codebase
-------------------------------
    from src.config import settings, constants

    llm_name   = settings.MODEL_NAME
    data_path  = constants.DATA_DIR
"""

from src.config.constants import (  # noqa: F401  — re-exported for convenience
    CHROMA_DISTANCE_METRIC,
    DATA_DIR,
    LOGS_DIR,
    MAX_CHUNK_OVERLAP,
    MAX_CHUNK_SIZE,
    MAX_TOKENS,
    MAX_TOP_K,
    PROMPTS_DIR,
    PROJECT_ROOT,
    STORAGE_DIR,
    SUPPORTED_EXTENSIONS,
    CV_PROMPT_FILE,
    INTERVIEW_PROMPT_FILE,
    ROADMAP_PROMPT_FILE,
    SYSTEM_PROMPT_FILE,
)
from src.config.settings import settings  # noqa: F401  — re-exported for convenience

__all__ = [
    # settings singleton
    "settings",
    # path constants
    "PROJECT_ROOT",
    "DATA_DIR",
    "STORAGE_DIR",
    "LOGS_DIR",
    "PROMPTS_DIR",
    # prompt file names
    "SYSTEM_PROMPT_FILE",
    "CV_PROMPT_FILE",
    "INTERVIEW_PROMPT_FILE",
    "ROADMAP_PROMPT_FILE",
    # ChromaDB
    "CHROMA_DISTANCE_METRIC",
    # limits
    "MAX_CHUNK_SIZE",
    "MAX_CHUNK_OVERLAP",
    "MAX_TOP_K",
    "MAX_TOKENS",
    # ingestion
    "SUPPORTED_EXTENSIONS",
]
