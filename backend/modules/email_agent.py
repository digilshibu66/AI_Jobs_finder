"""
Email body + email finding WITHOUT Gemini tools.
Uses:
- Gemini 2.0 Flash for email body
- Google Custom Search API for finding company contact pages
"""
import os
import re
import requests

try:
    import google.generativeai as genai
except Exception:
    genai = None


# ---------------- Gemini Setup --------------------

def _configure_gemini():
    if genai is None:
        raise RuntimeError("google.generativeai not installed.")
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


# ------------- Email Body Generation ---------------

def generate_mail_body(job_title, job_description, resume_text):
    """Generate personalized email body for job application."""
    _configure_gemini()

    prompt = f"""
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
"""

    model = genai.GenerativeModel("gemini-2.0-flash")
    resp = model.generate_content(prompt)
    return resp.text.strip()


# ---------------- Email Extraction ----------------

def extract_email(text):
    """Extract email address from text."""
    if not text:
        return None
    # Fixed regex pattern without escaped backslashes
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if emails:
        # Filter out invalid patterns
        invalid = ['noreply', 'no-reply', 'example.com', 'test.com']
        valid = [e for e in emails if not any(inv in e.lower() for inv in invalid)]
        return valid[0] if valid else None
    return None


# ---------------- Google Search -------------------

def google_search(query):
    api = os.environ.get("GOOGLE_SEARCH_API_KEY")
    cx = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")

    url = (
        f"https://www.googleapis.com/customsearch/v1?"
        f"key={api}&cx={cx}&q={query}"
    )

    data = requests.get(url).json()
    return data.get("items", [])


# ---------------- Website Scrape -------------------

def scrape_website_for_email(url):
    try:
        html = requests.get(url, timeout=6).text
        return extract_email(html)
    except:
        return None


# ---------------- Enhanced Email Finder with Gemini ---------------------

def find_company_email_with_gemini(job_data):
    """
    Use Gemini with Google Search grounding to find company email.
    Takes full job data including title, description, company, platform, etc.
    """
    _configure_gemini()
    
    job_title = job_data.get('title', '')
    company_name = job_data.get('company', '')
    description = job_data.get('description', '')[:500]
    platform = job_data.get('platform', '')
    skills = ', '.join(job_data.get('skills', [])[:5])
    source_url = job_data.get('source', '')
    
    print(f"  [SEARCH] Searching for contact email using Gemini AI...")
    
    try:
        # Use Gemini 2.0 Flash with Google Search grounding
        model = genai.GenerativeModel(
            "gemini-2.0-flash-exp",
            tools="google_search_retrieval"
        )
        
        search_prompt = f"""
I need to find the official contact email address to apply for this job:

Job Title: {job_title}
Company/Employer: {company_name}
Platform: {platform}
Job Description: {description}
Required Skills: {skills}
Job URL: {source_url}

Task:
1. Search Google to find the company's official website
2. Look for contact pages, career pages, or about pages
3. Find email addresses for:
   - HR/Recruiting department
   - Career/Jobs inquiries
   - General business contact
   - Specific contact mentioned in the job posting

4. Verify the email domain matches the company

IMPORTANT:
- Return ONLY the most relevant email address for job applications
- Format: email@domain.com
- If the job is from a freelance platform and no specific company email is found, search for "{company_name} contact email"
- Prioritize: careers@, jobs@, hr@, recruiting@, contact@, info@
- DO NOT return generic emails like: noreply@, no-reply@, support@
- If absolutely no email found after thorough search, return exactly: "NOT_FOUND"

Return format: Just the email address, nothing else.
"""
        
        response = model.generate_content(search_prompt)
        result = response.text.strip()
        
        print(f"  Gemini response: {result[:100]}")
        
        # Extract email from response
        email = extract_email(result)
        
        if email and 'NOT_FOUND' not in result.upper():
            # Validate email is not a common invalid pattern
            invalid_patterns = ['noreply', 'no-reply', 'donotreply', 'example.com', 'test.com']
            if not any(pattern in email.lower() for pattern in invalid_patterns):
                print(f"  [FOUND] Found valid email: {email}")
                return email
            else:
                print(f"  [WARNING] Email found but appears invalid: {email}")
        else:
            print(f"  [NOT_FOUND] No email found via Gemini Search")
    
    except Exception as e:
        print(f"  [ERROR] Gemini search error: {e}")
    
    return None


