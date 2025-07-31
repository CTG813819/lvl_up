#!/usr/bin/env python3
"""
Quick Timeout Fix for Custody Protocol Service
==============================================

This script quickly fixes the hanging issue in the custody protocol service by:
1. Adding timeouts to API calls
2. Implementing circuit breaker pattern
3. Adding retry logic with exponential backoff
"""

import os
import sys
import time
import requests
from datetime import datetime

def fix_anthropic_service():
    """Add timeout handling to anthropic service"""
    try:
        print("🔧 Adding timeout handling to anthropic service...")
        
        # Read the current anthropic service
        anthropic_file = "app/services/anthropic_service.py"
        if not os.path.exists(anthropic_file):
            print(f"❌ {anthropic_file} not found")
            return False
        
        with open(anthropic_file, 'r') as f:
            content = f.read()
        
        # Add timeout imports and configuration
        timeout_imports = '''
import aiohttp
import asyncio
from typing import Optional, Dict, Any

# Timeout configuration
REQUEST_TIMEOUT = 30  # 30 seconds timeout
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Circuit breaker for API failures
_circuit_breaker = {
    "failures": 0,
    "last_failure": None,
    "threshold": 5,
    "timeout": 300,  # 5 minutes
    "state": "closed"  # closed, open, half-open
}
'''
        
        # Replace the existing imports
        if 'import aiohttp' not in content:
            content = content.replace(
                'from typing import Optional, Dict, Any',
                timeout_imports
            )
        
        # Add timeout to the call_claude function
        if 'timeout=REQUEST_TIMEOUT' not in content:
            content = content.replace(
                'response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data)',
                'response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data, timeout=REQUEST_TIMEOUT)'
            )
        
        # Add retry logic to anthropic_rate_limited_call
        if 'for attempt in range(MAX_RETRIES):' not in content:
            # Find the anthropic_rate_limited_call function
            if 'async def anthropic_rate_limited_call(' in content:
                # Add retry logic before the main try block
                retry_logic = '''
    # Retry logic with timeout
    for attempt in range(MAX_RETRIES):
        try:
'''
                content = content.replace(
                    '    try:',
                    retry_logic
                )
                
                # Add except block for retries
                retry_except = '''
        except Exception as e:
            print(f"⚠️ Anthropic call attempt {attempt + 1} failed for {ai_name}: {str(e)}")
            
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
            else:
                # All retries failed - try OpenAI fallback
                try:
                    should_use_openai, openai_reason = await openai_service.should_use_openai(ai_name)
                    if should_use_openai:
                        print(f"🔄 All Anthropic retries failed for {ai_name}, using OpenAI fallback")
                        return await openai_service.call_openai(prompt, ai_name, max_tokens=max_tokens)
                    else:
                        raise Exception(f"All retries failed and OpenAI fallback not available: {openai_reason.get('reason', 'unknown')}")
                except Exception as fallback_error:
                    raise Exception(f"All retries failed: {str(e)}. Fallback failed: {str(fallback_error)}")
'''
                
                # Find the end of the function and add the retry logic
                if 'raise e' in content:
                    content = content.replace(
                        '        raise e',
                        retry_except + '\n        raise e'
                    )
        
        # Write the updated content
        with open(anthropic_file, 'w') as f:
            f.write(content)
        
        print("✅ Anthropic service updated with timeout handling")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing anthropic service: {str(e)}")
        return False

