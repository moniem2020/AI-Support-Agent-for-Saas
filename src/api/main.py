"""
FastAPI Application - Main entry point for the AI Support Agent API.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from src.api.routes import router

# Create FastAPI app
app = FastAPI(
    title="AI Support Agent API",
    description="Enterprise-grade AI-powered customer support agent with RAG, semantic caching, and multi-agent orchestration.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    """Add request timing to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = str(round(process_time, 2))
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url)
        }
    )


# Include routes
app.include_router(router, prefix="/api/v1", tags=["Support Agent"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Support Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("==> AI Support Agent API starting up...")
    print(f"Version: {app.version}")
    print(f"Environment: Development")
    print("API is ready to serve requests")
    print("=" * 50)
    print("Loading knowledge base indexes...")
    
    try:
        from src.rag.dense_retriever import dense_retriever
        from src.rag.sparse_retriever import sparse_retriever
        
        # Attempt to load existing indexes
        dense_retriever.load_index()
        sparse_retriever.load_index()
        print("[OK] Indexes loaded successfully")
    except Exception as e:
        print(f"[WARN] Could not load indexes: {e}")
        print("   Run the indexing script to build indexes")
    
    print("[OK] API ready to serve requests")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("[SHUTDOWN] AI Support Agent API shutting down...")
    
    try:
        from src.rag.dense_retriever import dense_retriever
        from src.rag.sparse_retriever import sparse_retriever
        
        dense_retriever.save_index()
        sparse_retriever.save_index()
        print("[OK] Indexes saved")
    except Exception as e:
        print(f"[WARN] Could not save indexes: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
