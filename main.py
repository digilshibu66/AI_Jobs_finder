"""
Entry point for the Freelance Mailer CLI.
Usage (example):
    python main.py
"""
import argparse
import sys
import os
import re
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Use absolute imports instead of relative imports
from scraper import scrape_jobs
from resume_embedder import extract_resume_text
from email_agent import generate_mail_body, find_company_email
from smtp_sender import send_email
from excel_logger import email_logger

def load_config():
    """Load configuration from .env file or environment variables."""
    # Load .env file if it exists
    load_dotenv()
    
    config = {
        'resume': os.getenv('RESUME_PATH'),
        'smtp_email': os.getenv('SMTP_EMAIL'),
        'smtp_password': os.getenv('SMTP_PASSWORD'),
        'send': os.getenv('SEND_EMAILS', 'false').lower() == 'true'
    }
    
    return config

def generate_fallback_email(company_name):
    """Generate a fallback email address based on common patterns."""
    if not company_name:
        return None
        
    # Clean the company name
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name).lower()
    
    # Common email patterns
    fallback_emails = [
        f"jobs@{clean_name}.com",
        f"hr@{clean_name}.com",
        f"careers@{clean_name}.com",
        f"info@{clean_name}.com",
        f"contact@{clean_name}.com",
        f"recruiting@{clean_name}.com",
        f"hiring@{clean_name}.com"
    ]
    
    return fallback_emails[0]  # Return the first one as fallback

def is_valid_target_email(email, company_name, platform):
    """Check if email is a valid target (not a freelance platform or generic email)."""
    if not email:
        return False
    
    email_lower = email.lower()
    
    # Block freelance platform domains
    blocked_domains = [
        'freelancer.com',
        'upwork.com',
        'fiverr.com',
        'guru.com',
        'peopleperhour.com',
        'toptal.com',
        'remoteok.com',
        '99designs.com'
    ]
    
    # Check if email is from a blocked platform
    for domain in blocked_domains:
        if domain in email_lower:
            return False
    
    # Block generic/fallback patterns if company is unknown
    if 'client' in company_name.lower() or company_name == platform:
        # This is a fallback email pattern, not a real company email
        return False
    
    # Block common generic emails
    generic_patterns = ['noreply', 'no-reply', 'donotreply', 'example.com']
    if any(pattern in email_lower for pattern in generic_patterns):
        return False
    
    return True

