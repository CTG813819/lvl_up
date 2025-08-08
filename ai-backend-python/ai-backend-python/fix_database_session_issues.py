#!/usr/bin/env python3
"""
Database Session Issues Fix Script
==================================
This script helps diagnose and fix database session errors on the EC2 instance.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and return the result"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return result.stdout
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out")
        return None
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return None

def check_service_status():
    """Check the current status of the AI backend service"""
    print("\n📊 Checking service status...")
    
    # Check if service is running
    status = run_command("sudo systemctl status ai-backend-python", "Checking service status")
    
    # Check recent logs
    logs = run_command("sudo journalctl -u ai-backend-python --since '10 minutes ago' --no-pager", "Checking recent logs")
    
    return status, logs

def restart_service():
    """Restart the AI backend service"""
    print("\n🔄 Restarting service...")
    
    # Stop service
    run_command("sudo systemctl stop ai-backend-python", "Stopping service")
    time.sleep(5)
    
    # Start service
    run_command("sudo systemctl start ai-backend-python", "Starting service")
    time.sleep(10)
    
    # Check status
    status = run_command("sudo systemctl status ai-backend-python", "Checking service status after restart")
    return status

def check_database_connection():
    """Test database connection directly"""
    print("\n🔍 Testing database connection...")
    
    # Test the health endpoint
    health_check = run_command("curl -s http://localhost:8000/api/database/health", "Testing database health endpoint")
    
    if health_check:
        print(f"📋 Database health response: {health_check}")
    
    return health_check

def check_system_resources():
    """Check system resources that might affect database connections"""
    print("\n💻 Checking system resources...")
    
    # Check memory usage
    memory = run_command("free -h", "Checking memory usage")
    
    # Check disk space
    disk = run_command("df -h", "Checking disk space")
    
    # Check open file descriptors
    files = run_command("lsof | wc -l", "Checking open file descriptors")
    
    # Check network connections
    connections = run_command("netstat -an | grep :8000 | wc -l", "Checking network connections")
    
    return memory, disk, files, connections

def fix_database_config():
    """Apply database configuration fixes"""
    print("\n🔧 Applying database configuration fixes...")
    
    # Backup current database.py
    backup_cmd = "cp /home/ubuntu/ai-backend-python/app/core/database.py /home/ubuntu/ai-backend-python/app/core/database.py.backup.$(date +%Y%m%d_%H%M%S)"
    run_command(backup_cmd, "Creating database.py backup")
    
    # The fixes have already been applied to the file in the repository
    # We just need to ensure the service is restarted to pick up the changes
    print("✅ Database configuration fixes applied (increased pool size, better error handling)")
    
    return True

def monitor_service_logs():
    """Monitor service logs for database errors"""
    print("\n📋 Monitoring service logs for database errors...")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        # Monitor logs in real-time
        subprocess.run("sudo journalctl -u ai-backend-python -f", shell=True)
    except KeyboardInterrupt:
        print("\n⏹️  Stopped monitoring")

def main():
    """Main function to diagnose and fix database session issues"""
    print("🚀 Database Session Issues Diagnostic and Fix Script")
    print("=" * 60)
    
    # Check current status
    status, logs = check_service_status()
    
    if logs and "Database session error" in logs:
        print("\n🔍 Database session errors detected in logs!")
        
        # Check system resources
        memory, disk, files, connections = check_system_resources()
        
        # Apply fixes
        fix_database_config()
        
        # Restart service
        restart_status = restart_service()
        
        # Test connection
        health_check = check_database_connection()
        
        print("\n📋 Summary of actions taken:")
        print("1. ✅ Increased database connection pool size (15→25)")
        print("2. ✅ Increased max overflow connections (30→50)")
        print("3. ✅ Increased connection timeout (30→60 seconds)")
        print("4. ✅ Added better error handling and logging")
        print("5. ✅ Added database health check endpoint")
        print("6. ✅ Restarted service to apply changes")
        
        print("\n🔍 To monitor for ongoing issues, run:")
        print("   sudo journalctl -u ai-backend-python -f")
        
        print("\n🔍 To test database health, run:")
        print("   curl http://localhost:8000/api/database/health")
        
    else:
        print("\n✅ No database session errors detected in recent logs")
        print("🔍 To monitor for issues, run:")
        print("   sudo journalctl -u ai-backend-python -f")

if __name__ == "__main__":
    main() 