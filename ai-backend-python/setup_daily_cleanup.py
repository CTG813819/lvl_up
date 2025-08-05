#!/usr/bin/env python3
"""
Setup daily cleanup script for proposals
This script sets up a cron job to run daily cleanup of old proposals
"""

import os
import sys
import subprocess
import requests
from datetime import datetime, timedelta

# Backend URL
BACKEND_URL = "http://34.202.215.209:8000"

def setup_daily_cleanup():
    """Set up daily cleanup cron job"""
    try:
        # Create the cleanup script
        cleanup_script = """#!/bin/bash
# Daily cleanup script for AI proposals
# This script runs daily to clean up old proposals

BACKEND_URL="http://34.202.215.209:8000"
LOG_FILE="/var/log/ai-proposal-cleanup.log"

echo "$(date): Starting daily proposal cleanup" >> $LOG_FILE

# Call the cleanup endpoint
curl -X POST "$BACKEND_URL/api/proposals/cleanup-daily" \\
     -H "Content-Type: application/json" \\
     --max-time 300 \\
     --retry 3 \\
     --retry-delay 10 \\
     -o /tmp/cleanup_response.json \\
     -w "HTTP_STATUS:%{http_code}" 2>> $LOG_FILE

# Check if cleanup was successful
if grep -q "HTTP_STATUS:200" /tmp/cleanup_response.json; then
    echo "$(date): Daily cleanup completed successfully" >> $LOG_FILE
    cat /tmp/cleanup_response.json >> $LOG_FILE
else
    echo "$(date): Daily cleanup failed" >> $LOG_FILE
    cat /tmp/cleanup_response.json >> $LOG_FILE
fi

# Clean up temp file
rm -f /tmp/cleanup_response.json

echo "$(date): Daily cleanup script finished" >> $LOG_FILE
"""

        # Write the script to a file
        script_path = "/usr/local/bin/ai-proposal-cleanup.sh"
        with open(script_path, 'w') as f:
            f.write(cleanup_script)
        
        # Make the script executable
        os.chmod(script_path, 0o755)
        
        # Add cron job to run daily at 2 AM
        cron_job = "0 2 * * * /usr/local/bin/ai-proposal-cleanup.sh"
        
        # Check if cron job already exists
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        existing_cron = result.stdout
        
        if cron_job not in existing_cron:
            # Add the new cron job
            if existing_cron.strip():
                new_cron = existing_cron.strip() + "\n" + cron_job
            else:
                new_cron = cron_job
            
            # Write the updated crontab
            subprocess.run(['crontab', '-'], input=new_cron, text=True)
            print("✅ Daily cleanup cron job added successfully")
        else:
            print("ℹ️ Daily cleanup cron job already exists")
        
        # Test the cleanup endpoint
        print("🧪 Testing cleanup endpoint...")
        test_cleanup()
        
        print("✅ Daily cleanup setup completed successfully")
        print(f"📝 Cleanup script: {script_path}")
        print(f"📝 Log file: /var/log/ai-proposal-cleanup.log")
        print("🕐 Cleanup runs daily at 2:00 AM")
        
    except Exception as e:
        print(f"❌ Error setting up daily cleanup: {e}")
        sys.exit(1)

def test_cleanup():
    """Test the cleanup endpoint"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/proposals/cleanup-daily",
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            cleaned_count = result.get('cleaned_count', 0)
            print(f"✅ Cleanup test successful: {cleaned_count} proposals cleaned")
        else:
            print(f"⚠️ Cleanup test returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Cleanup test failed: {e}")

def manual_cleanup():
    """Run manual cleanup"""
    try:
        print("🧹 Running manual cleanup...")
        response = requests.post(
            f"{BACKEND_URL}/api/proposals/cleanup-daily",
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            cleaned_count = result.get('cleaned_count', 0)
            print(f"✅ Manual cleanup completed: {cleaned_count} proposals cleaned")
        else:
            print(f"❌ Manual cleanup failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Manual cleanup error: {e}")

def check_cleanup_status():
    """Check the status of the cleanup system"""
    try:
        # Check if cron job exists
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        cron_jobs = result.stdout
        
        if "ai-proposal-cleanup.sh" in cron_jobs:
            print("✅ Daily cleanup cron job is active")
        else:
            print("❌ Daily cleanup cron job not found")
        
        # Check if log file exists
        log_file = "/var/log/ai-proposal-cleanup.log"
        if os.path.exists(log_file):
            print(f"✅ Cleanup log file exists: {log_file}")
            # Show last few lines
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    print("📝 Last cleanup log entries:")
                    for line in lines[-5:]:
                        print(f"   {line.strip()}")
        else:
            print("⚠️ Cleanup log file not found")
        
        # Test endpoint
        test_cleanup()
        
    except Exception as e:
        print(f"❌ Error checking cleanup status: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "setup":
            setup_daily_cleanup()
        elif command == "test":
            test_cleanup()
        elif command == "manual":
            manual_cleanup()
        elif command == "status":
            check_cleanup_status()
        else:
            print("Usage: python setup_daily_cleanup.py [setup|test|manual|status]")
    else:
        print("Setting up daily cleanup...")
        setup_daily_cleanup() 