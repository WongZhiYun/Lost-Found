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

from file.chat_v2.chat_config import config

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))

@dataclass
class EmailMessage:
    """Email message class"""
    to: List[str] # List of recipient email addresses
    subject: str # Subject line of the email
    html_body: str # HTML body of the email
    text_body: Optional[str] = None # Optional plain-text version
    reply_to: Optional[str] = None # Optional reply-to address


class EmailService:
    """Email service class"""
    
    def __init__(self, mail_config=None):
        # Load mail configuration
        self.mail_config = mail_config or config.get_mail_config()
        self._last_notification_times = {}  # For preventing duplicate sending
        
    def send(self, message: EmailMessage) -> bool:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = formataddr((self.mail_config['from_name'], self.mail_config['from_address']))
            msg['To'] = ', '.join(message.to)
            msg['Reply-To'] = message.reply_to or self.mail_config['from_address']

            if message.text_body:
                # Attach plain text if available
                text_part = MIMEText(message.text_body, 'plain', 'utf-8')
                msg.attach(text_part)

            # Attach HTML body
            html_part = MIMEText(message.html_body, 'html', 'utf-8')
            msg.attach(html_part)

            # Connect to SMTP server and send message
            with self._create_smtp_connection() as server:
                server.send_message(msg)

            logger.info(f"Email sent successfully to {', '.join(message.to)}")
            return True
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check username/password.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending email: {e}")
            return False
    
    def send_new_message_notification(self, recipient_email: str, recipient_name: str, 
                                    sender_name: str, message_count: int = 1) -> bool:
         
        #Sends a "new message" email notification with cooldown to prevent spamming.
        cooldown_key = f"{recipient_email}_{sender_name}"
        now = datetime.now()
        last_sent = self._last_notification_times.get(cooldown_key)

        if last_sent and now - last_sent < timedelta(seconds=config.EMAIL_NOTIFICATIONS_COOLDOWN):
            logger.info(f"Email notification cooldown active for {recipient_email}")
            return False

        # Enforce cooldown (prevent frequent duplicate emails)
        subject = f"{sender_name} sent you a new message"
        if message_count > 1:
            subject = f"{sender_name} sent you {message_count} new messages"

        # Generate HTML + plain text bodies
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
        
        # Build message object
        message = EmailMessage(
            to=[recipient_email],
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )
        
        # Send and update cooldown tracker
        success = self.send(message)
        if success:
            self._last_notification_times[cooldown_key] = now
        return success
    
    def _create_smtp_connection(self):
        """Create and return an SMTP (or SMTP_SSL) connection"""
        if self.mail_config['use_ssl']:
            server = smtplib.SMTP_SSL(self.mail_config['host'], self.mail_config['port'])
        else:
            server = smtplib.SMTP(self.mail_config['host'], self.mail_config['port'])
            if self.mail_config['use_tls']:
                server.starttls()
        
        # Log in if credentials are provided
        if self.mail_config['username'] and self.mail_config['password']:
            server.login(self.mail_config['username'], self.mail_config['password'])
        return server
    
    def _create_notification_html(self, recipient_name: str, sender_name: str, message_count: int) -> str:
         #Generate HTML body for message notification
        app_url = config.APP_URL
        app_name = config.APP_NAME
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body>
            <h2>Hi {recipient_name} </h2>
            <p><strong>{sender_name}</strong> sent you {'a new message' if message_count == 1 else f'{message_count} new messages'}!</p>
            <p><a href="{app_url}">View message</a></p>
            <small>To avoid spam, notifications are sent at most once every {config.EMAIL_NOTIFICATIONS_COOLDOWN // 60} minutes.</small>
        </body>
        </html>
        """
    
    def _create_notification_text(self, recipient_name: str, sender_name: str, message_count: int) -> str:
        #Generate plain text body for message notification
        app_url = config.APP_URL
        app_name = config.APP_NAME
        return f"""
        Hi {recipient_name},

        {sender_name} sent you {'a new message' if message_count == 1 else f'{message_count} new messages'}!

        Check it out: {app_url}

        ---
        This is an automated email from {app_name}.
        """

    def test_connection(self) -> bool:
        #Test SMTP connection to ensure server credentials work
        try:
            with self._create_smtp_connection() as server:
                logger.info("SMTP connection test successful")
                return True
        except Exception as e:
            logger.error(f"SMTP connection test failed: {str(e)}")
            return False
    
    def get_config_info(self) -> dict:
        #Return masked mail configuration info (for debugging)
        return {
            'host': self.mail_config['host'],
            'port': self.mail_config['port'],
            'username': self.mail_config['username'][:3] + '***' if self.mail_config['username'] else 'Not set',
            'from_address': self.mail_config['from_address'],
            'from_name': self.mail_config['from_name'],
            'use_tls': self.mail_config['use_tls'],
            'use_ssl': self.mail_config['use_ssl'],
            'password': '***' if self.mail_config.get('password') else 'Not set'
        }


# Global instance
try:
    email_service = EmailService() if config.EMAIL_NOTIFICATIONS_ENABLED else None
    if email_service:
        logger.info("Email service initialized successfully")
    else:
        logger.info("Email service disabled via configuration")
except Exception as e:
    email_service = None
    logger.warning(f"Email service initialization failed: {e}")
