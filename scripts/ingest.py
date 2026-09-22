import os
import sys
import glob
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma


from src.models.embeddings import get_embeddings

def extract_metadata(file_path: Path) -> dict:
    # Example: data/interview/AI_Interview_Guide.md -> type: interview
    parts = file_path.parts
    # Find index of 'data'
    try:
        data_idx = parts.index('data')
        document_type = parts[data_idx + 1] if len(parts) > data_idx + 2 else "unknown"
    except ValueError:
        document_type = "unknown"
        
    return {
        "source": str(file_path.absolute()),
        "file_name": file_path.name,
        "document_type": document_type,
        "language": "en"
    }

def process_markdown_file(file_path: Path) -> list[Document]:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(content)
    
    # Further split to ensure chunks aren't too massive for embeddings
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    
    final_docs = char_splitter.split_documents(md_header_splits)
    
    # Add metadata
    meta = extract_metadata(file_path)
    for doc in final_docs:
        doc.metadata.update(meta)
        
    return final_docs

def process_pdf_file(file_path: Path) -> list[Document]:
    loader = PyPDFLoader(str(file_path))
    docs = loader.load()
    
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    final_docs = char_splitter.split_documents(docs)
    
    meta = extract_metadata(file_path)
    for doc in final_docs:
        # PyPDFLoader already sets 'source' and 'page', we just update with our schema
        doc.metadata.update(meta)
        
    return final_docs

def main():
    print("Starting document ingestion pipeline...")
    t0 = time.time()
    
    data_dir = Path(os.path.join(os.path.dirname(__file__), '..', 'data'))
    
    if not data_dir.exists():
        print(f"Error: Directory {data_dir} does not exist.")
        sys.exit(1)
        
    # Discover files
    md_files = list(data_dir.rglob("*.md"))
    pdf_files = list(data_dir.rglob("*.pdf"))
    
    all_files = md_files + pdf_files
    print(f"Found {len(all_files)} files ({len(md_files)} Markdown, {len(pdf_files)} PDF).")
    
    all_documents = []
    
    for fpath in all_files:
        try:
            if fpath.suffix.lower() == '.md':
                docs = process_markdown_file(fpath)
            elif fpath.suffix.lower() == '.pdf':
                docs = process_pdf_file(fpath)
            else:
                continue
            all_documents.extend(docs)
        except Exception as e:
            print(f"Failed to process {fpath}: {e}")
            
    print(f"Generated {len(all_documents)} total chunked documents.")
    
    # Initialize Vector DB and Embeddings
    embeddings = get_embeddings()
    db_path = os.path.join(os.path.dirname(__file__), '..', 'storage', 'vector_db')
    os.makedirs(db_path, exist_ok=True)
    
    vectordb = Chroma(
        persist_directory=db_path,
        embedding_function=embeddings
    )
    
    print("Indexing documents into ChromaDB (Incremental mode via Hash IDs)...")
    
    import hashlib
    def get_id(doc):
        # Generate a unique hash based on content and metadata
        return hashlib.md5((doc.page_content + str(doc.metadata)).encode()).hexdigest()
        
    ids = [get_id(doc) for doc in all_documents]
    
    # Check existing documents
    existing_data = vectordb.get(ids=ids)
    existing_ids = set(existing_data.get('ids', []))
    
    new_docs = []
    new_ids = []
    
    for doc, doc_id in zip(all_documents, ids):
        if doc_id not in existing_ids:
            new_docs.append(doc)
            new_ids.append(doc_id)
            
    if new_docs:
        vectordb.add_documents(new_docs, ids=new_ids)
        result_msg = f"Added {len(new_docs)} new chunks. Skipped {len(existing_ids)} duplicates."
    else:
        result_msg = f"No new documents to add. Skipped {len(existing_ids)} duplicates."
        
    t_end = time.time()
    
    print("\n" + "="*50)
    print("INGESTION REPORT")
    print("="*50)
    print(f"Total Files Found      : {len(all_files)}")
    print(f"Total Chunks Generated : {len(all_documents)}")
    print(f"Indexing Result        : {result_msg}")
    print(f"Total Time             : {t_end - t0:.2f} seconds")
    print("="*50)

if __name__ == "__main__":
    main()
