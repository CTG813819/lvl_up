#!/usr/bin/env python3
"""
Script to check what models are available in sql_models.py on EC2
"""

import subprocess
import sys

def check_ec2_models():
    """Check what models are defined in sql_models.py on EC2"""
    
    # SSH command to check the models
    ssh_cmd = [
        "ssh", "-i", "New.pem", 
        "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com",
        "cd /home/ubuntu/ai-backend-python && python3 -c \"import sys; sys.path.append('.'); from app.models.sql_models import *; print('Available models:'); print([x for x in dir() if not x.startswith('_') and x[0].isupper()])\""
    ]
    
    try:
        print("🔍 Checking models available in EC2 sql_models.py...")
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Successfully checked EC2 models:")
            print(result.stdout)
        else:
            print("❌ Error checking EC2 models:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout while checking EC2 models")
    except Exception as e:
        print(f"❌ Exception while checking EC2 models: {e}")

if __name__ == "__main__":
    check_ec2_models() 