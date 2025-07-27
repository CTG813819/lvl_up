#!/usr/bin/env python3
"""
Fix Port Configuration Script
=============================
Updates the backend to use port 8000 instead of 4000
"""

import os
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def fix_port_configuration():
    """Fix the port configuration to use port 8000"""
    base_path = "/home/ubuntu/ai-backend-python"
    
    # Update main_optimized.py to use port 8000
    main_optimized_path = f"{base_path}/main_optimized.py"
    
    if os.path.exists(main_optimized_path):
        with open(main_optimized_path, 'r') as f:
            content = f.read()
        
        # Replace port 4000 with 8000
        content = content.replace('port=4000', 'port=8000')
        
        with open(main_optimized_path, 'w') as f:
            f.write(content)
        
        logger.info("✅ Updated main_optimized.py to use port 8000")
    
    # Update the original main.py as well
    main_path = f"{base_path}/main.py"
    
    if os.path.exists(main_path):
        with open(main_path, 'r') as f:
            content = f.read()
        
        # Replace port 4000 with 8000
        content = content.replace('port=4000', 'port=8000')
        
        with open(main_path, 'w') as f:
            f.write(content)
        
        logger.info("✅ Updated main.py to use port 8000")
    
    # Update the service configuration
    service_path = f"{base_path}/ai-backend-optimized.service"
    
    if os.path.exists(service_path):
        with open(service_path, 'r') as f:
            content = f.read()
        
        # Update the service to use main.py instead of main_optimized.py
        content = content.replace('ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python main_optimized.py', 
                                'ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python main.py')
        
        with open(service_path, 'w') as f:
            f.write(content)
        
        logger.info("✅ Updated service configuration to use main.py")
    
    # Reload systemd and restart service
    try:
        subprocess.run(["sudo", "cp", service_path, "/etc/systemd/system/"], check=True)
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        logger.info("✅ Reloaded systemd configuration")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to reload systemd: {e}")

if __name__ == "__main__":
    fix_port_configuration() 