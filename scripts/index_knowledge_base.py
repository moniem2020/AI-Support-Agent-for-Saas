"""
Knowledge Base Indexing Script.
Loads markdown files, chunks them, and builds FAISS + BM25 indexes.
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import KNOWLEDGE_BASE_DIR, INDEXES_DIR
from src.rag.chunker import chunker
from src.rag.chunker import chunker
from src.rag.dense_retriever import DenseRetriever
from src.rag.sparse_retriever import SparseRetriever


def load_markdown_files(directory: Path) -> list:
    """Load all markdown files from directory."""
    documents = []
    
    for file_path in directory.glob("*.md"):
        if file_path.name.startswith("."):
            continue
            
        print(f"  Loading: {file_path.name}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        documents.append({
            "content": content,
            "metadata": {
                "doc_id": file_path.stem,
                "filename": file_path.name,
                "source": str(file_path)
            }
        })
    
    return documents


def chunk_documents(documents: list) -> list:
    """Chunk all documents."""
    all_chunks = []
    
    for doc in documents:
        chunk_objs = chunker.chunk_document(
            content=doc["content"],
            doc_id=doc["metadata"]["doc_id"],
            metadata=doc["metadata"]
        )
        all_chunks.extend(chunk_objs)
        print(f"  {doc['metadata']['doc_id']}: {len(chunk_objs)} chunks")
    
    return all_chunks


def build_indexes(chunks: list):
    """Build and save FAISS and BM25 indexes."""
    # Build dense (FAISS) index
    # Build dense (FAISS) index
    print("\nBuilding FAISS index...")
    dense = DenseRetriever()
    dense.add_chunks(chunks)
    # dense.save_index() is called inside add_chunks
    print(f"  FAISS index saved with {len(chunks)} vectors")
    
    # Build sparse (BM25) index
    print("\nBuilding BM25 index...")
    sparse = SparseRetriever()
    sparse.add_chunks(chunks)
    # sparse.save_index() is called inside add_chunks
    print(f"  BM25 index saved with {len(chunks)} documents")


def main():
    """Main indexing function."""
    print("=" * 50)
    print("ProTaskFlow Knowledge Base Indexer")
    print("=" * 50)
    
    # Check for knowledge base files
    if not KNOWLEDGE_BASE_DIR.exists():
        print(f"Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}")
        return
    
    md_files = list(KNOWLEDGE_BASE_DIR.glob("*.md"))
    if not md_files:
        print(f"[WARN] No markdown files found in {KNOWLEDGE_BASE_DIR}")
        return
    
    print(f"\nFound {len(md_files)} markdown files")
    
    # Load documents
    print("\nLoading documents...")
    documents = load_markdown_files(KNOWLEDGE_BASE_DIR)
    
    if not documents:
        print("[ERROR] No documents loaded")
        return
    
    # Chunk documents
    print("\nChunking documents...")
    chunks = chunk_documents(documents)
    print(f"\nTotal chunks: {len(chunks)}")
    
    # Build indexes
    build_indexes(chunks)
    
    print("\n" + "=" * 50)
    print("[OK] Indexing complete!")
    print(f"Indexes saved to: {INDEXES_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    main()
