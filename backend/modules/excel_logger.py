"""Excel logger for tracking all email sending activities and scraped jobs."""
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
import hashlib

class EmailLogger:
    def __init__(self, log_file_path=None):
        # Use a consistent path for the Excel file
        if log_file_path is None:
            # Use a relative path from the project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.log_file_path = os.path.join(project_root, 'email_log.xlsx')
        else:
            self.log_file_path = log_file_path
            
        self.columns = [
            "timestamp",
            "job_title",
            "company",
            "to_email",
            "subject",
            "body",
            "status",
            "error_message",
            "source_url",
            "job_hash",  # Unique hash for each job to detect duplicates
            "email_sent"  # Track if email was sent for this job
        ]
        self._initialize_log_file()

    def _initialize_log_file(self):
        """Create the Excel file with headers if it doesn't exist."""
        try:
            # Ensure the directory exists
            log_dir = os.path.dirname(self.log_file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            if not os.path.exists(self.log_file_path):
                df = pd.DataFrame(columns=self.columns)
                df.to_excel(self.log_file_path, index=False, engine='openpyxl')
                print(f"Created new Excel log file at: {self.log_file_path}")
            else:
                print(f"Excel log file already exists at: {self.log_file_path}")
        except PermissionError:
            print(f"Permission denied: Cannot create {self.log_file_path}. Please check file permissions.")
        except Exception as e:
            print(f"Error initializing log file: {e}")

    def _generate_job_hash(self, job_data):
        """Generate a unique hash for a job based on its title, company, and source URL."""
        job_str = f"{job_data.get('title', '')}_{job_data.get('company', '')}_{job_data.get('url', '')}"
        return hashlib.md5(job_str.encode('utf-8')).hexdigest()

    def is_job_processed(self, job_data):
        """Check if a job has already been processed."""
        if not os.path.exists(self.log_file_path):
            return False
            
        try:
            job_hash = self._generate_job_hash(job_data)
            df = pd.read_excel(self.log_file_path, engine='openpyxl')
            
            # Check if 'job_hash' column exists (for backward compatibility)
            if 'job_hash' in df.columns:
                return job_hash in df['job_hash'].values
            return False
        except Exception as e:
            print(f"Error checking if job is processed: {e}")
            return False

    def _clean_text(self, text):
        """Clean text to handle encoding issues and masked content."""
        if not isinstance(text, str):
            return text
            
        # Fix encoding issues (mojibake)
        try:
            # Try to fix common encoding errors
            if "Ã" in text or "Â" in text:  # Common signs of UTF-8 decoded as Latin-1
                try:
                    text = text.encode('latin-1').decode('utf-8')
                except:
                    pass
        except:
            pass
            
        return text

    def log_job(self, job_data, email_sent=False, status="scraped", error_message=""):
        """Log a scraped job to the Excel file.
        
        Args:
            job_data: Dictionary containing job details
            email_sent: Boolean indicating if email was sent for this job
            status: Status of the job processing
            error_message: Any error message if processing failed
        """
        try:
            # Read existing data
            if os.path.exists(self.log_file_path):
                df = pd.read_excel(self.log_file_path, engine='openpyxl')
            else:
                df = pd.DataFrame(columns=self.columns)
            
            # Generate job hash
            job_hash = self._generate_job_hash(job_data)
            
            # Clean data fields
            title = self._clean_text(job_data.get('title', ''))
            company = self._clean_text(job_data.get('company', ''))
            email = self._clean_text(job_data.get('email', ''))
            subject = self._clean_text(job_data.get('subject', ''))
            body = self._clean_text(job_data.get('body', ''))
            error = self._clean_text(str(error_message)) if error_message else ""
            
            # Check if job already exists
            if 'job_hash' in df.columns and job_hash in df['job_hash'].values:
                # Update existing entry if needed
                mask = df['job_hash'] == job_hash
                if email_sent and not df.loc[mask, 'email_sent'].iloc[0]:
                    df.loc[mask, 'email_sent'] = True
                    df.loc[mask, 'status'] = status
                    df.loc[mask, 'timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if error:
                        df['error_message'] = df['error_message'].astype(object)
                        df.loc[mask, 'error_message'] = error
            else:
                # Create new entry
                new_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "job_title": title,
                    "company": company,
                    "to_email": email,
                    "subject": subject,
                    "body": body,
                    "status": status,
                    "error_message": error,
                    "source_url": job_data.get('url', ''),
                    "job_hash": job_hash,
                    "email_sent": email_sent
                }
                
                # Append new entry
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            
            # Save to Excel
            self._safe_write_to_excel(df)
            print(f"Logged job: {title} at {company}")
            
        except Exception as e:
            print(f"Failed to log job: {e}")

    def log_email(self, job_data, to_email, subject, body, status, error_message="", source_url=""):
        """Log email sending activity to Excel file."""
        try:
            # Add email fields to job data
            job_data = job_data.copy()
            job_data['email'] = to_email
            job_data['subject'] = subject
            job_data['body'] = body
            job_data['url'] = source_url
            
            # Log as a job with email sent
            self.log_job(job_data, email_sent=True, status=status, error_message=error_message)
            print(f"Logged email to {to_email} in {self.log_file_path}")
        except Exception as e:
            print(f"Failed to log email: {e}")

    def _safe_write_to_excel(self, df):
        """Safely write to Excel with retry mechanism."""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                df.to_excel(self.log_file_path, index=False, engine='openpyxl')
                print(f"Successfully wrote {len(df)} records to Excel file")
                return
            except PermissionError:
                if attempt < max_attempts - 1:
                    print(f"Attempt {attempt + 1}: Permission denied writing to {self.log_file_path}. Retrying...")
                    import time
                    time.sleep(2)  # Wait before retry
                else:
                    print(f"Permission denied: Cannot write to {self.log_file_path}. Please check if the file is open in another application.")
            except Exception as e:
                print(f"Error writing to Excel: {e}")
                break

    def delete_all_records(self):
        """Delete all records from the Excel log file."""
        try:
            # Create empty DataFrame with columns
            df = pd.DataFrame(columns=self.columns)
            
            # Write to Excel
            self._safe_write_to_excel(df)
            print(f"✅ All records deleted from {self.log_file_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to delete records: {e}")
            return False
    
    def delete_records_by_status(self, status):
        """Delete records with a specific status.
        
        Args:
            status: Status to filter (e.g., 'FAILED', 'SKIPPED', 'DRY_RUN')
        """
        try:
            if not os.path.exists(self.log_file_path):
                print(f"Log file does not exist: {self.log_file_path}")
                return False
            
            # Read existing data
            df = pd.read_excel(self.log_file_path, engine='openpyxl')
            initial_count = len(df)
            
            # Filter out records with the specified status
            df = df[df['status'].str.upper() != status.upper()]
            deleted_count = initial_count - len(df)
            
            if deleted_count > 0:
                # Save filtered data
                self._safe_write_to_excel(df)
                print(f"✅ Deleted {deleted_count} records with status '{status}'")
                return True
            else:
                print(f"No records found with status '{status}'")
                return False
        except Exception as e:
            print(f"❌ Failed to delete records: {e}")
            return False


# Global instance
email_logger = EmailLogger()