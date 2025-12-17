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
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
INDEXES_DIR = DATA_DIR / "indexes"

# Ensure directories exist
KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
INDEXES_DIR.mkdir(parents=True, exist_ok=True)

# Google API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Model Configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-002")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")

# Model Routing (tier-based)
LLM_TIER_1 = "gemini-1.5-flash-002"  # Fast, simple queries
LLM_TIER_2 = "gemini-1.5-pro-002"    # Complex queries

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
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
ESCALATION_THRESHOLD = float(os.getenv("ESCALATION_THRESHOLD", "0.5"))

# Model Routing Tiers
MODEL_TIERS = {
    "simple": GEMINI_MODEL,      # FAQs, greetings
    "standard": GEMINI_MODEL,    # Info retrieval
    "complex": GEMINI_MODEL_PRO, # Reasoning, analysis
    "specialized": GEMINI_MODEL_PRO  # Domain-specific
}
