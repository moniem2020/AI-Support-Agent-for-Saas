/**
 * AI Support Agent - Chat JavaScript
 * Handles message sending, receiving, and UI updates
 */

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const typingIndicator = document.getElementById('typingIndicator');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

// State
let isWaitingForResponse = false;
let chatHistory = []; // Store messages for persistence

// LocalStorage keys
const CHAT_STORAGE_KEY = 'protaskflow_chat_history';
const CHAT_TIMESTAMP_KEY = 'protaskflow_chat_timestamp';
const CHAT_EXPIRY_HOURS = 24; // Auto-expire after 24 hours

/**
 * Save chat history to localStorage with timestamp
 */
function saveChat() {
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(chatHistory));
    localStorage.setItem(CHAT_TIMESTAMP_KEY, Date.now().toString());
}

/**
 * Check if chat has expired
 */
function isChatExpired() {
    const savedTimestamp = localStorage.getItem(CHAT_TIMESTAMP_KEY);
    if (!savedTimestamp) return false;

    const elapsed = Date.now() - parseInt(savedTimestamp);
    const expiryMs = CHAT_EXPIRY_HOURS * 60 * 60 * 1000;
    return elapsed > expiryMs;
}

/**
 * Load chat history from localStorage (if not expired)
 */
function loadChat() {
    // Check for expiry first
    if (isChatExpired()) {
        console.log('Chat history expired, starting fresh');
        clearChat();
        return;
    }

    const saved = localStorage.getItem(CHAT_STORAGE_KEY);
    if (saved) {
        try {
            chatHistory = JSON.parse(saved);
            chatHistory.forEach(msg => {
                addMessageToDOM(msg.text, msg.role, msg.options || {}, msg.time);
            });
        } catch (e) {
            console.error('Failed to load chat history:', e);
            chatHistory = [];
        }
    }
}

/**
 * Clear chat history and start new conversation
 */
function clearChat() {
    chatHistory = [];
    localStorage.removeItem(CHAT_STORAGE_KEY);
    localStorage.removeItem(CHAT_TIMESTAMP_KEY);

    // Remove all messages from DOM
    const messages = chatMessages.querySelectorAll('.message');
    messages.forEach(msg => msg.remove());

    // Show welcome message again
    addWelcomeMessage();
}

/**
 * Add welcome message
 */
function addWelcomeMessage() {
    const welcomeText = `Hi! I'm your AI support assistant. I can help you with:
• Getting started with ProTaskFlow
• Understanding features and billing
• Troubleshooting issues
• Integrations and setup

How can I help you today?`;
    addMessageToDOM(welcomeText, 'assistant', {}, 'Just now');
}

/**
 * Initialize chat functionality
 */
function init() {
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    themeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
    });

    // New Chat button
    const newChatBtn = document.getElementById('newChatBtn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', () => {
            if (confirm('Start a new conversation? Your current chat will be cleared.')) {
                clearChat();
            }
        });
    }

    // Load saved chat history
    loadChat();

    // Focus input on load
    messageInput.focus();
}

/**
 * Send a message to the API
 */
async function sendMessage() {
    const message = messageInput.value.trim();

    if (!message || isWaitingForResponse) return;

    // Clear input
    messageInput.value = '';

    // Add user message to chat
    addMessage(message, 'user');

    // Show typing indicator
    showTyping();
    isWaitingForResponse = true;
    sendButton.disabled = true;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                user_id: 'web_user',
                ticket_id: null
            })
        });

        const data = await response.json();

        // Hide typing indicator
        hideTyping();

        // Add assistant response
        if (data.error) {
            addMessage(data.response || 'Sorry, something went wrong.', 'assistant', {
                isError: true
            });
        } else {
            addMessage(data.response, 'assistant', {
                sources: data.sources,
                confidence: data.confidence,
                escalated: data.escalated
            });
        }

    } catch (error) {
        console.error('Chat error:', error);
        hideTyping();
        addMessage('Sorry, I couldn\'t connect to the server. Please try again.', 'assistant', {
            isError: true
        });
    } finally {
        isWaitingForResponse = false;
        sendButton.disabled = false;
        messageInput.focus();
    }
}

/**
 * Add a message to the chat (saves to history + renders)
 */
function addMessage(text, role, options = {}) {
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Save to history for persistence
    chatHistory.push({ text, role, options, time: timeStr });
    saveChat();

    // Render to DOM
    addMessageToDOM(text, role, options, timeStr);
}

/**
 * Add a message to DOM only (used for loading saved messages)
 */
function addMessageToDOM(text, role, options = {}, timeStr = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    if (!timeStr) {
        const now = new Date();
        timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    // Avatar SVG
    const avatarSvg = role === 'user'
        ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
               <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
               <circle cx="12" cy="7" r="4"/>
           </svg>`
        : `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
               <circle cx="12" cy="12" r="10"/>
               <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
               <line x1="9" y1="9" x2="9.01" y2="9"/>
               <line x1="15" y1="9" x2="15.01" y2="9"/>
           </svg>`;

    // Sources are NOT displayed to users - kept in backend for:
    // - Developer debugging
    // - CS agent visibility on escalation
    // - Service improvement analytics
    let sourcesHtml = '';

    // Format text with line breaks
    const formattedText = text.split('\n').map(line => `<p>${line}</p>`).join('');

    messageDiv.innerHTML = `
        <div class="message-avatar">
            ${avatarSvg}
        </div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-author">${role === 'user' ? 'You' : 'AI Assistant'}</span>
                <span class="message-time">${timeStr}</span>
            </div>
            <div class="message-text ${options.isError ? 'error' : ''}">
                ${formattedText}
                ${sourcesHtml}
            </div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Show typing indicator
 */
function showTyping() {
    typingIndicator.style.display = 'block';
    scrollToBottom();
}

/**
 * Hide typing indicator
 */
function hideTyping() {
    typingIndicator.style.display = 'none';
}

/**
 * Scroll chat to bottom
 */
function scrollToBottom() {
    const chatContainer = document.querySelector('.chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);
