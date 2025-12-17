"""
Dense Retriever using FAISS vector store.
Handles semantic similarity search with Google embeddings.
"""
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from src.config import INDEXES_DIR, DENSE_TOP_K
from src.rag.embeddings import embedding_service
from src.rag.chunker import Chunk


class DenseRetriever:
    """FAISS-based dense retriever for semantic search."""
    
    def __init__(self, index_name: str = "support_kb"):
        self.index_name = index_name
        self.index_path = INDEXES_DIR / f"{index_name}_faiss"
        self.vector_store: Optional[FAISS] = None
        
        # Try to load existing index
        self._load_index()
    
    def _load_index(self) -> bool:
        """Load existing FAISS index if available."""
        if self.index_path.exists():
            try:
                self.vector_store = FAISS.load_local(
                    str(self.index_path),
                    embedding_service.embeddings,
                    allow_dangerous_deserialization=True
                )
                return True
            except Exception as e:
                print(f"Failed to load index: {e}")
        return False
    
    def save_index(self):
        """Persist FAISS index to disk."""
        if self.vector_store:
            self.vector_store.save_local(str(self.index_path))
    
    def add_chunks(self, chunks: List[Chunk]):
        """
        Add chunks to the vector store.
        
        Args:
            chunks: List of Chunk objects to index
        """
        documents = [
            Document(
                page_content=chunk.content,
                metadata={
                    **chunk.metadata,
                    "chunk_id": chunk.chunk_id
                }
            )
            for chunk in chunks
        ]
        
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(
                documents,
                embedding_service.embeddings
            )
        else:
            self.vector_store.add_documents(documents)
        
        self.save_index()
    
    def search(
        self,
        query: str,
        top_k: int = DENSE_TOP_K,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of results with content, metadata, and score
        """
        if self.vector_store is None:
            return []
        
        # Perform similarity search with scores
        results = self.vector_store.similarity_search_with_score(
            query,
            k=top_k
        )
        
        formatted_results = []
        for doc, score in results:
            # Apply filters if provided
            if filter_dict:
                if not all(
                    doc.metadata.get(k) == v 
                    for k, v in filter_dict.items()
                ):
                    continue
            
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(1 / (1 + score)),  # Convert distance to similarity
                "source": "dense"
            })
        
        return formatted_results
    
    def get_document_count(self) -> int:
        """Get total number of indexed documents."""
        if self.vector_store is None:
            return 0
        return len(self.vector_store.docstore._dict)


# Default dense retriever instance
# dense_retriever = DenseRetriever()
