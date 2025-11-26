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
import time, random, re
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

def scrape_google_jobs(limit=10, job_type='software'):
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

    print(f"\n🔍 Searching Google Jobs / LinkedIn listings for freelance {job_type} jobs...")

    queries = [
        f"Freelance {job_type} jobs remote",
        f"LinkedIn freelance {job_type}",
        f"Freelance {job_type} hiring",
    ]

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

def scrape_freelancer(limit=10, job_type='software'):
    jobs = []
    print(f"Scraping Freelancer.com for {job_type} jobs...")

    try:
        # Adjust URL based on job type
        if job_type == 'web':
            url = "https://www.freelancer.com/jobs/web-development/"
        elif job_type == 'mobile':
            url = "https://www.freelancer.com/jobs/mobile-app-development/"
        elif job_type == 'data':
            url = "https://www.freelancer.com/jobs/data-entry-analytics/"
        else:
            url = "https://www.freelancer.com/jobs/software-development/"
            
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

def scrape_remoteok(limit=10, job_type='software'):
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

def scrape_guru(limit=10, job_type='software'):
    jobs = []
    print(f"Scraping Guru.com for {job_type} jobs...")

    try:
        # Adjust URL based on job type
        if job_type == 'web':
            url = "https://www.guru.com/d/jobs/skill/web-development/"
        elif job_type == 'mobile':
            url = "https://www.guru.com/d/jobs/skill/mobile-app-development/"
        elif job_type == 'data':
            url = "https://www.guru.com/d/jobs/skill/data-analysis/"
        else:
            url = "https://www.guru.com/d/jobs/skill/software-development/"
            
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

def scrape_linkedin_jobs(limit=10, job_type='software'):
    """Scrape LinkedIn for normal (full-time) software jobs"""
    jobs = []
    print(f"Scraping LinkedIn for {job_type} jobs...")
    
    try:
        # LinkedIn job search URL
        url = f"https://www.linkedin.com/jobs/search/?keywords={job_type}&location=Remote&f_JT=F"
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
                
                # Check if job is related to the specified type
                if is_tech_related(title):
                    jobs.append({
                        "title": title,
                        "company": company,
                        "source": link,
                        "description": f"{title} at {company} - {location}",
                        "platform": "LinkedIn"
                    })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"LinkedIn scraping error: {e}")
    
    print(f"LinkedIn jobs: {len(jobs)}")
    return jobs[:limit]


# ---------------------------------------------------------------------------------------------------------------------
# INDEED JOBS
# ---------------------------------------------------------------------------------------------------------------------

def scrape_indeed_jobs(limit=10, job_type='software'):
    """Scrape Indeed for normal software jobs"""
    jobs = []
    print(f"Scraping Indeed for {job_type} jobs...")
    
    try:
        # Indeed job search URL
        url = f"https://www.indeed.com/jobs?q={job_type}&l=remote"
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
                
                # Check if job is related to the specified type
                if is_tech_related(title):
                    jobs.append({
                        "title": title,
                        "company": company,
                        "source": url,  # Indeed blocks direct links, so using search URL
                        "description": f"{title} at {company} - {location}",
                        "platform": "Indeed"
                    })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Indeed scraping error: {e}")
    
    print(f"Indeed jobs: {len(jobs)}")
    return jobs[:limit]


# ---------------------------------------------------------------------------------------------------------------------
# GLASSDOOR JOBS
# ---------------------------------------------------------------------------------------------------------------------

def scrape_glassdoor_jobs(limit=10, job_type='software'):
    """Scrape Glassdoor for normal software jobs"""
    jobs = []
    print(f"Scraping Glassdoor for {job_type} jobs...")
    
    try:
        # Glassdoor job search URL
        url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={job_type}&locT=C&locId=1147401&locKeyword=Remote&jobType="
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
                
                # Check if job is related to the specified type
                if is_tech_related(title):
                    jobs.append({
                        "title": title,
                        "company": company,
                        "source": link,
                        "description": f"{title} at {company} - {location}",
                        "platform": "Glassdoor"
                    })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Glassdoor scraping error: {e}")
    
    print(f"Glassdoor jobs: {len(jobs)}")
    return jobs[:limit]


# ---------------------------------------------------------------------------------------------------------------------
# GOOGLE NORMAL JOBS
# ---------------------------------------------------------------------------------------------------------------------

def scrape_google_normal_jobs(limit=10, job_type='software'):
    """Scrape Google for normal full-time software jobs"""
    jobs = []
    print(f"Scraping Google for normal {job_type} jobs...")
    
    try:
        # Google job search queries for full-time positions
        queries = [
            f"{job_type} full time remote job",
            f"{job_type} developer full time",
            f"{job_type} position remote full time",
        ]
        
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
                
                # Check if job is related to the specified type
                if is_tech_related(title + desc):
                    jobs.append({
                        "title": title,
                        "company": "Unknown / Google",
                        "source": link,
                        "description": desc,
                        "platform": "Google Search / Normal Jobs"
                    })
                    
    except Exception as e:
        print(f"Google normal jobs scraping error: {e}")
    
    print(f"Google normal jobs: {len(jobs)}")
    return jobs[:limit]


# ---------------------------------------------------------------------------------------------------------------------
# MAIN WRAPPER
# ---------------------------------------------------------------------------------------------------------------------

def scrape_jobs(limit=30, job_type='software', job_category='freelance'):
    """ Scrape jobs based on type and category """
    print(f"\n🚀 Starting {job_category.title()} {job_type.title()} Job Scraping...")

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
        # Pass job_type to each scraper function
        jobs = s(per_site, job_type) if s.__code__.co_argcount > 1 else s(per_site)
        results.extend(jobs)
        time.sleep(random.uniform(1, 3))

    # Remove duplicates
    unique = []
    seen = set()

    for j in results:
        key = j["title"].lower().replace(" ", "")
        if key not in seen:
            unique.append(j)
            seen.add(key)

    print(f"\n✅ TOTAL {job_category.upper()} JOBS COLLECTED: {len(unique)}")
    return unique[:limit]
