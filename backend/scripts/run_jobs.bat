@echo off
REM Batch script to run job searches on Windows

echo Freelance Mailer Package - Job Runner
echo ====================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run both freelance and normal job searches
echo Running both freelance and normal job searches...
python scripts\run_jobs.py --mode both

echo.
echo Job searches completed!
echo Check email_log.xlsx for results
pause