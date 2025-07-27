#!/usr/bin/env python3
"""
Simple OpenAI Test
=================

This script tests basic OpenAI API authentication without any complex setup.
"""

import os
import requests
import json

def test_simple_openai():
    """Test simple OpenAI API call"""
    
    print("🧪 Simple OpenAI API Test")
    print("=" * 40)
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No API key found in environment")
        return False
    
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")
    
    # Simple test with curl-like request
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",  # Use a simpler model
        "messages": [
            {"role": "user", "content": "Say hello"}
        ],
        "max_tokens": 10
    }
    
    print("\n🌐 Making API call...")
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"\n📊 Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"Response: {content}")
            return True
        else:
            print("❌ FAILED!")
            print(f"Response Body: {response.text}")
            
            # Try to parse error
            try:
                error_data = response.json()
                print(f"Error Type: {error_data.get('error', {}).get('type')}")
                print(f"Error Message: {error_data.get('error', {}).get('message')}")
                print(f"Error Code: {error_data.get('error', {}).get('code')}")
            except:
                print("Could not parse error response")
            
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_simple_openai()
    if success:
        print("\n🎉 OpenAI API is working!")
    else:
        print("\n❌ OpenAI API test failed") 