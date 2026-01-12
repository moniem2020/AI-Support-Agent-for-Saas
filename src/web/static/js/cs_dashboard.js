/**
 * CS Dashboard - JavaScript for ticket management
 */

const API_BASE = '/api/v1';
let currentTicketId = null;
let currentFilter = 'all';
let pollDetailsInterval = null;

/**
 * Initialize dashboard
 */
async function init() {
    // Setup filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            loadTickets();
        });
    });

    // Load initial data
    await loadTickets();

    // Poll for notifications every 10 seconds
    setInterval(loadNotifications, 10000);
}

/**
 * Load tickets from API
 */
async function loadTickets() {
    try {
        let url = `${API_BASE}/tickets`;
        if (currentFilter !== 'all') {
            url += `?status=${currentFilter}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        renderStats(data.stats);
        renderTickets(data.tickets);
        updateNotificationBadge(data.stats.unread_escalated);

    } catch (error) {
        console.error('Failed to load tickets:', error);
    }
}

/**
 * Load notification count
 */
async function loadNotifications() {
    try {
        const response = await fetch(`${API_BASE}/tickets/notifications`);
        const data = await response.json();
        updateNotificationBadge(data.unread_count);
    } catch (error) {
        console.error('Failed to load notifications:', error);
    }
}

/**
 * Update notification badge
 */
function updateNotificationBadge(count) {
    const badge = document.getElementById('notificationBadge');
    const countEl = document.getElementById('notificationCount');

    if (count > 0) {
        badge.classList.remove('hidden');
        countEl.textContent = count;
    } else {
        badge.classList.add('hidden');
    }
}

/**
 * Render stats grid
 */
function renderStats(stats) {
    const grid = document.getElementById('statsGrid');
    grid.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${stats.total}</div>
            <div class="stat-label">Total</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.ai_resolved}</div>
            <div class="stat-label">AI Resolved</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.pending_review}</div>
            <div class="stat-label">Pending</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.in_progress}</div>
            <div class="stat-label">In Progress</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.resolved}</div>
            <div class="stat-label">Resolved</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.closed}</div>
            <div class="stat-label">Closed</div>
        </div>
    `;
}

/**
 * Render tickets table
 */
function renderTickets(tickets) {
    const tbody = document.getElementById('ticketsBody');
    const emptyState = document.getElementById('emptyState');

    if (tickets.length === 0) {
        tbody.innerHTML = '';
        emptyState.classList.remove('hidden');
        return;
    }

    emptyState.classList.add('hidden');

    tbody.innerHTML = tickets.map(ticket => {
        const time = new Date(ticket.created_at).toLocaleString();
        const unreadClass = !ticket.read && ticket.needs_escalation ? 'unread' : '';
        const subject = ticket.subject || ticket.query.substring(0, 50) + '...';
        const category = ticket.category || '-';
        const priority = ticket.priority || 'normal';

        return `
            <tr class="${unreadClass}" onclick="openTicket('${ticket.id}')">
                <td><strong>#${ticket.id}</strong></td>
                <td class="query-preview">${escapeHtml(subject)}</td>
                <td>${category}</td>
                <td><span class="priority-badge priority-${priority}">${priority}</span></td>
                <td><span class="status-badge status-${ticket.status}">${formatStatus(ticket.status)}</span></td>
                <td>${(ticket.confidence * 100).toFixed(0)}%</td>
                <td>${ticket.assigned_to || '-'}</td>
                <td>${time}</td>
            </tr>
        `;
    }).join('');
}

/**
 * Format status for display
 */
function formatStatus(status) {
    const labels = {
        'ai_resolved': 'AI Resolved',
        'pending_review': 'Pending Review',
        'in_progress': 'In Progress',
        'resolved': 'Resolved',
        'closed': 'Closed'
    };
    return labels[status] || status;
}

/**
 * Open ticket detail modal with chat interface
 */
async function openTicket(ticketId) {
    currentTicketId = ticketId;
    if (pollDetailsInterval) clearInterval(pollDetailsInterval);

    try {
        const response = await fetch(`${API_BASE}/tickets/${ticketId}`);
        const ticket = await response.json();

        renderTicketModalContent(ticket);

        document.getElementById('ticketModal').classList.add('active');

        // Start polling for chat updates
        pollDetailsInterval = setInterval(() => refreshTicketDetails(ticketId), 3000);

        // Also refresh list to mark read
        loadTickets();
    } catch (error) {
        console.error('Failed to load ticket:', error);
    }
}

/**
 * Poll for ticket updates (chat history)
 */
async function refreshTicketDetails(ticketId) {
    if (!ticketId || ticketId !== currentTicketId) return;
    try {
        const response = await fetch(`${API_BASE}/tickets/${ticketId}`);
        const ticket = await response.json();
        updateChatHistory(ticket.messages);
    } catch (e) { }
}

/**
 * Render the modal structure (Sidebar + Chat Area)
 */
function renderTicketModalContent(ticket) {
    const details = document.getElementById('ticketDetails');
    const subject = escapeHtml(ticket.subject || ticket.query.substring(0, 50));

    details.innerHTML = `
        <div class="modal-body-layout">
            <div class="ticket-sidebar">
                <div class="ticket-detail">
                    <label>Ticket ID</label>
                    <div class="ticket-detail-value">#${ticket.id}</div>
                </div>
                <div class="ticket-detail">
                    <label>Subject</label>
                    <div class="ticket-detail-value"><strong>${subject}</strong></div>
                </div>
                <div class="ticket-detail">
                    <label>User</label>
                    <div class="ticket-detail-value">${ticket.user_id}</div>
                </div>
                <div class="ticket-detail">
                    <label>Category</label>
                    <div class="ticket-detail-value">${ticket.category || '-'}</div>
                </div>
                
                <hr style="border: 0; border-top: 1px solid var(--border-subtle); margin: 1rem 0;">
                
                <div class="ticket-detail">
                    <label>Update Status</label>
                    <select class="status-select" id="statusSelect">
                        <option value="pending_review">Pending Review</option>
                        <option value="in_progress">In Progress</option>
                        <option value="resolved">Resolved</option>
                        <option value="closed">Closed</option>
                    </select>
                </div>
                
                <div class="ticket-detail">
                    <label>Internal Notes</label>
                    <textarea class="notes-input" id="notesInput" placeholder="Internal notes..." rows="4">${ticket.notes || ''}</textarea>
                </div>
                
                <button class="btn btn-secondary" style="width: 100%; margin-top: 1rem;" onclick="updateTicket()">Save Notes & Status</button>
            </div>

            <div class="chat-main-area">
                <div class="chat-history-container" id="chatHistory">
                    <!-- Chat messages injected here -->
                </div>
                
                <div class="chat-input-area">
                    <textarea class="notes-input" id="replyInput" style="height: 60px; min-height: 60px;" placeholder="Type a message... (Enter to send)"></textarea>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                         <span style="font-size: 0.8rem; color: var(--text-tertiary);">Shift+Enter for new line</span>
                         <button class="btn btn-primary" onclick="sendReply()">Send Reply</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Set status
    document.getElementById('statusSelect').value = ticket.status;

    // Initial Chat Render
    updateChatHistory(ticket.messages);

    // Setup Enter key to send
    const replyInput = document.getElementById('replyInput');
    replyInput.focus();
    replyInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendReply();
        }
    });
}

/**
 * Update chat history DOM
 */
function updateChatHistory(messages) {
    const container = document.getElementById('chatHistory');
    if (!container) return;

    // Preserve scroll if at bottom
    const wasAtBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 100;

    if (!messages || messages.length === 0) {
        container.innerHTML = '<div style="text-align: center; color: var(--text-tertiary); margin-top: 2rem;">No messages yet</div>';
        return;
    }

    const html = messages.map(msg => `
        <div class="chat-bubble ${msg.role === 'user' ? 'user' : (msg.role === 'agent' ? 'agent' : 'ai')}">
            <div class="chat-meta">
                <span>${msg.role === 'user' ? 'User' : (msg.role === 'agent' ? 'Agent' : 'AI')}</span>
                <span>${new Date(msg.timestamp).toLocaleTimeString()}</span>
            </div>
            ${escapeHtml(msg.content)}
        </div>
    `).join('');

    // Only update if content changed (simple check optional, but innerHTML is fast enough for text)
    if (container.innerHTML !== html) {
        container.innerHTML = html;
        if (wasAtBottom) container.scrollTop = container.scrollHeight;
    }
}

/**
 * Close modal
 */
function closeModal() {
    document.getElementById('ticketModal').classList.remove('active');
    currentTicketId = null;
    if (pollDetailsInterval) {
        clearInterval(pollDetailsInterval);
        pollDetailsInterval = null;
    }
}

/**
 * Update ticket status
 */
async function updateTicket() {
    if (!currentTicketId) return;

    const status = document.getElementById('statusSelect').value;
    const notes = document.getElementById('notesInput').value;

    try {
        const response = await fetch(`${API_BASE}/tickets/${currentTicketId}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                status: status,
                notes: notes,
                assigned_to: 'CS Agent'  // In real app, get from session
            })
        });

        if (response.ok) {
            closeModal();
            loadTickets();
        } else {
            alert('Failed to update ticket');
        }

    } catch (error) {
        console.error('Failed to update ticket:', error);
        alert('Failed to update ticket');
    }
}

/**
 * Send reply to customer
 */
async function sendReply() {
    if (!currentTicketId) return;

    const input = document.getElementById('replyInput');
    const message = input.value.trim();
    if (!message) return;

    try {
        // Optimistic UI update: clear input
        input.value = '';

        const response = await fetch(`${API_BASE}/tickets/${currentTicketId}/reply`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                agent_id: 'cs_agent'
            })
        });

        if (response.ok) {
            // Fetch latest messages immediately
            refreshTicketDetails(currentTicketId);
        } else {
            alert('Failed to send reply');
            input.value = message; // Restore on failure
        }

    } catch (error) {
        console.error('Failed to send reply:', error);
        alert('Failed to send reply');
        input.value = message; // Restore on failure
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize on load
document.addEventListener('DOMContentLoaded', init);
