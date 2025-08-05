#!/usr/bin/env python3
"""
OpenAI API Key Update Script
Updates the OpenAI API key in the .env file
"""

import os
import re
from pathlib import Path

def update_openai_key():
    """Update OpenAI API key in .env file"""
    
    # Get the current directory
    current_dir = Path.cwd()
    env_file = current_dir / ".env"
    
    print("🔑 OpenAI API Key Update")
    print("=" * 50)
    
    # Check if .env file exists
    if not env_file.exists():
        print("❌ .env file not found!")
        print(f"Expected location: {env_file}")
        return False
    
    # Read current .env file
    try:
        with open(env_file, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False
    
    # Check if OPENAI_API_KEY exists
    if "OPENAI_API_KEY=" not in content:
        print("❌ OPENAI_API_KEY not found in .env file")
        print("Please add: OPENAI_API_KEY=your_new_key_here")
        return False
    
    # Get new API key from user
    print("📝 Please enter your new OpenAI API key:")
    print("(The key should start with 'sk-')")
    new_key = input("API Key: ").strip()
    
    if not new_key:
        print("❌ No API key provided")
        return False
    
    if not new_key.startswith("sk-"):
        print("⚠️  Warning: API key doesn't start with 'sk-'")
        print("Are you sure this is correct? (y/N): ", end="")
        confirm = input().strip().lower()
        if confirm != 'y':
            print("❌ Update cancelled")
            return False
    
    # Update the API key in .env file
    try:
        # Use regex to replace the API key
        pattern = r'OPENAI_API_KEY=.*'
        replacement = f'OPENAI_API_KEY={new_key}'
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
            
            # Write back to .env file
            with open(env_file, 'w') as f:
                f.write(new_content)
            
            print("✅ OpenAI API key updated successfully!")
            print(f"📁 Updated file: {env_file}")
            
            # Verify the update
            print("\n🔍 Verifying update...")
            with open(env_file, 'r') as f:
                updated_content = f.read()
            
            if f'OPENAI_API_KEY={new_key}' in updated_content:
                print("✅ Verification successful!")
                return True
            else:
                print("❌ Verification failed - key not found in file")
                return False
                
        else:
            print("❌ OPENAI_API_KEY line not found in .env file")
            return False
            
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def test_new_key():
    """Test the new API key"""
    print("\n🧪 Testing new API key...")
    
    # Import and run the test
    try:
        import test_simple_openai
        print("✅ Test script imported successfully")
    except ImportError as e:
        print(f"❌ Could not import test script: {e}")
        return False
    
    # Run the test
    try:
        result = test_simple_openai.test_openai_api()
        if result:
            print("✅ API key test passed!")
            return True
        else:
            print("❌ API key test failed!")
            return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting OpenAI API Key Update Process")
    print("=" * 50)
    
    # Update the key
    if update_openai_key():
        print("\n" + "=" * 50)
        print("🔄 Testing the new API key...")
        
        # Test the new key
        if test_new_key():
            print("\n🎉 SUCCESS! OpenAI API key is working correctly.")
            print("The backend should now be able to use OpenAI as a fallback.")
        else:
            print("\n⚠️  The API key was updated but the test failed.")
            print("Please check your OpenAI account and API key permissions.")
    else:
        print("\n❌ Failed to update OpenAI API key.")
        print("Please check the error messages above.") 