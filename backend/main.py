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
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules'))
from modules.scraper import scrape_jobs
from modules.resume_embedder import extract_resume_text
from modules.email_agent import generate_mail_body, find_company_email
from modules.smtp_sender import send_email
from modules.excel_logger import email_logger
from modules.motivational_letter_generator import generate_motivational_letter, save_motivational_letter_as_pdf

def load_config():
    """Load configuration from .env file or environment variables."""
    # Load .env file from the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(project_root, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        # Fallback to default load_dotenv behavior
        load_dotenv()
    
    config = {
        'resume': os.getenv('RESUME_PATH'),
        'smtp_email': os.getenv('SMTP_EMAIL'),
        'smtp_password': os.getenv('SMTP_PASSWORD'),
        'send': os.getenv('SEND_EMAILS', 'false').lower() == 'true',
        'job_type': os.getenv('JOB_TYPE', 'software'),
        'job_category': os.getenv('JOB_CATEGORY', 'freelance'),  # freelance or normal
        'job_limit': int(os.getenv('JOB_LIMIT', '30')),
        'motivational_letter': os.getenv('GENERATE_MOTIVATIONAL_LETTER', 'true').lower() == 'true'
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

def run(resume_path, smtp_email, smtp_password, dry_run=True, generate_motivational_letter_flag=True):
    print("Loading resume ->", resume_path)
    resume_text = extract_resume_text(resume_path)
    print("Resume text loaded.")
    # Note: We're not printing resume_text directly to avoid Unicode encoding issues

    print("Scraping jobs...")
    jobs = scrape_jobs(limit=args.job_limit, job_type=args.job_type, job_category=args.job_category)
    print(f"Found {len(jobs)} {args.job_category} job(s) for '{args.job_type}' type.")

    for job in jobs:
        print("\n" + "="*80)
        print(f"Processing Job: {job['title'][:70]}")
        print(f"Platform: {job['platform']} | Budget: {job.get('budget', 'N/A')}")
        print("="*80)
        
        # Create personalized email body using resume
        try:
            print("Generating personalized email...")
            body = generate_mail_body(job['title'], job.get('description',''), resume_text)
            print("[SUCCESS] Email generated successfully")
        except Exception as e:
            print(f"[ERROR] Error generating email body: {e}")
            continue
            
        # Generate motivational letter if requested
        motivational_letter_path = None
        if generate_motivational_letter_flag:
            try:
                print("Generating motivational letter...")
                letter_content = generate_motivational_letter(job['title'], job.get('description',''), resume_text)
                # Save motivational letter as PDF
                letter_filename = f"motivational_letter_{job['title'][:30].replace(' ', '_').replace('/', '_')}.pdf"
                letter_filename = re.sub(r'[<>:"/\\|?*]', '_', letter_filename)  # Remove invalid characters
                motivational_letter_path = os.path.join(os.path.dirname(resume_path), letter_filename)
                motivational_letter_path = save_motivational_letter_as_pdf(letter_content, motivational_letter_path)
                print(f"[SUCCESS] Motivational letter generated: {motivational_letter_path}")
            except Exception as e:
                print(f"[ERROR] Error generating motivational letter: {e}")
                motivational_letter_path = None
        
        # Find company/client email
        to_email = job.get('email')  # Check if email was extracted from job posting
        
        if to_email:
            print(f"  [FOUND] Email found in job posting: {to_email}")
        else:
            print(f"  [SEARCH] Searching for contact email...")
            try:
                # Pass full job data to the email finder for better search results
                to_email = find_company_email(job['title'], job.get('company',''), job_data=job)
            except Exception as e:
                print(f"  [ERROR] Error finding company email: {e}")
                to_email = None
        
        # Validate the email - skip if it's a platform email or generic fallback
        if to_email:
            if not is_valid_target_email(to_email, job.get('company', ''), job.get('platform', '')):
                print(f"  [INVALID] Email '{to_email}' is not a valid client/company email (platform or generic)")
                print(f"  [SKIP] Skipping - Only sending to actual company/client emails")
                
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
                print(f"[FALLBACK] Using fallback email: {to_email}")
            else:
                print(f"  [NOT_FOUND] No valid company/client email found for this job")
                print(f"  [SKIP] Skipping - Only sending to actual company/client emails, not platforms")
                
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
            if motivational_letter_path and os.path.exists(motivational_letter_path):
                print(f"Motivational Letter: {motivational_letter_path}")
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
                # Prepare attachments - resume and motivational letter
                attachments = [resume_path]
                if motivational_letter_path and os.path.exists(motivational_letter_path):
                    attachments.append(motivational_letter_path)
                
                send_email(smtp_email, smtp_password, to_email, subject, body, attachments)
                print("[SUCCESS] Email sent successfully!")
                
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
                print(f"[FAILED] Failed to send email: {e}")
                
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
    parser.add_argument('--job-type', default=config['job_type'], help='Job type to search for (default: software)')
    parser.add_argument('--job-category', default=config['job_category'], choices=['freelance', 'normal'], help='Job category (default: freelance)')
    parser.add_argument('--job-limit', type=int, default=config['job_limit'], help='Number of jobs to process (default: 30)')
    parser.add_argument('--keywords', default='', help='Keywords to search for (comma-separated)')
    parser.add_argument('--job-field', default='tech', help='Job field to search for (tech, marketing, design, business, healthcare, finance, other)')
    parser.add_argument('--generate-motivational-letter', action='store_true', default=config['motivational_letter'], help='Generate motivational letter (default: true)')
    
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
    
    run(args.resume, args.smtp_email, args.smtp_password, dry_run=not args.send, generate_motivational_letter_flag=args.generate_motivational_letter)