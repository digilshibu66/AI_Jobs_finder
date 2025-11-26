"""Excel logger for tracking all email sending activities."""
import os
import pandas as pd
from datetime import datetime
from pathlib import Path


class EmailLogger:
    def __init__(self, log_file_path="email_log.xlsx"):
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
            "source_url"
        ]
        self._initialize_log_file()

    def _initialize_log_file(self):
        """Create the Excel file with headers if it doesn't exist."""
        try:
            if not os.path.exists(self.log_file_path):
                df = pd.DataFrame(columns=self.columns)
                df.to_excel(self.log_file_path, index=False, engine='openpyxl')
        except PermissionError:
            print(f"Permission denied: Cannot create {self.log_file_path}. Please check file permissions.")
        except Exception as e:
            print(f"Error initializing log file: {e}")

    def log_email(self, job_data, to_email, subject, body, status, error_message="", source_url=""):
        """Log email sending activity to Excel file."""
        try:
            # Read existing data
            if os.path.exists(self.log_file_path):
                existing_df = pd.read_excel(self.log_file_path, engine='openpyxl')
            else:
                existing_df = pd.DataFrame(columns=self.columns)
            
            # Create new entry
            new_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "job_title": job_data.get('title', ''),
                "company": job_data.get('company', ''),
                "to_email": to_email,
                "subject": subject,
                "body": body,
                "status": status,
                "error_message": error_message,
                "source_url": source_url
            }
            
            # Append new entry
            new_df = pd.DataFrame([new_entry])
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            
            # Save to Excel with a retry mechanism
            self._safe_write_to_excel(updated_df)
            
            print(f"Logged email to {to_email} in {self.log_file_path}")
        except Exception as e:
            print(f"Failed to log email: {e}")

    def _safe_write_to_excel(self, df):
        """Safely write to Excel with retry mechanism."""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                df.to_excel(self.log_file_path, index=False, engine='openpyxl')
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


# Global instance
email_logger = EmailLogger()