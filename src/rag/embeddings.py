"""
Embedding Service using Google's text-embedding-004 model.
Handles document and query embedding with caching.
"""
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.config import GOOGLE_API_KEY, EMBEDDING_MODEL


class EmbeddingService:
    """Embedding service with Google's text-embedding model."""
    
    _instance = None
    _embeddings = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._embeddings is None:
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model=EMBEDDING_MODEL,
                google_api_key=GOOGLE_API_KEY
            )
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents."""
        return self._embeddings.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        return self._embeddings.embed_query(text)
    
    @property
    def embeddings(self) -> GoogleGenerativeAIEmbeddings:
        """Get the underlying embeddings object for LangChain compatibility."""
        return self._embeddings


# Singleton instance
embedding_service = EmbeddingService()
