#!/usr/bin/env python3
"""
Final Fix for Custody Protocol Service
======================================

This script completely fixes the custody_protocol_service.py by removing all
problematic timeout modifications and restoring it to a working state.
"""

import os
import sys
import re

def fix_custody_protocol_service():
    """Fix the custody protocol service by removing problematic timeout code"""
    try:
        print("🔧 Fixing custody protocol service...")
        
        custody_file = "app/services/custody_protocol_service.py"
        if not os.path.exists(custody_file):
            print(f"❌ {custody_file} not found")
            return False
        
        # Read the current file
        with open(custody_file, 'r') as f:
            content = f.read()
        
        # Create a backup
        backup_file = custody_file + ".backup3"
        with open(backup_file, 'w') as f:
            f.write(content)
        print(f"✅ Backup created: {backup_file}")
        
        # Fix 1: Remove problematic timeout configurations
        content = re.sub(r'# Timeout configuration.*?\n', '', content, flags=re.DOTALL)
        content = re.sub(r'TIMEOUT_CONFIG = \{.*?\}\n', '', content, flags=re.DOTALL)
        
        # Fix 2: Remove problematic try-except blocks with timeout
        content = re.sub(r'try:\s*\n\s*# Add timeout to API calls.*?except asyncio\.TimeoutError:.*?return \{.*?\}\n', '', content, flags=re.DOTALL)
        
        # Fix 3: Remove specific problematic except block around line 231
        lines = content.split('\n')
        fixed_lines = []
        skip_until_end = False
        
        for i, line in enumerate(lines):
            # Skip lines that are part of problematic timeout blocks
            if 'except asyncio.TimeoutError:' in line:
                # Find the end of this except block
                skip_until_end = True
                continue
            
            if skip_until_end:
                # Check if this line starts a new block or is the end of the except
                if line.strip().startswith('except ') or line.strip().startswith('finally ') or line.strip().startswith('else:'):
                    skip_until_end = False
                elif line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                    # This is a new block, stop skipping
                    skip_until_end = False
                else:
                    # Still in the except block, skip this line
                    continue
            
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Fix 4: Remove any remaining problematic timeout imports or configurations
        content = re.sub(r'import asyncio\n', '', content)
        content = re.sub(r'from typing import.*?Any.*?\n', 'from typing import Dict, List, Optional, Any\n', content)
        
        # Fix 5: Ensure proper imports at the top
        if 'from enum import Enum' not in content:
            content = content.replace('import structlog', 'import structlog\nfrom enum import Enum')
        
        # Write the fixed content
        with open(custody_file, 'w') as f:
            f.write(content)
        
        print("✅ Custody protocol service fixed")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing custody protocol service: {str(e)}")
        return False

def restart_backend_service():
    """Restart the backend service"""
    try:
        print("🔄 Restarting backend service...")
        os.system("sudo systemctl restart ai-backend-python.service")
        return True
    except Exception as e:
        print(f"❌ Error restarting service: {str(e)}")
        return False

def main():
    """Main function"""
    print("🔧 Final Fix for Custody Protocol Service")
    print("=" * 40)
    
    # Fix the service
    if fix_custody_protocol_service():
        print("✅ Service fixed")
        
        # Restart the service
        if restart_backend_service():
            print("✅ Backend service restarted")
            print("\n🎉 Fix completed successfully!")
            print("The custody protocol service has been fixed and should now work properly.")
        else:
            print("❌ Failed to restart backend service")
    else:
        print("❌ Failed to fix service")

if __name__ == "__main__":
    main() 