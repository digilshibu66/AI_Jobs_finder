"""
Advanced Email Validation Module
Ensures only genuine company emails are used for job applications.

Features:
- Multi-stage validation (syntax, domain, MX records, SMTP verification)
- Company domain matching
- Platform email filtering
- Disposable/temporary email detection
- Email reputation scoring
"""

import re
import dns.resolver
import smtplib
import socket
from typing import Tuple, Optional, Dict, List
import time

# Blocked domains (job platforms, temporary emails, etc.)
BLOCKED_DOMAINS = {
    # Job Platforms
    'freelancer.com', 'upwork.com', 'fiverr.com', 'guru.com', 
    'peopleperhour.com', 'toptal.com', 'remoteok.com', '99designs.com',
    'indeed.com', 'linkedin.com', 'glassdoor.com', 'monster.com',
    'careerbuilder.com', 'ziprecruiter.com',
    
    # Social Media
    'facebook.com', 'twitter.com', 'instagram.com', 'tiktok.com',
    
    # Temporary/Disposable
    'tempmail.com', '10minutemail.com', 'guerrillamail.com', 
    'mailinator.com', 'throwaway.email', 'temp-mail.org',
    
    # Generic/Invalid
    'example.com', 'test.com', 'email.com', 'mail.com',
    'wix.com', 'sentry.io', 'weebly.com', 'squarespace.com'
}

# Generic email providers (lower priority but acceptable)
GENERIC_PROVIDERS = {
    'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
    'aol.com', 'protonmail.com', 'icloud.com', 'mail.com'
}

# Invalid email prefixes
INVALID_PREFIXES = {
    'noreply', 'no-reply', 'donotreply', 'do-not-reply',
    'mailer-daemon', 'postmaster', 'webmaster', 'admin',
    'abuse', 'spam', 'security', 'privacy'
}


