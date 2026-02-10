"""
Email body + email finding using AI (Gemini/OpenRouter).
Uses:
- AI for email body generation
- Google Custom Search API for finding company contact pages
"""
import os
import re
import requests
import json
import time
import random
from bs4 import BeautifulSoup
from .ai_wrapper import call_ai_api
from .email_validator import EmailValidator, get_best_emails

# ---------------- Email Body Generation ----------------

def generate_mail_body(job_title, job_description, resume_text, ai_model=None):
    """Generate personalized email body for job application."""
    
    messages = [
        {
            "role": "user",
            "content": f"""
        Write a highly personalized and professional job application email.

        Job Title: {job_title}
        Job Description: {job_description}

        My Resume:
        {resume_text[:4000]}

        Guidelines:
        - Start with ONLY "Hi Sir," as the greeting (no other greeting)
        - Address the specific project needs mentioned in the job description
        - Highlight 3-4 most relevant skills that match the job requirements
        - Mention 1-2 specific achievements or projects from my resume that are relevant
        - Show enthusiasm for this specific project/role
        - Keep it concise (8-12 sentences after the greeting)
        - Professional but friendly tone
        - End with: "I've attached my resume for your review. I'd love to discuss how I can contribute to your project. Looking forward to hearing from you."

        IMPORTANT:
        - MUST start with "Hi Sir," only
        - Make it feel personal, not template-like
        - Reference specific technologies or requirements from the job description
        - Don't use phrases like "I am writing to apply"
        - Start the body with a compelling opening that shows you understand their needs

        Return only the email body starting with "Hi Sir," (no subject line).
        
        CRITICAL INSTRUCTIONS:
        - REPLACE ALL PLACEHOLDERS. Do NOT use brackets like [Company Name].
        - Use the actual Job Title: "{job_title}"
        - If the Company Name is missing or "*****", use company name in {job_description}.
        - Do not use generic placeholders like [Source].
        """
        }
    ]

    response = call_ai_api(messages, ai_model)
    if not response:
        raise ValueError("AI generated empty response")
        
    response = response.strip()
    
    # Clean up markdown syntax that might look bad in plain text
    response = response.replace("**", "").replace("__", "")
    
    return response


# ---------------- Email Extraction ----------------

def extract_email(text):
    """Extract email address from text."""
    if not text:
        return None
    # Fixed regex pattern without escaped backslashes
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if emails:
        # Filter out invalid patterns
        invalid = ['noreply', 'no-reply', 'example.com', 'test.com', 'wix.com', 'sentry.io', 'email.com']
        valid = [e for e in emails if not any(inv in e.lower() for inv in invalid)]
        return valid[0] if valid else None
    return None


# ---------------- Google Search -------------------

def google_search(query):
    api = os.environ.get("GOOGLE_SEARCH_API_KEY")
    cx = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")

    if not api or not cx:
        print("  [WARNING] Google Search API missing. Cannot search.")
        return []

    url = (
        f"https://www.googleapis.com/customsearch/v1?"
        f"key={api}&cx={cx}&q={query}"
    )

    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return data.get("items", [])
    except Exception as e:
        print(f"  [ERROR] Google Search failed: {e}")
        return []


# ---------------- FREE Domain Discovery (No API Required) ----------------

def guess_company_domain(company_name):
    """
    Guess company domain by trying common patterns.
    Returns list of likely domains to try.
    """
    if not company_name:
        return []
    
    # Clean company name
    clean_name = company_name.lower()
    # Remove common suffixes
    suffixes_to_remove = [
        ' private limited', ' pvt ltd', ' pvt. ltd.', ' limited', ' ltd',
        ' inc', ' inc.', ' llc', ' corporation', ' corp', ' technologies',
        ' solutions', ' services', ' software', ' digital', ' labs'
    ]
    for suffix in suffixes_to_remove:
        clean_name = clean_name.replace(suffix, '')
    
    # Remove special characters and spaces
    clean_name = re.sub(r'[^a-z0-9]', '', clean_name)
    
    if not clean_name:
        return []
    
    # Try common TLDs
    guesses = [
        f"{clean_name}.com",
        f"{clean_name}.io",
        f"{clean_name}.co",
        f"{clean_name}.in",  # India
        f"{clean_name}.ai",
    ]
    
    return guesses