def run(resume_path, smtp_email, smtp_password, dry_run=True):
    print("Loading resume ->", resume_path)
    resume_text = extract_resume_text(resume_path)
    print("Resume text loaded.", resume_text[:200])

    print("Scraping jobs...")
    jobs = scrape_jobs(limit=20)  # Increased limit for better job coverage
    print(f"Found {len(jobs)} job(s).")

    for job in jobs:
        print("\n" + "="*80)
        print(f"Processing Job: {job['title'][:70]}")
        print(f"Platform: {job['platform']} | Budget: {job.get('budget', 'N/A')}")
        print("="*80)
        
        # Create personalized email body using resume
        try:
            print("Generating personalized email...")
            body = generate_mail_body(job['title'], job.get('description',''), resume_text)
            print("✓ Email generated successfully")
        except Exception as e:
            print(f"✗ Error generating email body: {e}")
            continue
            
        # Find company/client email
        to_email = job.get('email')  # Check if email was extracted from job posting
        
        if to_email:
            print(f"  ✓ Email found in job posting: {to_email}")
        else:
            print(f"  🔍 Searching for contact email...")
            try:
                # Pass full job data to the email finder for better search results
                to_email = find_company_email(job['title'], job.get('company',''), job_data=job)
            except Exception as e:
                print(f"  ✗ Error finding company email: {e}")
                to_email = None
        
        # Validate the email - skip if it's a platform email or generic fallback
        if to_email:
            if not is_valid_target_email(to_email, job.get('company', ''), job.get('platform', '')):
                print(f"  ✗ Email '{to_email}' is not a valid client/company email (platform or generic)")
                print(f"  ⚠ Skipping - Only sending to actual company/client emails")
                
                # Log the skipped job
                email_logger.log_email(
                    job_data=job,
                    to_email=to_email,
                    subject="",
                    body="",
                    status="SKIPPED",
                    error_message="Not a valid company email - platform or generic email",
                    source_url=job.get('source', '')
                )
                continue
                
        # If still no email, try fallback method (but validate it too)
        if not to_email:
            company_name = job.get('company', '')
            to_email = generate_fallback_email(company_name)
            
            if to_email and is_valid_target_email(to_email, company_name, job.get('platform', '')):
                print(f"⚠ Using fallback email: {to_email}")
            else:
                print(f"  ✗ No valid company/client email found for this job")
                print(f"  ⚠ Skipping - Only sending to actual company/client emails, not platforms")
                
                # Log the skipped job
                email_logger.log_email(
                    job_data=job,
                    to_email="",
                    subject="",
                    body=body,
                    status="SKIPPED",
                    error_message="No valid company email found - only platform email available",
                    source_url=job.get('source', '')
                )
                continue
            
        print(f"\nTarget Email: {to_email}")
        subject = f"Application for {job['title'][:60]} - Experienced Developer"

        if dry_run:
            print("\n" + "-"*80)
            print("DRY RUN MODE - Email Preview")
            print("-"*80)
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"\nBody:\n{body[:600]}...")
            print("-"*80)
            
            # Log the email attempt
            email_logger.log_email(
                job_data=job,
                to_email=to_email,
                subject=subject,
                body=body,
                status="DRY_RUN",
                source_url=job.get('source', '')
            )
        else:
            try:
                print(f"\nSending email to {to_email}...")
                send_email(smtp_email, smtp_password, to_email, subject, body, resume_path)
                print("✓ Email sent successfully!")
                
                # Log successful email sending
                email_logger.log_email(
                    job_data=job,
                    to_email=to_email,
                    subject=subject,
                    body=body,
                    status="SUCCESS",
                    source_url=job.get('source', '')
                )
            except Exception as e:
                print(f"✗ Failed to send email: {e}")
                
                # Log failed email sending
                email_logger.log_email(
                    job_data=job,
                    to_email=to_email,
                    subject=subject,
                    body=body,
                    status="FAILED",
                    error_message=str(e),
                    source_url=job.get('source', '')
                )
    
    print("\n" + "="*80)
    print(f"Job Processing Complete! Processed {len(jobs)} jobs.")
    print("Check email_log.xlsx for detailed records.")
    print("="*80)

if __name__ == '__main__':
    # Load configuration
    config = load_config()
    
    # Use config values, fallback to command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', default=config['resume'], help='Path to resume PDF')
    parser.add_argument('--smtp-email', default=config['smtp_email'], help='SMTP sender email')
    parser.add_argument('--smtp-password', default=config['smtp_password'], help='SMTP app password')
    parser.add_argument('--send', action='store_true', default=config['send'], help='Actually send emails (default is dry run)')
    
    args = parser.parse_args()
    
    # Validate required arguments
    if not args.resume:
        print("Error: Resume path is required. Set RESUME_PATH in .env or use --resume argument.")
        sys.exit(1)
        
    if not args.smtp_email:
        print("Error: SMTP email is required. Set SMTP_EMAIL in .env or use --smtp-email argument.")
        sys.exit(1)
        
    if not args.smtp_password:
        print("Error: SMTP password is required. Set SMTP_PASSWORD in .env or use --smtp-password argument.")
        sys.exit(1)
    
    # Check if GEMINI_API_KEY is set
    if not os.getenv('GEMINI_API_KEY'):
        print("Error: GEMINI_API_KEY environment variable is not set.")
        sys.exit(1)
    
    run(args.resume, args.smtp_email, args.smtp_password, dry_run=not args.send)