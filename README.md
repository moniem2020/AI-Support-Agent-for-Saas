# AI Support Agent

Enterprise-grade multi-agent customer support system with RAG, powered by Google Gemini.

## Features

- 🔀 **Hybrid Retrieval**: Dense (FAISS) + Sparse (BM25) with reranking
- 🧠 **Multi-Agent System**: Router, Retriever, Responder, Quality, Escalation
- 💾 **Semantic Caching**: 60-90% cost reduction
- 🔒 **Security**: PII detection, prompt injection defense
- 📊 **Observability**: Latency, cost, hallucination tracking

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Run the API
uvicorn src.api.main:app --reload

# Run the UI
streamlit run src/ui/app.py
```

## Project Structure

```
ai-support-agent/
├── src/
│   ├── agents/        # Multi-agent orchestration
│   ├── rag/           # Hybrid RAG pipeline
│   ├── cache/         # Semantic caching
│   ├── security/      # PII & injection defense
│   ├── observability/ # Metrics & evaluation
│   ├── api/           # FastAPI backend
│   └── ui/            # Streamlit dashboard
├── data/
│   ├── knowledge_base/
│   └── indexes/
└── tests/
```

## License

MIT
