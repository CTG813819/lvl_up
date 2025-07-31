#!/usr/bin/env python3
"""
Fix GitHub Configuration Script
Fixes the malformed GitHub configuration on the EC2 instance
"""

import os
import subprocess
import sys

def run_ssh_command(command):
    """Run SSH command on EC2 instance"""
    try:
        # Use the provided SSH key and EC2 instance
        ssh_cmd = [
            "ssh", "-i", "New.pem", 
            "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com",
            command
        ]
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def fix_github_config():
    """Fix the GitHub configuration on EC2"""
    print("🔧 Fixing GitHub configuration on EC2 instance...")
    
    # Your valid GitHub token from the configuration
    github_token = "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"
    github_username = "CTG813819"
    github_email = "canicegonzague@gmail.com"
    github_repo = "CTG813819/Lvl_UP"
    github_repo_url = "https://github.com/CTG813819/Lvl_UP.git"
    
    # Create a proper .env file content
    env_content = f"""# Database Configuration
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require
DATABASE_NAME=neondb
PORT=4000
HOST=0.0.0.0
DEBUG=false

# GitHub Configuration (FIXED)
GITHUB_TOKEN={github_token}
GITHUB_REPO={github_repo}
GITHUB_REPO_URL={github_repo_url}
GITHUB_USERNAME={github_username}
GITHUB_EMAIL={github_email}

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
EXPERIMENT_REPOSITORY_URL={github_repo_url}
EXPERIMENT_BRANCH=main
EXPERIMENT_AUTO_PUSH=true

# Git Configuration
GIT_ENABLED=true
REPOSITORY_URL={github_repo_url}
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
    
    # Write the .env file to EC2
    print("📝 Writing corrected .env file to EC2...")
    
    # Create the .env file content on EC2
    success, output, error = run_ssh_command(f"cd /home/ubuntu/ai-backend-python && cat > .env << 'EOF'\n{env_content}\nEOF")
    
    if not success:
        print(f"❌ Failed to write .env file: {error}")
        return False
    
    print("✅ .env file written successfully")
    
    # Verify the configuration
    print("🔍 Verifying GitHub configuration...")
    success, output, error = run_ssh_command("cd /home/ubuntu/ai-backend-python && grep 'GITHUB_TOKEN' .env")
    
    if success and output.strip():
        print("✅ GitHub token found in .env file")
        # Show the token (masked for security)
        token_line = output.strip()
        if "=" in token_line:
            token_value = token_line.split("=", 1)[1]
            masked_token = token_value[:10] + "..." + token_value[-4:] if len(token_value) > 14 else "***"
            print(f"   Token: {masked_token}")
    else:
        print("❌ GitHub token not found in .env file")
        return False
    
    # Test GitHub API access
    print("🧪 Testing GitHub API access...")
    test_script = f"""
import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def test_github():
    token = os.getenv('GITHUB_TOKEN')
    repo = os.getenv('GITHUB_REPO')
    
    if not token or not repo:
        print("❌ Missing GitHub token or repo configuration")
        return False
    
    headers = {{
        "Authorization": f"token {{token}}",
        "Accept": "application/vnd.github.v3+json"
    }}
    
    url = f"https://api.github.com/repos/{{repo}}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ GitHub API access successful")
                    print(f"   Repository: {{data.get('name', 'Unknown')}}")
                    print(f"   Description: {{data.get('description', 'No description')}}")
                    return True
                else:
                    print(f"❌ GitHub API access failed: {{response.status}}")
                    return False
    except Exception as e:
        print(f"❌ GitHub API test error: {{e}}")
        return False

# Run the test
asyncio.run(test_github())
"""
    
    # Write and run the test script
    success, output, error = run_ssh_command(f"cd /home/ubuntu/ai-backend-python && cat > test_github.py << 'EOF'\n{test_script}\nEOF")
    
    if success:
        success, output, error = run_ssh_command("cd /home/ubuntu/ai-backend-python && python3 test_github.py")
        if success:
            print(output)
        else:
            print(f"❌ GitHub test failed: {error}")
            print(f"Output: {output}")
    
    # Clean up test file
    run_ssh_command("cd /home/ubuntu/ai-backend-python && rm -f test_github.py")
    
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
    
    print("\n🎉 GitHub configuration fix completed!")
    print("=" * 50)
    print("The Imperium agent should now be able to access GitHub without 401 errors.")
    print("Check the logs to verify the fix worked:")
    print("sudo journalctl -u ai-backend-python -f")
    
    return True

if __name__ == "__main__":
    fix_github_config() 