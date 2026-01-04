"""
Flask Web Application - Professional AI Support Chat Interface
Styled like modern YC AI startups (Linear, Vercel, Anthropic)
"""
from flask import Flask, render_template, request, jsonify, Response
from functools import wraps
import requests
import os

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# API Backend URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# CS Dashboard Credentials (from environment variables)
CS_USERNAME = os.getenv("CS_USERNAME", "admin")
CS_PASSWORD = os.getenv("CS_PASSWORD", "support123")


def check_auth(username, password):
    """Check if username/password match."""
    return username == CS_USERNAME and password == CS_PASSWORD


def authenticate():
    """Send 401 response to trigger Basic Auth."""
    return Response(
        'Access denied. Please provide valid credentials.',
        401,
        {'WWW-Authenticate': 'Basic realm="CS Dashboard"'}
    )


def requires_auth(f):
    """Decorator for routes requiring authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    """Render the main chat interface."""
    return render_template('index.html')


@app.route('/cs')
@requires_auth
def cs_dashboard():
    """Render the CS agent dashboard (requires authentication)."""
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
