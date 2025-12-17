"""Test script to debug agent pipeline issues."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 50)
print("Testing Agent Pipeline")
print("=" * 50)

# Test 1: Import and basic checks
print("\n[1] Testing imports...")
try:
    from src.config import GOOGLE_API_KEY, MODEL_ROUTING
    print(f"  API Key: {'Set' if GOOGLE_API_KEY else 'MISSING!'}")
    print(f"  MODEL_ROUTING: {MODEL_ROUTING}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    sys.exit(1)

# Test 2: Test retrievers
print("\n[2] Testing retrievers...")
try:
    from src.rag.dense_retriever import dense_retriever
    from src.rag.sparse_retriever import sparse_retriever
    print(f"  Dense retriever loaded: {dense_retriever is not None}")
    print(f"  Sparse retriever loaded: {sparse_retriever is not None}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test router agent
print("\n[3] Testing router agent...")
try:
    from src.agents.router import router_agent
    print(f"  Router agent loaded: {router_agent is not None}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test responder agent  
print("\n[4] Testing responder agent...")
try:
    from src.agents.responder import responder_agent
    print(f"  Responder agent loaded: {responder_agent is not None}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test support agent graph
print("\n[5] Testing support agent graph...")
try:
    from src.agents.graph import support_agent
    print(f"  Support agent loaded: {support_agent is not None}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Process a simple query
print("\n[6] Testing query processing...")
try:
    result = support_agent.process("hi", user_id="test", ticket_id="t1")
    print(f"  Response: {result.get('response', 'N/A')[:100]}...")
    print(f"  Confidence: {result.get('confidence', 'N/A')}")
    print(f"  Escalated: {result.get('escalated', 'N/A')}")
    print(f"  Sources: {result.get('sources', [])}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Test Complete")
print("=" * 50)
