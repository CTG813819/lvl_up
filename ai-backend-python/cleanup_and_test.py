#!/usr/bin/env python3
"""
Cleanup and Test Script
=======================

This script will:
1. Kill all duplicate uvicorn processes
2. Test the correct health endpoint
3. Verify the backend is working properly
"""

import subprocess
import time
import json
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        logger.error(f"Error running command '{command}': {e}")
        return -1, "", str(e)

def kill_duplicate_processes():
    """Kill all uvicorn processes except the one managed by systemd"""
    logger.info("🔪 Killing duplicate uvicorn processes...")
    
    # Get all uvicorn processes
    code, output, error = run_command("ps aux | grep uvicorn | grep -v grep")
    if code == 0 and output.strip():
        lines = output.strip().split('\n')
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                pid = parts[1]
                cmd = ' '.join(parts[10:])
                
                # Only kill processes that are not managed by systemd (no --workers flag)
                if 'uvicorn' in cmd and '--workers' not in cmd:
                    logger.info(f"Killing process {pid}: {cmd}")
                    run_command(f"kill -9 {pid}")
                    time.sleep(1)
    
    logger.info("✅ Duplicate processes killed")

def test_backend():
    """Test the backend endpoints"""
    logger.info("🧪 Testing backend endpoints...")
    
    # Test the correct health endpoint
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            logger.info(f"✅ Health endpoint working: {health_data}")
        else:
            logger.error(f"❌ Health endpoint failed: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"❌ Health endpoint error: {e}")
    
    # Test the status endpoint
    try:
        response = requests.get("http://localhost:8000/api/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            logger.info(f"✅ Status endpoint working: {status_data}")
        else:
            logger.error(f"❌ Status endpoint failed: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"❌ Status endpoint error: {e}")
    
    # Test the root endpoint
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ Root endpoint working: {response.text[:100]}...")
        else:
            logger.error(f"❌ Root endpoint failed: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"❌ Root endpoint error: {e}")

def check_service_status():
    """Check the systemd service status"""
    logger.info("🔍 Checking service status...")
    
    code, output, error = run_command("sudo systemctl status ai-backend-python.service")
    if code == 0:
        logger.info("✅ Service status:")
        for line in output.split('\n')[:10]:  # Show first 10 lines
            if line.strip():
                logger.info(f"  {line}")
    else:
        logger.error(f"❌ Service status check failed: {error}")

def check_processes():
    """Check running processes"""
    logger.info("🔍 Checking running processes...")
    
    code, output, error = run_command("ps aux | grep python | grep -v grep")
    if code == 0:
        logger.info("✅ Running Python processes:")
        for line in output.split('\n'):
            if line.strip():
                logger.info(f"  {line}")
    else:
        logger.info("No Python processes found")

def main():
    """Main cleanup and test function"""
    logger.info("🚀 Starting cleanup and test...")
    
    # Kill duplicate processes
    kill_duplicate_processes()
    
    # Wait a moment for processes to settle
    time.sleep(2)
    
    # Check service status
    check_service_status()
    
    # Check processes
    check_processes()
    
    # Test backend
    test_backend()
    
    logger.info("✅ Cleanup and test complete!")

if __name__ == "__main__":
    main() 