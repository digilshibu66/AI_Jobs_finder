"""
Email retry handler with queue management and retry logic.
"""
import os
import json
import time
import smtplib
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_HOURS = 1
RETRY_QUEUE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'retry_queue.json')

def should_retry_later(dsn_code: Optional[str] = None) -> bool:
    """Determine if an email should be retried based on DSN code.
    
    Args:
        dsn_code: The DSN code from the email server
        
    Returns:
        bool: True if the email should be retried, False otherwise
    """
    if not dsn_code:
        return False
        
    # 4.x.x are temporary failures that should be retried
    if dsn_code.startswith('4'):
        return True
        
    # 5.x.x are permanent failures that should not be retried
    if dsn_code.startswith('5'):
        return False
        
    # Default to not retry for unknown DSN codes
    return False

def should_retry_on_exception(exception: Exception) -> bool:
    """Determine if an email should be retried based on the exception type.
    
    Args:
        exception: The exception that was raised
        
    Returns:
        bool: True if the email should be retried, False otherwise
    """
    # Retry on temporary/transient errors
    transient_errors = (
        smtplib.SMTPServerDisconnected,
        smtplib.SMTPConnectError,
        smtplib.SMTPResponseException,
        TimeoutError,
        ConnectionError,
        TimeoutError
    )
    
    return isinstance(exception, transient_errors)

def add_to_retry_queue(
    job_data: Dict[str, Any],
    to_email: str,
    subject: str,
    body: str,
    attachments: List[str],
    attempt: int = 1,
    last_attempt_time: Optional[float] = None
) -> None:
    """Add a failed email to the retry queue.
    
    Args:
        job_data: The job data dictionary
        to_email: Recipient email address
        subject: Email subject
        body: Email body
        attachments: List of attachment paths
        attempt: Current attempt number (starts at 1)
        last_attempt_time: Timestamp of last attempt (default: current time)
    """
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(RETRY_QUEUE_FILE), exist_ok=True)
    
    # Load existing queue
    queue = load_retry_queue()
    
    # Create queue item
    queue_item = {
        'job_data': job_data,
        'to_email': to_email,
        'subject': subject,
        'body': body,
        'attachments': attachments,
        'attempt': attempt,
        'last_attempt_time': last_attempt_time or time.time(),
        'next_attempt_time': time.time() + (RETRY_DELAY_HOURS * 3600 * (2 ** (attempt - 1))),  # Exponential backoff
        'added_time': time.time()
    }
    
    # Add to queue
    queue.append(queue_item)
    
    # Save queue
    save_retry_queue(queue)

def process_retry_queue(smtp_email: str, smtp_password: str, max_retries: int = MAX_RETRY_ATTEMPTS) -> Dict[str, int]:
    """Process the retry queue and attempt to resend failed emails.
    
    Args:
        smtp_email: SMTP email address
        smtp_password: SMTP password
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dict with counts of processed, succeeded, and failed emails
    """
    from modules.smtp_sender import send_email
    
    # Load the queue
    queue = load_retry_queue()
    if not queue:
        return {'processed': 0, 'succeeded': 0, 'failed': 0, 'deferred': 0}
    
    current_time = time.time()
    processed = 0
    succeeded = 0
    failed = 0
    deferred = 0
    remaining_queue = []
    
    print(f"\nProcessing retry queue with {len(queue)} items...")
    
    for item in queue:
        # Skip if not time to retry yet
        if item['next_attempt_time'] > current_time:
            remaining_queue.append(item)
            deferred += 1
            continue
            
        processed += 1
        print(f"\nRetrying email to {item['to_email']} (attempt {item['attempt'] + 1} of {max_retries})...")
        
        try:
            # Try to send the email
            send_result = send_email(
                sender_email=smtp_email,
                sender_password=smtp_password,
                to_email=item['to_email'],
                subject=item['subject'],
                body=item['body'],
                attachment_paths=item['attachments'],
                enable_dsn=True,
                max_retries=1  # We're handling retries at the queue level
            )
            
            if send_result.get('success'):
                print(f"  Successfully resent email to {item['to_email']}")
                succeeded += 1
            else:
                # Check if we should retry again
                if item['attempt'] < max_retries and should_retry_later(send_result.get('dsn')):
                    print(f"  Will retry again later (attempt {item['attempt'] + 1} of {max_retries})")
                    item['attempt'] += 1
                    item['last_attempt_time'] = time.time()
                    item['next_attempt_time'] = time.time() + (RETRY_DELAY_HOURS * 3600 * (2 ** (item['attempt'] - 1)))
                    remaining_queue.append(item)
                    failed += 1
                else:
                    print(f"  Max retries reached or permanent failure for {item['to_email']}")
                    # Log the final failure
                    from modules.excel_logger import email_logger
                    email_logger.log_email(
                        job_data=item['job_data'],
                        to_email=item['to_email'],
                        subject=item['subject'],
                        body=item['body'],
                        status="FAILED",
                        error_message=send_result.get('error', 'Max retries reached'),
                        source_url=item['job_data'].get('url', '')
                    )
                    failed += 1
                    
        except Exception as e:
            error_msg = str(e)
            print(f"  Error resending email: {error_msg}")
            
            # Check if we should retry again
            if item['attempt'] < max_retries and should_retry_on_exception(e):
                print(f"  Will retry again later (attempt {item['attempt'] + 1} of {max_retries})")
                item['attempt'] += 1
                item['last_attempt_time'] = time.time()
                item['next_attempt_time'] = time.time() + (RETRY_DELAY_HOURS * 3600 * (2 ** (item['attempt'] - 1)))
                remaining_queue.append(item)
                failed += 1
            else:
                print(f"  Max retries reached or permanent error for {item['to_email']}")
                # Log the final failure
                from modules.excel_logger import email_logger
                email_logger.log_email(
                    job_data=item['job_data'],
                    to_email=item['to_email'],
                    subject=item['subject'],
                    body=item['body'],
                    status="ERROR",
                    error_message=error_msg,
                    source_url=item['job_data'].get('url', '')
                )
                failed += 1
    
    # Save the updated queue
    save_retry_queue(remaining_queue)
    
    print(f"\nRetry queue processing complete:")
    print(f"- Processed: {processed}")
    print(f"- Succeeded: {succeeded}")
    print(f"- Failed: {failed}")
    print(f"- Deferred: {deferred}")
    print(f"- Remaining in queue: {len(remaining_queue)}")
    
    return {
        'processed': processed,
        'succeeded': succeeded,
        'failed': failed,
        'deferred': deferred,
        'remaining': len(remaining_queue)
    }

def load_retry_queue() -> List[Dict[str, Any]]:
    """Load the retry queue from disk."""
    if not os.path.exists(RETRY_QUEUE_FILE):
        return []
        
    try:
        with open(RETRY_QUEUE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading retry queue: {e}")
        return []

def save_retry_queue(queue: List[Dict[str, Any]]) -> None:
    """Save the retry queue to disk."""
    try:
        with open(RETRY_QUEUE_FILE, 'w') as f:
            json.dump(queue, f, indent=2)
    except IOError as e:
        print(f"Error saving retry queue: {e}")

def clear_retry_queue() -> bool:
    """Clear the retry queue."""
    try:
        if os.path.exists(RETRY_QUEUE_FILE):
            os.remove(RETRY_QUEUE_FILE)
        return True
    except Exception as e:
        print(f"Error clearing retry queue: {e}")
        return False
