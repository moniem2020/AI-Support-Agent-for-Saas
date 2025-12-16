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

# Custom CSS for extreme modern styling
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

<style>
    /* ==========================================
       CSS VARIABLES - Design System Tokens
       ========================================== */
    :root {
        /* Color Palette - Vibrant gradients */
        --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --gradient-success: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --gradient-warning: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        --gradient-cosmic: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        
        /* Glassmorphism colors */
        --glass-bg: rgba(255, 255, 255, 0.08);
        --glass-border: rgba(255, 255, 255, 0.18);
        --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        
        /* Shadows - Multi-layer depth */
        --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.1);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15), 0 10px 10px rgba(0, 0, 0, 0.04);
        --shadow-glow: 0 0 20px rgba(102, 126, 234, 0.5), 0 0 40px rgba(102, 126, 234, 0.3);
        
        /* Border Radius */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
        
        /* Transitions - Material Design easing */
        --transition-fast: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-base: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-slow: 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        
        /* Typography */
        --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    }
    
    /* ==========================================
       GLOBAL STYLES - Base foundation
       ========================================== */
    * {
        font-family: var(--font-sans) !important;
    }
    
    /* Smooth scroll behavior */
    html {
        scroll-behavior: smooth;
    }
    
    /* Enhanced main container */
    .main {
        background: linear-gradient(180deg, 
            rgba(102, 126, 234, 0.03) 0%, 
            rgba(118, 75, 162, 0.03) 100%);
    }
    
    /* ==========================================
       METRICS CARDS - Glassmorphism + Glow
       Technical: backdrop-filter for blur, multi-layer shadows
       ========================================== */
    [data-testid="metric-container"] {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(10px) saturate(180%);
        -webkit-backdrop-filter: blur(10px) saturate(180%);
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 20px !important;
        box-shadow: var(--glass-shadow), var(--shadow-md) !important;
        transition: all var(--transition-base) !important;
        position: relative;
        overflow: hidden;
    }
    
    /* Hover effect: Lift + glow */
    [data-testid="metric-container"]:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: var(--shadow-glow), var(--shadow-xl) !important;
        border-color: rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Animated gradient background on hover */
    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(102, 126, 234, 0.1), 
            transparent);
        transition: left var(--transition-slow);
    }
    
    [data-testid="metric-container"]:hover::before {
        left: 100%;
    }
    
    /* ==========================================
       BUTTONS - Gradient + Animation
       Technical: GPU-accelerated transforms, will-change hint
       ========================================== */
    .stButton > button {
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        letter-spacing: 0.3px;
        box-shadow: var(--shadow-md) !important;
        transition: all var(--transition-base) !important;
        position: relative;
        overflow: hidden;
        cursor: pointer;
        will-change: transform, box-shadow;
    }
    
    /* Button hover: Lift + intense glow */
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05) !important;
        box-shadow: var(--shadow-glow), var(--shadow-xl) !important;
    }
    
    /* Button active: Press down */
    .stButton > button:active {
        transform: translateY(-1px) scale(1.02) !important;
    }
    
    /* Shimmer effect on button */
    .stButton > button::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg,
            transparent 30%,
            rgba(255, 255, 255, 0.3) 50%,
            transparent 70%
        );
        transform: rotate(45deg);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { transform: translateX(-100%) rotate(45deg); }
        50% { transform: translateX(100%) rotate(45deg); }
    }
    
    /* ==========================================
       TABS - Modern segmented control
       ========================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        padding: 6px;
        border-radius: var(--radius-lg);
        border: 1px solid var(--glass-border);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-md) !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all var(--transition-base) !important;
        border: none !important;
    }
    
    /* Active tab: Gradient background */
    .stTabs [aria-selected="true"] {
        background: var(--gradient-primary) !important;
        color: white !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    /* Inactive tab: Hover effect */
    .stTabs [aria-selected="false"]:hover {
        background: rgba(102, 126, 234, 0.1) !important;
    }
    
    /* ==========================================
       CHAT MESSAGES - Bubble style
       ========================================== */
    .stChatMessage {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(10px) saturate(180%);
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 16px !important;
        margin: 12px 0 !important;
        box-shadow: var(--shadow-md) !important;
        transition: all var(--transition-base) !important;
    }
    
    .stChatMessage:hover {
        transform: translateX(4px);
        box-shadow: var(--shadow-lg) !important;
    }
    
    /* ==========================================
       INPUT FIELDS - Neon focus glow
       ========================================== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: var(--radius-md) !important;
        border: 2px solid rgba(102, 126, 234, 0.2) !important;
        transition: all var(--transition-base) !important;
        background: var(--glass-bg) !important;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15), 
                    0 0 20px rgba(102, 126, 234, 0.3) !important;
        transform: scale(1.01);
    }
    
    /* ==========================================
       EXPANDERS - Accordion style
       ========================================== */
    .streamlit-expanderHeader {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(10px);
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--glass-border) !important;
        font-weight: 600 !important;
        transition: all var(--transition-base) !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(102, 126, 234, 0.1) !important;
        transform: translateX(4px);
    }
    
    /* ==========================================
       SIDEBAR - Enhanced glass panel
       ========================================== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, 
            rgba(102, 126, 234, 0.05) 0%, 
            rgba(118, 75, 162, 0.05) 100%) !important;
        backdrop-filter: blur(20px) saturate(180%);
        border-right: 1px solid var(--glass-border) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        animation: fadeIn 0.6s ease-out;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* ==========================================
       STATUS BADGES - Color-coded indicators
       ========================================== */
    .stSuccess {
        background: var(--gradient-success) !important;
        color: white !important;
        border-radius: var(--radius-md) !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
        box-shadow: var(--shadow-md) !important;
        animation: pulse 2s ease-in-out infinite;
    }
    
    .stError {
        background: var(--gradient-secondary) !important;
        color: white !important;
        border-radius: var(--radius-md) !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    .stWarning {
        background: var(--gradient-warning) !important;
        color: white !important;
        border-radius: var(--radius-md) !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.02); opacity: 0.95; }
    }
    
    /* ==========================================
       SCROLLBAR - Custom styled
       ========================================== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(102, 126, 234, 0.05);
        border-radius: var(--radius-sm);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--gradient-primary);
        border-radius: var(--radius-sm);
        transition: all var(--transition-base);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%);
    }
    
    /* ==========================================
       LOADING SPINNER - Enhanced animation
       ========================================== */
    .stSpinner > div {
        border-top-color: #667eea !important;
        animation: spin 0.8s cubic-bezier(0.4, 0, 0.2, 1) infinite !important;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* ==========================================
       CODE BLOCKS - Monospace with style
       ========================================== */
    code {
        font-family: var(--font-mono) !important;
        background: var(--glass-bg) !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        border: 1px solid var(--glass-border) !important;
        font-size: 0.9em !important;
    }
    
    pre {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius-md) !important;
        padding: 16px !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    /* ==========================================
       PERFORMANCE: Reduce motion for accessibility
       ========================================== */
    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
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
