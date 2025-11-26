#!/usr/bin/env python3
"""
Main entry point for the Freelance Mailer Package.
"""

import subprocess
import sys
import os

def main():
    # Change to src directory and run main.py
    src_dir = os.path.join(os.path.dirname(__file__), 'src')
    
    # Build command
    cmd = [sys.executable, os.path.join(src_dir, 'main.py')] + sys.argv[1:]
    
    # Run the command
    try:
        result = subprocess.run(cmd, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

if __name__ == '__main__':
    main()