def scrape_multiple_urls_for_email(urls):
    """Try scraping multiple URLs to find an email address."""
    for url in urls:
        try:
            print(f"  Checking {url[:60]}...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=8)
            
            if response.status_code == 200:
                # Look for emails in the page
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
                
                # Filter and prioritize
                priority_keywords = ['career', 'job', 'hr', 'recruit', 'hiring', 'contact']
                invalid_patterns = ['noreply', 'no-reply', 'example.com', 'privacy', 'unsubscribe']
                
                valid_emails = []
                for email in emails:
                    if not any(inv in email.lower() for inv in invalid_patterns):
                        # Check if email contains priority keywords
                        if any(kw in email.lower() for kw in priority_keywords):
                            return email
                        valid_emails.append(email)
                
                # Return first valid email if no priority match
                if valid_emails:
                    return valid_emails[0]
        except Exception as e:
            continue
    
    return None


def find_company_email(job_title, company_name, job_data=None):
    """
    Find company/client email using multiple strategies:
    1️⃣ Use Gemini with Google Search grounding (primary method)
    2️⃣ Google Custom Search API + website scraping
    3️⃣ Generate common email patterns as fallback
    """
    
    # If we have full job data, use the enhanced Gemini search
    if job_data:
        email = find_company_email_with_gemini(job_data)
        if email:
            return email
    else:
        # Fallback to basic Gemini search with just title and company
        _configure_gemini()
        
        try:
            model = genai.GenerativeModel(
                "gemini-2.0-flash-exp",
                tools="google_search_retrieval"
            )
            
            search_prompt = f"""
Find the official contact email for job applications:

Company: {company_name}
Job: {job_title}

Search for the company's website and find:
- HR/careers/jobs email
- Contact/inquiry email

Return ONLY the email address (format: email@domain.com)
If not found, return: NOT_FOUND
"""
            
            response = model.generate_content(search_prompt)
            result = response.text.strip()
            email = extract_email(result)
            
            if email and 'NOT_FOUND' not in result.upper():
                print(f"  [FOUND] Found email via Gemini: {email}")
                return email
        
        except Exception as e:
            print(f"  [ERROR] Gemini search failed: {e}")
    
    # Strategy 2: Try Google Custom Search API (if configured)
    api_key = os.environ.get("GOOGLE_SEARCH_API_KEY")
    cx = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
    
    if api_key and cx:
        try:
            print(f"  [SEARCH] Trying Google Custom Search API...")
            query = f"{company_name} contact email careers jobs hr"
            search_results = google_search(query)
            
            # Collect URLs to scrape
            urls_to_check = []
            for item in search_results[:5]:
                link = item.get("link", "")
                snippet = item.get("snippet", "")
                
                # Check snippet for email first
                email = extract_email(snippet)
                if email:
                    print(f"  [FOUND] Found email in search snippet: {email}")
                    return email
                
                # Add URL to check list
                if link and ('contact' in link.lower() or 'about' in link.lower() or 'career' in link.lower()):
                    urls_to_check.insert(0, link)
                elif link:
                    urls_to_check.append(link)
            
            # Try scraping collected URLs
            if urls_to_check:
                email = scrape_multiple_urls_for_email(urls_to_check[:3])
                if email:
                    print(f"  [FOUND] Found email from website: {email}")
                    return email
        
        except Exception as e:
            print(f"  [ERROR] Google Search API failed: {e}")
    
    # Strategy 3: Generate common email patterns
    if company_name and company_name != "Freelancer.com Client":
        # Don't generate fallback for platform companies or unknown clients
        platform_indicators = ['client', 'freelancer.com', 'upwork', 'guru', 'fiverr']
        if any(indicator in company_name.lower() for indicator in platform_indicators):
            print(f"  [WARNING] Company '{company_name}' appears to be a platform or unknown client")
            print(f"  [SKIP] Not generating fallback email for platform")
            return None
        
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name).lower()
        
        # Only generate if we have a real company name (minimum 3 chars)
        if len(clean_name) >= 3:
            # Try to extract domain if it's a recognizable company
            common_patterns = [
                f"jobs@{clean_name}.com",
                f"careers@{clean_name}.com",
                f"hr@{clean_name}.com",
                f"recruiting@{clean_name}.com",
                f"contact@{clean_name}.com",
            ]
            
            # Return first pattern as best guess
            fallback = common_patterns[0]
            print(f"  [WARNING] Using fallback email pattern: {fallback}")
            return fallback
    
    return None
