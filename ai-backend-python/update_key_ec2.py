#!/usr/bin/env python3
"""
OpenAI API Key Update Script for EC2
Updates the OpenAI API key in the .env file with the provided key
"""

import os
import re
from pathlib import Path

def update_openai_key():
    """Update OpenAI API key in .env file with the new key"""
    
    # The new API key
    new_key = "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"
    
    # Get the current directory
    current_dir = Path.cwd()
    env_file = current_dir / ".env"
    
    print("🔑 OpenAI API Key Update for EC2")
    print("=" * 50)
    print(f"New Key: {new_key[:20]}...{new_key[-10:]}")
    
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
        print("Adding new OPENAI_API_KEY line...")
        
        # Add the new line to the end of the file
        try:
            with open(env_file, 'a') as f:
                f.write(f"\nOPENAI_API_KEY={new_key}\n")
            print("✅ Added OPENAI_API_KEY to .env file")
            return True
        except Exception as e:
            print(f"❌ Error adding to .env file: {e}")
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

def reload_environment():
    """Reload environment variables"""
    print("\n🔄 Reloading environment variables...")
    
    # Source the .env file
    try:
        import subprocess
        result = subprocess.run(['bash', '-c', 'source .env && env | grep OPENAI_API_KEY'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Environment variables reloaded")
            print(f"Current key: {result.stdout.strip()}")
            return True
        else:
            print("⚠️  Could not reload environment variables")
            return False
    except Exception as e:
        print(f"⚠️  Error reloading environment: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting OpenAI API Key Update Process")
    print("=" * 50)
    
    # Update the key
    if update_openai_key():
        print("\n" + "=" * 50)
        print("🔄 Reloading environment...")
        reload_environment()
        
        print("\n🧪 Testing the new API key...")
        
        # Test the new key
        if test_new_key():
            print("\n🎉 SUCCESS! OpenAI API key is working correctly.")
            print("The backend should now be able to use OpenAI as a fallback.")
            print("\n📋 Next steps:")
            print("1. Restart the backend: sudo systemctl restart ai-backend")
            print("2. Check logs: sudo journalctl -u ai-backend -f")
            print("3. Monitor token usage and fallback behavior")
        else:
            print("\n⚠️  The API key was updated but the test failed.")
            print("Please check your OpenAI account and API key permissions.")
    else:
        print("\n❌ Failed to update OpenAI API key.")
        print("Please check the error messages above.") 