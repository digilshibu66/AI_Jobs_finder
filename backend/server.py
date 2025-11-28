from flask import Flask, jsonify, request, send_from_directory
import pandas as pd
import os
from datetime import datetime
import subprocess
import sys
from dotenv import set_key, load_dotenv
import numpy as np

app = Flask(__name__, static_folder='../frontend/dist')

# Path to the Excel log file - FIXED PATH ISSUE
# Use /app/email_log.xlsx as the default path
EXCEL_FILE_PATH = '/app/email_log.xlsx'

# Get the backend directory path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

# Serve static files from the React build
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve the React frontend"""
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

def read_excel_data():
    """Read data from the Excel log file"""
    try:
        print(f"Looking for Excel file at: {EXCEL_FILE_PATH}")
        if os.path.exists(EXCEL_FILE_PATH):
            df = pd.read_excel(EXCEL_FILE_PATH)
            print(f"Found {len(df)} records in Excel file")
            # Handle NaN values by replacing them with empty strings
            df = df.replace({np.nan: ''})
            # Convert DataFrame to list of dictionaries
            data = df.to_dict('records')
            return data
        else:
            print(f"Excel file not found at: {EXCEL_FILE_PATH}")
            return []
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

def get_statistics(logs):
    """Calculate statistics from logs"""
    total = len(logs)
    # Use lowercase 'status' to match the Excel column name
    success = sum(1 for log in logs if log.get('status', '').upper() == 'SUCCESS')
    failed = sum(1 for log in logs if log.get('status', '').upper() == 'FAILED')
    skipped = sum(1 for log in logs if log.get('status', '').upper() == 'SKIPPED')
    dry_run = sum(1 for log in logs if log.get('status', '').upper() == 'DRY_RUN')
    
    return {
        'totalJobs': total,
        'success': success,
        'failed': failed,
        'skipped': skipped,
        'dryRun': dry_run
    }

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get all logs"""
    try:
        logs = read_excel_data()
        return jsonify({
            'success': True,
            'data': logs
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics"""
    try:
        logs = read_excel_data()
        stats = get_statistics(logs)
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/run-jobs', methods=['POST'])
def run_jobs():
    """Run the job processing script"""
    try:
        # Get parameters from request
        data = request.json or {}
        job_category = data.get('jobCategory', 'freelance')
        job_type = data.get('jobType', 'software')
        job_limit = data.get('jobLimit', 30)
        send_emails = data.get('sendEmails', False)
        keywords = data.get('keywords')
        job_field = data.get('jobField')
        generate_motivational_letter = data.get('generateMotivationalLetter', True)
        
        # Build command with correct path
        cmd = [
            sys.executable, 
            os.path.join(BACKEND_DIR, 'main.py'),
            '--job-category', job_category,
            '--job-type', job_type,
            '--job-limit', str(job_limit)
        ]
        
        # Add optional parameters
        if keywords:
            cmd.extend(['--keywords', keywords])
        if job_field:
            cmd.extend(['--job-field', job_field])
        
        if send_emails:
            cmd.append('--send')
            
        if generate_motivational_letter:
            cmd.append('--generate-motivational-letter')
            
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=BACKEND_DIR  # Set working directory to backend
        )
        
        return jsonify({
            'success': True,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Backend is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/run-jobs-modified', methods=['POST'])
def run_jobs_modified():
    """Run the job processing script by modifying .env file first"""
    try:
        # Get parameters from request
        data = request.json or {}
        job_type = data.get('jobType', 'software')
        job_category = data.get('jobCategory', 'freelance')
        job_limit = data.get('jobLimit', 30)
        generate_motivational_letter = data.get('generateMotivationalLetter', True)
        
        # Path to .env file in the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(project_root, '.env')
        
        # Update .env file with new values
        set_key(env_path, 'JOB_TYPE', job_type)
        set_key(env_path, 'JOB_CATEGORY', job_category)
        set_key(env_path, 'JOB_LIMIT', str(job_limit))
        set_key(env_path, 'GENERATE_MOTIVATIONAL_LETTER', str(generate_motivational_letter).lower())
        
        # Reload environment variables
        load_dotenv(env_path, override=True)
        
        # Build command to run main.py WITH correct path
        cmd = [
            sys.executable, 
            os.path.join(BACKEND_DIR, 'main.py')
        ]
        
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=BACKEND_DIR  # Set working directory to backend
        )
        
        return jsonify({
            'success': True,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Serve static files
@app.route('/simple_control.html')
def serve_control_panel():
    """Serve the simple control panel HTML file"""
    try:
        with open('simple_control.html', 'r') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/html'}
    except Exception as e:
        return f'Error loading file: {str(e)}', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)