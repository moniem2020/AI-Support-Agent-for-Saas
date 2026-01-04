"""
Ticketing System for CS Agent Dashboard.
Tracks all customer requests and their resolution status.
"""
from src.tickets.ticket_store import ticket_store, Ticket, TicketStatus

__all__ = ["ticket_store", "Ticket", "TicketStatus"]
