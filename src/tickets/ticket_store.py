"""
Ticket Storage - Manages customer support tickets.
Provides in-memory storage with JSON file persistence.
"""
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel


class TicketStatus(str, Enum):
    """Ticket workflow status."""
    AI_RESOLVED = "ai_resolved"           # AI handled successfully
    PENDING_REVIEW = "pending_review"     # Escalated, waiting for CS
    IN_PROGRESS = "in_progress"           # CS agent working on it
    RESOLVED = "resolved"                 # CS resolved it
    CLOSED = "closed"                     # Ticket closed


class Ticket(BaseModel):
    """Customer support ticket."""
    id: str
    user_id: str
    query: str
    response: str
    created_at: str
    
    # AI handling info
    ai_resolved: bool = False
    needs_escalation: bool = False
    escalation_reason: str = ""
    confidence: float = 0.0
    
    # Status tracking
    status: TicketStatus = TicketStatus.PENDING_REVIEW
    
    # CS agent info
    assigned_to: Optional[str] = None
    read: bool = False
    notes: str = ""
    updated_at: Optional[str] = None


class TicketStore:
    """In-memory ticket storage with JSON persistence."""
    
    def __init__(self, storage_path: str = "data/tickets.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.tickets: Dict[str, Ticket] = {}
        self._load()
    
    def _load(self):
        """Load tickets from JSON file."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for ticket_data in data:
                        ticket = Ticket(**ticket_data)
                        self.tickets[ticket.id] = ticket
            except Exception as e:
                print(f"Failed to load tickets: {e}")
    
    def _save(self):
        """Save tickets to JSON file."""
        try:
            with open(self.storage_path, 'w') as f:
                data = [t.model_dump() for t in self.tickets.values()]
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Failed to save tickets: {e}")
    
    def create(
        self,
        user_id: str,
        query: str,
        response: str,
        ai_resolved: bool,
        needs_escalation: bool,
        escalation_reason: str = "",
        confidence: float = 0.0
    ) -> Ticket:
        """Create a new ticket."""
        ticket_id = str(uuid.uuid4())[:8]
        
        # Determine initial status
        if ai_resolved and not needs_escalation:
            status = TicketStatus.AI_RESOLVED
        else:
            status = TicketStatus.PENDING_REVIEW
        
        ticket = Ticket(
            id=ticket_id,
            user_id=user_id,
            query=query,
            response=response,
            created_at=datetime.now().isoformat(),
            ai_resolved=ai_resolved,
            needs_escalation=needs_escalation,
            escalation_reason=escalation_reason,
            confidence=confidence,
            status=status
        )
        
        self.tickets[ticket_id] = ticket
        self._save()
        return ticket
    
    def get(self, ticket_id: str) -> Optional[Ticket]:
        """Get a ticket by ID."""
        return self.tickets.get(ticket_id)
    
    def list_all(
        self,
        status: Optional[TicketStatus] = None,
        needs_escalation: Optional[bool] = None,
        limit: int = 100
    ) -> List[Ticket]:
        """List tickets with optional filters."""
        result = list(self.tickets.values())
        
        if status is not None:
            result = [t for t in result if t.status == status]
        
        if needs_escalation is not None:
            result = [t for t in result if t.needs_escalation == needs_escalation]
        
        # Sort by created_at descending (newest first)
        result.sort(key=lambda t: t.created_at, reverse=True)
        
        return result[:limit]
    
    def mark_as_read(self, ticket_id: str) -> Optional[Ticket]:
        """Mark ticket as read by CS agent."""
        ticket = self.tickets.get(ticket_id)
        if ticket:
            ticket.read = True
            ticket.updated_at = datetime.now().isoformat()
            self._save()
        return ticket
    
    def assign(self, ticket_id: str, agent_name: str) -> Optional[Ticket]:
        """Assign ticket to CS agent."""
        ticket = self.tickets.get(ticket_id)
        if ticket:
            ticket.assigned_to = agent_name
            ticket.status = TicketStatus.IN_PROGRESS
            ticket.updated_at = datetime.now().isoformat()
            self._save()
        return ticket
    
    def update_status(
        self,
        ticket_id: str,
        status: TicketStatus,
        notes: str = ""
    ) -> Optional[Ticket]:
        """Update ticket status."""
        ticket = self.tickets.get(ticket_id)
        if ticket:
            ticket.status = status
            if notes:
                ticket.notes = notes
            ticket.updated_at = datetime.now().isoformat()
            self._save()
        return ticket
    
    def get_notification_count(self) -> int:
        """Get count of unread escalated tickets."""
        return sum(
            1 for t in self.tickets.values()
            if t.needs_escalation and not t.read and t.status == TicketStatus.PENDING_REVIEW
        )
    
    def get_stats(self) -> Dict[str, int]:
        """Get ticket statistics."""
        stats = {
            "total": len(self.tickets),
            "ai_resolved": 0,
            "pending_review": 0,
            "in_progress": 0,
            "resolved": 0,
            "closed": 0,
            "unread_escalated": self.get_notification_count()
        }
        
        for ticket in self.tickets.values():
            if ticket.status == TicketStatus.AI_RESOLVED:
                stats["ai_resolved"] += 1
            elif ticket.status == TicketStatus.PENDING_REVIEW:
                stats["pending_review"] += 1
            elif ticket.status == TicketStatus.IN_PROGRESS:
                stats["in_progress"] += 1
            elif ticket.status == TicketStatus.RESOLVED:
                stats["resolved"] += 1
            elif ticket.status == TicketStatus.CLOSED:
                stats["closed"] += 1
        
        return stats


# Global ticket store instance
ticket_store = TicketStore()
