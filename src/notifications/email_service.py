"""
Email Notifications Service.
Sends email notifications for ticket updates using SMTP.
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

from src.config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, 
    EMAIL_FROM_NAME, EMAIL_ENABLED
)

logger = logging.getLogger(__name__)


class EmailService:
    """SMTP-based email service for sending notifications."""
    
    def __init__(self):
        self.host = SMTP_HOST
        self.port = SMTP_PORT
        self.user = SMTP_USER
        self.password = SMTP_PASSWORD
        self.from_name = EMAIL_FROM_NAME
        self.enabled = EMAIL_ENABLED
    
    def _get_connection(self) -> Optional[smtplib.SMTP]:
        """Create SMTP connection."""
        if not self.enabled:
            logger.info("Email notifications disabled")
            return None
            
        if not all([self.host, self.port, self.user, self.password]):
            logger.warning("SMTP configuration incomplete, skipping email")
            return None
        
        try:
            server = smtplib.SMTP(self.host, self.port)
            server.starttls()
            server.login(self.user, self.password)
            return server
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {e}")
            return None
    
    def _create_html_email(
        self,
        to_email: str,
        subject: str,
        heading: str,
        body_html: str
    ) -> MIMEMultipart:
        """Create a styled HTML email."""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{self.from_name} <{self.user}>"
        msg['To'] = to_email
        
        # Plain text fallback
        plain_text = f"{heading}\n\n{body_html.replace('<br>', '\n').replace('</p>', '\n')}"
        
        # HTML template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .content {{ padding: 30px; color: #333; line-height: 1.6; }}
                .message-box {{ background: #f8f9fa; border-left: 4px solid #667eea; padding: 15px; margin: 20px 0; border-radius: 0 8px 8px 0; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                .btn {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 AI Support Agent</h1>
                </div>
                <div class="content">
                    <h2>{heading}</h2>
                    {body_html}
                </div>
                <div class="footer">
                    <p>This is an automated message from AI Support Agent.</p>
                    <p>© {datetime.now().year} Your Company. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(plain_text, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        return msg
    
    def send_agent_reply_notification(
        self,
        to_email: str,
        ticket_id: str,
        ticket_subject: str,
        agent_message: str
    ) -> bool:
        """Send notification when an agent replies to a ticket."""
        server = self._get_connection()
        if not server:
            return False
        
        try:
            subject = f"[Ticket #{ticket_id}] New reply from support"
            heading = "A support agent has replied to your ticket"
            body = f"""
                <p>Your support ticket <strong>#{ticket_id}</strong> regarding "<em>{ticket_subject}</em>" has received a new reply.</p>
                <div class="message-box">
                    <p><strong>Agent's Message:</strong></p>
                    <p>{agent_message}</p>
                </div>
                <p>If you have any further questions, simply continue the conversation in your chat window.</p>
            """
            
            msg = self._create_html_email(to_email, subject, heading, body)
            server.sendmail(self.user, to_email, msg.as_string())
            server.quit()
            
            logger.info(f"Sent agent reply notification to {to_email} for ticket #{ticket_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send agent reply notification: {e}")
            return False
    
    def send_status_change_notification(
        self,
        to_email: str,
        ticket_id: str,
        ticket_subject: str,
        old_status: str,
        new_status: str
    ) -> bool:
        """Send notification when ticket status changes."""
        server = self._get_connection()
        if not server:
            return False
        
        try:
            status_messages = {
                'in_progress': ("We're on it! 🔧", "A support agent is now working on your ticket."),
                'resolved': ("Issue Resolved! ✅", "Your support ticket has been marked as resolved. We hope this helped!"),
                'closed': ("Ticket Closed 📁", "Your support ticket has been closed. Thank you for contacting us!")
            }
            
            heading, description = status_messages.get(
                new_status, 
                ("Status Update", f"Your ticket status has changed to: {new_status}")
            )
            
            subject = f"[Ticket #{ticket_id}] {heading}"
            body = f"""
                <p>Your support ticket <strong>#{ticket_id}</strong> regarding "<em>{ticket_subject}</em>" has been updated.</p>
                <div class="message-box">
                    <p><strong>New Status:</strong> {new_status.replace('_', ' ').title()}</p>
                    <p>{description}</p>
                </div>
                <p>Thank you for using our support service.</p>
            """
            
            msg = self._create_html_email(to_email, subject, heading, body)
            server.sendmail(self.user, to_email, msg.as_string())
            server.quit()
            
            logger.info(f"Sent status change notification to {to_email} for ticket #{ticket_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send status change notification: {e}")
            return False
    
    def send_escalation_confirmation(
        self,
        to_email: str,
        ticket_id: str,
        ticket_subject: str
    ) -> bool:
        """Send confirmation when ticket is escalated to human agent."""
        server = self._get_connection()
        if not server:
            return False
        
        try:
            subject = f"[Ticket #{ticket_id}] Your request has been escalated"
            heading = "You've been connected with our support team"
            body = f"""
                <p>Your support ticket <strong>#{ticket_id}</strong> regarding "<em>{ticket_subject}</em>" has been escalated to our human support team.</p>
                <div class="message-box">
                    <p><strong>What happens next?</strong></p>
                    <p>A support agent will review your request and respond as soon as possible. You'll receive an email notification when they reply.</p>
                </div>
                <p>Thank you for your patience!</p>
            """
            
            msg = self._create_html_email(to_email, subject, heading, body)
            server.sendmail(self.user, to_email, msg.as_string())
            server.quit()
            
            logger.info(f"Sent escalation confirmation to {to_email} for ticket #{ticket_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send escalation confirmation: {e}")
            return False


# Singleton instance
email_service = EmailService()