def scrape_google_search(query):
    """
    Scrape Google search results page (no API needed).
    Returns list of URLs from search results.
    """
    try:
        print(f"  [SEARCH] Scraping Google for: {query}")
        from urllib.parse import quote
        
        # Google search URL
        search_url = f"https://www.google.com/search?q={quote(query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        resp = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find result links
        results = []
        for link in soup.find_all('a'):
            href = link.get('href', '')
            # Google result links are in format /url?q=ACTUAL_URL
            if '/url?q=' in href:
                # Extract actual URL
                actual_url = href.split('/url?q=')[1].split('&')[0]
                if actual_url.startswith('http'):
                    results.append({'link': actual_url})
        
        print(f"  [SEARCH] Found {len(results)} results")
        return results
    except Exception as e:
        print(f"  [ERROR] Google scraping failed: {e}")
        return []


# ---------------- SMTP Verification ----------------

def verify_email_smtp(email):
    """
    Verify email existence via SMTP ping.
    Returns: (is_valid: bool, method: str)
    
    NOTE: This is intentionally permissive - if MX record exists, we assume valid
    to avoid false negatives on real emails that have strict SMTP servers.
    """
    import smtplib
    import dns.resolver
    import socket

    domain = email.split('@')[-1]
    print(f"  [SMTP] Verifying {email}...")

    try:
        # 1. Get MX Record - this is the most reliable check
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)
        print(f"  [SMTP] MX Record found: {mx_record}")
        
        # If MX exists, the domain can receive emails
        # We'll be optimistic and assume the email is valid
        # This prevents false negatives on strict mail servers
        print(f"  [SMTP] Valid (MX exists)")
        return True, "mx_valid"
        
    except Exception as e:
        print(f"  [SMTP] Could not resolve MX for {domain}: {e}")
        return False, "mx_fail"


# ---------------- Key Person Search (DEPRECATED/UNUSED) ----------------
# Kept for reference but removed from main flow

def find_key_people(company_name, role="CEO"):
    """
    Search for specific roles at a company using Google.
    Returns: Name string or None
    """
    print(f"  [PEOPLE] Searching for {role} of {company_name}...")
    query = f"{company_name} {role} LinkedIn"
    results = google_search(query)
    
    for item in results[:3]:
        title = item.get("title", "")
        # ... (rest of logic) ...
    return None

def generate_email_patterns(name, company_conf):
    return []

def find_company_email_with_openrouter(job_data, ai_model=None):
    return None

def verify_email_authenticity(email, company_name=None, ai_model=None):
    return True


# ---------------- MAIN EMAIL FINDER ----------------

