"""
Streamlit UI Components - Reusable UI elements for the dashboard.
"""
import streamlit as st
from typing import Dict, Any, List, Optional


def chat_message(role: str, content: str, metadata: Dict[str, Any] = None):
    """
    Render a chat message bubble.
    
    Args:
        role: 'user' or 'assistant'
        content: Message content
        metadata: Optional metadata (confidence, sources, etc.)
    """
    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(content)
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(content)
            
            if metadata:
                # Show metadata in expander
                with st.expander("ℹ️ Response Details", expanded=False):
                    cols = st.columns(3)
                    
                    with cols[0]:
                        confidence = metadata.get("confidence", 0)
                        color = "green" if confidence >= 0.7 else "orange" if confidence >= 0.5 else "red"
                        st.markdown(f"**Confidence**: :{color}[{confidence:.0%}]")
                    
                    with cols[1]:
                        if metadata.get("cache_hit"):
                            st.markdown("**Cache**: ✅ Hit")
                        else:
                            st.markdown("**Cache**: ❌ Miss")
                    
                    with cols[2]:
                        latency = metadata.get("latency_ms", 0)
                        st.markdown(f"**Latency**: {latency:.0f}ms")
                    
                    sources = metadata.get("sources", [])
                    if sources:
                        st.markdown(f"**Sources**: {', '.join(sources)}")
                    
                    if metadata.get("escalated"):
                        st.warning(f"⚠️ Escalated: {metadata.get('escalation_reason', 'Unknown')}")


def metrics_card(title: str, value: Any, delta: str = None, icon: str = "📊"):
    """
    Render a metrics card.
    
    Args:
        title: Metric title
        value: Metric value
        delta: Optional delta/change indicator
        icon: Emoji icon
    """
    st.metric(
        label=f"{icon} {title}",
        value=value,
        delta=delta
    )


def metrics_dashboard(stats: Dict[str, Any]):
    """
    Render the full metrics dashboard.
    
    Args:
        stats: Aggregated metrics from the API
    """
    st.subheader("📊 Performance Metrics")
    
    # Main metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Requests",
            stats.get("total_requests", 0),
            help="Total number of processed requests"
        )
    
    with col2:
        avg_latency = stats.get("avg_latency_ms", 0)
        st.metric(
            "Avg Latency",
            f"{avg_latency:.0f}ms",
            help="Average response time"
        )
    
    with col3:
        cache_rate = stats.get("cache_hit_rate", 0)
        st.metric(
            "Cache Hit Rate",
            f"{cache_rate:.0%}",
            help="Percentage of requests served from cache"
        )
    
    with col4:
        confidence = stats.get("avg_confidence", 0)
        st.metric(
            "Avg Confidence",
            f"{confidence:.0%}",
            help="Average response confidence"
        )
    
    # Secondary metrics
    st.divider()
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric(
            "Total Tokens",
            f"{stats.get('total_tokens', 0):,}",
            help="Total tokens consumed"
        )
    
    with col6:
        cost = stats.get("total_cost_usd", 0)
        st.metric(
            "Total Cost",
            f"${cost:.4f}",
            help="Estimated API cost"
        )
    
    with col7:
        escalation = stats.get("escalation_rate", 0)
        st.metric(
            "Escalation Rate",
            f"{escalation:.0%}",
            help="Percentage of escalated requests"
        )
    
    with col8:
        p95 = stats.get("p95_latency_ms", 0)
        st.metric(
            "P95 Latency",
            f"{p95:.0f}ms",
            help="95th percentile latency"
        )


def source_citation(sources: List[Dict[str, Any]]):
    """
    Render source citations.
    
    Args:
        sources: List of source documents with metadata
    """
    if not sources:
        st.info("No sources available for this response.")
        return
    
    st.markdown("**📚 Sources:**")
    
    for i, source in enumerate(sources, 1):
        with st.expander(f"Source {i}: {source.get('doc_id', 'Unknown')}", expanded=False):
            st.markdown(source.get("content_preview", "No preview available"))
            if "relevance_score" in source:
                st.caption(f"Relevance: {source['relevance_score']:.2f}")


def sidebar_info(cache_stats: Dict[str, Any], escalation_stats: Dict[str, Any]):
    """
    Render sidebar with system information.
    
    Args:
        cache_stats: Cache statistics
        escalation_stats: Escalation queue stats
    """
    with st.sidebar:
        st.title("🤖 AI Support Agent")
        st.caption("Powered by Gemini + RAG")
        
        st.divider()
        
        # Cache info
        st.subheader("💾 Cache Status")
        st.metric("Entries", cache_stats.get("total_entries", 0))
        st.metric("Hit Rate", f"{cache_stats.get('hit_rate', 0):.0%}")
        
        st.divider()
        
        # Escalation queue
        st.subheader("🎫 Escalation Queue")
        st.metric("Pending", escalation_stats.get("total", 0))
        
        priorities = escalation_stats.get("by_priority", {})
        if priorities:
            for priority, count in priorities.items():
                color = {"critical": "🔴", "high": "🟠", "medium": "🟡", "normal": "🟢"}.get(priority, "⚪")
                st.caption(f"{color} {priority.capitalize()}: {count}")
        
        st.divider()
        
        # Actions
        st.subheader("⚙️ Actions")
        if st.button("🗑️ Clear Cache"):
            return "clear_cache"
        
        if st.button("🔄 Refresh Metrics"):
            return "refresh"
    
    return None


def document_uploader():
    """Render document upload interface."""
    st.subheader("📄 Add Documents")
    
    uploaded_files = st.file_uploader(
        "Upload knowledge base documents",
        type=["txt", "md", "pdf"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) ready to index")
        
        if st.button("🚀 Index Documents"):
            return uploaded_files
    
    return None


def error_message(message: str, details: str = None):
    """Render an error message."""
    st.error(f"❌ {message}")
    if details:
        with st.expander("Details"):
            st.code(details)


def success_message(message: str):
    """Render a success message."""
    st.success(f"✅ {message}")


def loading_spinner(message: str = "Processing..."):
    """Return a loading spinner context."""
    return st.spinner(message)
