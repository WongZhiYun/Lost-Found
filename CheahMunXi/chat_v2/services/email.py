"""
Email Service
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from config import config

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))

@dataclass
class EmailMessage:
    """Email message class"""
    to: List[str]
    subject: str
    html_body: str
    text_body: Optional[str] = None
    reply_to: Optional[str] = None

class EmailService:
    """Email service class"""
    
    def __init__(self, mail_config=None):
        self.mail_config = mail_config or config.get_mail_config()
        self._last_notification_times = {}  # For preventing duplicate sending
        
    def send(self, message: EmailMessage) -> bool:
        """
        Send email
        
        Args:
            message: Email message object
            
        Returns:
            bool: Whether the email was sent successfully
        """
        try:
            # Create email object
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = formataddr((self.mail_config['from_name'], self.mail_config['from_address']))
            msg['To'] = ', '.join(message.to)
            
            if message.reply_to:
                msg['Reply-To'] = message.reply_to
            
            # Add text and HTML content
            if message.text_body:
                text_part = MIMEText(message.text_body, 'plain', 'utf-8')
                msg.attach(text_part)
            
            html_part = MIMEText(message.html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Send email
            with self._create_smtp_connection() as server:
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {', '.join(message.to)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_new_message_notification(self, recipient_email: str, recipient_name: str, 
                                    sender_name: str, message_count: int = 1) -> bool:
        """
        Send new message notification (prevent duplicate sending)

        Args:
            recipient_email: Recipient email
            recipient_name: Recipient name
            sender_name: Sender name
            message_count: Message count
            
        Returns:
            bool: Whether the email was sent successfully
        """
        # Check if in cooling time (5 minutes)
        cooldown_key = f"{recipient_email}_{sender_name}"
        now = datetime.now()
        last_sent = self._last_notification_times.get(cooldown_key)
        
        if last_sent and now - last_sent < timedelta(seconds=config.EMAIL_NOTIFICATIONS_COOLDOWN):
            logger.info(f"Email notification cooldown active for {recipient_email}")
            return False
        
        # Create email content
        subject = f"{sender_name} sent you a new message"
        if message_count > 1:
            subject = f"{sender_name} sent you {message_count} new messages"
        
        html_body = self._create_notification_html(
            recipient_name=recipient_name,
            sender_name=sender_name,
            message_count=message_count
        )
        
        text_body = self._create_notification_text(
            recipient_name=recipient_name,
            sender_name=sender_name,
            message_count=message_count
        )
        
        message = EmailMessage(
            to=[recipient_email],
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )
        
        # Send email
        success = self.send(message)
        if success:
            # Record sending time
            self._last_notification_times[cooldown_key] = now
        
        return success
    
    def _create_smtp_connection(self):
        """Create SMTP connection"""
        server = smtplib.SMTP(self.mail_config['host'], self.mail_config['port'])
        
        if self.mail_config['use_tls']:
            server.starttls()
        elif self.mail_config['use_ssl']:
            server = smtplib.SMTP_SSL(self.mail_config['host'], self.mail_config['port'])
        
        if self.mail_config['username'] and self.mail_config['password']:
            server.login(self.mail_config['username'], self.mail_config['password'])
        
        return server
    
    def _create_notification_html(self, recipient_name: str, sender_name: str, message_count: int) -> str:
        """Create HTML email template"""
        app_url = config.APP_URL
        app_name = config.APP_NAME
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>New Message Notification</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #269DD4; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: white; padding: 30px; border: 1px solid #e0e0e0; border-radius: 0 0 8px 8px; }}
                .button {{ background: #269DD4; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💬 {app_name}</h1>
                    <p>New Message Notification</p>
                </div>
                <div class="content">
                    <h2>Hi {recipient_name}! 👋</h2>
                    <p><strong>{sender_name}</strong> sent you {'a new message' if message_count == 1 else f'{message_count} new messages'}!</p>
                    
                    <p>Check it out:</p>
                    <a href="{app_url}" class="button">View Message</a>
                    
                    <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
                    <p style="color: #666; font-size: 14px;">
                        💡 To avoid email spam, we send at most one notification email every 10 minutes.
                    </p>
                </div>
                <div class="footer">
                    <p>This is an automated email, please do not reply.</p>
                    <p>&copy; 2024 {app_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_notification_text(self, recipient_name: str, sender_name: str, message_count: int) -> str:
        """Create plain text email content"""
        app_url = config.APP_URL
        app_name = config.APP_NAME
        
        return f"""
        Hi {recipient_name}!

        {sender_name} sent you {'a new message' if message_count == 1 else f'{message_count} new messages'}!

        Check it out: {app_url}

        💡 To avoid email spam, we send at most one notification email every 10 minutes.

        ---
        This is an automated email, please do not reply.
        © 2024 {app_name}. All rights reserved.
        """
    
    def test_connection(self) -> bool:
        """Test SMTP connection"""
        try:
            with self._create_smtp_connection() as server:
                logger.info("✅ \SMTP connection test successful")
                return True
        except Exception as e:
            logger.error(f"SMTP connection test failed: {str(e)}")
            return False
    
    def get_config_info(self) -> dict:
        """Get email configuration info (masked)"""
        return {
            'host': self.mail_config['host'],
            'port': self.mail_config['port'],
            'username': self.mail_config['username'][:3] + '***' if self.mail_config['username'] else 'Not set',
            'from_address': self.mail_config['from_address'],
            'from_name': self.mail_config['from_name'],
            'use_tls': self.mail_config['use_tls'],
            'use_ssl': self.mail_config['use_ssl'],
        }

# Create global email service instance
try:
    email_service = EmailService() if config.EMAIL_NOTIFICATIONS_ENABLED else None
    if email_service:
        logger.info("Email service initialized successfully")
    else:
        logger.info("Email service disabled via configuration")
except Exception as e:
    email_service = None
    logger.warning(f"Email service initialization failed: {e}")
