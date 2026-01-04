/**
 * CS Dashboard - JavaScript for ticket management
 */

const API_BASE = '/api/v1';
let currentTicketId = null;
let currentFilter = 'all';

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

        return `
            <tr class="${unreadClass}" onclick="openTicket('${ticket.id}')">
                <td><strong>#${ticket.id}</strong></td>
                <td>${ticket.user_id}</td>
                <td class="query-preview">${escapeHtml(ticket.query)}</td>
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
 * Open ticket detail modal
 */
async function openTicket(ticketId) {
    currentTicketId = ticketId;

    try {
        const response = await fetch(`${API_BASE}/tickets/${ticketId}`);
        const ticket = await response.json();

        // Render ticket details
        const details = document.getElementById('ticketDetails');
        details.innerHTML = `
            <div class="ticket-detail">
                <label>Ticket ID</label>
                <div class="ticket-detail-value">#${ticket.id}</div>
            </div>
            <div class="ticket-detail">
                <label>User</label>
                <div class="ticket-detail-value">${ticket.user_id}</div>
            </div>
            <div class="ticket-detail">
                <label>Query</label>
                <div class="ticket-detail-value">${escapeHtml(ticket.query)}</div>
            </div>
            <div class="ticket-detail">
                <label>AI Response</label>
                <div class="ticket-detail-value">${escapeHtml(ticket.response)}</div>
            </div>
            <div class="ticket-detail">
                <label>Status</label>
                <div class="ticket-detail-value">
                    <span class="status-badge status-${ticket.status}">${formatStatus(ticket.status)}</span>
                    ${ticket.needs_escalation ? '<span class="status-badge status-pending_review" style="margin-left: 0.5rem">Needs Escalation</span>' : ''}
                    ${ticket.ai_resolved ? '<span class="status-badge status-ai_resolved" style="margin-left: 0.5rem">AI Handled</span>' : ''}
                </div>
            </div>
            ${ticket.escalation_reason ? `
            <div class="ticket-detail">
                <label>Escalation Reason</label>
                <div class="ticket-detail-value">${escapeHtml(ticket.escalation_reason)}</div>
            </div>
            ` : ''}
            <div class="ticket-detail">
                <label>Confidence</label>
                <div class="ticket-detail-value">${(ticket.confidence * 100).toFixed(0)}%</div>
            </div>
            <div class="ticket-detail">
                <label>Created</label>
                <div class="ticket-detail-value">${new Date(ticket.created_at).toLocaleString()}</div>
            </div>
            ${ticket.assigned_to ? `
            <div class="ticket-detail">
                <label>Assigned To</label>
                <div class="ticket-detail-value">${ticket.assigned_to}</div>
            </div>
            ` : ''}
        `;

        // Set current status in dropdown
        document.getElementById('statusSelect').value = ticket.status;
        document.getElementById('notesInput').value = ticket.notes || '';

        // Show modal
        document.getElementById('ticketModal').classList.add('active');

        // Refresh tickets (to update read status)
        loadTickets();

    } catch (error) {
        console.error('Failed to load ticket:', error);
    }
}

/**
 * Close modal
 */
function closeModal() {
    document.getElementById('ticketModal').classList.remove('active');
    currentTicketId = null;
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
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize on load
document.addEventListener('DOMContentLoaded', init);
