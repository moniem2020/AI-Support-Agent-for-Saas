"""
AI Support Agent - Configuration Module
Centralized configuration for all system components.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
INDEXES_DIR = DATA_DIR / "indexes"

# Ensure directories exist
KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
INDEXES_DIR.mkdir(parents=True, exist_ok=True)

# Google API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Model Configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")

# Model Routing (tier-based)
LLM_TIER_1 = "gemini-2.0-flash"  # Fast, simple queries
LLM_TIER_2 = "gemini-2.5-pro"    # Complex queries

# Cache Settings
SEMANTIC_CACHE_THRESHOLD = float(os.getenv("SEMANTIC_CACHE_THRESHOLD", "0.90"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))

# Retrieval Settings
DENSE_TOP_K = int(os.getenv("DENSE_TOP_K", "10"))
SPARSE_TOP_K = int(os.getenv("SPARSE_TOP_K", "10"))
RERANK_TOP_K = int(os.getenv("RERANK_TOP_K", "5"))

# Chunking Settings
CHUNK_SIZE = 512
CHUNK_OVERLAP = 77  # ~15% overlap

# Agent Settings
MAX_RETRIES = 2
CONFIDENCE_THRESHOLD = 0.7
ESCALATION_THRESHOLD = 0.5

# Model Routing Tiers
MODEL_ROUTING = {
    "simple": LLM_TIER_1,    # Basic FAQs
    "moderate": LLM_TIER_1,  # Standard support
    "complex": LLM_TIER_2,   # Reasoning, analysis
}
