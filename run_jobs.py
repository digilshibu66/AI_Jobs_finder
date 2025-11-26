#!/usr/bin/env python3
"""
Simple script to run job searches from the root directory.
"""

import subprocess
import sys
import os

def main():
    # Run the script in the scripts directory
    scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
    script_path = os.path.join(scripts_dir, 'run_jobs.py')
    
    # Build command
    cmd = [sys.executable, script_path] + sys.argv[1:]
    
    # Run the command
    try:
        result = subprocess.run(cmd, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

if __name__ == '__main__':
    main()