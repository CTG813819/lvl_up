#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project path
sys.path.append('/home/ubuntu/ai-backend-python')

def fix_project_warmaster_syntax():
    """Fix syntax error in Project Warmaster service file"""
    
    print("🔧 Fixing Project Warmaster service syntax...")
    
    # Read current service file
    service_file_path = '/home/ubuntu/ai-backend-python/app/services/project_berserk_service.py'
    
    try:
        with open(service_file_path, 'r') as f:
            current_content = f.read()
    except FileNotFoundError:
        print(f"❌ Service file not found: {service_file_path}")
        return
    
    # Fix the imports section
    fixed_imports = '''import asyncio
import random
import time
import json
import logging
import hashlib
import secrets
import base64
import hmac
import re
import threading
import socket
import ssl
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

from app.models.project_berserk import (
    ProjectBerserk,
    BerserkLearningSession,
    BerserkSelfImprovement,
    BerserkDeviceIntegration
)

logger = logging.getLogger(__name__)
'''
    
    # Find where the imports end and the global data starts
    global_data_start = current_content.find('_global_live_data = {')
    if global_data_start != -1:
        # Replace everything from the beginning to the global data start
        after_imports = current_content[global_data_start:]
        fixed_content = fixed_imports + '\n' + after_imports
    else:
        print("❌ Could not find global data structure")
        return
    
    # Write the fixed service file
    try:
        with open(service_file_path, 'w') as f:
            f.write(fixed_content)
        
        print("✅ Project Warmaster service syntax fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing syntax: {e}")

if __name__ == "__main__":
    fix_project_warmaster_syntax() 