from flask import Flask, jsonify, request, send_from_directory, Response
import pandas as pd
import os
from datetime import datetime
import subprocess
import sys
from dotenv import set_key, load_dotenv
import numpy as np
import threading
import queue
import json

app = Flask(__name__, static_folder='../frontend/dist')

# Path to the Excel log file (in backend directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE_PATH = os.path.join(BACKEND_DIR, 'email_log.xlsx')

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
    """Get logs with optional filtering via query parameters"""
    try:
        logs = read_excel_data()
        
        # Get filter parameters from query string
        status = request.args.get('status', '').strip()
        platform = request.args.get('platform', '').strip()
        date = request.args.get('date', '').strip()
        search = request.args.get('search', '').strip().lower()
        
        # Apply filters if provided
        filtered_logs = []
        for log in logs:
            # Normalize field names
            log_status = str(log.get('status', log.get('Status', ''))).upper()
            log_platform = str(log.get('platform', log.get('Platform', '')))
            log_timestamp = str(log.get('timestamp', log.get('Timestamp', '')))
            log_title = str(log.get('job_title', log.get('Job Title', ''))).lower()
            log_company = str(log.get('company', log.get('Company', ''))).lower()
            log_email = str(log.get('to_email', log.get('To Email', ''))).lower()
            
            # Status filter
            if status and log_status != status.upper():
                continue
            
            # Platform filter
            if platform and log_platform != platform:
                continue
            
            # Date filter (compare date part only)
            if date:
                try:
                    from datetime import datetime
                    log_date = datetime.fromisoformat(log_timestamp.replace('Z', '+00:00'))
                    if log_date.strftime('%Y-%m-%d') != date:
                        continue
                except:
                    continue
            
            # Search filter
            if search and not (search in log_title or search in log_company or search in log_email):
                continue
            
            filtered_logs.append(log)
        
        return jsonify({
            'success': True,
            'data': filtered_logs,
            'total': len(logs),
            'filtered': len(filtered_logs)
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

@app.route('/api/logs/filters', methods=['GET'])
def get_log_filters():
    """Get unique filter options from logs"""
    try:
        logs = read_excel_data()
        
        statuses = set()
        platforms = set()
        dates = set()
        
        for log in logs:
            # Get status
            status = str(log.get('status', log.get('Status', ''))).strip()
            if status:
                statuses.add(status.upper())
            
            # Get platform
            platform = str(log.get('platform', log.get('Platform', ''))).strip()
            if platform:
                platforms.add(platform)
            
            # Get date
            timestamp = str(log.get('timestamp', log.get('Timestamp', ''))).strip()
            if timestamp:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    dates.add(dt.strftime('%Y-%m-%d'))
                except:
                    pass
        
        return jsonify({
            'success': True,
            'statuses': sorted(list(statuses)),
            'platforms': sorted(list(platforms)),
            'dates': sorted(list(dates), reverse=True)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/run-jobs', methods=['POST'])
def run_jobs():
    """Run the job processing script with live streaming output"""
    try:
        # Get parameters from request
        data = request.json or {}
        job_category = data.get('jobCategory', 'freelance')
        job_type = data.get('jobType', 'software')
        job_limit = data.get('jobLimit', 30)
        send_emails = data.get('sendEmails', False)
        generate_motivational_letter = data.get('generateMotivationalLetter', True)
        ai_model = data.get('aiModel', 'meta-llama/llama-3.3-70b-instruct:free')
        location = data.get('location')
        job_name = data.get('jobName')
        
        # Build command
        cmd = [
            sys.executable, '-u',  # -u for unbuffered output
            os.path.join(BACKEND_DIR, 'main.py'),
            '--job-category', job_category,
            '--job-type', job_type,
            '--job-limit', str(job_limit)
        ]
        
        if send_emails:
            cmd.append('--send')
            
        if generate_motivational_letter:
            cmd.append('--generate-motivational-letter')
            
        cmd.extend(['--ai-model', ai_model])
        
        if location:
            cmd.extend(['--location', location])
        if job_name:
            cmd.extend(['--job-name', job_name])
        
        # Run synchronously and capture output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=BACKEND_DIR,
            bufsize=1
        )
        
        # Collect all output
        output_lines = []
        for line in process.stdout:
            output_lines.append(line)
        
        process.wait()
        
        return jsonify({
            'success': True,
            'output': ''.join(output_lines),
            'returncode': process.returncode
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/run-jobs-stream', methods=['POST'])
def run_jobs_stream():
    """Run jobs with Server-Sent Events for live streaming"""
    data = request.json or {}
    
    def generate():
        job_category = data.get('jobCategory', 'freelance')
        job_type = data.get('jobType', 'software')
        job_limit = data.get('jobLimit', 30)
        send_emails = data.get('sendEmails', False)
        generate_motivational_letter = data.get('generateMotivationalLetter', True)
        ai_model = data.get('aiModel', 'meta-llama/llama-3.3-70b-instruct:free')
        location = data.get('location')
        job_name = data.get('jobName')
        
        # Build command
        cmd = [
            sys.executable, '-u',
            os.path.join(BACKEND_DIR, 'main.py'),
            '--job-category', job_category,
            '--job-type', job_type,
            '--job-limit', str(job_limit)
        ]
        
        if send_emails:
            cmd.append('--send')
        if generate_motivational_letter:
            cmd.append('--generate-motivational-letter')
        cmd.extend(['--ai-model', ai_model])
        if location:
            cmd.extend(['--location', location])
        if job_name:
            cmd.extend(['--job-name', job_name])
        
        yield 'data: ' + json.dumps({'type': 'start', 'message': 'Starting job search...'}) + '\n\n'
        cmd_str = ' '.join(cmd)
        yield 'data: ' + json.dumps({'type': 'info', 'message': 'Command: ' + cmd_str}) + '\n\n'
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=BACKEND_DIR,
                bufsize=1
            )
            
            for line in process.stdout:
                yield 'data: ' + json.dumps({'type': 'log', 'message': line.strip()}) + '\n\n'
            
            process.wait()
            
            if process.returncode == 0:
                yield 'data: ' + json.dumps({'type': 'complete', 'message': 'Job processing completed successfully!'}) + '\n\n'
            else:
                yield 'data: ' + json.dumps({'type': 'error', 'message': 'Process exited with code ' + str(process.returncode)}) + '\n\n'
                
        except Exception as e:
            yield 'data: ' + json.dumps({'type': 'error', 'message': str(e)}) + '\n\n'
    
    return Response(generate(), mimetype='text/event-stream')

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
        ai_model = data.get('aiModel', 'meta-llama/llama-3.3-70b-instruct:free')
        location = data.get('location')
        job_name = data.get('jobName')
        
        # Path to .env file in the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(project_root, '.env')
        
        # Update .env file with new values
        set_key(env_path, 'JOB_TYPE', job_type)
        set_key(env_path, 'JOB_CATEGORY', job_category)
        set_key(env_path, 'JOB_LIMIT', str(job_limit))
        set_key(env_path, 'GENERATE_MOTIVATIONAL_LETTER', str(generate_motivational_letter).lower())
        set_key(env_path, 'AI_MODEL', ai_model)
        if location:
            set_key(env_path, 'LOCATION', location)
        if job_name:
            set_key(env_path, 'JOB_NAME', job_name)
        
        # Reload environment variables
        load_dotenv(env_path, override=True)
        
        # Build command to run main.py WITH correct path
        cmd = [
            sys.executable, 
            os.path.join(BACKEND_DIR, 'main.py'),
            '--job-category', job_category,
            '--job-type', job_type,
            '--job-limit', str(job_limit),
            '--ai-model', ai_model
        ]
        
        # Add location and job name parameters
        if location:
            cmd.extend(['--location', location])
        if job_name:
            cmd.extend(['--job-name', job_name])
            
        # Add other flags
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


# Delete records endpoint
@app.route('/api/logs/delete', methods=['POST'])
def delete_logs():
    """Delete records from Excel log"""
    try:
        data = request.json or {}
        delete_all = data.get('deleteAll', False)
        status_filter = data.get('status', None)
        
        # Import email_logger
        sys.path.insert(0, BACKEND_DIR)
        from modules.excel_logger import email_logger
        
        if delete_all:
            # Delete all records
            success = email_logger.delete_all_records()
            if success:
                return jsonify({
                    'success': True,
                    'message': 'All records deleted successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to delete records'
                }), 500
                
        elif status_filter:
            # Delete by status
            success = email_logger.delete_records_by_status(status_filter)
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Records with status "{status_filter}" deleted successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'No records found with status "{status_filter}"'
                }), 404
        else:
            return jsonify({
                'success': False,
                'message': 'Please specify deleteAll or status parameter'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)