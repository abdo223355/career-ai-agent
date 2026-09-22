from langchain_huggingface import HuggingFaceEmbeddings

def get_embeddings():
    """
    Returns the configured embedding model for the project.
    """
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
