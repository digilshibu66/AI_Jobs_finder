#!/bin/bash

# Shell script to run job searches on Unix/Linux/Mac

echo "Freelance Mailer Package - Job Runner"
echo "===================================="

# Check if Python is available
if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Run both freelance and normal job searches
echo "Running both freelance and normal job searches..."
python3 scripts/run_jobs.py --mode both

echo ""
echo "Job searches completed!"
echo "Check email_log.xlsx for results"