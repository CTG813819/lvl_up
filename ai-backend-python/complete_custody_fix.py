#!/usr/bin/env python3
"""
Complete Fix for Custody Protocol Service
=========================================

This script completely removes all problematic timeout code and restores
the custody protocol service to a working state.
"""

import os
import sys

def complete_custody_fix():
    """Complete fix for custody protocol service"""
    try:
        print("🔧 Applying complete fix to custody protocol service...")
        
        custody_file = "app/services/custody_protocol_service.py"
        if not os.path.exists(custody_file):
            print(f"❌ {custody_file} not found")
            return False
        
        # Create a backup
        backup_file = custody_file + ".backup4"
        with open(custody_file, 'r') as f:
            content = f.read()
        
        with open(backup_file, 'w') as f:
            f.write(content)
        print(f"✅ Backup created: {backup_file}")
        
        # Read the original backup that has the TestCategory and TestDifficulty classes
        original_backup = custody_file + ".backup"
        if os.path.exists(original_backup):
            with open(original_backup, 'r') as f:
                original_content = f.read()
            
            # Remove all problematic timeout-related code from the original
            lines = original_content.split('\n')
            fixed_lines = []
            skip_block = False
            in_problematic_try = False
            
            for line in lines:
                # Skip timeout configuration blocks
                if 'TIMEOUT_CONFIG' in line or '# Timeout configuration' in line:
                    skip_block = True
                    continue
                
                # Skip problematic try blocks with timeout
                if 'try:' in line and ('timeout' in line.lower() or 'Timeout' in line):
                    in_problematic_try = True
                    continue
                
                # Skip problematic except blocks
                if 'except asyncio.TimeoutError:' in line or 'except Exception as e:' in line:
                    if in_problematic_try:
                        in_problematic_try = False
                        skip_block = True
                        continue
                
                # Skip lines in problematic blocks
                if skip_block:
                    if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                        skip_block = False
                    else:
                        continue
                
                # Skip timeout-related imports
                if 'import asyncio' in line and 'from enum import Enum' not in original_content:
                    continue
                
                fixed_lines.append(line)
            
            # Ensure we have the Enum import
            if 'from enum import Enum' not in '\n'.join(fixed_lines):
                # Find the import section and add it
                for i, line in enumerate(fixed_lines):
                    if line.startswith('import ') or line.startswith('from '):
                        fixed_lines.insert(i, 'from enum import Enum')
                        break
            
            # Write the fixed content
            with open(custody_file, 'w') as f:
                f.write('\n'.join(fixed_lines))
            
            print("✅ Custody protocol service completely fixed")
            return True
        else:
            print("❌ Original backup not found")
            return False
        
    except Exception as e:
        print(f"❌ Error applying complete fix: {str(e)}")
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
    print("🔧 Complete Fix for Custody Protocol Service")
    print("=" * 40)
    
    # Apply the complete fix
    if complete_custody_fix():
        print("✅ Service fixed")
        
        # Restart the service
        if restart_backend_service():
            print("✅ Backend service restarted")
            print("\n🎉 Complete fix applied successfully!")
            print("The custody protocol service should now work properly.")
        else:
            print("❌ Failed to restart backend service")
    else:
        print("❌ Failed to apply complete fix")

if __name__ == "__main__":
    main() 