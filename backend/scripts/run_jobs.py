#!/usr/bin/env python3
"""
Script to run job searches for both freelance and normal positions.
"""

import subprocess
import sys
import argparse
import os
from datetime import datetime

def run_job_search(job_category, job_type='software', job_limit=30):
    """Run job search for specified category and type."""
    print(f"\n{'='*60}")
    print(f"Running {job_category.upper()} job search for '{job_type}' jobs")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # Build command - run from src directory
    cmd = [
        sys.executable, os.path.join('src', 'main.py'),
        '--job-category', job_category,
        '--job-type', job_type,
        '--job-limit', str(job_limit)
    ]
    
    # Run the command
    try:
        result = subprocess.run(cmd, check=True, text=True, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error running job search: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Run job searches')
    parser.add_argument('--job-type', default='software', 
                       help='Job type to search for (default: software)')
    parser.add_argument('--job-limit', type=int, default=30,
                       help='Number of jobs to process (default: 30)')
    parser.add_argument('--mode', choices=['both', 'freelance', 'normal'], 
                       default='both',
                       help='Which job categories to search (default: both)')
    
    args = parser.parse_args()
    
    print("Freelance Mailer Package - Job Runner")
    print(f"Job Type: {args.job_type}")
    print(f"Job Limit: {args.job_limit}")
    print(f"Mode: {args.mode}")
    
    success_count = 0
    
    if args.mode in ['both', 'freelance']:
        if run_job_search('freelance', args.job_type, args.job_limit):
            success_count += 1
            
    if args.mode in ['both', 'normal']:
        if run_job_search('normal', args.job_type, args.job_limit):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"Completed! Successfully ran {success_count} job search(es)")
    print(f"Check email_log.xlsx for results")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()