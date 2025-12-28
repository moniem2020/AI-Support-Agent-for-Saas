"""
Flask Web Application - Professional AI Support Chat Interface
Styled like modern YC AI startups (Linear, Vercel, Anthropic)
"""
from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# API Backend URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


@app.route('/')
def index():
    """Render the main chat interface."""
    return render_template('index.html')


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
