#!/usr/bin/env python3
"""
Quick fix for custody protocol service initialization
Removes the call to testing_service.initialize() which doesn't exist
"""

import re

def fix_custody_service():
    """Fix the custody protocol service initialization"""
    
    # Read the current file with UTF-8 encoding
    with open('ai-backend-python/app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the line that calls testing_service.initialize()
    # Find the line: await instance.testing_service.initialize()
    pattern = r'^\s*await instance\.testing_service\.initialize\(\)\s*$'
    content = re.sub(pattern, '', content, flags=re.MULTILINE)
    
    # Write the fixed content back
    with open('ai-backend-python/app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed custody protocol service initialization")

if __name__ == "__main__":
    fix_custody_service()