#!/usr/bin/env python3
"""
Remove Optimized Service Script
===============================

This script will completely remove the ai-backend-optimized.service
since we're now using the optimized version in the original service.
"""

import subprocess
import logging
import os

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

def remove_optimized_service():
    """Remove the optimized service completely"""
    logger.info("🗑️ Removing ai-backend-optimized.service...")
    
    # Stop the service if it's running
    logger.info("🛑 Stopping optimized service...")
    run_command("sudo systemctl stop ai-backend-optimized.service")
    
    # Disable the service
    logger.info("🔒 Disabling optimized service...")
    run_command("sudo systemctl disable ai-backend-optimized.service")
    
    # Remove the service file
    logger.info("🗑️ Removing service file...")
    run_command("sudo rm -f /etc/systemd/system/ai-backend-optimized.service")
    
    # Reload systemd
    logger.info("🔄 Reloading systemd...")
    run_command("sudo systemctl daemon-reload")
    
    # Reset failed units
    logger.info("🔄 Resetting failed units...")
    run_command("sudo systemctl reset-failed")
    
    logger.info("✅ Optimized service removed")

def check_services():
    """Check what services are available"""
    logger.info("🔍 Checking available services...")
    
    # Check if optimized service still exists
    code, output, error = run_command("sudo systemctl status ai-backend-optimized.service")
    if code == 0:
        logger.warning("⚠️ Optimized service still exists")
        logger.info(output)
    else:
        logger.info("✅ Optimized service successfully removed")
    
    # Check main service
    code, output, error = run_command("sudo systemctl status ai-backend-python.service")
    if code == 0:
        logger.info("✅ Main service status:")
        for line in output.split('\n')[:5]:
            if line.strip():
                logger.info(f"  {line}")
    else:
        logger.error("❌ Main service not found")

def main():
    """Main removal function"""
    logger.info("🚀 Starting optimized service removal...")
    
    # Remove the optimized service
    remove_optimized_service()
    
    # Check services
    check_services()
    
    logger.info("✅ Optimized service removal complete!")

if __name__ == "__main__":
    main() 