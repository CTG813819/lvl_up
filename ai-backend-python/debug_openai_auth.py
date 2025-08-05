#!/usr/bin/env python3
"""
Debug OpenAI Authentication
==========================

This script helps debug OpenAI authentication issues.
"""

import asyncio
import sys
import os
import requests
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_database
from app.services.openai_service import openai_service

async def debug_openai_auth():
    """Debug OpenAI authentication"""
    
    try:
        print("🔍 Debugging OpenAI Authentication")
        print("=" * 50)
        
        # Initialize database
        await init_database()
        
        # Check API key
        print("\n🔑 API Key Check:")
        print("-" * 30)
        
        api_key = openai_service.api_key
        if api_key:
            print(f"✅ API key is loaded")
            print(f"   Length: {len(api_key)} characters")
            print(f"   Starts with: {api_key[:10]}...")
            print(f"   Ends with: ...{api_key[-4:]}")
            
            # Check if it looks like a valid OpenAI key
            if api_key.startswith("sk-"):
                print("✅ Key format looks correct (starts with sk-)")
            else:
                print("⚠️  Key format may be incorrect (should start with sk-)")
        else:
            print("❌ No API key found")
            return False
        
        # Test direct API call
        print("\n🌐 Testing Direct API Call:")
        print("-" * 30)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4o-mini",  # Use a simpler model for testing
            "messages": [
                {"role": "user", "content": "Hello, this is a test."}
            ],
            "max_tokens": 10
        }
        
        try:
            print("Making direct API call...")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ API call successful!")
                result = response.json()
                print(f"Response: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
            elif response.status_code == 401:
                print("❌ 401 Unauthorized - API key is invalid")
                print("Response body:", response.text)
            elif response.status_code == 429:
                print("⚠️ 429 Rate Limited - API key is valid but rate limited")
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                print("Response body:", response.text)
                
        except Exception as e:
            print(f"❌ API call failed: {str(e)}")
        
        # Check environment variables
        print("\n🔧 Environment Variables:")
        print("-" * 30)
        
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key:
            print("✅ OPENAI_API_KEY found in environment")
            print(f"   Length: {len(env_key)} characters")
            print(f"   Starts with: {env_key[:10]}...")
        else:
            print("❌ OPENAI_API_KEY not found in environment")
        
        # Check .env file
        print("\n📄 .env File Check:")
        print("-" * 30)
        
        env_file = ".env"
        if os.path.exists(env_file):
            print("✅ .env file exists")
            with open(env_file, 'r') as f:
                content = f.read()
                if "OPENAI_API_KEY" in content:
                    print("✅ OPENAI_API_KEY found in .env file")
                    # Find the line with the API key
                    for line in content.split('\n'):
                        if line.startswith("OPENAI_API_KEY="):
                            key_value = line.split('=', 1)[1]
                            print(f"   Key value: {key_value[:10]}...")
                            break
                else:
                    print("❌ OPENAI_API_KEY not found in .env file")
        else:
            print("❌ .env file not found")
        
        # Recommendations
        print("\n💡 Recommendations:")
        print("-" * 30)
        
        if response.status_code == 401:
            print("1. Check if your OpenAI API key is valid")
            print("2. Verify the key hasn't expired")
            print("3. Check if you have sufficient credits")
            print("4. Try generating a new API key")
            print("5. Make sure the key starts with 'sk-'")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        return False

async def main():
    """Main function"""
    success = await debug_openai_auth()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 