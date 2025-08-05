#!/usr/bin/env python3
"""
Check GitHub Token Status
========================

Quick script to check GitHub token configuration and test access.
This helps diagnose the 401 authentication issues with Guardian and Conquest AI.
"""

import os
import requests
import subprocess
from pathlib import Path

def check_environment_token():
    """Check for GitHub token in environment variables"""
    print("🔍 Checking environment variables...")
    
    token = os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_ACCESS_TOKEN')
    if token:
        print(f"✅ Found GitHub token in environment (length: {len(token)})")
        return token
    else:
        print("❌ No GitHub token found in environment variables")
        return None

def check_config_files():
    """Check config files for GitHub token"""
    print("\n🔍 Checking config files...")
    
    base_dir = Path("/home/ubuntu/ai-backend-python")
    config_files = [
        base_dir / "app" / "core" / "config.py",
        base_dir / ".env",
        base_dir / "config.json"
    ]
    
    for config_file in config_files:
        if config_file.exists():
            print(f"📁 Checking {config_file}")
            try:
                with open(config_file, 'r') as f:
                    content = f.read()
                    if 'GITHUB_TOKEN' in content or 'github_token' in content:
                        print(f"✅ GitHub token reference found in {config_file.name}")
                        # Try to extract token
                        lines = content.split('\n')
                        for line in lines:
                            if 'GITHUB_TOKEN' in line and '=' in line:
                                token = line.split('=')[1].strip().strip('"\'')
                                if token and len(token) > 10:
                                    print(f"✅ Token extracted from {config_file.name}")
                                    return token
                    else:
                        print(f"❌ No GitHub token found in {config_file.name}")
            except Exception as e:
                print(f"⚠️ Could not read {config_file}: {e}")
        else:
            print(f"❌ Config file not found: {config_file}")
    
    return None

def test_github_access(token):
    """Test GitHub API access with token"""
    print(f"\n🧪 Testing GitHub API access...")
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # Test user endpoint
        response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ GitHub access successful!")
            print(f"   User: {user_data.get('login', 'Unknown')}")
            print(f"   Name: {user_data.get('name', 'Unknown')}")
            print(f"   Email: {user_data.get('email', 'Unknown')}")
            return True
        else:
            print(f"❌ GitHub API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ GitHub API test failed: {e}")
        return False

def test_repository_access(token, repo_name="lvl_up"):
    """Test access to specific repository"""
    print(f"\n🔍 Testing repository access: {repo_name}")
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # Try to get repository info
        response = requests.get(f'https://api.github.com/repos/{repo_name}', headers=headers, timeout=10)
        if response.status_code == 200:
            repo_data = response.json()
            print(f"✅ Repository access successful!")
            print(f"   Name: {repo_data.get('full_name', repo_name)}")
            print(f"   Private: {repo_data.get('private', 'Unknown')}")
            print(f"   Description: {repo_data.get('description', 'No description')}")
            return True
        else:
            print(f"❌ Repository access failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Repository access test failed: {e}")
        return False

def check_service_environment():
    """Check if services have environment variables"""
    print("\n🔍 Checking service environment variables...")
    
    services = ['guardian-ai.service', 'conquest-ai.service']
    
    for service in services:
        try:
            # Check service file for environment variables
            service_file = Path(f"/etc/systemd/system/{service}")
            if service_file.exists():
                with open(service_file, 'r') as f:
                    content = f.read()
                    if 'Environment=' in content:
                        print(f"✅ {service} has environment variables")
                        # Extract environment lines
                        lines = content.split('\n')
                        for line in lines:
                            if line.strip().startswith('Environment='):
                                print(f"   {line.strip()}")
                    else:
                        print(f"❌ {service} missing environment variables")
            else:
                print(f"❌ Service file not found: {service}")
                
        except Exception as e:
            print(f"⚠️ Could not check {service}: {e}")

def main():
    """Main function"""
    print("🚀 GitHub Token Status Check")
    print("=" * 50)
    
    # Check environment
    token = check_environment_token()
    
    # Check config files if no environment token
    if not token:
        token = check_config_files()
    
    # Test GitHub access if token found
    if token:
        if test_github_access(token):
            test_repository_access(token)
        else:
            print("\n❌ GitHub token is invalid or expired!")
            print("💡 Please generate a new token with proper permissions")
    else:
        print("\n❌ No GitHub token found!")
        print("💡 To fix this:")
        print("   1. Go to GitHub.com → Settings → Developer settings → Personal access tokens")
        print("   2. Generate a new token with 'repo' and 'read:user' permissions")
        print("   3. Set it as: export GITHUB_TOKEN='your_token_here'")
    
    # Check service environment
    check_service_environment()
    
    print("\n" + "=" * 50)
    print("✅ Token check completed!")

if __name__ == "__main__":
    main() 