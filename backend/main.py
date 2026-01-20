"""
Entry point for the Freelance Mailer CLI.
Usage (example):
    python main.py
"""
import argparse
import sys
import os
import re
import time
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
from modules.retry_handler import (
    add_to_retry_queue,
    should_retry_later,
    should_retry_on_exception,
    process_retry_queue
)

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
        'motivational_letter': os.getenv('GENERATE_MOTIVATIONAL_LETTER', 'true').lower() == 'true',
        'ai_model': os.getenv('AI_MODEL', 'meta-llama/llama-3.3-70b-instruct:free'),
        'location': os.getenv('LOCATION'),
        'job_name': os.getenv('JOB_NAME')
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
    
    # Reject masked emails
    if '*' in email:
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

def run(resume_path, smtp_email, smtp_password,
        dry_run=True,
        generate_motivational_letter_flag=True,
        max_jobs=30,
        job_type='software',
        job_category='freelance',
        job_field='tech',
        ai_model='meta-llama/llama-3.3-70b-instruct:free',
        location=None,
        job_name=None,
        process_retries=True):
    print("Loading resume ->", resume_path)
    resume_text = extract_resume_text(resume_path)
    print("Resume text loaded.")
    # Note: We're not printing resume_text directly to avoid Unicode encoding issues

    # Create motivational letters directory if it doesn't exist
    motivational_letters_dir = os.path.join(os.path.dirname(resume_path), 'motivational_letters')
    os.makedirs(motivational_letters_dir, exist_ok=True)

    print(f"\n[SCRAPER] Looking for {job_category} jobs...")
    # For normal jobs, we prioritize job_name, for freelance jobs we use job_type
    scraped_jobs = scrape_jobs(limit=max_jobs*2, job_type=job_type, job_category=job_category, location=location, job_name=job_name)
    print(f"Found {len(scraped_jobs)} jobs")

    if not scraped_jobs:
        print("No jobs found. Exiting...")
        return
    
    # Filter out already processed jobs
    jobs = []
    for job in scraped_jobs:
        if not email_logger.is_job_processed(job):
            jobs.append(job)
            # Log the job as scraped (but not yet processed for email)
            email_logger.log_job(job, email_sent=False, status="scraped")
    
    print(f"Found {len(jobs)} new jobs to process (skipping {len(scraped_jobs) - len(jobs)} already processed jobs)")
    
    if not jobs:
        print("No new jobs to process. Exiting...")
        return

    # Process each job (up to max_jobs)
    for i, job in enumerate(jobs[:max_jobs], 1):
        job_title = job.get('title', 'Untitled')
        company = job.get('company', 'Unknown Company')
        print("\n" + "="*80)
        print(f"Processing job {i}/{min(len(jobs), max_jobs)}: {job_title} at {company}")
        if 'platform' in job:
            print(f"Platform: {job['platform']} | Budget: {job.get('budget', 'N/A')}")
        print("="*80)
        
        # Update job status to processing
        email_logger.log_job(job, email_sent=False, status="processing")
        
        # Create personalized email body using resume
        try:
            print("Generating personalized email...")
            body = generate_mail_body(job['title'], job.get('description',''), resume_text, ai_model)
            print("[SUCCESS] Email generated successfully")
        except Exception as e:
            print(f"[ERROR] Error generating email body: {e}")
            continue
        
        # Common subject used for all logging paths
        subject = f"Application for {job['title']} position"
            
        # Generate motivational letter if requested
        motivational_letter_path = None
        if generate_motivational_letter_flag:
            try:
                print("Generating motivational letter...")
                letter_content = generate_motivational_letter(job['title'], job.get('description',''), resume_text, ai_model)
                # Save motivational letter as PDF in the motivational_letters folder
                letter_filename = f"motivational_letter_{job['title'][:30].replace(' ', '_').replace('/', '_')}.pdf"
                letter_filename = re.sub(r'[<>:"/\\|?*]', '_', letter_filename)  # Remove invalid characters
                motivational_letter_path = os.path.join(motivational_letters_dir, letter_filename)
                motivational_letter_path = save_motivational_letter_as_pdf(letter_content, motivational_letter_path)
                print(f"[SUCCESS] Motivational letter generated: {motivational_letter_path}")
            except Exception as e:
                print(f"[ERROR] Error generating motivational letter: {e}")
                motivational_letter_path = None
        
        # Find company/client email
        to_email = job.get('email')  # Check if email was extracted from job posting
        
        # If email is masked or invalid, treat it as not found so we search for it
        if to_email and '*' in to_email:
            print(f"  [INFO] Email '{to_email}' is masked/hidden. Will search for valid email.")
            to_email = None

        if to_email:
            print(f"  [FOUND] Email found in job posting: {to_email}")
        else:
            print(f"  [SEARCH] Searching for contact email...")
            try:
                # Pass full job data to the email finder for better search results
                to_email = find_company_email(job['title'], job.get('company',''), job_data=job, ai_model=ai_model)
                
                if not to_email:
                    print("  [INFO] No valid email found for this job")
                    # Log as skipped since we cannot find any email
                    email_logger.log_email(
                        job_data=job,
                        to_email="",
                        subject=subject,
                        body=body,
                        status="SKIPPED",
                        error_message="No valid email found for this job",
                        source_url=job.get('source', '')
                    )
                    continue
                    
            except Exception as e:
                error_msg = f"Error finding company email: {e}"
                print(f"  [ERROR] {error_msg}")
                # Treat search errors as FAILED attempts in the log
                email_logger.log_email(
                    job_data=job,
                    to_email="",
                    subject=subject,
                    body=body,
                    status="FAILED",
                    error_message=error_msg,
                    source_url=job.get('source', '')
                )
                continue
        
        # Validate the email - skip if it's a platform email or generic fallback
        if to_email:
            if not is_valid_target_email(to_email, job.get('company', ''), job.get('platform', '')):
                print(f"  [INVALID] Email '{to_email}' is not a valid client/company email (platform or generic)")
                print(f"  [SKIP] Skipping - Only sending to actual company/client emails")
                
                # Log the skipped job with subject/body for visibility
                email_logger.log_email(
                    job_data=job,
                    to_email=to_email,
                    subject=subject,
                    body=body,
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
                    subject=subject,
                    body=body,
                    status="SKIPPED",
                    error_message="No valid company email found - only platform email available",
                    source_url=job.get('source', '')
                )
                continue
            
        print(f"\nTarget Email: {to_email}")

        # Prepare attachments
        attachments = [resume_path]
        if motivational_letter_path:
            attachments.append(motivational_letter_path)
            
        # Send email if we have a valid recipient
        if to_email:
            print(f"Sending email to {to_email}...")
            
            try:
                if not dry_run:
                    # Enhanced email sending with retries and DSN
                    send_result = send_email(
                        sender_email=smtp_email,
                        sender_password=smtp_password,
                        to_email=to_email,
                        subject=subject,
                        body=body,
                        attachment_paths=attachments,
                        enable_dsn=True,
                        max_retries=3
                    )
                    
                    if send_result.get('success'):
                        status = "SENT"
                        print(f"Email sent successfully! (Attempts: {send_result['retry_count']})")
                        if send_result['retry_count'] > 1:
                            print(f"  [NOTE] Email required {send_result['retry_count']} attempts to send")
                    else:
                        status = "FAILED"
                        error_msg = send_result.get('error', 'Unknown error')
                        print(f"Failed to send email: {error_msg}")
                        
                else:
                    # Dry run mode
                    print("[DRY RUN] Would send email to:", to_email)
                    print("Subject:", subject)
                    print("Body preview:", body[:200] + "...")
                    print("Attachments:", [os.path.basename(a) for a in attachments])
                    status = "DRY_RUN"
                
                # Log the email with delivery status
                email_logger.log_email(
                    job_data=job,
                    to_email=to_email,
                    subject=subject,
                    body=body,
                    status=status,
                    error_message=send_result.get('error', '') if not dry_run and status == "FAILED" else '',
                    source_url=job.get('url', '')
                )
                
                # If email failed to send, add to retry queue
                if not dry_run and status == "FAILED":
                    retry_later = should_retry_later(send_result.get('dsn'))
                    if retry_later:
                        print(f"  [RETRY] Will retry this email later (DSN: {send_result.get('dsn')})")
                        # Add to retry queue (you can implement this as needed)
                        add_to_retry_queue(job, to_email, subject, body, attachments)
            except Exception as e:
                error_msg = str(e)
                print(f"Error in email process: {error_msg}")
                
                # Log the failure
                email_logger.log_email(
                    job_data=job,
                    to_email=to_email,
                    subject=subject,
                    body=body,
                    status="ERROR",
                    error_message=error_msg,
                    source_url=job.get('url', '')
                )
                
                # Check if we should retry based on exception type
                if should_retry_on_exception(e):
                    print("  [RETRY] Will retry this email due to temporary error")
                    add_to_retry_queue(job, to_email, subject, body, attachments)
            
            # Add a delay between jobs to reduce API rate limiting (free tier needs 10+ seconds)
            job_delay = int(os.getenv('JOB_DELAY', '10'))
            print(f"  [DELAY] Waiting {job_delay}s before next job to avoid rate limits...")
            time.sleep(job_delay)
    
    # Process retry queue if enabled
    if process_retries and not dry_run:
        print("\n" + "="*80)
        print("Processing retry queue...")
        print("="*80)
        retry_stats = process_retry_queue(smtp_email, smtp_password)
        print(f"Retry queue processed: {retry_stats['succeeded']} succeeded, {retry_stats['failed']} failed")
    
    print("\n" + "="*80)
    print(f"Job Processing Complete! Processed {len(jobs)} jobs.")
    if not dry_run:
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
    parser.add_argument('--job-field', default='tech', help='Job field to search for (tech, marketing, design, business, healthcare, finance, education, legal, manufacturing, hospitality, nonprofit, pharma, agriculture, construction, retail, other)')
    parser.add_argument('--generate-motivational-letter', action='store_true', default=config['motivational_letter'], help='Generate motivational letter (default: true)' )
    parser.add_argument('--ai-model', default='meta-llama/llama-3.3-70b-instruct:free', help='AI model to use for generation (default: meta-llama/llama-3.3-70b-instruct:free). See README for available models.')
    parser.add_argument('--location', help='Location to search for jobs')
    parser.add_argument('--job-name', help='Specific job name to search for')
    
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
    
    # Check if OPENROUTER_API_KEY is set
    if not os.getenv('OPENROUTER_API_KEY'):
        print("Error: OPENROUTER_API_KEY environment variable is not set.")
        sys.exit(1)
    
    run(
        args.resume,
        args.smtp_email,
        args.smtp_password,
        dry_run=not args.send,
        generate_motivational_letter_flag=args.generate_motivational_letter,
        max_jobs=args.job_limit,
        job_type=args.job_type,
        job_category=args.job_category,
        job_field=args.job_field,
        ai_model=args.ai_model,
        location=args.location,
        job_name=args.job_name
    )