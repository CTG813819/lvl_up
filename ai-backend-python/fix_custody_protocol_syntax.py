#!/usr/bin/env python3
"""
Fix Custody Protocol Service Syntax Error
=========================================

This script fixes the syntax error in custody_protocol_service.py that was caused
by the timeout fix script.
"""

import os
import sys

def fix_custody_protocol_syntax():
    """Fix the syntax error in custody_protocol_service.py"""
    try:
        print("🔧 Fixing custody protocol service syntax error...")
        
        # Read the current custody protocol service
        custody_file = "app/services/custody_protocol_service.py"
        if not os.path.exists(custody_file):
            print(f"❌ {custody_file} not found")
            return False
        
        # Create a backup first
        backup_file = custody_file + ".backup"
        with open(custody_file, 'r') as f:
            content = f.read()
        
        with open(backup_file, 'w') as f:
            f.write(content)
        print(f"✅ Backup created: {backup_file}")
        
        # Fix the problematic syntax error around line 231
        # The issue is with the except asyncio.TimeoutError: block
        
        # Remove the problematic timeout configuration that was added
        if 'CUSTODY_TEST_TIMEOUT = 60' in content:
            # Remove the timeout configuration
            content = content.replace('''
# Timeout configuration
CUSTODY_TEST_TIMEOUT = 60  # 60 seconds for custody tests
API_TIMEOUT = 30  # 30 seconds for API calls
''', '')
        
        # Fix the problematic except block
        if 'except asyncio.TimeoutError:' in content:
            # Find and fix the problematic section
            # Look for the pattern where there's an except without a proper try block
            problematic_pattern = '''
        except asyncio.TimeoutError:
            logger.error(f"Timeout in custody test execution for {ai_type}")
            return {
                "passed": False,
                "score": 0,
                "duration": 0,
                "error": "Test execution timed out",
                "timestamp": datetime.utcnow().isoformat()
            }
'''
            
            # Remove the problematic except block
            content = content.replace(problematic_pattern, '')
        
        # Fix any remaining asyncio.wait_for calls that were incorrectly added
        if 'asyncio.wait_for(' in content:
            # Remove the asyncio.wait_for wrapper
            content = content.replace(
                'ai_response = await asyncio.wait_for(anthropic_rate_limited_call(',
                'ai_response = await anthropic_rate_limited_call('
            )
            content = content.replace(
                '),\n            timeout=API_TIMEOUT',
                ')'
            )
            
            content = content.replace(
                'evaluation = await asyncio.wait_for(anthropic_rate_limited_call(',
                'evaluation = await anthropic_rate_limited_call('
            )
            content = content.replace(
                '),\n            timeout=API_TIMEOUT',
                ')'
            )
        
        # Write the fixed content
        with open(custody_file, 'w') as f:
            f.write(content)
        
        print("✅ Custody protocol service syntax error fixed")
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
    print("🔧 Fixing Custody Protocol Service Syntax Error")
    print("=" * 55)
    
    # Fix the syntax error
    if fix_custody_protocol_syntax():
        print("✅ Syntax error fixed")
        
        # Restart the service
        if restart_backend_service():
            print("✅ Backend service restarted")
            print("\n🎉 Fix completed successfully!")
            print("The backend service should now start without syntax errors.")
        else:
            print("❌ Failed to restart backend service")
    else:
        print("❌ Failed to fix syntax error")

if __name__ == "__main__":
    main() 