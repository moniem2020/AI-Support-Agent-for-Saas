"""
Sparse Retriever using BM25 for keyword matching.
Catches exact terminology that dense retrieval might miss.
"""
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
import re

from src.config import INDEXES_DIR, SPARSE_TOP_K
from src.rag.chunker import Chunk


class SparseRetriever:
    """BM25-based sparse retriever for keyword matching."""
    
    def __init__(self, index_name: str = "support_kb"):
        self.index_name = index_name
        self.index_path = INDEXES_DIR / f"{index_name}_bm25.pkl"
        
        self.bm25: Optional[BM25Okapi] = None
        self.documents: List[Dict[str, Any]] = []
        self.tokenized_corpus: List[List[str]] = []
        
        # Try to load existing index
        self.load_index()
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization with lowercasing and punctuation removal."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        # Remove very short tokens
        return [t for t in tokens if len(t) > 2]
    
    def load_index(self) -> bool:
        """Load existing BM25 index if available."""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data['documents']
                    self.tokenized_corpus = data['tokenized_corpus']
                    
                    if self.tokenized_corpus:
                        self.bm25 = BM25Okapi(self.tokenized_corpus)
                    else:
                        print("Warning: Loaded empty BM25 index")
                        self.bm25 = None
                return True
            except Exception as e:
                print(f"Failed to load BM25 index: {e}")
        return False
    
    def save_index(self):
        """Persist BM25 index to disk."""
        with open(self.index_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'tokenized_corpus': self.tokenized_corpus
            }, f)
    
    def add_chunks(self, chunks: List[Chunk]):
        """
        Add chunks to the BM25 index.
        
        Args:
            chunks: List of Chunk objects to index
        """
        for chunk in chunks:
            doc_data = {
                "content": chunk.content,
                "metadata": {
                    **chunk.metadata,
                    "chunk_id": chunk.chunk_id
                }
            }
            self.documents.append(doc_data)
            self.tokenized_corpus.append(self._tokenize(chunk.content))
        
        # Rebuild BM25 index
        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)
        
        self.save_index()
    
    def search(
        self,
        query: str,
        top_k: int = SPARSE_TOP_K,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for matching documents using BM25.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of results with content, metadata, and score
        """
        if self.bm25 is None or not self.documents:
            return []
        
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k indices
        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k * 2]  # Get extra for filtering
        
        results = []
        for idx in top_indices:
            if len(results) >= top_k:
                break
                
            doc = self.documents[idx]
            
            # Apply filters if provided
            if filter_dict:
                if not all(
                    doc["metadata"].get(k) == v 
                    for k, v in filter_dict.items()
                ):
                    continue
            
            # Normalize score to 0-1 range
            max_score = max(scores) if max(scores) > 0 else 1
            normalized_score = scores[idx] / max_score
            
            results.append({
                "content": doc["content"],
                "metadata": doc["metadata"],
                "score": float(normalized_score),
                "source": "sparse"
            })
        
        return results
    
    def get_document_count(self) -> int:
        """Get total number of indexed documents."""
        return len(self.documents)


# Default sparse retriever instance
sparse_retriever = SparseRetriever()
