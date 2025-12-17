"""
Refined Premium UI Styles - Professional & Functional
Modern SaaS aesthetic with proper visibility and usability
"""

PREMIUM_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
/* ==================== DESIGN SYSTEM ==================== */
:root {
    --primary: #6366f1;
    --primary-hover: #4f46e5;
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
    
    /* Light theme - clean and professional */
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --bg-tertiary: #f1f5f9;
    --border-color: #e2e8f0;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    
    --radius-sm: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --radius-xl: 1rem;
    
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ==================== GLOBAL STYLES ==================== */
* {
    font-family: var(--font-sans) !important;
}

/* Keep Streamlit menu and controls visible */
#MainMenu {visibility: visible !important;}

/* Main container */
.main {
    background: var(--bg-secondary) !important;
}

.block-container {
    padding-top: 2rem !important;
    max-width: 1200px !important;
}

/* ==================== SIDEBAR ==================== */
[data-testid="stSidebar"] {
    background: var(--bg-primary) !important;
    border-right: 1px solid var(--border-color) !important;
}

[data-testid="stSidebar"] h1 {
    color: var(--primary) !important;
    font-weight: 700 !important;
    font-size: 1.75rem !important;
}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: var(--text-secondary) !important;
}

/* Sidebar status badge */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: var(--text-primary) !important;
}

/* ==================== METRICS CARDS ==================== */
[data-testid="metric-container"] {
    background: white !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1.25rem !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.2s ease !important;
}

[data-testid="metric-container"]:hover {
    box-shadow: var(--shadow-md) !important;
    border-color: var(--primary) !important;
    transform: translateY(-2px);
}

[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-size: 1.875rem !important;
    font-weight: 700 !important;
}

/* ==================== BUTTONS ==================== */
.stButton > button {
    background: var(--primary) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 0.625rem 1.25rem !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: var(--primary-hover) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px);
}

.stButton > button:active {
    transform: translateY(0);
}

/* Secondary button style */
.stButton > button[kind="secondary"] {
    background: white !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
}

.stButton > button[kind="secondary"]:hover {
    background: var(--bg-tertiary) !important;
}

/* ==================== INPUTS ==================== */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: white !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    padding: 0.625rem 0.875rem !important;
    font-size: 0.938rem !important;
    transition: all 0.2s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    outline: none !important;
}

.stTextInput > label,
.stTextArea > label {
    color: var(--text-primary) !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    margin-bottom: 0.5rem !important;
}

/* ==================== CHAT MESSAGES ==================== */
.stChatMessage {
    background: white !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1rem !important;
    margin: 0.75rem 0 !important;
    box-shadow: var(--shadow-sm) !important;
}

.stChatMessage[data-testid="user-message"] {
    border-left: 3px solid var(--primary) !important;
}

.stChatMessage[data-testid="assistant-message"] {
    border-left: 3px solid var(--success) !important;
}

.stChatMessage p {
    color: var(--text-primary) !important;
    line-height: 1.6 !important;
}

/* Chat input */
.stChatInputContainer {
    border-top: 1px solid var(--border-color) !important;
    background: white !important;
    padding: 1rem !important;
}

/* ==================== TABS ==================== */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.25rem;
    background: var(--bg-tertiary) !important;
    padding: 0.25rem !important;
    border-radius: var(--radius-lg) !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(99, 102, 241, 0.1) !important;
    color: var(--text-primary) !important;
}

.stTabs [aria-selected="true"] {
    background: white !important;
    color: var(--primary) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ==================== DATAFRAMES ==================== */
[data-testid="stDataFrame"] {
    background: white !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-lg) !important;
}

[data-testid="stDataFrame"] th {
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
}

[data-testid="stDataFrame"] td {
    color: var(--text-primary) !important;
}

/* ==================== ALERTS ==================== */
.stAlert {
    background: white !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem !important;
}

.stSuccess {
    border-left: 4px solid var(--success) !important;
    background: rgba(16, 185, 129, 0.05) !important;
}

.stWarning {
    border-left: 4px solid var(--warning) !important;
    background: rgba(245, 158, 11, 0.05) !important;
}

.stError {
    border-left: 4px solid var(--error) !important;
    background: rgba(239, 68, 68, 0.05) !important;
}

.stInfo {
    border-left: 4px solid var(--primary) !important;
    background: rgba(99, 102, 241, 0.05) !important;
}

/* ==================== TYPOGRAPHY ==================== */
h1 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    font-size: 2rem !important;
    letter-spacing: -0.025em !important;
}

h2 {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 1.5rem !important;
}

h3 {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 1.25rem !important;
}

p {
    color: var(--text-secondary) !important;
    line-height: 1.6 !important;
}

code {
    background: var(--bg-tertiary) !important;
    color: var(--primary) !important;
    padding: 0.2rem 0.4rem !important;
    border-radius: 0.25rem !important;
    font-size: 0.875em !important;
}

/* ==================== STATUS BADGES ==================== */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 600;
}

.badge-success {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success);
}

.badge-error {
    background: rgba(239, 68, 68, 0.1);
    color: var(--error);
}

/* ==================== SCROLLBAR ==================== */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: var(--bg-tertiary);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted);
}

/* ==================== EXPANDER ==================== */
.streamlit-expanderHeader {
    background: white !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    padding: 0.75rem 1rem !important;
}

.streamlit-expanderHeader:hover {
    border-color: var(--primary) !important;
    background: var(--bg-tertiary) !important;
}

/* ==================== SELECT & RADIO ==================== */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: white !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-md) !important;
}

.stRadio > label,
.stCheckbox > label {
    color: var(--text-primary) !important;
    font-weight: 500 !important;
}

/* ==================== ENSURE VISIBILITY ==================== */
/* Make sure all text is readable */
[data-testid="stMarkdownContainer"] p {
    color: var(--text-secondary) !important;
}

[data-testid="stMarkdownContainer"] strong {
    color: var(--text-primary) !important;
}

/* Sidebar items */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: var(--text-secondary) !important;
}

/* Keep all interactive elements visible and accessible */
button svg {
    color: inherit !important;
}

</style>
"""

def inject_premium_css():
    """Inject refined premium CSS styles"""
    import streamlit as st
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)
