"""
src/prompts/contextualize_question_prompt.py
============================================
Defines CONTEXTUALIZE_Q_PROMPT — the ChatPromptTemplate used by
``create_history_aware_retriever`` to rewrite the latest user message
into a self-contained standalone question.

Why this step exists
--------------------
In a multi-turn conversation a user often asks follow-up questions that
contain pronouns or implicit references:

    Turn 1 Q: "What skills does a data scientist need?"
    Turn 2 Q: "How long does it take to learn them?"

The retriever cannot search for "them" — it needs a fully resolved query:

    "How long does it take to learn the skills needed to become a data scientist?"

This prompt instructs the model to perform that resolution using the
conversation history *without* answering the question.

Template variables
------------------
chat_history : list[BaseMessage]
    The previous conversation turns, injected via ``MessagesPlaceholder``.
    LangChain's ``create_history_aware_retriever`` populates this automatically.
input : str
    The raw latest user message.
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

CONTEXTUALIZE_Q_PROMPT: ChatPromptTemplate = ChatPromptTemplate.from_messages(
    [
        # ------------------------------------------------------------------
        # System turn — task definition
        # ------------------------------------------------------------------
        (
            "system",
            "You are a question-rewriting assistant. "
            "Your only task is to rewrite the user's latest question into a "
            "fully self-contained standalone question that can be understood "
            "without any prior conversation history.\n\n"
            "Rules:\n"
            "- Resolve all pronouns (it, they, he, she, this, that, those, "
            "these, them, their) using the conversation history.\n"
            "- Preserve the original intent and meaning exactly.\n"
            "- Do NOT answer the question.\n"
            "- Do NOT add information that was not implied by the original question.\n"
            "- Return ONLY the rewritten standalone question — nothing else.\n"
            "- If the question is already self-contained, return it unchanged.",
        ),
        # ------------------------------------------------------------------
        # Conversation history — populated automatically by LangChain
        # ------------------------------------------------------------------
        MessagesPlaceholder("chat_history"),
        # ------------------------------------------------------------------
        # Human turn — the raw latest question to be rewritten
        # ------------------------------------------------------------------
        (
            "human",
            "{input}",
        ),
    ]
)
