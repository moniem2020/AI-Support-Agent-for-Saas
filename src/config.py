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

# Google API Keys (multi-key rotation for quota management)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Main key for complex queries
GOOGLE_API_KEY_FAST = os.getenv("GOOGLE_API_KEY_FAST", GOOGLE_API_KEY)  # Fast key for simple queries

# API Key Pool for rotation when quota is exceeded (for complex queries)
_api_keys_pool_str = os.getenv("GOOGLE_API_KEYS_POOL", GOOGLE_API_KEY or "")
GOOGLE_API_KEYS_POOL = [k.strip() for k in _api_keys_pool_str.split(",") if k.strip()]
if not GOOGLE_API_KEYS_POOL and GOOGLE_API_KEY:
    GOOGLE_API_KEYS_POOL = [GOOGLE_API_KEY]

# Model Configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")

# Model Routing (tier-based) - using gemini-2.5-flash (confirmed working with quota)
# FAST models use separate API key to avoid quota conflicts
LLM_TIER_FAST = "gemini-2.0-flash-lite"  # Fastest model for greetings/simple queries
LLM_TIER_1 = "gemini-2.5-flash"  # Standard queries
LLM_TIER_2 = "gemini-2.5-flash"  # Complex queries (same model for stability)

# Model routing map - maps complexity to (model_name, api_key)
MODEL_ROUTING = {
    "simple": LLM_TIER_FAST,
    "moderate": LLM_TIER_1,
    "complex": LLM_TIER_2,
}

# API key routing - which key to use for which tier
API_KEY_ROUTING = {
    "simple": "fast",      # Use fast key
    "moderate": "main",    # Use main key  
    "complex": "main",     # Use main key
}

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