def find_company_email(job_title, company_name, job_data=None, ai_model=None):
    """
    Find company/client email using comprehensive scraping strategy with advanced validation:
    1️⃣ Identify company domain via multiple methods (job URL, domain patterns, Google)
    2️⃣ Comprehensively crawl entire website (recursive, depth-limited) for all emails
    3️⃣ Advanced validation using EmailValidator (syntax, domain, MX, scoring)
    4️⃣ Score emails by relevance and company match
    5️⃣ Return ONLY validated, high-quality company emails
    
    Configuration via environment variables:
    - CRAWL_DEPTH: Max crawl depth (default: 2)
    - CRAWL_MAX_PAGES: Max pages to visit (default: 15)
    - CRAWL_TIMEOUT: Timeout per page (default: 5s)
    - TOTAL_CRAWL_TIME_LIMIT: Max total crawl time (default: 60s)
    """
    if not company_name or '*' in company_name:
         print(f"  [SKIP] Company name missing or masked.")
         return []

    # Step 0: Check if it's a platform/pseudo-company
    platform_indicators = ['client', 'freelancer', 'upwork', 'guru', 'fiverr', 'remoteok']
    if any(p in company_name.lower() for p in platform_indicators):
        print(f"  [SKIP] Skipping platform placeholder: {company_name}")
        return []

    print(f"  [FIND] Starting enhanced email search for {company_name}...")
    
    # Initialize email validator
    validator = EmailValidator()
    
    # Step 0.5: Try to extract domain from job source URL
    domain = None
    if job_data and job_data.get('source'):
        source_url = job_data.get('source')
        match = re.search(r'https?://(?:www\.)?([^/]+)', source_url)
        if match:
            candidate_domain = match.group(1)
            ignored_domains = ['linkedin.com', 'facebook.com', 'twitter.com', 'instagram.com', 'freelancer.com', 'upwork.com', 'indeed.com', 'glassdoor.com', 'google.com', 'remoteok.com']
            if candidate_domain not in ignored_domains:
                domain = candidate_domain
                print(f"  [DOMAIN] Found via job source: {domain}")

    # Step 1: Find Company Domain via FREE methods (no API needed)
    if not domain:
        # Method 1: Try common domain patterns first (fastest)
        print(f"  [GUESS] Trying common domain patterns...")
        guessed_domains = guess_company_domain(company_name)
        
        for guess in guessed_domains:
            try:
                # Quick check if domain responds
                test_url = f"https://{guess}"
                resp = requests.get(test_url, timeout=3, allow_redirects=True)
                if resp.status_code == 200:
                    domain = guess
                    print(f"  [DOMAIN] Found via pattern guess: {domain}")
                    break
            except:
                continue
        
        # Method 2: Try Google Search API if available
        if not domain:
            try:
                # Try API first
                results = google_search(f"{company_name} official website")
                if results:
                    for item in results[:3]:
                        link = item.get("link", "")
                        match = re.search(r'https?://(?:www\.)?([^/]+)', link)
                        if match:
                            candidate_domain = match.group(1)
                            ignored_domains = ['linkedin.com', 'facebook.com', 'twitter.com', 'instagram.com', 'freelancer.com', 'upwork.com']
                            if candidate_domain not in ignored_domains:
                                domain = candidate_domain
                                print(f"  [DOMAIN] Found via Google API: {domain}")
                                break
            except Exception as e:
                print(f"  [INFO] Google API not available: {e}")
        
        # Method 3: Scrape Google search page (no API)
        if not domain:
            try:
                print(f"  [FALLBACK] Trying free Google search scraping...")
                results = scrape_google_search(f"{company_name} official website")
                for item in results[:5]:
                    link = item.get("link", "")
                    match = re.search(r'https?://(?:www\.)?([^/]+)', link)
                    if match:
                        candidate_domain = match.group(1)
                        ignored_domains = ['linkedin.com', 'facebook.com', 'twitter.com', 'instagram.com', 'freelancer.com', 'upwork.com', 'wikipedia.org', 'crunchbase.com']
                        if candidate_domain not in ignored_domains:
                            domain = candidate_domain
                            print(f"  [DOMAIN] Found via Google scraping: {domain}")
                            break
            except Exception as e:
                print(f"  [ERROR] Google scraping failed: {e}")

    # Step 2: Comprehensive Website Scraping Strategy
    if domain:
        # Get configuration from environment or use defaults
        crawl_depth = int(os.getenv('CRAWL_DEPTH', '2'))  # Default: 2 levels deep
        crawl_max_pages = int(os.getenv('CRAWL_MAX_PAGES', '15'))  # Default: 15 pages
        crawl_timeout = int(os.getenv('CRAWL_TIMEOUT', '5'))  # Default: 5s per page
        total_time_limit = int(os.getenv('TOTAL_CRAWL_TIME_LIMIT', '60'))  # Default: 60s total
        
        # Use comprehensive scraper for better results
        base_url = f"https://{domain}"
        print(f"  [STRATEGY] Starting comprehensive website crawl for {domain}...")
        
        try:
            # Comprehensive crawl returns [(email, score, metadata), ...]
            email_results = comprehensive_website_scraper(
                base_url=base_url,
                max_depth=crawl_depth,
                max_pages=crawl_max_pages,
                timeout=crawl_timeout,
                total_time_limit=total_time_limit
            )
            
            if email_results:
                print(f"  [FOUND] Found {len(email_results)} emails from website crawl")
                
                # Extract just the email addresses
                found_emails = [email for email, score, metadata in email_results]
                
                # Use advanced validator to filter and rank
                print(f"  [VALIDATE] Validating emails with advanced quality scoring...")
                validated_results = validator.batch_validate(
                    emails=found_emails,
                    company_name=company_name,
                    job_domain=domain
                )
                
                if validated_results:
                    print(f"  [SUCCESS] Found {len(validated_results)} validated emails:")
                    for i, result in enumerate(validated_results[:5], 1):
                        print(f"    {i}. {result['email']} (score: {result['score']}/100 - {result['recommendation']})")
                    
                    # Return only highly recommended or acceptable emails
                    best_emails = [r['email'] for r in validated_results 
                                  if r['recommendation'] in ['highly_recommended', 'acceptable']]
                    
                    if best_emails:
                        return best_emails
                    else:
                        print(f"  [WARNING] Emails found but quality scores too low")
                else:
                    print(f"  [WARNING] All emails failed validation checks")
            else:
                print(f"  [INFO] Comprehensive crawl found no emails on website")
                
        except Exception as e:
            print(f"  [ERROR] Comprehensive crawl failed: {e}")
            print(f"  [FALLBACK] Will try generic email patterns...")

    # Fallback Strategy: Generic Emails (info@, careers@, etc)
    if domain:
        print("  [FALLBACK] Checking generic company emails...")
        generic_prefixes = ['careers', 'jobs', 'hr', 'recruiting', 'info', 'hello', 'contact']
        generic_candidates = [f"{prefix}@{domain}" for prefix in generic_prefixes]
        
        # Validate generic emails
        validated_results = validator.batch_validate(
            emails=generic_candidates,
            company_name=company_name,
            job_domain=domain
        )
        
        if validated_results:
            print(f"  [SUCCESS] Found {len(validated_results)} validated generic emails:")
            for i, result in enumerate(validated_results[:3], 1):
                print(f"    {i}. {result['email']} (score: {result['score']}/100)")
            
            # Return top validated generic emails
            best_emails = [r['email'] for r in validated_results[:3] 
                          if r['recommendation'] in ['highly_recommended', 'acceptable']]
            
            if best_emails:
                return best_emails
                 
    print("  [INFO] No validated email found. Skipping this job.")
    return []  # Return empty list instead of None



