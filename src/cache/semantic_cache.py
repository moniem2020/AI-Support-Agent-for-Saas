"""
Semantic Cache - Embedding-based similarity caching for query responses.
Reduces API costs by 60-90% for repeated or similar queries.
"""
import time
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
import faiss

from src.rag.embeddings import embedding_service
from src.config import SEMANTIC_CACHE_THRESHOLD, CACHE_TTL_SECONDS


@dataclass
class CacheEntry:
    """A single cache entry with TTL support."""
    query: str
    response: str
    embedding: np.ndarray
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    hits: int = 0
    
    def is_expired(self, ttl: int) -> bool:
        """Check if entry has expired."""
        return time.time() - self.created_at > ttl


class SemanticCache:
    """
    Semantic similarity cache using FAISS for fast nearest neighbor search.
    Caches query-response pairs and retrieves based on embedding similarity.
    """
    
    def __init__(
        self,
        similarity_threshold: float = SEMANTIC_CACHE_THRESHOLD,
        ttl_seconds: int = CACHE_TTL_SECONDS,
        max_entries: int = 10000
    ):
        self.similarity_threshold = similarity_threshold
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        
        # Storage
        self.entries: List[CacheEntry] = []
        self.index: Optional[faiss.IndexFlatIP] = None  # Inner product for cosine sim
        self._dimension: Optional[int] = None
        
        # Metrics
        self.total_hits = 0
        self.total_misses = 0
    
    def _ensure_index(self, dimension: int) -> None:
        """Initialize FAISS index if not exists."""
        if self.index is None or self._dimension != dimension:
            self._dimension = dimension
            self.index = faiss.IndexFlatIP(dimension)  # Inner product = cosine for normalized vectors
    
    def _normalize(self, embedding: np.ndarray) -> np.ndarray:
        """Normalize embedding for cosine similarity."""
        norm = np.linalg.norm(embedding)
        if norm > 0:
            return embedding / norm
        return embedding
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        if not self.entries:
            return
        
        current_time = time.time()
        valid_indices = []
        valid_entries = []
        valid_embeddings = []
        
        for i, entry in enumerate(self.entries):
            if not entry.is_expired(self.ttl_seconds):
                valid_indices.append(i)
                valid_entries.append(entry)
                valid_embeddings.append(entry.embedding)
        
        if len(valid_entries) < len(self.entries):
            self.entries = valid_entries
            if valid_embeddings and self._dimension:
                self.index = faiss.IndexFlatIP(self._dimension)
                embeddings_matrix = np.vstack(valid_embeddings).astype('float32')
                self.index.add(embeddings_matrix)
    
    def get(self, query: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Get cached response for a query if similar enough.
        
        Returns:
            Tuple of (response, metadata) if cache hit, None otherwise.
        """
        if not self.entries or self.index is None:
            self.total_misses += 1
            return None
        
        # Cleanup expired entries periodically
        if len(self.entries) > 0 and self.entries[0].is_expired(self.ttl_seconds):
            self._cleanup_expired()
            if not self.entries:
                self.total_misses += 1
                return None
        
        # Embed query
        query_embedding = np.array(embedding_service.embed_query(query), dtype='float32')
        query_embedding = self._normalize(query_embedding).reshape(1, -1)
        
        # Search
        scores, indices = self.index.search(query_embedding, 1)
        
        if len(indices) > 0 and indices[0][0] != -1:
            best_score = scores[0][0]
            best_idx = indices[0][0]
            
            if best_score >= self.similarity_threshold:
                entry = self.entries[best_idx]
                if not entry.is_expired(self.ttl_seconds):
                    entry.hits += 1
                    self.total_hits += 1
                    return entry.response, {
                        **entry.metadata,
                        "cache_hit": True,
                        "similarity_score": float(best_score),
                        "original_query": entry.query
                    }
        
        self.total_misses += 1
        return None
    
    def put(
        self,
        query: str,
        response: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        Cache a query-response pair.
        
        Args:
            query: The original query
            response: The generated response
            metadata: Optional metadata (sources, confidence, etc.)
        """
        # Embed query
        query_embedding = np.array(embedding_service.embed_query(query), dtype='float32')
        query_embedding = self._normalize(query_embedding)
        
        # Initialize index if needed
        self._ensure_index(len(query_embedding))
        
        # Check if similar entry exists (update instead of duplicate)
        if self.entries:
            query_reshaped = query_embedding.reshape(1, -1)
            scores, indices = self.index.search(query_reshaped, 1)
            if len(indices) > 0 and indices[0][0] != -1:
                if scores[0][0] >= 0.98:  # Very similar, update existing
                    idx = indices[0][0]
                    self.entries[idx].response = response
                    self.entries[idx].metadata = metadata or {}
                    self.entries[idx].created_at = time.time()
                    return
        
        # Evict oldest if at capacity
        if len(self.entries) >= self.max_entries:
            self._cleanup_expired()
            if len(self.entries) >= self.max_entries:
                # Remove oldest entries
                remove_count = len(self.entries) - self.max_entries + 100
                self.entries = self.entries[remove_count:]
                if self.entries:
                    self.index = faiss.IndexFlatIP(self._dimension)
                    embeddings_matrix = np.vstack([e.embedding for e in self.entries]).astype('float32')
                    self.index.add(embeddings_matrix)
        
        # Add new entry
        entry = CacheEntry(
            query=query,
            response=response,
            embedding=query_embedding,
            metadata=metadata or {}
        )
        self.entries.append(entry)
        self.index.add(query_embedding.reshape(1, -1))
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.entries = []
        self.index = None
        self._dimension = None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        hit_rate = 0.0
        total = self.total_hits + self.total_misses
        if total > 0:
            hit_rate = self.total_hits / total
        
        return {
            "total_entries": len(self.entries),
            "total_hits": self.total_hits,
            "total_misses": self.total_misses,
            "hit_rate": hit_rate,
            "similarity_threshold": self.similarity_threshold,
            "ttl_seconds": self.ttl_seconds
        }


# Lazy initialization to avoid slow model loading on import
_semantic_cache_instance: Optional[SemanticCache] = None


def get_semantic_cache() -> SemanticCache:
    """
    Get or create the semantic cache singleton.
    Uses lazy initialization to avoid loading embedding model on import.
    """
    global _semantic_cache_instance
    if _semantic_cache_instance is None:
        _semantic_cache_instance = SemanticCache()
    return _semantic_cache_instance


# Backwards compatibility: access the instance via property
class _SemanticCacheSingleton:
    """Proxy to provide backward-compatible attribute access."""
    
    def __getattr__(self, name):
        return getattr(get_semantic_cache(), name)
    
    def __call__(self):
        return get_semantic_cache()


semantic_cache = _SemanticCacheSingleton()
