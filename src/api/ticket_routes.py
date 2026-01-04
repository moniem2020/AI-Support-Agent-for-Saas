"""
Ticket API Routes - Endpoints for CS Agent Dashboard.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from src.tickets.ticket_store import ticket_store, Ticket, TicketStatus


router = APIRouter(prefix="/tickets", tags=["tickets"])


class TicketResponse(BaseModel):
    """Ticket response model."""
    id: str
    user_id: str
    query: str
    response: str
    created_at: str
    ai_resolved: bool
    needs_escalation: bool
    escalation_reason: str
    confidence: float
    status: str
    assigned_to: Optional[str]
    read: bool
    notes: str
    updated_at: Optional[str]


class TicketListResponse(BaseModel):
    """Ticket list response."""
    tickets: List[TicketResponse]
    total: int
    stats: dict


class UpdateStatusRequest(BaseModel):
    """Request to update ticket status."""
    status: str
    notes: Optional[str] = ""
    assigned_to: Optional[str] = None


class NotificationResponse(BaseModel):
    """Notification count response."""
    unread_count: int


@router.get("", response_model=TicketListResponse)
async def list_tickets(
    status: Optional[str] = None,
    needs_escalation: Optional[bool] = None,
    limit: int = 100
):
    """
    List all tickets with optional filters.
    
    - **status**: Filter by status (ai_resolved, pending_review, in_progress, resolved, closed)
    - **needs_escalation**: Filter by escalation status
    - **limit**: Max tickets to return
    """
    status_enum = None
    if status:
        try:
            status_enum = TicketStatus(status)
        except ValueError:
            raise HTTPException(400, f"Invalid status: {status}")
    
    tickets = ticket_store.list_all(
        status=status_enum,
        needs_escalation=needs_escalation,
        limit=limit
    )
    
    return TicketListResponse(
        tickets=[TicketResponse(
            id=t.id,
            user_id=t.user_id,
            query=t.query,
            response=t.response,
            created_at=t.created_at,
            ai_resolved=t.ai_resolved,
            needs_escalation=t.needs_escalation,
            escalation_reason=t.escalation_reason,
            confidence=t.confidence,
            status=t.status.value,
            assigned_to=t.assigned_to,
            read=t.read,
            notes=t.notes,
            updated_at=t.updated_at
        ) for t in tickets],
        total=len(tickets),
        stats=ticket_store.get_stats()
    )


@router.get("/notifications", response_model=NotificationResponse)
async def get_notifications():
    """Get count of unread escalated tickets."""
    return NotificationResponse(
        unread_count=ticket_store.get_notification_count()
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str):
    """
    Get ticket details and mark as read.
    
    Opening a ticket marks it as read, clearing the notification.
    """
    ticket = ticket_store.get(ticket_id)
    if not ticket:
        raise HTTPException(404, f"Ticket not found: {ticket_id}")
    
    # Mark as read when viewed
    ticket_store.mark_as_read(ticket_id)
    ticket = ticket_store.get(ticket_id)
    
    return TicketResponse(
        id=ticket.id,
        user_id=ticket.user_id,
        query=ticket.query,
        response=ticket.response,
        created_at=ticket.created_at,
        ai_resolved=ticket.ai_resolved,
        needs_escalation=ticket.needs_escalation,
        escalation_reason=ticket.escalation_reason,
        confidence=ticket.confidence,
        status=ticket.status.value,
        assigned_to=ticket.assigned_to,
        read=ticket.read,
        notes=ticket.notes,
        updated_at=ticket.updated_at
    )


@router.put("/{ticket_id}/status", response_model=TicketResponse)
async def update_ticket_status(ticket_id: str, request: UpdateStatusRequest):
    """
    Update ticket status.
    
    - **status**: New status
    - **notes**: Optional CS agent notes
    - **assigned_to**: Optional agent name to assign
    """
    ticket = ticket_store.get(ticket_id)
    if not ticket:
        raise HTTPException(404, f"Ticket not found: {ticket_id}")
    
    try:
        status_enum = TicketStatus(request.status)
    except ValueError:
        raise HTTPException(400, f"Invalid status: {request.status}")
    
    # Assign if provided
    if request.assigned_to:
        ticket_store.assign(ticket_id, request.assigned_to)
    
    # Update status
    ticket = ticket_store.update_status(ticket_id, status_enum, request.notes or "")
    
    return TicketResponse(
        id=ticket.id,
        user_id=ticket.user_id,
        query=ticket.query,
        response=ticket.response,
        created_at=ticket.created_at,
        ai_resolved=ticket.ai_resolved,
        needs_escalation=ticket.needs_escalation,
        escalation_reason=ticket.escalation_reason,
        confidence=ticket.confidence,
        status=ticket.status.value,
        assigned_to=ticket.assigned_to,
        read=ticket.read,
        notes=ticket.notes,
        updated_at=ticket.updated_at
    )
