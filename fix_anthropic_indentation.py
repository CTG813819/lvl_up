#!/usr/bin/env python3
"""
Fix Anthropic Service Indentation Error
=======================================

This script fixes the indentation error in anthropic_service.py that was caused
by the timeout fix script.
"""

import os
import sys

def fix_anthropic_service_indentation():
    """Fix the indentation error in anthropic_service.py"""
    try:
        print("🔧 Fixing anthropic service indentation error...")
        
        # Read the current anthropic service
        anthropic_file = "app/services/anthropic_service.py"
        if not os.path.exists(anthropic_file):
            print(f"❌ {anthropic_file} not found")
            return False
        
        # Create a backup first
        backup_file = anthropic_file + ".backup"
        with open(anthropic_file, 'r') as f:
            content = f.read()
        
        with open(backup_file, 'w') as f:
            f.write(content)
        print(f"✅ Backup created: {backup_file}")
        
        # Restore the original clean version
        original_content = '''import os
import json
import time
import asyncio
import requests
import structlog
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = structlog.get_logger()

# Anthropic API configuration
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Rate limiting configuration
RATE_LIMIT_CALLS = 50
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_RESET_TIME = 60  # seconds

# Rate limiting state
rate_limit_calls = 0
rate_limit_reset_time = time.time() + RATE_LIMIT_RESET_TIME

def reset_rate_limit():
    """Reset rate limiting counters"""
    global rate_limit_calls, rate_limit_reset_time
    rate_limit_calls = 0
    rate_limit_reset_time = time.time() + RATE_LIMIT_RESET_TIME

def check_rate_limit():
    """Check if we can make an API call"""
    global rate_limit_calls, rate_limit_reset_time
    
    # Reset if window has passed
    if time.time() > rate_limit_reset_time:
        reset_rate_limit()
    
    # Check if we're within limits
    if rate_limit_calls >= RATE_LIMIT_CALLS:
        wait_time = rate_limit_reset_time - time.time()
        if wait_time > 0:
            logger.warning(f"Rate limit reached, waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)
            reset_rate_limit()
    
    return True

async def anthropic_rate_limited_call(prompt: str, ai_name: str, max_tokens: int = 4000) -> str:
    """
    Make a rate-limited call to Anthropic Claude API
    
    Args:
        prompt: The prompt to send to Claude
        ai_name: Name of the AI for logging
        max_tokens: Maximum tokens for response
        
    Returns:
        The response from Claude
    """
    if not ANTHROPIC_API_KEY:
        raise Exception("ANTHROPIC_API_KEY not configured")
    
    # Check rate limit
    check_rate_limit()
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
    }
    
    data = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        # Increment rate limit counter
        global rate_limit_calls
        rate_limit_calls += 1
        
        result = response.json()
        return result["content"][0]["text"]
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Anthropic API call failed for {ai_name}: {str(e)}")
        raise e

async def call_claude(prompt: str, max_tokens: int = 4000) -> str:
    """
    Simple wrapper for calling Claude
    
    Args:
        prompt: The prompt to send
        max_tokens: Maximum tokens for response
        
    Returns:
        The response from Claude
    """
    return await anthropic_rate_limited_call(prompt, "claude", max_tokens)
'''
        
        # Write the fixed content
        with open(anthropic_file, 'w') as f:
            f.write(original_content)
        
        print("✅ Anthropic service indentation error fixed")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing anthropic service: {str(e)}")
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
    print("🔧 Fixing Anthropic Service Indentation Error")
    print("=" * 50)
    
    # Fix the indentation error
    if fix_anthropic_service_indentation():
        print("✅ Indentation error fixed")
        
        # Restart the service
        if restart_backend_service():
            print("✅ Backend service restarted")
            print("\n🎉 Fix completed successfully!")
            print("The backend service should now start without errors.")
        else:
            print("❌ Failed to restart backend service")
    else:
        print("❌ Failed to fix indentation error")

if __name__ == "__main__":
    main() 