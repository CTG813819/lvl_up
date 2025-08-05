#!/usr/bin/env python3
"""
Verify OpenAI API Key
====================

This script helps verify if the OpenAI API key is valid and troubleshoot authentication issues.
"""

import os
import sys
import requests
import json

def verify_openai_key():
    """Verify the OpenAI API key"""
    
    print("🔍 Verifying OpenAI API Key")
    print("=" * 50)
    
    # Get the API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OpenAI API key found in environment")
        return False
    
    print(f"\n🔑 API Key Details:")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Starts with: {api_key[:10]}...")
    print(f"   Ends with: ...{api_key[-4:]}")
    
    if not api_key.startswith("sk-"):
        print("❌ API key format is incorrect (should start with sk-)")
        return False
    
    print("✅ API key format looks correct")
    
    # Test different endpoints
    print("\n🌐 Testing API Endpoints:")
    print("-" * 40)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Models endpoint (simpler test)
    print("\n1. Testing Models Endpoint...")
    try:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers,
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Models endpoint successful!")
            models = response.json()
            available_models = [model['id'] for model in models.get('data', [])]
            print(f"   Available models: {len(available_models)} models")
            print(f"   Sample models: {available_models[:5]}")
        elif response.status_code == 401:
            print("   ❌ 401 Unauthorized - API key is invalid")
            print(f"   Response: {response.text}")
        elif response.status_code == 429:
            print("   ⚠️ 429 Rate Limited - API key is valid but rate limited")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 2: Chat completions endpoint
    print("\n2. Testing Chat Completions Endpoint...")
    try:
        data = {
            "model": "gpt-4o-mini",  # Use a simpler model
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "max_tokens": 10
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Chat completions successful!")
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"   Response: {content}")
        elif response.status_code == 401:
            print("   ❌ 401 Unauthorized - API key is invalid")
            print(f"   Response: {response.text}")
        elif response.status_code == 429:
            print("   ⚠️ 429 Rate Limited - API key is valid but rate limited")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 3: Check account status
    print("\n3. Checking Account Status...")
    try:
        response = requests.get(
            "https://api.openai.com/v1/dashboard/billing/subscription",
            headers=headers,
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Account status check successful!")
            account_info = response.json()
            print(f"   Account info: {json.dumps(account_info, indent=2)}")
        elif response.status_code == 401:
            print("   ❌ 401 Unauthorized - Cannot check account status")
        else:
            print(f"   ⚠️ Status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Recommendations
    print("\n💡 Troubleshooting Recommendations:")
    print("-" * 40)
    
    print("1. Check your OpenAI account:")
    print("   - Go to https://platform.openai.com/account/api-keys")
    print("   - Verify the key exists and is active")
    print("   - Check if the key has expired")
    
    print("\n2. Check your account status:")
    print("   - Go to https://platform.openai.com/account/billing")
    print("   - Verify you have sufficient credits")
    print("   - Check if your account is suspended")
    
    print("\n3. Generate a new API key:")
    print("   - Delete the old key")
    print("   - Create a new key")
    print("   - Update your .env file")
    
    print("\n4. Check key permissions:")
    print("   - Ensure the key has the right permissions")
    print("   - Check if there are any IP restrictions")
    
    return True

if __name__ == "__main__":
    verify_openai_key() 