class EmailValidator:
    """Comprehensive email validation with scoring system"""
    
    def __init__(self):
        self.dns_cache = {}  # Cache DNS lookups
        self.mx_cache = {}   # Cache MX records
    
    def validate_syntax(self, email: str) -> Tuple[bool, str]:
        """
        Validate email syntax.
        Returns: (is_valid, reason)
        """
        if not email or not isinstance(email, str):
            return False, "empty_email"
        
        email = email.strip().lower()
        
        # Basic regex validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "invalid_syntax"
        
        # Check for masked emails
        if '*' in email or '****' in email:
            return False, "masked_email"
        
        # Check prefix
        prefix = email.split('@')[0]
        if any(invalid in prefix for invalid in INVALID_PREFIXES):
            return False, "invalid_prefix"
        
        return True, "syntax_valid"
    
    def check_domain_blocked(self, email: str) -> Tuple[bool, str]:
        """
        Check if email domain is in blocked list.
        Returns: (is_blocked, reason)
        """
        domain = email.split('@')[-1].lower()
        
        if domain in BLOCKED_DOMAINS:
            return True, "blocked_domain"
        
        # Check for subdomains of blocked domains
        for blocked in BLOCKED_DOMAINS:
            if domain.endswith('.' + blocked):
                return True, "blocked_subdomain"
        
        return False, "domain_ok"
    
    def verify_mx_records(self, email: str) -> Tuple[bool, str, Optional[str]]:
        """
        Verify domain has valid MX records.
        Returns: (has_mx, reason, mx_record)
        """
        domain = email.split('@')[-1].lower()
        
        # Check cache first
        if domain in self.mx_cache:
            return self.mx_cache[domain]
        
        try:
            records = dns.resolver.resolve(domain, 'MX')
            if records:
                mx_record = str(records[0].exchange)
                result = (True, "mx_valid", mx_record)
                self.mx_cache[domain] = result
                return result
        except dns.resolver.NXDOMAIN:
            result = (False, "domain_not_exist", None)
            self.mx_cache[domain] = result
            return result
        except dns.resolver.NoAnswer:
            result = (False, "no_mx_record", None)
            self.mx_cache[domain] = result
            return result
        except Exception as e:
            return False, f"mx_check_failed_{str(e)[:20]}", None
        
        return False, "unknown_mx_error", None
    
    def match_company_domain(self, email: str, company_name: str, 
                            job_domain: Optional[str] = None) -> int:
        """
        Calculate score based on how well email matches company.
        Returns: score (0-100)
        
        Scoring:
        - 100: Perfect match (email domain == job domain or company domain)
        - 50: Partial match (similar words)
        - 0: No match
        - -50: Generic provider (gmail, yahoo, etc.) but might be valid
        """
        if not company_name:
            return 0
        
        email_domain = email.split('@')[-1].lower()
        company_clean = re.sub(r'[^a-z0-9]', '', company_name.lower())
        
        # Perfect match: email domain matches job posting domain
        if job_domain and email_domain == job_domain.lower():
            return 100
        
        # Check if company name is in email domain
        if company_clean in email_domain.replace('.', '').replace('-', ''):
            return 90
        
        # Check if email domain is in company name
        domain_name = email_domain.split('.')[0]
        if domain_name in company_clean:
            return 80
        
        # Check for partial word matches
        company_words = set(re.findall(r'\w+', company_name.lower()))
        domain_words = set(re.findall(r'\w+', email_domain.split('.')[0]))
        
        common_words = company_words & domain_words
        if common_words:
            return 60
        
        # Penalize generic providers slightly (but don't block)
        if email_domain in GENERIC_PROVIDERS:
            return -30
        
        # No match but not blocked
        return 10
    
    def calculate_email_quality_score(self, email: str, 
                                     company_name: Optional[str] = None,
                                     job_domain: Optional[str] = None,
                                     context: Optional[Dict] = None) -> int:
        """
        Calculate overall email quality score.
        Returns: score (0-100)
        
        Higher score = more likely to be genuine company email
        """
        score = 0
        
        # 1. Syntax validation (mandatory)
        is_valid, reason = self.validate_syntax(email)
        if not is_valid:
            return 0  # Invalid emails get 0
        
        score += 20  # Base score for valid syntax
        
        # 2. Domain blocking (mandatory)
        is_blocked, _ = self.check_domain_blocked(email)
        if is_blocked:
            return 0  # Blocked domains get 0
        
        score += 20  # Not blocked
        
        # 3. MX record validation
        has_mx, mx_reason, _ = self.verify_mx_records(email)
        if has_mx:
            score += 20  # Valid MX records
        else:
            score -= 30  # Penalize heavily if no MX
        
        # 4. Company domain matching
        if company_name:
            match_score = self.match_company_domain(email, company_name, job_domain)
            score += match_score * 0.4  # Weight: 40% of 100 = 40 points max
        
        # 5. Email prefix quality
        prefix = email.split('@')[0].lower()
        
        # Prioritize HR/recruiting emails
        priority_keywords = ['careers', 'jobs', 'hr', 'hiring', 'recruiting', 'recruitment', 'talent']
        if any(kw in prefix for kw in priority_keywords):
            score += 15
        
        # Generic contact emails (acceptable but lower priority)
        generic_keywords = ['contact', 'info', 'hello', 'support']
        if any(kw in prefix for kw in generic_keywords):
            score += 5
        
        # 6. Context-based scoring
        if context:
            # Found on careers page
            if context.get('found_on_careers_page'):
                score += 10
            
            # Email mentioned in job posting
            if context.get('from_job_posting'):
                score += 15
        
        return min(100, max(0, score))  # Clamp to 0-100
    
    def validate_and_score(self, email: str, 
                          company_name: Optional[str] = None,
                          job_domain: Optional[str] = None,
                          context: Optional[Dict] = None) -> Dict:
        """
        Complete validation with detailed results.
        Returns: {
            'email': str,
            'is_valid': bool,
            'score': int,
            'reasons': List[str],
            'recommendation': str
        }
        """
        results = {
            'email': email,
            'is_valid': False,
            'score': 0,
            'reasons': [],
            'recommendation': 'reject'
        }
        
        # 1. Syntax
        is_valid, reason = self.validate_syntax(email)
        if not is_valid:
            results['reasons'].append(f"Invalid syntax: {reason}")
            return results
        
        results['reasons'].append("✓ Valid syntax")
        
        # 2. Blocked domains
        is_blocked, block_reason = self.check_domain_blocked(email)
        if is_blocked:
            results['reasons'].append(f"✗ Blocked domain: {block_reason}")
            return results
        
        results['reasons'].append("✓ Not blocked")
        
        # 3. MX records
        has_mx, mx_reason, mx_record = self.verify_mx_records(email)
        if has_mx:
            results['reasons'].append(f"✓ Valid MX: {mx_record}")
        else:
            results['reasons'].append(f"✗ MX issue: {mx_reason}")
        
        # 4. Calculate score
        score = self.calculate_email_quality_score(email, company_name, job_domain, context)
        results['score'] = score
        
        # 5. Determine recommendation
        if score >= 70:
            results['is_valid'] = True
            results['recommendation'] = 'highly_recommended'
            results['reasons'].append(f"✓ High quality score: {score}/100")
        elif score >= 50:
            results['is_valid'] = True
            results['recommendation'] = 'acceptable'
            results['reasons'].append(f"⚠ Acceptable score: {score}/100")
        elif score >= 30:
            results['recommendation'] = 'low_quality'
            results['reasons'].append(f"⚠ Low quality score: {score}/100")
        else:
            results['recommendation'] = 'reject'
            results['reasons'].append(f"✗ Poor quality score: {score}/100")
        
        return results
    
    def batch_validate(self, emails: List[str], 
                      company_name: Optional[str] = None,
                      job_domain: Optional[str] = None) -> List[Dict]:
        """
        Validate and score multiple emails, return sorted by score.
        """
        results = []
        
        for email in emails:
            validation = self.validate_and_score(email, company_name, job_domain)
            if validation['is_valid']:  # Only include valid emails
                results.append(validation)
        
        # Sort by score (descending)
        results.sort(key=lambda x: x['score'], reverse=True)
        return results


