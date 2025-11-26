"""
Advanced Scraper utilities for software/tech freelancing jobs.
Now includes:
 - Freelancer.com
 - RemoteOK
 - Guru.com
 - Upwork
 - Google Job Search (software jobs + LinkedIn job listings)
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

def is_tech_related(text: str):
    if not text:
        return False
    t = text.lower()
    return any(k in t for k in TECH_KEYWORDS)


# ---------------------------------------------------------------------------------------------------------------------
# GOOGLE SEARCH → LINKEDIN JOBS
# ---------------------------------------------------------------------------------------------------------------------

def scrape_google_jobs(limit=10):
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

    print("\n🔍 Searching Google Jobs / LinkedIn listings...")

    queries = [
        "Freelance software developer jobs remote",
        "LinkedIn freelance python developer",
        "Freelance web developer hiring",
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

def scrape_freelancer(limit=10):
    jobs = []
    print("Scraping Freelancer.com...")

    try:
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

def scrape_remoteok(limit=10):
    jobs = []
    print("Scraping RemoteOK...")

    try:
        url = "https://remoteok.com/api"
        r = requests.get(url, headers=get_headers(), timeout=10)
        data = r.json()[1:]  # Skip metadata item

        for j in data:
            if len(jobs) >= limit:
                break

            title = j.get("position", "")
            if not is_tech_related(title):
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

def scrape_guru(limit=10):
    jobs = []
    print("Scraping Guru.com...")

    try:
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
# MAIN WRAPPER
# ---------------------------------------------------------------------------------------------------------------------

def scrape_jobs(limit=25):
    """ Scrape from all platforms """
    print("\n🚀 Starting Full Software Job Scraping...")

    results = []

    scrapers = [
        scrape_freelancer,
        scrape_remoteok,
        scrape_guru,
        scrape_google_jobs
    ]

    per_site = max(5, limit // len(scrapers))

    for s in scrapers:
        jobs = s(per_site)
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

    print(f"\n✅ TOTAL JOBS COLLECTED: {len(unique)}")
    return unique[:limit]
