#!/usr/bin/env python3
"""
Script to restart the AI backend service and verify it's working
"""

import subprocess
import time
import sys

def restart_service():
    """Restart the AI backend service and verify it's working"""
    
    print("🔄 Restarting AI backend service...")
    
    try:
        # Restart the service
        result = subprocess.run(['sudo', 'systemctl', 'restart', 'ai-backend-python'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Service restarted successfully")
        else:
            print(f"❌ Failed to restart service: {result.stderr}")
            return False
        
        # Wait a moment for the service to start
        print("⏳ Waiting for service to start...")
        time.sleep(5)
        
        # Check service status
        status_result = subprocess.run(['sudo', 'systemctl', 'is-active', 'ai-backend-python'], 
                                     capture_output=True, text=True, timeout=10)
        
        if status_result.returncode == 0 and status_result.stdout.strip() == 'active':
            print("✅ Service is running successfully")
            
            # Check recent logs
            print("📋 Recent service logs:")
            log_result = subprocess.run(['sudo', 'journalctl', '-u', 'ai-backend-python', '-n', '20', '--no-pager'], 
                                      capture_output=True, text=True, timeout=10)
            
            if log_result.returncode == 0:
                print(log_result.stdout)
            else:
                print("⚠️ Could not retrieve logs")
            
            return True
        else:
            print("❌ Service is not running")
            print(f"Status: {status_result.stdout.strip()}")
            
            # Show error logs
            print("📋 Error logs:")
            error_log_result = subprocess.run(['sudo', 'journalctl', '-u', 'ai-backend-python', '-n', '10', '--no-pager'], 
                                            capture_output=True, text=True, timeout=10)
            
            if error_log_result.returncode == 0:
                print(error_log_result.stdout)
            else:
                print("⚠️ Could not retrieve error logs")
            
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = restart_service()
    sys.exit(0 if success else 1)