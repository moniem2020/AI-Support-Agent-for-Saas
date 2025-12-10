"""
Streamlit Dashboard - Main UI for the AI Support Agent.
Features: Chat interface, metrics dashboard, admin panel.
"""
import streamlit as st
import requests
from typing import Dict, Any, List
import json

# Page config
st.set_page_config(
    page_title="AI Support Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium look
st.markdown("""
<style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Chat messages */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
    }
    
    /* Metrics cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: white;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.1);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "metrics" not in st.session_state:
    st.session_state.metrics = {}
if "cache_stats" not in st.session_state:
    st.session_state.cache_stats = {}


def call_api(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Make API call and return response."""
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=60)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API. Make sure the server is running."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    except Exception as e:
        return {"error": str(e)}


def refresh_metrics():
    """Refresh metrics from API."""
    st.session_state.metrics = call_api("metrics")
    st.session_state.cache_stats = call_api("cache/stats")


def render_sidebar():
    """Render the sidebar."""
    with st.sidebar:
        st.title("🤖 AI Support Agent")
        st.caption("Enterprise Customer Support powered by Gemini + RAG")
        
        st.divider()
        
        # System Status
        st.subheader("🔌 System Status")
        health = call_api("health")
        if "error" in health:
            st.error("❌ API Offline")
            st.caption(health["error"])
        else:
            status = health.get("status", "unknown")
            if status == "healthy":
                st.success("✅ All Systems Operational")
            else:
                st.warning(f"⚠️ Status: {status}")
        
        st.divider()
        
        # Cache Stats
        st.subheader("💾 Cache")
        cache = st.session_state.cache_stats
        if cache and "error" not in cache:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Entries", cache.get("total_entries", 0))
            with col2:
                st.metric("Hit Rate", f"{cache.get('hit_rate', 0):.0%}")
            
            if st.button("🗑️ Clear Cache", use_container_width=True):
                result = call_api("cache/clear", method="POST")
                if "error" not in result:
                    st.success("Cache cleared!")
                    refresh_metrics()
        
        st.divider()
        
        # Escalation Queue
        st.subheader("🎫 Escalations")
        escalations = call_api("escalations")
        if escalations and "error" not in escalations:
            st.metric("Pending", escalations.get("total", 0))
            priorities = escalations.get("by_priority", {})
            for priority, count in priorities.items():
                icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "normal": "🟢"}.get(priority, "⚪")
                st.caption(f"{icon} {priority.capitalize()}: {count}")
        
        st.divider()
        
        # Refresh button
        if st.button("🔄 Refresh", use_container_width=True):
            refresh_metrics()
            st.rerun()


def render_metrics_tab():
    """Render the metrics dashboard tab."""
    st.header("📊 Performance Dashboard")
    
    metrics = st.session_state.metrics
    if not metrics or "error" in metrics:
        st.info("No metrics available yet. Start chatting to generate metrics!")
        return
    
    # Main KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 Total Requests",
            f"{metrics.get('total_requests', 0):,}",
            help="Total number of processed requests"
        )
    
    with col2:
        st.metric(
            "⚡ Avg Latency",
            f"{metrics.get('avg_latency_ms', 0):.0f}ms",
            help="Average response time"
        )
    
    with col3:
        st.metric(
            "💾 Cache Hit Rate",
            f"{metrics.get('cache_hit_rate', 0):.0%}",
            help="Percentage served from cache"
        )
    
    with col4:
        st.metric(
            "🎯 Avg Confidence",
            f"{metrics.get('avg_confidence', 0):.0%}",
            help="Average response confidence"
        )
    
    st.divider()
    
    # Secondary metrics
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric(
            "📝 Total Tokens",
            f"{metrics.get('total_tokens', 0):,}"
        )
    
    with col6:
        st.metric(
            "💰 Est. Cost",
            f"${metrics.get('total_cost_usd', 0):.4f}"
        )
    
    with col7:
        st.metric(
            "🚨 Escalation Rate",
            f"{metrics.get('escalation_rate', 0):.0%}"
        )
    
    with col8:
        st.metric(
            "📈 P95 Latency",
            f"{metrics.get('p95_latency_ms', 0):.0f}ms"
        )
    
    # Breakdown charts
    st.divider()
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("📊 Requests by Model")
        model_data = metrics.get("requests_per_model", {})
        if model_data:
            st.bar_chart(model_data)
        else:
            st.info("No model data yet")
    
    with col_chart2:
        st.subheader("🏷️ Requests by Intent")
        intent_data = metrics.get("requests_per_intent", {})
        if intent_data:
            st.bar_chart(intent_data)
        else:
            st.info("No intent data yet")


