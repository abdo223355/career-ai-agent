"""
src/prompts/qa_prompt.py
========================
Defines QA_PROMPT — the ChatPromptTemplate used for the main
retrieval-augmented generation (RAG) answer step.

Template variables
------------------
system_prompt : str
    The static system instruction from ``system_prompt.py``.
    Injected once per chain construction so the system message is never
    duplicated across turns.
context : str
    The concatenated retrieved document chunks produced by the retriever.
    Formatted by LangChain's ``format_documents`` helper before insertion.
input : str
    The current (already contextualised) user question.
"""

from langchain_core.prompts import ChatPromptTemplate

QA_PROMPT: ChatPromptTemplate = ChatPromptTemplate.from_messages(
    [
        # ------------------------------------------------------------------
        # System turn — static policy + dynamic context + instruction
        # ------------------------------------------------------------------
        (
            "system",
            "{system_prompt}"
            "\n\n"
            "## Retrieved context\n\n"
            "{context}"
            "\n\n"
            "Use ONLY the retrieved context above to answer the question. "
            "If the answer is not present in the context, say so clearly.",
        ),
        # ------------------------------------------------------------------
        # Human turn — the contextualised question
        # ------------------------------------------------------------------
        (
            "human",
            "{input}",
        ),
    ]
)