# ---------------- Comprehensive Website Scraping ----------------

def extract_domain_from_url(url):
    """Extract clean domain from URL."""
    if not url:
        return None
    match = re.search(r'https?://(?:www\.)?([^/]+)', url)
    return match.group(1) if match else None


def is_internal_link(link, base_domain):
    """Check if a link is internal to the base domain."""
    if not link or not base_domain:
        return False
    
    # Handle relative URLs
    if link.startswith('/'):
        return True
    
    # Extract domain from link
    link_domain = extract_domain_from_url(link)
    if not link_domain:
        return False
    
    # Compare domains (ignore www)
    base_clean = base_domain.replace('www.', '')
    link_clean = link_domain.replace('www.', '')
    
    return base_clean == link_clean


def extract_all_emails(text):
    """Extract all valid email addresses from text."""
    if not text:
        return []
    
    # Find all potential emails
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    
    # Filter out garbage emails
    invalid_patterns = [
        'example.com', 'test.com', 'wix.com', 'sentry.io', 
        'email.com', 'noreply', 'no-reply', 'donotreply',
        'webmaster', '.png', '.jpg', '.gif', '.css', '.js'
    ]
    
    valid_emails = []
    for email in emails:
        email_lower = email.lower()
        if not any(inv in email_lower for inv in invalid_patterns):
            valid_emails.append(email)
    
    return list(set(valid_emails))  # Return unique emails


