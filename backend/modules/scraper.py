"""
Advanced Scraper utilities for software/tech jobs.
Supports both freelance and normal (full-time/part-time) positions.

Freelance sources:
 - Freelancer.com
 - RemoteOK
 - Guru.com
 - Upwork
 - Google Job Search (freelance listings)
 
Normal job sources:
 - LinkedIn Jobs
 - Indeed
 - Glassdoor
 - Google Job Search (full-time listings)
"""

import requests
from bs4 import BeautifulSoup
import time, random, re, os
from urllib.parse import urljoin, quote

# ---------------------------------------------------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------------------------------------------------

TECH_KEYWORDS = [
    'software', 'developer', 'programming', 'python', 'javascript', 'java', 'web',
    'frontend', 'backend', 'fullstack', 'mobile', 'app', 'api', 'database', 'devops',
    'react', 'node', 'angular', 'vue', 'django', 'flask', 'machine learning', 'ai',
    'data science', 'cloud', 'aws', 'azure', 'docker', 'kubernetes', 'engineer',
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0",
    "Mozilla/5.0 (Windows NT 10.0; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# ---------------------------------------------------------------------------------------------------------------------
# COMPANY CLASSIFICATION
# ---------------------------------------------------------------------------------------------------------------------

FAANG_COMPANIES = [
    'facebook', 'meta', 'amazon', 'apple', 'netflix', 'google', 'alphabet',
    'microsoft', 'tesla', 'nvidia', 'adobe', 'salesforce', 'oracle', 'ibm', 'intel'
]

BIG_TECH_COMPANIES = [
    'infosys', 'tcs', 'tata consultancy services', 'wipro', 'hcl', 'tech mahindra',
    'accenture', 'capgemini', 'cognizant', 'deloitte', 'pwc', 'kpmg', 'ey',
    'jpmorgan', 'goldman sachs', 'morgan stanley', 'cisco', 'dell', 'hp', 'lenovo',
    'samsung', 'lg', 'sony', 'panasonic', 'siemens', 'ge', 'bosch', 'boeing', 'airbus'
]

def get_company_type(company_name):
    """Classify company into FAANG, Big Tech, or Local"""
    if not company_name or company_name in ["Unknown Company", "Freelancer Client", "Guru Client", "RemoteOK"]:
        return "unknown"
        
    name_lower = company_name.lower()
    
    if any(c in name_lower for c in FAANG_COMPANIES):
        return "faang"
        
    if any(c in name_lower for c in BIG_TECH_COMPANIES):
        return "big_tech"
        
    # Startups/Agencies often have specific keywords
    if any(k in name_lower for k in ['startup', 'technologies', 'solutions', 'labs', 'digital', 'studio', 'agency', 'consulting']):
        return "startup_or_agency"
        
    return "local"

def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

# ---------------------------------------------------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------------------------------------------------

def is_tech_related(text: str, job_type: str = 'software'):
    """Check if text is tech related and matches the job type."""
    if not text:
        return False
    
    t = text.lower()
    
    # Always check for tech keywords
    has_tech_keywords = any(k in t for k in TECH_KEYWORDS)
    
    # If job_type is 'software', we're looking for general software jobs
    # If job_type is more specific, check if it's in the text
    if job_type and job_type != 'software':
        job_type_match = job_type.lower() in t
        return has_tech_keywords and job_type_match
    
    return has_tech_keywords


# ---------------------------------------------------------------------------------------------------------------------
# GOOGLE SEARCH → LINKEDIN JOBS
# ---------------------------------------------------------------------------------------------------------------------

def scrape_google_jobs(limit=10, job_type='software', location=None, job_name=None):
    """
    Searches Google for:
        - "Software Developer Remote"
        - "Freelance Software Work"
        - "LinkedIn freelance developer jobs"
    Extracts:
        - Title
        - Snippet
        - Link (LinkedIn/Direct website)
    """

    print(f"\n[SEARCH] Searching Google Jobs / LinkedIn listings for freelance {job_type} jobs...")

    # Build search queries based on job type, location, and job name
    base_queries = [
        f"Freelance {job_type} jobs remote",
        f"LinkedIn freelance {job_type}",
        f"Freelance {job_type} hiring",
    ]
    
    # Add location to queries if provided
    if location:
        base_queries.extend([
            f"Freelance {job_type} jobs remote {location}",
            f"LinkedIn freelance {job_type} {location}",
        ])
    
    # Add job name to queries if provided
    if job_name:
        name_queries = []
        for q in base_queries:
            name_queries.append(f"{q} {job_name}")
        base_queries.extend(name_queries)
    
    queries = base_queries

    jobs = []

    for q in queries:
        try:
            url = f"https://www.google.com/search?q={quote(q)}&num=20"
            r = requests.get(url, headers=get_headers(), timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")

            results = soup.select("div.g")

            for rblock in results:
                if len(jobs) >= limit:
                    break

                # Title
                title_tag = rblock.find("h3")
                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)

                # URL
                link_tag = rblock.find("a")
                if not link_tag:
                    continue
                link = link_tag.get("href")

                # Snippet
                snippet = rblock.find("span")
                desc = snippet.get_text(strip=True) if snippet else title

                if not is_tech_related(title + desc):
                    continue

                jobs.append({
                    "title": title,
                    "company": "Unknown / Google",
                    "source": link,
                    "description": desc,
                    "platform": "Google Search / LinkedIn"
                })

        except Exception as e:
            print("Google scraping error:", e)

    print(f"Google/LinkedIn Jobs Found: {len(jobs)}")
    return jobs[:limit]


# ---------------------------------------------------------------------------------------------------------------------
# FREELANCER.COM
# ---------------------------------------------------------------------------------------------------------------------

def scrape_freelancer(limit=10, job_type='software', location=None, job_name=None):
    jobs = []
    print(f"Scraping Freelancer.com for {job_type} jobs...")

    try:
        # Adjust URL based on job type
        # Base URL based on job type
        if job_type == 'web':
            base_url = "https://www.freelancer.com/jobs/web-development/"
        elif job_type == 'mobile':
            base_url = "https://www.freelancer.com/jobs/mobile-app-development/"
        elif job_type == 'data':
            base_url = "https://www.freelancer.com/jobs/data-entry-analytics/"
        else:
            base_url = "https://www.freelancer.com/jobs/software-development/"
        
        # Add search parameters if provided
        search_params = []
        if job_name:
            search_params.append(f"search={quote(job_name)}")
        if location:
            search_params.append(f"location={quote(location)}")
        
        # Construct final URL
        if search_params:
            url = f"{base_url}?{'&'.join(search_params)}"
        else:
            url = base_url
            
        r = requests.get(url, headers=get_headers(), timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        cards = soup.find_all("div", class_="JobSearchCard-item")

        for c in cards:
            if len(jobs) >= limit:
                break

            title_tag = c.find("a", class_="JobSearchCard-primary-heading-link")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            desc_tag = c.find("p", class_="JobSearchCard-primary-description")
            desc = desc_tag.get_text(strip=True) if desc_tag else title

            if not is_tech_related(title + desc):
                continue

            jobs.append({
                "title": title,
                "company": "Freelancer Client",
                "source": urljoin(url, title_tag.get("href", "")),
                "description": desc,
                "platform": "Freelancer.com"
            })
    except Exception as e:
        print("Error:", e)

    print("Freelancer jobs:", len(jobs))
    return jobs[:limit]


# ---------------------------------------------------------------------------------------------------------------------
# REMOTEOK API
# ---------------------------------------------------------------------------------------------------------------------

def scrape_remoteok(limit=10, job_type='software', location=None, job_name=None):
    jobs = []
    print(f"Scraping RemoteOK for {job_type} jobs...")

    try:
        url = "https://remoteok.com/api"
        r = requests.get(url, headers=get_headers(), timeout=10)
        data = r.json()[1:]  # Skip metadata item

        for j in data:
            if len(jobs) >= limit:
                break

            title = j.get("position", "")
            if not is_tech_related(title, job_type):
                continue

            jobs.append({
                "title": title,
                "company": j.get("company", "RemoteOK"),
                "source": f"https://remoteok.com{j.get('url','')}",
                "description": ", ".join(j.get("tags", [])[:5]),
                "platform": "RemoteOK"
            })

    except Exception as e:
        print("RemoteOK error:", e)

    print("RemoteOK jobs:", len(jobs))
    return jobs[:limit]


# ---------------------------------------------------------------------------------------------------------------------
# GURU.COM
# ---------------------------------------------------------------------------------------------------------------------

def scrape_guru(limit=10, job_type='software', location=None, job_name=None):
    jobs = []
    print(f"Scraping Guru.com for {job_type} jobs...")

    try:
        # Adjust URL based on job type
        # Base URL based on job type
        if job_type == 'web':
            base_url = "https://www.guru.com/d/jobs/skill/web-development/"
        elif job_type == 'mobile':
            base_url = "https://www.guru.com/d/jobs/skill/mobile-app-development/"
        elif job_type == 'data':
            base_url = "https://www.guru.com/d/jobs/skill/data-analysis/"
        else:
            base_url = "https://www.guru.com/d/jobs/skill/software-development/"
        
        # Add search parameters if provided
        search_params = []
        if job_name:
            search_params.append(f"search={quote(job_name)}")
        if location:
            search_params.append(f"location={quote(location)}")
        
        # Construct final URL
        if search_params:
            url = f"{base_url}?{'&'.join(search_params)}"
        else:
            url = base_url
            
        r = requests.get(url, headers=get_headers(), timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        cards = soup.find_all("div", class_="job-card")

        for c in cards:
            if len(jobs) >= limit:
                break

            title_tag = c.find("a", class_="job-title")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            desc_tag = c.find("div", class_="description")
            desc = desc_tag.get_text(strip=True) if desc_tag else title

            if not is_tech_related(title + desc):
                continue

            jobs.append({
                "title": title,
                "company": "Guru Client",
                "source": urljoin(url, title_tag.get("href", "")),
                "description": desc,
                "platform": "Guru"
            })

    except Exception as e:
        print("Guru error:", e)

    print("Guru jobs:", len(jobs))
    return jobs[:limit]


# ---------------------------------------------------------------------------------------------------------------------
# LINKEDIN JOBS
# ---------------------------------------------------------------------------------------------------------------------

def scrape_linkedin_jobs(limit=10, job_name=None, location=None):
    """Scrape LinkedIn for normal (full-time) jobs"""
    jobs = []
    print(f"Scraping LinkedIn for jobs...")
    
    try:
        # LinkedIn job search URL with job name and location
        params = []
        if job_name:
            params.append(f"keywords={job_name}")
        else:
            params.append("keywords=software developer")
        
        if location:
            params.append(f"location={location}")
        else:
            params.append("location=Remote")
        params.append("f_JT=F")
        
        url = f"https://www.linkedin.com/jobs/search/?{'&'.join(params)}"
        r = requests.get(url, headers=get_headers(), timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Find job cards
        job_cards = soup.find_all("div", class_="base-card", limit=limit*2)
        
        for card in job_cards:
            if len(jobs) >= limit:
                break
                
            try:
                title_elem = card.find("h3", class_="base-search-card__title")
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                
                company_elem = card.find("h4", class_="base-search-card__subtitle")
                company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                
                location_elem = card.find("span", class_="job-search-card__location")
                location = location_elem.get_text(strip=True) if location_elem else "Remote"
                
                link_elem = card.find("a", class_="base-card__link")
                link = link_elem.get("href", "") if link_elem else ""
                
                # For normal jobs, we don't filter by tech keywords since job_name is more specific
                description = f"{title} at {company} - {location}"
                jobs.append({
                    "title": title,
                    "company": company,
                    "source": link,
                    "description": description,
                    "platform": "LinkedIn",
                    "relevance_score": _calculate_relevance_score(title, description, job_name, company, location, location)
                })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"LinkedIn scraping error: {e}")
    
    # Sort jobs by relevance score
    jobs.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    print(f"LinkedIn jobs: {len(jobs)}")
    return jobs[:limit]


# ---------------------------------------------------------------------------------------------------------------------
# INDEED JOBS
# ---------------------------------------------------------------------------------------------------------------------

def scrape_indeed_jobs(limit=10, job_name=None, location=None):
    """Scrape Indeed for normal jobs"""
    jobs = []
    print(f"Scraping Indeed for jobs...")
    
    try:
        # Indeed job search URL with job name and location
        params = []
        if job_name:
            params.append(f"q={job_name}")
        else:
            params.append("q=software developer")
        if location:
            params.append(f"l={location}")
        else:
            params.append("l=remote")
        
        url = f"https://www.indeed.com/jobs?{'&'.join(params)}"
        r = requests.get(url, headers=get_headers(), timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Find job cards
        job_cards = soup.find_all("div", class_="job_seen_beacon", limit=limit*2)
        
        for card in job_cards:
            if len(jobs) >= limit:
                break
                
            try:
                title_elem = card.find("h2", class_="jobTitle")
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                
                company_elem = card.find("span", class_="companyName")
                company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                
                location_elem = card.find("div", class_="companyLocation")
                location = location_elem.get_text(strip=True) if location_elem else "Remote"
                
                # For normal jobs, we don't filter by tech keywords since job_name is more specific
                description = f"{title} at {company} - {location}"
                jobs.append({
                    "title": title,
                    "company": company,
                    "source": url,  # Indeed blocks direct links, so using search URL
                    "description": description,
                    "platform": "Indeed",
                    "relevance_score": _calculate_relevance_score(title, description, job_name, company, location, location)
                })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Indeed scraping error: {e}")
    
    # Sort jobs by relevance score
    jobs.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    print(f"Indeed jobs: {len(jobs)}")
    return jobs[:limit]


# ---------------------------------------------------------------------------------------------------------------------
# GLASSDOOR JOBS
# ---------------------------------------------------------------------------------------------------------------------

def scrape_glassdoor_jobs(limit=10, job_name=None, location=None):
    """Scrape Glassdoor for normal jobs"""
    jobs = []
    print(f"Scraping Glassdoor for jobs...")
    
    try:
        # Glassdoor job search URL with job name and location
        params = []
        if job_name:
            params.append(f"sc.keyword={job_name}")
        else:
            params.append("sc.keyword=software developer")
        
        # Handle location parameter
        if location:
            params.append(f"locKeyword={location}")
        else:
            params.append("locT=C&locId=1147401&locKeyword=Remote")
        params.append("jobType=")
        
        url = f"https://www.glassdoor.com/Job/jobs.htm?{'&'.join(params)}"
        r = requests.get(url, headers=get_headers(), timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Find job listings
        job_listings = soup.find_all("li", class_="react-job-listing", limit=limit*2)
        
        for listing in job_listings:
            if len(jobs) >= limit:
                break
                
            try:
                title_elem = listing.find("a", class_="jobLink")
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                
                company_elem = listing.find("span", class_="employer-name")
                company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                
                location_elem = listing.find("span", class_="location")
                location = location_elem.get_text(strip=True) if location_elem else "Remote"
                
                link_elem = listing.find("a", class_="jobLink")
                link = "https://www.glassdoor.com" + link_elem.get("href", "") if link_elem else ""
                
                # For normal jobs, we don't filter by tech keywords since job_name is more specific
                description = f"{title} at {company} - {location}"
                jobs.append({
                    "title": title,
                    "company": company,
                    "source": link,
                    "description": description,
                    "platform": "Glassdoor",
                    "relevance_score": _calculate_relevance_score(title, description, job_name, company, location, location)
                })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Glassdoor scraping error: {e}")
    
    # Sort jobs by relevance score
    jobs.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    print(f"Glassdoor jobs: {len(jobs)}")
    return jobs[:limit]


# ---------------------------------------------------------------------------------------------------------------------
# GOOGLE NORMAL JOBS
# ---------------------------------------------------------------------------------------------------------------------

def scrape_google_normal_jobs(limit=10, job_name=None, location=None):
    """Scrape Google for normal full-time software jobs"""
    jobs = []
    print(f"Scraping Google for normal jobs...")
    
    try:
        # Google job search queries for full-time positions
        # Build search queries based on job name and location
        base_queries = [
            f"{job_name} full time remote job" if job_name else "software developer full time remote job",
            f"{job_name} developer full time" if job_name else "software developer full time",
            f"{job_name} position remote full time" if job_name else "software position remote full time",
        ]
        
        # Add location to queries if provided
        if location:
            location_queries = []
            for q in base_queries:
                location_queries.append(f"{q} {location}")
            base_queries.extend(location_queries)
        
        queries = base_queries
        
        for q in queries:
            if len(jobs) >= limit:
                break
                
            url = f"https://www.google.com/search?q={quote(q)}&num=20"
            r = requests.get(url, headers=get_headers(), timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            
            results = soup.select("div.g")
            
            for rblock in results:
                if len(jobs) >= limit:
                    break
                    
                # Title
                title_tag = rblock.find("h3")
                if not title_tag:
                    continue
                    
                title = title_tag.get_text(strip=True)
                
                # URL
                link_tag = rblock.find("a")
                if not link_tag:
                    continue
                link = link_tag.get("href")
                
                # Snippet
                snippet = rblock.find("span")
                desc = snippet.get_text(strip=True) if snippet else title
                
                # For normal jobs, we don't filter by tech keywords since job_name is more specific
                # But we should still rank jobs based on relevance to the job_name
                jobs.append({
                    "title": title,
                    "company": "Unknown / Google",
                    "source": link,
                    "description": desc,
                    "platform": "Google Search / Normal Jobs",
                    "relevance_score": _calculate_relevance_score(title, desc, job_name, "Unknown / Google", None, location)
                })
                
    except Exception as e:
        print(f"Google normal jobs scraping error: {e}")
    
    # Sort jobs by relevance score
    jobs.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    print(f"Google normal jobs: {len(jobs)}")
    return jobs[:limit]


def _calculate_relevance_score(title, description, job_name, company=None, job_location=None, user_location=None):
    """
    Calculate relevance score based on:
    1. Location Match (40 points)
    2. Company Type (30 points)
    3. Job Match (30 points)
    """
    score = 0
    
    # 1. Location Score (Max 40)
    if user_location and job_location:
        u_loc = user_location.lower()
        j_loc = job_location.lower()
        
        if u_loc in j_loc or j_loc in u_loc:
            score += 40  # Exact/Close match
        elif "remote" in j_loc:
            score += 15  # Remote is okay but less preferred if prioritizing local
        else:
            score += 5   # Different location
    elif user_location:
        # If user specified location but job has no location, penalize slightly
        score += 10
    else:
        # No location preference
        score += 20
        
    # 2. Company Score (Max 30)
    # Check if we should exclude FAANG
    exclude_faang = os.environ.get('EXCLUDE_FAANG', 'false').lower() == 'true'
    company_priority = os.environ.get('COMPANY_PRIORITY', 'local').lower()
    
    company_type = get_company_type(company)
    
    if company_type == "faang":
        if exclude_faang:
            return -100 # Filter out
        score += 10 # Low priority for FAANG if we want local
    elif company_type == "big_tech":
        score += 15
    elif company_type == "startup_or_agency":
        score += 25
    elif company_type == "local":
        score += 30 # Highest priority for local
    else:
        score += 10 # Unknown
        
    # 3. Job Match Score (Max 30)
    if not job_name:
        score += 15
    else:
        job_name_lower = job_name.lower()
        title_lower = title.lower()
        desc_lower = description.lower()
        
        # Higher weight for exact matches in title
        if job_name_lower in title_lower:
            score += 30
        
        # Medium weight for partial matches in title
        words = job_name_lower.split()
        match_count = sum(1 for word in words if len(word) > 2 and word in title_lower)
        if match_count > 0:
            score += 10 + (match_count * 5)
        
        # Lower weight for matches in description
        if job_name_lower in desc_lower:
            score += 5
            
    return score


# ---------------------------------------------------------------------------------------------------------------------
# MAIN WRAPPER
# ---------------------------------------------------------------------------------------------------------------------

def scrape_jobs(limit=30, job_type='software', job_category='freelance', location=None, job_name=None):
    """ Scrape jobs based on type and category """
    location_str = f" in {location}" if location else ""
    job_name_str = f" for {job_name}" if job_name else ""
    print(f"\n[SCRAPING] Starting {job_category.title()} jobs{job_name_str}{location_str}...")
    
    results = []
    
    if job_category == 'freelance':
        scrapers = [
            scrape_freelancer,
            scrape_remoteok,
            scrape_guru,
            scrape_google_jobs
        ]
    else:  # normal jobs
        scrapers = [
            scrape_linkedin_jobs,
            scrape_indeed_jobs,
            scrape_glassdoor_jobs,
            scrape_google_normal_jobs
        ]
    
    per_site = max(5, limit // len(scrapers))
    
    for s in scrapers:
        try:
            # Pass appropriate arguments based on job category and function signature
            if job_category == 'freelance':
                # Freelance jobs use job_type, location, and job_name
                if 'location' in s.__code__.co_varnames and 'job_name' in s.__code__.co_varnames:
                    jobs = s(per_site, job_type, location, job_name)
                else:
                    jobs = s(per_site, job_type)
            else:
                # Normal jobs only use job_name and location (job_type becomes job_name for normal jobs)
                if 'job_name' in s.__code__.co_varnames and 'location' in s.__code__.co_varnames:
                    # Special case for normal jobs: we pass job_name as the first parameter (instead of job_type)
                    jobs = s(per_site, job_name, location)
                elif 'job_name' in s.__code__.co_varnames:
                    jobs = s(per_site, job_name)
                elif 'location' in s.__code__.co_varnames:
                    jobs = s(per_site, location)
                else:
                    jobs = s(per_site)
            results.extend(jobs)
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"Error scraping with {s.__name__}: {e}")
            continue
    
    # Remove duplicates
    unique = []
    seen = set()
    
    for j in results:
        key = j["title"].lower().replace(" ", "")
        if key not in seen:
            unique.append(j)
            seen.add(key)
    
    # Sort by relevance score for both normal and freelance jobs (if score exists)
    unique.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    # Log top 3 priority jobs
    print("\n[PRIORITY] Top 3 jobs based on scoring:")
    for i, j in enumerate(unique[:3], 1):
        print(f"  {i}. {j['title']} at {j.get('company', 'Unknown')} (Score: {j.get('relevance_score', 0)})")
    
    print(f"\n[TOTAL] TOTAL {job_category.upper()} JOBS COLLECTED: {len(unique)}")
    return unique[:limit]