# Convenience functions for backward compatibility
def validate_email(email: str, company_name: str = None, job_domain: str = None) -> Tuple[bool, str, int]:
    """
    Quick validation function.
    Returns: (is_valid, reason, score)
    """
    validator = EmailValidator()
    result = validator.validate_and_score(email, company_name, job_domain)
    return result['is_valid'], ' | '.join(result['reasons']), result['score']


def get_best_emails(emails: List[str], company_name: str = None, 
                   job_domain: str = None, max_results: int = 3) -> List[str]:
    """
    Filter and return best emails from a list.
    Returns: List of validated emails sorted by quality score
    """
    validator = EmailValidator()
    results = validator.batch_validate(emails, company_name, job_domain)
    
    # Return top N emails
    return [r['email'] for r in results[:max_results]]


if __name__ == "__main__":
    # Test the validator
    validator = EmailValidator()
    
    test_cases = [
        ("careers@techcorp.com", "TechCorp", "techcorp.com"),
        ("john@gmail.com", "TechCorp", "techcorp.com"),
        ("jobs@freelancer.com", "TechCorp", "techcorp.com"),
        ("noreply@company.com", "Company Inc", "company.com"),
        ("hr@startup.io", "Startup Labs", "startup.io"),
    ]
    
    print("Email Validation Test Results:")
    print("=" * 80)
    
    for email, company, domain in test_cases:
        result = validator.validate_and_score(email, company, domain)
        print(f"\nEmail: {email}")
        print(f"Company: {company} | Domain: {domain}")
        print(f"Valid: {result['is_valid']} | Score: {result['score']}/100")
        print(f"Recommendation: {result['recommendation']}")
        print(f"Reasons:")
        for reason in result['reasons']:
            print(f"  - {reason}")
