import os
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_core.documents import BaseDocumentCompressor
from langchain_core.callbacks import Callbacks
from pydantic import ConfigDict
from typing import Sequence, Optional, Any
from langchain_core.documents import Document
from langchain_classic.retrievers import ContextualCompressionRetriever
import functools

@functools.lru_cache(maxsize=1)
def get_cross_encoder():
    return HuggingFaceCrossEncoder(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")

@functools.lru_cache(maxsize=1)
def get_vectordb(embeddings):
    base_dir = os.getcwd()
    if base_dir.endswith("notebook"):
        db_path = "../storage/vector_db"
    else:
        db_path = "storage/vector_db"
        
    return Chroma(
        persist_directory=db_path,
        embedding_function=embeddings
    )

class CustomCrossEncoderReranker(BaseDocumentCompressor):
    model: Any
    top_n: int = 3
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        if not documents:
            return []
        
        text_pairs = [[query, doc.page_content] for doc in documents]
        scores = self.model.score(text_pairs)
        
        scored_docs = list(zip(documents, scores))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        top_docs = []
        for doc, score in scored_docs[:self.top_n]:
            doc.metadata["relevance_score"] = float(score)
            top_docs.append(doc)
            
        return top_docs

def get_advanced_retriever(embeddings, document_types: Optional[list[str]] = None):
    """
    Returns the production-ready Ensemble Retriever (Vector + BM25) 
    wrapped with a Cross-Encoder Reranker.
    Supports dynamic filtering via document_types.
    """
    vectordb = get_vectordb(embeddings)
    
    search_kwargs = {"k": 10}
    if document_types:
        # Chroma expects an $in operator for multiple values
        search_kwargs["filter"] = {"document_type": {"$in": document_types}}
        
    base_retriever = vectordb.as_retriever(search_kwargs=search_kwargs)
    
    # 3. BM25 Retriever
    all_docs_data = vectordb.get()
    filtered_docs = []
    
    for txt, meta in zip(all_docs_data['documents'], all_docs_data['metadatas']):
        if document_types and meta.get("document_type") not in document_types:
            continue
        filtered_docs.append(Document(page_content=txt, metadata=meta))
    
    if not filtered_docs:
        # Fallback to base retriever if BM25 cannot be built
        ensemble_retriever = base_retriever
    else:
        bm25_retriever = BM25Retriever.from_documents(filtered_docs)
        bm25_retriever.k = 10
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, base_retriever],
            weights=[0.5, 0.5]
        )
    
    # 5. Cross-Encoder Reranker
    cross_encoder = get_cross_encoder()
    compressor = CustomCrossEncoderReranker(model=cross_encoder, top_n=3)
    
    advanced_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=ensemble_retriever
    )
    
    return advanced_retriever
