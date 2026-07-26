import os
from langchain_openai import ChatOpenAI

def get_llm():
    """
    Returns the configured primary ChatModel for the agent.
    """
    return ChatOpenAI(
        model="gpt-5-mini",
        api_key=os.environ.get("OPENAI_API_KEY", "dummy")
    )
