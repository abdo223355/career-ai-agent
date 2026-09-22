"""
src/cache/normalizer.py
=======================
Question normalization and hashing utilities for the response cache.

Normalization makes semantically equivalent questions map to the same
cache key, even when phrasing or formatting differs slightly.

Normalization pipeline
----------------------
    1. Decode bytes → str (if necessary)
    2. Lowercase
    3. Strip leading/trailing whitespace
    4. Collapse multiple consecutive whitespace characters into one space
    5. Normalize common punctuation variants (curly quotes → straight, etc.)
    6. Strip trailing punctuation that does not change meaning

Examples
--------
    "What is LangGraph?"     → "what is langgraph"
    "What is langgraph ?"    → "what is langgraph"
    "what is LangGraph"      → "what is langgraph"
    "  WHAT  IS  LangGraph " → "what is langgraph"
"""

from __future__ import annotations

import hashlib
import re
import unicodedata


# ── Punctuation normalisation map ─────────────────────────────────────────────
_PUNCT_REPLACEMENTS: list[tuple[str, str]] = [
    # Curly quotes → straight quotes
    ("\u2018", "'"),
    ("\u2019", "'"),
    ("\u201c", '"'),
    ("\u201d", '"'),
    # Em-dash / en-dash → hyphen
    ("\u2013", "-"),
    ("\u2014", "-"),
    # Ellipsis → three dots
    ("\u2026", "..."),
]

# Trailing punctuation that does not change question meaning
_TRAILING_PUNCT = re.compile(r"[?!.,;:\-]+$")

# Multiple consecutive whitespace → single space
_MULTI_SPACE = re.compile(r"\s+")


def normalize_question(text: str) -> str:
    """
    Normalize a user question for deterministic cache key generation.

    Parameters
    ----------
    text:
        Raw user message as received from the UI.

    Returns
    -------
    str
        Normalized form suitable for hashing and storage.
    """
    if not text:
        return ""

    # Handle bytes gracefully
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="ignore")

    # 1. Unicode NFKC normalisation (handles half-width chars, ligatures, etc.)
    text = unicodedata.normalize("NFKC", text)

    # 2. Apply punctuation replacements
    for original, replacement in _PUNCT_REPLACEMENTS:
        text = text.replace(original, replacement)

    # 3. Lowercase
    text = text.lower()

    # 4. Collapse whitespace
    text = _MULTI_SPACE.sub(" ", text)

    # 5. Strip
    text = text.strip()

    # 6. Remove trailing punctuation (e.g., trailing "?" or ".")
    text = _TRAILING_PUNCT.sub("", text).strip()

    return text


def hash_question(normalized: str) -> str:
    """
    Return the SHA-256 hex digest of a normalized question string.

    Parameters
    ----------
    normalized:
        Output of :func:`normalize_question`.

    Returns
    -------
    str
        64-character lowercase hex string (SHA-256).
    """
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
