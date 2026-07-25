"""
src/prompts
===========
Public API for the prompts package.

This package provides three artefacts consumed by the RAG chain:

SYSTEM_PROMPT
    A plain string. Injected as the ``{system_prompt}`` variable inside
    ``QA_PROMPT``. Written as a constant (not a template) because it
    contains no runtime variables — it is static policy text.

QA_PROMPT
    A ``ChatPromptTemplate`` for the final answer generation step.
    Variables: ``{system_prompt}``, ``{context}``, ``{input}``.

CONTEXTUALIZE_Q_PROMPT
    A ``ChatPromptTemplate`` for the history-aware retrieval step.
    Rewrites a follow-up question into a fully self-contained standalone
    question using the prior ``{chat_history}``.
    Variables: ``{chat_history}`` (via ``MessagesPlaceholder``), ``{input}``.

Typical usage
-------------
    from src.prompts import SYSTEM_PROMPT, QA_PROMPT, CONTEXTUALIZE_Q_PROMPT

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, CONTEXTUALIZE_Q_PROMPT
    )
    question_answer_chain = create_stuff_documents_chain(llm, QA_PROMPT)
    rag_chain = create_retrieval_chain(
        history_aware_retriever, question_answer_chain
    )
    response = rag_chain.invoke({
        "input": user_question,
        "chat_history": chat_history,
        "system_prompt": SYSTEM_PROMPT,
    })
"""

from src.prompts.contextualize_question_prompt import CONTEXTUALIZE_Q_PROMPT
from src.prompts.qa_prompt import QA_PROMPT
from src.prompts.system_prompt import SYSTEM_PROMPT

__all__: list[str] = [
    "SYSTEM_PROMPT",
    "QA_PROMPT",
    "CONTEXTUALIZE_Q_PROMPT",
]
