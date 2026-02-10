"""
Simple CLI to delete activity records from email_log.xlsx

Usage:
    python delete_records.py --all                  # Delete all records
    python delete_records.py --status FAILED        # Delete records by status
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.excel_logger import email_logger
import argparse


def main():
    parser = argparse.ArgumentParser(description='Delete activity records from email_log.xlsx')
    parser.add_argument('--all', action='store_true', help='Delete all records')
    parser.add_argument('--status', type=str, help='Delete records with specific status (e.g., FAILED, SKIPPED)')
    
    args = parser.parse_args()
    
    # Check if at least one option is provided
    if not args.all and not args.status:
        print("❌ Error: Please specify --all or --status")
        parser.print_help()
        return
    
    # Confirm before deleting
    if args.all:
        confirm = input("⚠️  Delete ALL records? This cannot be undone! (yes/no): ")
        if confirm.lower() == 'yes':
            success = email_logger.delete_all_records()
            if success:
                print("✅ All records deleted successfully!")
        else:
            print("❌ Deletion cancelled.")
    
    elif args.status:
        confirm = input(f"⚠️  Delete all records with status '{args.status}'? (yes/no): ")
        if confirm.lower() == 'yes':
            success = email_logger.delete_records_by_status(args.status)
            if success:
                print(f"✅ Records with status '{args.status}' deleted successfully!")
        else:
            print("❌ Deletion cancelled.")


if __name__ == '__main__':
    main()