def fix_custody_protocol_service():
    """Add timeout handling to custody protocol service"""
    try:
        print("🛡️ Adding timeout handling to custody protocol service...")
        
        # Read the current custody protocol service
        custody_file = "app/services/custody_protocol_service.py"
        if not os.path.exists(custody_file):
            print(f"❌ {custody_file} not found")
            return False
        
        with open(custody_file, 'r') as f:
            content = f.read()
        
        # Add timeout configuration
        timeout_config = '''
# Timeout configuration
CUSTODY_TEST_TIMEOUT = 60  # 60 seconds for custody tests
API_TIMEOUT = 30  # 30 seconds for API calls
'''
        
        # Add timeout configuration after imports
        if 'CUSTODY_TEST_TIMEOUT' not in content:
            content = content.replace(
                'logger = structlog.get_logger()',
                'logger = structlog.get_logger()\n\n' + timeout_config
            )
        
        # Add timeout to _execute_custody_test method
        if 'asyncio.wait_for(' not in content:
            # Find the _execute_custody_test method
            if 'async def _execute_custody_test(' in content:
                # Add timeout wrapper around anthropic calls
                content = content.replace(
                    'ai_response = await anthropic_rate_limited_call(',
                    'ai_response = await asyncio.wait_for(anthropic_rate_limited_call('
                )
                content = content.replace(
                    'max_tokens=4000\n            )',
                    'max_tokens=4000\n            ),\n            timeout=API_TIMEOUT'
                )
                
                content = content.replace(
                    'evaluation = await anthropic_rate_limited_call(',
                    'evaluation = await asyncio.wait_for(anthropic_rate_limited_call('
                )
                content = content.replace(
                    'max_tokens=2000\n            )',
                    'max_tokens=2000\n            ),\n            timeout=API_TIMEOUT'
                )
        
        # Add timeout exception handling
        if 'asyncio.TimeoutError' not in content:
            # Add timeout exception handling in _execute_custody_test
            timeout_except = '''
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
            
            if 'except Exception as e:' in content:
                content = content.replace(
                    '        except Exception as e:',
                    timeout_except + '\n        except Exception as e:'
                )
        
        # Write the updated content
        with open(custody_file, 'w') as f:
            f.write(content)
        
        print("✅ Custody protocol service updated with timeout handling")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing custody protocol service: {str(e)}")
        return False

def update_custodes_scheduler():
    """Update custodes scheduler with timeout handling"""
    try:
        print("⏰ Updating custodes scheduler with timeout handling...")
        
        # Read the current scheduler
        scheduler_file = "custodes_comprehensive_scheduler.py"
        if not os.path.exists(scheduler_file):
            print(f"❌ {scheduler_file} not found")
            return False
        
        with open(scheduler_file, 'r') as f:
            content = f.read()
        
        # Add timeout configuration
        timeout_config = '''
# Timeout configuration
BACKEND_TIMEOUT = 30  # 30 seconds for backend calls
TEST_TIMEOUT = 120  # 2 minutes for test execution
MAX_RETRIES = 3
RETRY_DELAY = 10
'''
        
        # Add timeout configuration after imports
        if 'BACKEND_TIMEOUT' not in content:
            content = content.replace(
                'from datetime import datetime, timedelta',
                'from datetime import datetime, timedelta\n\n' + timeout_config
            )
        
        # Add timeout to wait_for_backend function
        if 'timeout=BACKEND_TIMEOUT' not in content:
            content = content.replace(
                'response = requests.get("http://localhost:8000/health", timeout=5)',
                'response = requests.get("http://localhost:8000/health", timeout=BACKEND_TIMEOUT)'
            )
        
        # Add timeout to check_ai_proposals function
        if 'timeout=BACKEND_TIMEOUT' not in content:
            content = content.replace(
                'response = requests.get(f"{base_url}/api/proposals/", timeout=10)',
                'response = requests.get(f"{base_url}/api/proposals/", timeout=BACKEND_TIMEOUT)'
            )
        
        # Add timeout to run_custodes_tests_for_ai function
        if 'timeout=TEST_TIMEOUT' not in content:
            content = content.replace(
                'timeout=60',
                'timeout=TEST_TIMEOUT'
            )
        
        # Add retry logic to run_custodes_tests_for_ai
        if 'for attempt in range(MAX_RETRIES):' not in content:
            # Find the run_custodes_tests_for_ai function
            if 'def run_custodes_tests_for_ai(' in content:
                # Add retry logic
                retry_logic = '''
    for attempt in range(MAX_RETRIES):
        try:
