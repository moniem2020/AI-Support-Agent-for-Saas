"""
Semantic Chunker with hierarchical relationships.
Implements sliding window with overlap and semantic boundaries.
"""
from typing import List, Dict, Any
from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import CHUNK_SIZE, CHUNK_OVERLAP


@dataclass
class Chunk:
    """A document chunk with metadata."""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    parent_id: str | None = None


class SemanticChunker:
    """
    Semantic chunker with hierarchical parent-child relationships.
    Uses 15% overlap to preserve context at boundaries.
    """
    
    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Primary splitter for chunks
        self.primary_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", "! ", "? ", ", ", " ", ""],
            length_function=len
        )
        
        # Parent splitter for larger context (3x chunk size)
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size * 3,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n"],
            length_function=len
        )
    
    def chunk_document(
        self,
        content: str,
        doc_id: str,
        metadata: Dict[str, Any] = None
    ) -> List[Chunk]:
        """
        Split a document into chunks with hierarchical relationships.
        
        Args:
            content: Document text content
            doc_id: Unique document identifier
            metadata: Additional metadata to attach
            
        Returns:
            List of Chunk objects with parent-child relationships
        """
        metadata = metadata or {}
        chunks = []
        
        # Create parent chunks first
        parent_texts = self.parent_splitter.split_text(content)
        
        for parent_idx, parent_text in enumerate(parent_texts):
            parent_id = f"{doc_id}_parent_{parent_idx}"
            
            # Create child chunks from parent
            child_texts = self.primary_splitter.split_text(parent_text)
            
            for child_idx, child_text in enumerate(child_texts):
                chunk_id = f"{doc_id}_chunk_{parent_idx}_{child_idx}"
                
                chunk_metadata = {
                    **metadata,
                    "doc_id": doc_id,
                    "parent_id": parent_id,
                    "parent_content": parent_text[:500],  # Store truncated parent for context
                    "chunk_index": len(chunks),
                    "total_chunks": None  # Will be updated after processing
                }
                
                chunks.append(Chunk(
                    content=child_text,
                    metadata=chunk_metadata,
                    chunk_id=chunk_id,
                    parent_id=parent_id
                ))
        
        # Update total chunks count
        for chunk in chunks:
            chunk.metadata["total_chunks"] = len(chunks)
        
        return chunks
    
    def chunk_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Chunk]:
        """
        Process multiple documents.
        
        Args:
            documents: List of dicts with 'content', 'doc_id', and optional 'metadata'
            
        Returns:
            List of all chunks from all documents
        """
        all_chunks = []
        
        for doc in documents:
            chunks = self.chunk_document(
                content=doc["content"],
                doc_id=doc["doc_id"],
                metadata=doc.get("metadata", {})
            )
            all_chunks.extend(chunks)
        
        return all_chunks


# Default chunker instance
chunker = SemanticChunker()