def render_chat_tab():
    """Render the chat interface tab."""
    st.header("💬 Support Chat")
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])
            
            # Show metadata for assistant messages
            if msg["role"] == "assistant" and "metadata" in msg:
                meta = msg["metadata"]
                with st.expander("ℹ️ Response Details", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        conf = meta.get("confidence", 0)
                        color = "green" if conf >= 0.7 else "orange" if conf >= 0.5 else "red"
                        st.markdown(f"**Confidence**: :{color}[{conf:.0%}]")
                    
                    with col2:
                        cache = "✅ Hit" if meta.get("cache_hit") else "❌ Miss"
                        st.markdown(f"**Cache**: {cache}")
                    
                    with col3:
                        st.markdown(f"**Latency**: {meta.get('latency_ms', 0):.0f}ms")
                    
                    sources = meta.get("sources", [])
                    if sources:
                        st.markdown(f"**Sources**: {', '.join(sources)}")
                    
                    st.caption(f"Model: {meta.get('model_used', 'N/A')} | Intent: {meta.get('intent', 'N/A')}")
                    
                    if meta.get("escalated"):
                        st.warning(f"⚠️ Escalated: {meta.get('escalation_reason', 'Unknown')}")
    
    # Chat input
    if prompt := st.chat_input("How can I help you today?"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                response = call_api("chat", method="POST", data={"message": prompt})
                
                if "error" in response:
                    st.error(f"Error: {response['error']}")
                    content = "I apologize, but I'm having trouble connecting to the backend. Please try again later."
                    metadata = {}
                else:
                    content = response.get("response", "No response generated")
                    metadata = {
                        "confidence": response.get("confidence", 0),
                        "cache_hit": response.get("cache_hit", False),
                        "latency_ms": response.get("latency_ms", 0),
                        "sources": response.get("sources", []),
                        "model_used": response.get("model_used", ""),
                        "intent": response.get("intent", ""),
                        "escalated": response.get("escalated", False),
                        "escalation_reason": response.get("escalation_reason", "")
                    }
                
                st.markdown(content)
                
                # Show metadata
                if metadata:
                    with st.expander("ℹ️ Response Details", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            conf = metadata.get("confidence", 0)
                            color = "green" if conf >= 0.7 else "orange" if conf >= 0.5 else "red"
                            st.markdown(f"**Confidence**: :{color}[{conf:.0%}]")
                        
                        with col2:
                            cache = "✅ Hit" if metadata.get("cache_hit") else "❌ Miss"
                            st.markdown(f"**Cache**: {cache}")
                        
                        with col3:
                            st.markdown(f"**Latency**: {metadata.get('latency_ms', 0):.0f}ms")
        
        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": content,
            "metadata": metadata
        })
        
        # Refresh metrics
        refresh_metrics()


def render_admin_tab():
    """Render the admin panel tab."""
    st.header("⚙️ Admin Panel")
    
    # Document indexing
    st.subheader("📄 Index Documents")
    
    with st.form("index_form"):
        doc_content = st.text_area(
            "Document Content",
            height=200,
            placeholder="Paste document content here..."
        )
        doc_title = st.text_input("Document Title (optional)")
        
        submitted = st.form_submit_button("🚀 Index Document")
        
        if submitted and doc_content:
            with st.spinner("Indexing..."):
                data = {
                    "documents": [{
                        "content": doc_content,
                        "metadata": {"title": doc_title} if doc_title else {}
                    }]
                }
                result = call_api("index", method="POST", data=data)
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                elif result.get("success"):
                    st.success(f"✅ Indexed {result.get('documents_indexed', 0)} document(s)")
                else:
                    st.warning(f"Indexing had issues: {result.get('errors', [])}")
    
    st.divider()
    
    # Recent requests
    st.subheader("📜 Recent Requests")
    recent = call_api("metrics/recent?count=5")
    
    if recent and not isinstance(recent, dict) or "error" not in recent:
        if isinstance(recent, list) and recent:
            for req in recent:
                with st.expander(f"🎫 {req.get('request_id', 'N/A')} - {req.get('timestamp', 'N/A')[:19]}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Latency", f"{req.get('latency_ms', 0):.0f}ms")
                    with col2:
                        st.metric("Tokens", req.get("tokens", 0))
                    with col3:
                        st.metric("Confidence", f"{req.get('confidence', 0):.0%}")
        else:
            st.info("No recent requests")
    
    st.divider()
    
    # Clear chat history
    st.subheader("🧹 Clear Data")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.success("Chat history cleared!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset Metrics", use_container_width=True):
            st.session_state.metrics = {}
            st.success("Metrics reset!")
            st.rerun()


def main():
    """Main application entry point."""
    # Render sidebar
    render_sidebar()
    
    # Initial metrics load
    if not st.session_state.metrics:
        refresh_metrics()
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Metrics", "⚙️ Admin"])
    
    with tab1:
        render_chat_tab()
    
    with tab2:
        render_metrics_tab()
    
    with tab3:
        render_admin_tab()


if __name__ == "__main__":
    main()
