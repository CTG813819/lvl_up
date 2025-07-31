#!/usr/bin/env python3
"""
Simple GitHub Token Fix
Tests and fixes GitHub token issues
"""

import os
import subprocess
import sys

def run_ssh_command(command):
    """Run SSH command on EC2 instance"""
    try:
        ssh_cmd = [
            "ssh", "-i", "New.pem", 
            "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com",
            command
        ]
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_current_github_token():
    """Test the current GitHub token to see if it works"""
    print("🧪 Testing current GitHub token...")
    
    # Test the current token directly
    test_script = '''
import requests

# Test the current token
token = "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"
repo = "CTG813819/Lvl_UP"

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}

# Test 1: User info
print("Testing user info...")
response = requests.get("https://api.github.com/user", headers=headers)
print(f"User info status: {response.status_code}")
if response.status_code == 200:
    user_data = response.json()
    print(f"User: {user_data.get('login', 'Unknown')}")
else:
    print(f"Error: {response.text}")

# Test 2: Repository info
print("\\nTesting repository access...")
response = requests.get(f"https://api.github.com/repos/{repo}", headers=headers)
print(f"Repository status: {response.status_code}")
if response.status_code == 200:
    repo_data = response.json()
    print(f"Repository: {repo_data.get('name', 'Unknown')}")
else:
    print(f"Error: {response.text}")

# Test 3: Repository contents
print("\\nTesting repository contents...")
response = requests.get(f"https://api.github.com/repos/{repo}/contents", headers=headers)
print(f"Contents status: {response.status_code}")
if response.status_code == 200:
    contents = response.json()
    print(f"Found {len(contents)} items in repository")
else:
    print(f"Error: {response.text}")

# Test 4: Check token scopes
print("\\nChecking token scopes...")
response = requests.get("https://api.github.com/user", headers=headers)
if response.status_code == 200:
    scopes = response.headers.get('X-OAuth-Scopes', '')
    print(f"Token scopes: {scopes}")
else:
    print("Could not check scopes")
'''
    
    # Write and run the test script on EC2
    success, output, error = run_ssh_command(f"cd /home/ubuntu/ai-backend-python && cat > test_token.py << 'EOF'\n{test_script}\nEOF")
    
    if success:
        success, output, error = run_ssh_command("cd /home/ubuntu/ai-backend-python && python3 test_token.py")
        if success:
            print("Token test results:")
            print(output)
        else:
            print(f"❌ Token test failed: {error}")
            print(f"Output: {output}")
    
    # Clean up
    run_ssh_command("cd /home/ubuntu/ai-backend-python && rm -f test_token.py")
    
    return success

def fix_github_config():
    """Fix GitHub configuration"""
    print("🔧 Fixing GitHub configuration...")
    
    # Create a clean .env file with proper GitHub configuration
    env_content = """# Database Configuration
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require
DATABASE_NAME=neondb
PORT=4000
HOST=0.0.0.0
DEBUG=false

# GitHub Configuration (CLEAN)
GITHUB_TOKEN=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
GITHUB_REPO=CTG813819/Lvl_UP
GITHUB_REPO_URL=https://github.com/CTG813819/Lvl_UP.git
GITHUB_USERNAME=CTG813819
GITHUB_EMAIL=canicegonzague@gmail.com

# AI Configuration
AUTO_IMPROVEMENT_ENABLED=true
GROWTH_ANALYSIS_INTERVAL=3600
GROWTH_THRESHOLD=0.6

# Repository Configuration
REPO_BRANCH=main
REPO_PATH=/home/ubuntu/ai-backend-python/repo

# AI Learning Configuration
LEARNING_ENABLED=true
LEARNING_CYCLE_INTERVAL=300
MAX_LEARNING_CYCLES=100

# Experiment Configuration
EXPERIMENT_REPOSITORY_URL=https://github.com/CTG813819/Lvl_UP.git
EXPERIMENT_BRANCH=main
EXPERIMENT_AUTO_PUSH=true

# Git Configuration
GIT_ENABLED=true
REPOSITORY_URL=https://github.com/CTG813819/Lvl_UP.git
AUTO_PUSH_ENABLED=true
CREATE_ISSUES_ENABLED=true

# ML Settings
ML_MODEL_PATH=./models
ENABLE_ML_LEARNING=true
ML_CONFIDENCE_THRESHOLD=0.7

# Security
CORS_ORIGINS=["*"]
TRUSTED_HOSTS=["*"]

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# File paths
UPLOAD_PATH=./uploads
TEMP_PATH=./temp

# Proposal settings
MAX_PROPOSAL_LENGTH=10000
PROPOSAL_TIMEOUT=300

# Flutter Validation
SKIP_FLUTTER_VALIDATION=false
"""
    
    # Write the clean .env file to EC2
    print("📝 Writing clean .env file...")
    success, output, error = run_ssh_command(f"cd /home/ubuntu/ai-backend-python && cat > .env << 'EOF'\n{env_content}\nEOF")
    
    if not success:
        print(f"❌ Failed to write .env file: {error}")
        return False
    
    print("✅ Clean .env file written")
    
    # Restart the backend service
    print("🔄 Restarting AI backend service...")
    success, output, error = run_ssh_command("sudo systemctl restart ai-backend-python")
    
    if success:
        print("✅ AI backend service restarted")
    else:
        print(f"❌ Failed to restart service: {error}")
    
    # Check service status
    print("📊 Checking service status...")
    success, output, error = run_ssh_command("sudo systemctl status ai-backend-python --no-pager")
    
    if success:
        print("Service status:")
        print(output)
    else:
        print(f"❌ Failed to get service status: {error}")
    
    return True

def main():
    """Main function to fix GitHub issues"""
    print("🔧 GitHub Token Fix Script")
    print("=" * 40)
    
    # First test the current token
    test_current_github_token()
    
    # Then fix the configuration
    fix_github_config()
    
    print("\n🎉 GitHub fix completed!")
    print("=" * 40)
    print("If you're still getting 401 errors, you need to create a new GitHub token:")
    print("1. Go to GitHub.com → Settings → Developer settings → Personal access tokens")
    print("2. Generate new token with 'repo' and 'workflow' permissions")
    print("3. Replace the token in the .env file")
    print("\nCheck the logs to see if the fix worked:")
    print("sudo journalctl -u ai-backend-python -f")

if __name__ == "__main__":
    main() 