def calculate_email_score(email, domain, page_url, page_content):
    """
    Calculate relevance score for an email address.
    Higher score = more likely to be the right contact email.
    """
    score = 0
    
    if not email or not domain:
        return score
    
    # 1. Domain Match (Highest Priority - 50 points)
    email_lower = email.lower()
    domain_clean = domain.replace('www.', '').lower()
    
    if domain_clean in email_lower:
        score += 50
    
    # 2. Email Prefix Keywords (30 points max)
    prefix = email_lower.split('@')[0]
    keyword_scores = {
        'careers': 30,
        'jobs': 30,
        'hr': 25,
        'hiring': 25,
        'recruiting': 20,
        'recruitment': 20,
        'talent': 15,
        'people': 15,
        'contact': 15,
        'hello': 10,
        'info': 10,
        'admin': 5,
        'support': 5
    }
    
    # Award highest matching keyword score
    for keyword, points in keyword_scores.items():
        if keyword in prefix:
            score += points
            break  # Only count highest matching keyword
    
    # 3. Page Context (20 points max)
    if page_url and page_content:
        page_text = (page_url + ' ' + page_content).lower()
        context_keywords = ['career', 'job', 'hire', 'recruiting', 'about', 'contact', 'team', 'work with us']
        
        for keyword in context_keywords:
            if keyword in page_text:
                score += 3  # Up to 20+ points for highly relevant pages
    
    # 4. Penalties
    # Penalize generic/spam emails heavily
    spam_indicators = ['noreply', 'no-reply', 'donotreply', 'donot', 'webmaster']
    for indicator in spam_indicators:
        if indicator in email_lower:
            score -= 100  # Effectively eliminates these emails
    
    # Penalize non-company domains (gmail, yahoo, etc.) slightly
    generic_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
    if any(gd in email_lower for gd in generic_domains):
        score -= 10
    
    return max(0, score)  # Don't allow negative scores


