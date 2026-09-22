import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables from .env
load_dotenv()

# Single production ChatModel instance using OpenRouter
llm = ChatOpenAI(
    model=os.environ.get("MODEL_NAME", "openai/gpt-5-mini"),
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=float(os.environ.get("TEMPERATURE", "0.0")),
    max_tokens=1024
)

def get_llm():
    """
    Returns the single shared ChatModel instance for all agents.
    """
    return llm
