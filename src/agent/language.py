import re
from typing import Optional, List, Any

# Arabic Unicode character ranges
ARABIC_PATTERN = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')

def detect_language(text: Optional[str]) -> str:
    """
    Detects language ('ar' or 'en') from input text.
    If any Arabic characters are found in the string, returns 'ar', otherwise 'en'.
    """
    if not text:
        return "en"
    if ARABIC_PATTERN.search(text):
        return "ar"
    return "en"

def detect_conversation_language(
    user_message: Optional[str] = None,
    cv_text: Optional[str] = None,
    messages: Optional[List[Any]] = None,
    current_detected: Optional[str] = None
) -> str:
    """
    Detects language based on priority:
    1. Direct user message (if present)
    2. Uploaded CV text (if present and contains Arabic)
    3. Conversation history messages
    4. Previously detected language state
    5. Default 'en'
    """
    # Check current user message first
    if user_message and user_message.strip():
        if ARABIC_PATTERN.search(user_message):
            return "ar"
        else:
            return "en"

    # Check CV text if available
    if cv_text and ARABIC_PATTERN.search(cv_text):
        return "ar"

    # Check messages in history
    if messages:
        for msg in reversed(messages):
            content = getattr(msg, "content", "") or str(msg)
            if ARABIC_PATTERN.search(content):
                return "ar"

    # Fallback to current detected or default 'en'
    return current_detected or "en"

def get_language_prompt_instruction(lang: str) -> str:
    """
    Returns system prompt instructions for language compliance and technical terms preservation.
    """
    if lang == "ar":
        return (
            "\n\nCRITICAL LANGUAGE INSTRUCTION:\n"
            "Respond in ARABIC (اللغة العربية).\n"
            "Rules:\n"
            "- Write fluent, professional Arabic for all explanations, feedback, summaries, and advice.\n"
            "- KEEP ALL TECHNICAL TERMS, TOOL NAMES, FRAMEWORK NAMES, PROGRAMMING LANGUAGES, "
            "AND ABBREVIATIONS IN ENGLISH (e.g., Python, LangChain, LangGraph, PyTorch, Docker, RAG, "
            "SQL, ATS, PostgreSQL, ChromaDB, REST API, Microservices, GitHub, System Design).\n"
            "- Do NOT translate technical terms into Arabic."
        )
    else:
        return (
            "\n\nCRITICAL LANGUAGE INSTRUCTION:\n"
            "Respond in ENGLISH.\n"
            "Provide professional, clear, and structured career guidance in English."
        )