def comprehensive_website_scraper(base_url, max_depth=3, max_pages=20, timeout=5, total_time_limit=60):
    """
    Comprehensively crawl a website to find all email addresses.
    
    Args:
        base_url: Starting URL (e.g., https://example.com)
        max_depth: Maximum depth to crawl (0 = homepage only, 1 = homepage + direct links, etc.)
        max_pages: Maximum total pages to visit
        timeout: Timeout per page request in seconds
        total_time_limit: Maximum total time for entire crawl in seconds
        
    Returns:
        List of (email, score, metadata) tuples sorted by score (descending)
    """
    import time as time_module
    from urllib.parse import urljoin, urlparse
    
    print(f"  [COMPREHENSIVE] Starting deep crawl of {base_url}...")
    print(f"  [CONFIG] Max depth: {max_depth}, Max pages: {max_pages}, Timeout: {timeout}s")
    
    start_time = time_module.time()
    
    # Extract domain
    domain = extract_domain_from_url(base_url)
    if not domain:
        print(f"  [ERROR] Could not extract domain from {base_url}")
        return []
    
    # Initialize tracking
    visited_urls = set()
    emails_found = {}  # email -> {score, pages, first_found}
    urls_to_visit = [(base_url, 0)]  # (url, depth)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Crawl loop
    while urls_to_visit and len(visited_urls) < max_pages:
        # Check time limit
        if time_module.time() - start_time > total_time_limit:
            print(f"  [TIMEOUT] Reached total time limit of {total_time_limit}s")
            break
        
        current_url, depth = urls_to_visit.pop(0)
        
        # Skip if already visited or depth exceeded
        if current_url in visited_urls or depth > max_depth:
            continue
        
        try:
            # Fetch page
            print(f"  [CRAWL] Depth {depth}: {current_url}")
            resp = requests.get(current_url, timeout=timeout, headers=headers, allow_redirects=True)
            
            if resp.status_code != 200:
                continue
            
            visited_urls.add(current_url)
            
            # Parse page
            soup = BeautifulSoup(resp.text, 'html.parser')
            page_text = soup.get_text()
            
            # Extract emails from this page
            page_emails = extract_all_emails(resp.text)
            
            if page_emails:
                print(f"  [FOUND] {len(page_emails)} emails on this page")
            
            # Score and store emails
            for email in page_emails:
                score = calculate_email_score(email, domain, current_url, page_text)
                
                if email not in emails_found:
                    emails_found[email] = {
                        'score': 0,
                        'pages': [],
                        'first_found': current_url
                    }
                
                # Accumulate scores from multiple pages
                emails_found[email]['score'] += score
                emails_found[email]['pages'].append(current_url)
            
            # Extract links for next depth level
            if depth < max_depth:
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(current_url, href)
                    
                    # Filter: only internal links, no anchors, no duplicates
                    if (is_internal_link(absolute_url, domain) and 
                        '#' not in absolute_url.split('/')[-1] and
                        absolute_url not in visited_urls and
                        absolute_url not in [u[0] for u in urls_to_visit]):
                        
                        urls_to_visit.append((absolute_url, depth + 1))
        
        except Exception as e:
            print(f"  [ERROR] Failed to crawl {current_url}: {e}")
            continue
    
    # Sort emails by score
    sorted_emails = sorted(
        [(email, data['score'], data) for email, data in emails_found.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    print(f"  [COMPREHENSIVE] Crawled {len(visited_urls)} pages, found {len(sorted_emails)} unique emails")
    
    if sorted_emails:
        print(f"  [TOP EMAILS] Top 5 by score:")
        for i, (email, score, data) in enumerate(sorted_emails[:5], 1):
            print(f"    {i}. {email} (score: {score}, found on {len(data['pages'])} pages)")
    
    return sorted_emails


# ---------------- Company Site Crawler ----------------


def crawl_company_emails(domain):
    """
    Crawl company pages for emails and score them based on relevance.
    FREE "GOOGLE-AI-LIKE" PYTHON APPROACH
    """
    if not domain:
        return None
        
    print(f"  [CRAWL] Starting site crawl for {domain}...")
    
    pages = [
        "",         # Homepage
        "/careers",
        "/jobs",
        "/about",
        "/contact",
        "/join-us",
        "/team",
        "/about-us"
    ]
    
    keywords = ["career", "job", "hr", "recruit", "hiring", "talent", "people", "work"]
    results = []
    checked_emails = set()
    
    # Try http and https
    protocol = "https://"
    
    for page in pages:
        try:
            url = f"{protocol}{domain}{page}"
            print(f"  [CRAWL] Checking {url}...")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            resp = None
            try:
                resp = requests.get(url, timeout=5, headers=headers)
            except:
                # Try http if https fails
                if protocol == "https://":
                    url = f"http://{domain}{page}"
                    try:
                        resp = requests.get(url, timeout=5, headers=headers)
                    except:
                        pass
            
            if not resp or resp.status_code != 200:
                continue
                
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text().lower()
            
            # Simple mostly-correct email regex
            page_emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resp.text))
            
            for email in page_emails:
                if email in checked_emails:
                    continue
                checked_emails.add(email)
                
                # Filter garbage
                if any(x in email.lower() for x in ['example.com', 'wix.com', 'sentry', 'noreply', 'no-reply']):
                    continue
                
                # Validation: Domain match is huge bonus but not strictly required (some use gmail)
                # But for safety, we prioritize domain match
                domain_match = domain.replace('www.', '') in email.lower()
                
                score = 0
                if domain_match:
                    score += 5
                
                # Keyword scoring (from user's logic)
                page_score = sum(1 for k in keywords if k in text)
                
                # Also check if email itself contains keywords
                email_lower = email.lower()
                if any(k in email_lower for k in keywords):
                    score += 5
                
                total_score = score + page_score
                results.append((email, total_score))
                
        except Exception as e:
            # print(f"  [CRAWL] Error on {page}: {e}")
            pass
            
    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)
    
    found_emails = [x[0] for x in results]
    if found_emails:
        print(f"  [CRAWL] Found {len(found_emails)} potential emails: {', '.join(found_emails[:5])}...")
        return found_emails
        
    print(f"  [CRAWL] No emails found via crawling.")
    return []