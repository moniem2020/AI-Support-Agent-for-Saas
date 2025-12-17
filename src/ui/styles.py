"""
Premium UI Styles for AI Support Agent
Modern YC startup aesthetic with glassmorphism and premium design
"""

PREMIUM_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500;600&display=swap" rel="stylesheet">

<style>
/* ==================== DESIGN TOKENS ==================== */
:root {
    /* Modern Color Palette */
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --primary-light: #818cf8;
    --accent: #ec4899;
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
    
    /*Dark Theme */
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-tertiary: #334155;
    --text-primary: #f1f5f9;
    --text-secondary: #cbd5e1;
    --text-muted: #94a3b8;
    
    /* Glassmorphism */
    --glass-bg: rgba(30, 41, 59, 0.6);
    --glass-border: rgba(148, 163, 184, 0.1);
    
    /* Shadows & Effects */
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
    --shadow-glow: 0 0 20px rgba(99, 102, 241, 0.3);
    
    /* Border Radius */
    --radius-sm: 0.5rem;
    --radius-md: 0.75rem;
    --radius-lg: 1rem;
    --radius-xl: 1.5rem;
    
    /* Transitions */
    --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    
    /* Typography */
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'Fira Code', 'Consolas', monospace;
}

/* ==================== GLOBAL RESET ==================== */
* {
    font-family: var(--font-sans) !important;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ==================== MAIN CONTAINER ==================== */
.main {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px !important;
}

/* ==================== SIDEBAR ==================== */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--glass-border) !important;
}

[data-testid="stSidebar"] > div:first-child {
    background: transparent !important;
}

[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
}

/* ==================== PREMIUM METRICS CARDS ==================== */
[data-testid="metric-container"] {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(12px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(12px) saturate(180%) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1.5rem !important;
    box-shadow: var(--shadow-md) !important;
    transition: var(--transition) !important;
}

[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg), var(--shadow-glow) !important;
    border-color: var(--primary-light) !important;
}

[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.875rem !important;
    font-weight: 600 !important;
}

/* ==================== PREMIUM BUTTONS ==================== */
.stButton > button {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.025em !important;
    box-shadow: var(--shadow-md) !important;
    transition: var(--transition) !important;
    text-transform: none !important;
}

.stButton > button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: var(--shadow-lg), var(--shadow-glow) !important;
}

.stButton > button:active {
    transform: translateY(0);
}

/* ==================== PREMIUM INPUTS ==================== */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--glass-bg) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.938rem !important;
    transition: var(--transition) !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    outline: none !important;
}

.stTextInput > label,
.stTextArea > label {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
}

/* ==================== CHAT MESSAGES ====================*/
[data-testid="chat-message-container"] {
    background: var(--glass-bg) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1rem !important;
    margin: 0.75rem 0 !important;
    backdrop-filter: blur(8px) !important;
    transition: var(--transition) !important;
}

[data-testid="chat-message-container"]:hover {
    border-color: var(--glass-border) !important;
    background: rgba(30, 41, 59, 0.7) !important;
}

.stChatMessage {
    background: transparent !important;
}

.stChatMessage [data-testid="stMarkdownContainer"] p {
    color: var(--text-primary) !important;
    font-size: 0.938rem !important;
    line-height: 1.6 !important;
}

/* User messages - accent color */
[data-testid="chat-message-container"].user {
    border-left: 3px solid var(--primary) !important;
}

/* Assistant messages - success color */
[data-testid="chat-message-container"].assistant {
    border-left: 3px solid var(--success) !important;
}

/* Status Messages - icons */
.status-healthy {
    color: var(--success) !important;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600 !important;
}

.status-offline {
    color: var(--error) !important;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600 !important;
}

/* ==================== PREMIUM TABS ==================== */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: var(--bg-secondary) !important;
    padding: 0.5rem !important;
    border-radius: var(--radius-lg) !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    padding: 0.75rem 1.5rem !important;
    transition: var(--transition) !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: var(--glass-bg) !important;
    color: var(--text-primary) !important;
}

.stTabs [aria-selected="true"] {
    background: var(--primary) !important;
    color: white !important;
    box-shadow: var(--shadow-md) !important;
}

/* ==================== DATAFRAME & TABLES ==================== */
[data-testid="stDataFrame"] {
    background: var(--glass-bg) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1rem !important;
}

[data-testid="stDataFrame"] table {
    color: var(--text-primary) !important;
}

[data-testid="stDataFrame"] th {
    background: var(--bg-tertiary) !important;
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
}

/* ==================== ALERTS & NOTIFICATIONS ==================== */
.stAlert {
    background: var(--glass-bg) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-lg) !important;
    backdrop-filter: blur(8px) !important;
    padding: 1rem 1.25rem !important;
}

.stSuccess {
    border-left: 4px solid var(--success) !important;
}

.st Warning {
    border-left: 4px solid var(--warning) !important;
}

.stError {
    border-left: 4px solid var(--error) !important;
}

.stInfo {
    border-left: 4px solid var(--primary) !important;
}

/* ==================== TYPOGRAPHY ==================== */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
}

h1 {
    font-size: 2.5rem !important;
    background: linear-gradient(135deg, var(--primary-light), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

p {
    color: var(--text-secondary) !important;
    line-height: 1.6 !important;
}

code {
    background: var(--bg-tertiary) !important;
    color: var(--accent) !important;
    padding: 0.2rem 0.4rem !important;
    border-radius: 0.25rem !important;
    font-family: var(--font-mono) !important;
    font-size: 0.875em !important;
}

/* ==================== SCROLLBAR ==================== */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--bg-tertiary);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(99, 102, 241, 0.5);
}

/* ==================== ANIMATIONS ==================== */
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.animate-in {
    animation: slideIn 0.3s ease-out;
}

/* ==================== CUSTOM COMPONENTS ==================== */
.premium-card {
    background: var(--glass-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    box-shadow: var(--shadow-md);
    transition: var(--transition);
}

.premium-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.025em;
}

.badge-success {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success);
    border: 1px solid var(--success);
}

.badge-error {
    background: rgba(239, 68, 68, 0.1);
    color: var(--error);
    border: 1px solid var(--error);
}

.badge-warning {
    background: rgba(245, 158, 11, 0.1);
    color: var(--warning);
    border: 1px solid var(--warning);
}

.badge-info {
    background: rgba(99, 102, 241, 0.1);
    color: var(--primary);
    border: 1px solid var(--primary);
}

/* ==================== LOADING STATES ==================== */
.stSpinner > div {
    border-color: var(--primary) !important;
}

/* ==================== EXPANDER ==================== */
.streamlit-expanderHeader {
    background: var(--glass-bg) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}

.streamlit-expanderHeader:hover {
    border-color: var(--primary) !important;
}

/* ==================== SELECT BOX ==================== */
.stSelectbox > div > div {
    background: var(--glass-bg) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
}

/* ==================== RADIO & CHECKBOX ==================== */
.stRadio > label, .stCheckbox > label {
    color: var(--text-primary) !important;
    font-weight: 500 !important;
}

/* ==================== SLIDER ==================== */
.stSlider > div > div > div {
    background: var(--primary) !important;
}

</style>
"""

def inject_premium_css():
    """Inject premium CSS styles into Streamlit app"""
    import streamlit as st
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)
