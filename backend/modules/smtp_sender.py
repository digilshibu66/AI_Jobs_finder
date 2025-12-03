"""Enhanced SMTP sender with delivery status notification and retry mechanism.

Features:
- Delivery Status Notifications (DSN)
- Automatic retries for temporary failures
- Detailed error reporting
"""
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formatdate
import os
from typing import List, Optional, Dict, Any

SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def send_email(
    sender_email: str,
    sender_password: str,
    to_email: str,
    subject: str,
    body: str,
    attachment_paths: Optional[List[str]] = None,
    enable_dsn: bool = True,
    max_retries: int = MAX_RETRIES
) -> Dict[str, Any]:
    """Send an email with delivery status notification and retry mechanism.
    
    Args:
        sender_email: Sender's email address
        sender_password: Sender's email password or app password
        to_email: Recipient's email address
        subject: Email subject
        body: Email body
        attachment_paths: List of file paths to attach
        enable_dsn: Whether to request delivery status notifications
        max_retries: Maximum number of retry attempts for temporary failures
        
    Returns:
        Dict containing delivery status information
        
    Raises:
        ValueError: For invalid email addresses or missing parameters
        smtplib.SMTPException: For SMTP-related errors after all retries
    """
    if not to_email:
        raise ValueError('to_email is required')
    
    # Initialize result dictionary
    result = {
        'success': False,
        'message_id': None,
        'dsn': None,
        'retry_count': 0,
        'error': None
    }
    
    # Create message with DSN headers if enabled
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg['Date'] = formatdate(localtime=True)
    msg['Message-ID'] = f'<{int(time.time())}@{sender_email.split("@")[-1]}>'
    
    # Add DSN headers if enabled
    if enable_dsn:
        msg['Disposition-Notification-To'] = sender_email
        msg['X-Confirm-Reading-To'] = sender_email
        msg['Return-Receipt-To'] = sender_email
    
    msg.attach(MIMEText(body, 'plain'))

    # Handle multiple attachments
    if attachment_paths:
        for attachment_path in attachment_paths:
            if attachment_path and os.path.exists(attachment_path):
                filename = os.path.basename(attachment_path)
                with open(attachment_path, 'rb') as f:
                    part = MIMEApplication(f.read(), _subtype='pdf')
                    part.add_header('Content-Disposition', 'attachment', filename=filename)
                    msg.attach(part)
    
    # Try sending with retries
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
            server.starttls()
            server.login(sender_email, sender_password)
            
            # Send the message
            server.send_message(msg)
            
            # If we get here, the message was sent successfully
            result.update({
                'success': True,
                'message_id': msg['Message-ID'],
                'retry_count': attempt + 1
            })
            return result
            
        except smtplib.SMTPRecipientsRefused as e:
            # Permanent failure - don't retry
            error_msg = f"Permanent delivery failure: {e}"
            result['error'] = error_msg
            result['dsn'] = '5.1.1'  # Bad destination mailbox address
            raise smtplib.SMTPRecipientsRefused(error_msg) from e
            
        except (smtplib.SMTPDataError, smtplib.SMTPNotSupportedError) as e:
            # Permanent failure - don't retry
            error_msg = f"Permanent delivery failure: {e}"
            result['error'] = error_msg
            result['dsn'] = '5.0.0'  # Other permanent failure
            raise smtplib.SMTPDataError(error_msg) from e
            
        except (smtplib.SMTPServerDisconnected, 
                smtplib.SMTPConnectError,
                smtplib.SMTPResponseException,
                TimeoutError,
                ConnectionError) as e:
            # Temporary failure - retry
            last_exception = e
            result['retry_count'] = attempt + 1
            
            if attempt < max_retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
                continue
            
            # If we've exhausted all retries
            error_msg = f"Temporary delivery failure after {max_retries} attempts: {e}"
            result['error'] = error_msg
            result['dsn'] = '4.0.0'  # Temporary failure
            raise smtplib.SMTPException(error_msg) from e
            
        except Exception as e:
            # Unexpected error
            error_msg = f"Unexpected error: {e}"
            result['error'] = error_msg
            result['dsn'] = '5.0.0'  # Other permanent failure
            raise smtplib.SMTPException(error_msg) from e
            
        finally:
            try:
                if 'server' in locals():
                    server.quit()
            except Exception:
                pass
    
    return result