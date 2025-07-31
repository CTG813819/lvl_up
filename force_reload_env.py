#!/usr/bin/env python3
"""
Force Reload Environment Variables
=================================

This script forces a complete reload of environment variables from .env file.
"""

import os
import sys
from dotenv import load_dotenv

def force_reload_env():
    """Force reload environment variables"""
    
    print("🔄 Force Reloading Environment Variables")
    print("=" * 50)
    
    # Step 1: Clear existing environment variables
    print("\n🧹 Clearing existing environment variables...")
    
    # Remove any existing OpenAI-related environment variables
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
        print("✅ Cleared OPENAI_API_KEY from environment")
    
    if 'OPENAI_MODEL' in os.environ:
        del os.environ['OPENAI_MODEL']
        print("✅ Cleared OPENAI_MODEL from environment")
    
    if 'OPENAI_BASE_URL' in os.environ:
        del os.environ['OPENAI_BASE_URL']
        print("✅ Cleared OPENAI_BASE_URL from environment")
    
    # Step 2: Force reload from .env file
    print("\n📄 Force reloading from .env file...")
    
    # Load .env file with override
    load_dotenv(override=True)
    
    # Step 3: Check the loaded values
    print("\n🔍 Checking loaded environment variables:")
    print("-" * 40)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OPENAI_API_KEY loaded")
        print(f"   Length: {len(api_key)} characters")
        print(f"   Starts with: {api_key[:10]}...")
        print(f"   Ends with: ...{api_key[-4:]}")
        
        if api_key.startswith("sk-"):
            print("✅ Key format is correct (starts with sk-)")
        else:
            print("❌ Key format is incorrect (should start with sk-)")
    else:
        print("❌ OPENAI_API_KEY not found")
    
    model = os.getenv("OPENAI_MODEL")
    if model:
        print(f"✅ OPENAI_MODEL: {model}")
    else:
        print("❌ OPENAI_MODEL not found")
    
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        print(f"✅ OPENAI_BASE_URL: {base_url}")
    else:
        print("❌ OPENAI_BASE_URL not found")
    
    # Step 4: Test the configuration
    print("\n🧪 Testing configuration...")
    print("-" * 40)
    
    if api_key and api_key.startswith("sk-"):
        print("✅ Configuration looks good!")
        print("\n📋 Next Steps:")
        print("1. Restart your virtual environment")
        print("2. Run: python debug_openai_auth.py")
        print("3. Run: python test_complete_integration.py")
        return True
    else:
        print("❌ Configuration still has issues")
        print("\n🔧 Troubleshooting:")
        print("1. Check your .env file for correct API key")
        print("2. Make sure there are no duplicate entries")
        print("3. Restart your terminal session")
        return False

if __name__ == "__main__":
    success = force_reload_env()
    if not success:
        sys.exit(1) 