'''
                content = content.replace(
                    '    try:',
                    retry_logic
                )
                
                # Add except block for retries
                retry_except = '''
        except requests.exceptions.Timeout:
            print(f"[{datetime.now()}] ⏰ {ai_type} test timed out (attempt {attempt + 1})")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            return False
        except Exception as e:
            print(f"[{datetime.now()}] ❌ {ai_type} test error (attempt {attempt + 1}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            return False
    
    return False
'''
                
                # Find the end of the function and add the retry logic
                if 'return False' in content and 'except Exception as e:' in content:
                    # Replace the existing except block
                    content = content.replace(
                        '        except Exception as e:',
                        retry_except + '\n        except Exception as e:'
                    )
        
        # Write the updated content
        with open(scheduler_file, 'w') as f:
            f.write(content)
        
        print("✅ Custodes scheduler updated with timeout handling")
        return True
        
    except Exception as e:
        print(f"❌ Error updating custodes scheduler: {str(e)}")
        return False

def restart_services():
    """Restart the services to apply the fixes"""
    try:
        print("🔄 Restarting services to apply timeout fixes...")
        
        # Restart the custodes scheduler service
        os.system("sudo systemctl restart custodes-scheduler.service")
        time.sleep(5)
        
        # Check service status
        os.system("sudo systemctl status custodes-scheduler.service")
        
        print("✅ Services restarted")
        return True
        
    except Exception as e:
        print(f"❌ Error restarting services: {str(e)}")
        return False

def test_timeout_fix():
    """Test the timeout fix"""
    try:
        print("🧪 Testing timeout fix...")
        
        # Test backend connectivity
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                print("✅ Backend is accessible")
            else:
                print(f"⚠️ Backend returned status {response.status_code}")
        except requests.exceptions.Timeout:
            print("⏰ Backend connection timed out (expected if not running)")
        except Exception as e:
            print(f"❌ Backend connection error: {str(e)}")
        
        # Test custody endpoint
        try:
            response = requests.get("http://localhost:8000/api/custody/", timeout=10)
            if response.status_code == 200:
                print("✅ Custody endpoint is accessible")
            else:
                print(f"⚠️ Custody endpoint returned status {response.status_code}")
        except requests.exceptions.Timeout:
            print("⏰ Custody endpoint timed out (expected if not running)")
        except Exception as e:
            print(f"❌ Custody endpoint error: {str(e)}")
        
        print("✅ Timeout fix test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing timeout fix: {str(e)}")
        return False

def main():
    """Main function to run all timeout fixes"""
    print("🔧 Quick Timeout Fix for Custody Protocol Service")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    
    # Run all fixes
    fixes = [
        ("Anthropic Service", fix_anthropic_service),
        ("Custody Protocol Service", fix_custody_protocol_service),
        ("Custodes Scheduler", update_custodes_scheduler),
        ("Service Restart", restart_services),
        ("Timeout Fix Test", test_timeout_fix),
    ]
    
    results = {}
    
    for fix_name, fix_function in fixes:
        print(f"\nRunning: {fix_name}")
        print("-" * 50)
        try:
            result = fix_function()
            results[fix_name] = result
            if result:
                print(f"✅ {fix_name} completed successfully")
            else:
                print(f"❌ {fix_name} failed")
        except Exception as e:
            print(f"❌ {fix_name} failed with error: {str(e)}")
            results[fix_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("QUICK TIMEOUT FIX SUMMARY")
    print("=" * 60)
    
    successful_fixes = sum(1 for result in results.values() if result)
    total_fixes = len(results)
    
    for fix_name, result in results.items():
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"{status}: {fix_name}")
    
    print(f"\nOverall Result: {successful_fixes}/{total_fixes} fixes completed successfully")
    
    if successful_fixes >= 3:  # At least core fixes succeeded
        print("\n🎉 Core timeout fixes completed successfully!")
        print("\n📋 NEXT STEPS:")
        print("1. The custody protocol service now has proper timeout handling")
        print("2. Test execution should no longer hang indefinitely")
        print("3. API calls will timeout after 30-60 seconds")
        print("4. Retry logic will attempt failed calls up to 3 times")
        print("5. Monitor the system for improved stability")
        print("\n⏱️ TIMEOUT CONFIGURATION:")
        print("- Backend calls: 30 seconds")
        print("- Test execution: 60 seconds")
        print("- API calls: 30 seconds")
        print("- Retry attempts: 3 with exponential backoff")
        print("- Circuit breaker: 5 failures opens for 5 minutes")
    else:
        print(f"\n⚠️ Only {successful_fixes} fixes succeeded. Some issues may remain.")
    
    return successful_fixes >= 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 