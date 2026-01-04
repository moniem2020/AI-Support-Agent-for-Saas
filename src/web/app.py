"""
Flask Web Application - Professional AI Support Chat Interface
Styled like modern YC AI startups (Linear, Vercel, Anthropic)
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import os

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Secret key for sessions
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-prod")

# API Backend URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# CS Dashboard Credentials (from environment variables)
CS_USERNAME = os.getenv("CS_USERNAME", "admin")
CS_PASSWORD = os.getenv("CS_PASSWORD", "support123")


@app.route('/')
def index():
    """Render the main chat interface."""
    return render_template('index.html')


@app.route('/cs/login', methods=['GET', 'POST'])
def cs_login():
    """CS agent login page."""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username == CS_USERNAME and password == CS_PASSWORD:
            session['cs_authenticated'] = True
            session['cs_username'] = username
            return redirect(url_for('cs_dashboard'))
        else:
            return render_template('cs_login.html', error=True)
    
    # Already logged in?
    if session.get('cs_authenticated'):
        return redirect(url_for('cs_dashboard'))
    
    return render_template('cs_login.html')


@app.route('/cs/logout')
def cs_logout():
    """Logout from CS dashboard."""
    session.pop('cs_authenticated', None)
    session.pop('cs_username', None)
    return redirect(url_for('cs_login'))


@app.route('/cs')
def cs_dashboard():
    """Render the CS agent dashboard (requires authentication)."""
    if not session.get('cs_authenticated'):
        return redirect(url_for('cs_login'))
    return render_template('cs_dashboard.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Proxy chat requests to the backend API."""
    try:
        data = request.json
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "message": data.get("message", ""),
                "user_id": data.get("user_id", "web_user"),
                "ticket_id": data.get("ticket_id")
            },
            timeout=30
        )
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": True,
            "response": "Sorry, I'm having trouble connecting to the backend. Please try again.",
            "confidence": 0
        }), 500


@app.route('/api/health')
def health():
    """Health check endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return jsonify(response.json())
    except:
        return jsonify({"status": "unhealthy", "error": "Cannot reach backend"}), 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
