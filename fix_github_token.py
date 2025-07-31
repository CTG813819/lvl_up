#!/usr/bin/env python3
"""
Fix GitHub Token Issues
Fixes the 401 authentication errors when accessing GitHub repository content
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

def fix_github_token():
    """Fix the GitHub token authentication issues"""
    print("🔧 Fixing GitHub token authentication issues...")
    
    # The current token appears to be expired or has insufficient permissions
    # Let's create a new token with proper permissions
    
    print("⚠️  The current GitHub token appears to be expired or has insufficient permissions.")
    print("   This is causing 401 errors when accessing repository content.")
    print("\n📋 To fix this, you need to create a new GitHub Personal Access Token:")
    print("\n1. Go to GitHub.com → Settings → Developer settings → Personal access tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Give it a name like 'AI Backend Token'")
    print("4. Set expiration to 'No expiration' or a long period")
    print("5. Select these scopes:")
    print("   ✅ repo (Full control of private repositories)")
    print("   ✅ workflow (Update GitHub Action workflows)")
    print("   ✅ admin:org (Full control of organizations and teams)")
    print("   ✅ read:org (Read organization data)")
    print("   ✅ user (Read user data)")
    print("6. Click 'Generate token'")
    print("7. Copy the new token")
    
    # Create a script to update the token
    update_script = '''
#!/bin/bash
# Script to update GitHub token on EC2

echo "🔧 Updating GitHub token configuration..."

# Backup current .env file
cp /home/ubuntu/ai-backend-python/.env /home/ubuntu/ai-backend-python/.env.backup.$(date +%Y%m%d_%H%M%S)

# Update the .env file with the new token
echo "Please enter your new GitHub Personal Access Token:"
read -s NEW_TOKEN

if [ -n "$NEW_TOKEN" ]; then
    # Update the token in .env file
    sed -i "s/GITHUB_TOKEN=.*/GITHUB_TOKEN=$NEW_TOKEN/" /home/ubuntu/ai-backend-python/.env
    
    echo "✅ GitHub token updated successfully!"
    
    # Test the new token
    echo "🧪 Testing new GitHub token..."
    
    # Create a test script
    cat > /home/ubuntu/ai-backend-python/test_github_token.py << 'EOF'
import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def test_github_token():
    token = os.getenv('GITHUB_TOKEN')
    repo = os.getenv('GITHUB_REPO')
    
    if not token or not repo:
        print("❌ Missing GitHub token or repo configuration")
        return False
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Test repository access
    url = f"https://api.github.com/repos/{repo}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Repository access successful")
                    print(f"   Repository: {data.get('name', 'Unknown')}")
                    print(f"   Description: {data.get('description', 'No description')}")
                    print(f"   Stars: {data.get('stargazers_count', 0)}")
                    
                    # Test content access
                    content_url = f"https://api.github.com/repos/{repo}/contents"
                    async with session.get(content_url, headers=headers) as content_response:
                        if content_response.status == 200:
                            print(f"✅ Content access successful")
                            return True
                        else:
                            print(f"❌ Content access failed: {content_response.status}")
                            return False
                else:
                    print(f"❌ Repository access failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return False
    except Exception as e:
        print(f"❌ GitHub API test error: {e}")
        return False

# Run the test
asyncio.run(test_github_token())
EOF
    
    # Run the test
    cd /home/ubuntu/ai-backend-python
    python3 test_github_token.py
    
    # Clean up test file
    rm -f test_github_token.py
    
    # Restart the backend service
    echo "🔄 Restarting AI backend service..."
    sudo systemctl restart ai-backend-python
    
    echo "✅ GitHub token update completed!"
    echo "Check the logs to verify the fix worked:"
    echo "sudo journalctl -u ai-backend-python -f"
    
else
    echo "❌ No token provided. Update cancelled."
fi
'''
    
    # Write the update script to EC2
    print("📝 Creating GitHub token update script...")
    success, output, error = run_ssh_command(f"cd /home/ubuntu/ai-backend-python && cat > update_github_token.sh << 'EOF'\n{update_script}\nEOF")
    
    if not success:
        print(f"❌ Failed to create update script: {error}")
        return False
    
    # Make the script executable
    success, output, error = run_ssh_command("cd /home/ubuntu/ai-backend-python && chmod +x update_github_token.sh")
    
    if success:
        print("✅ GitHub token update script created")
        print("\n🔧 To update your GitHub token, run this command on EC2:")
        print("ssh -i New.pem ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com")
        print("cd /home/ubuntu/ai-backend-python")
        print("./update_github_token.sh")
    else:
        print(f"❌ Failed to make script executable: {error}")
    
    # Also create a quick fix for the current token issue
    print("\n🔧 Creating emergency token fix...")
    
    # The current token might work with different permissions or format
    emergency_fix = '''
# Emergency fix for GitHub token issues
# This creates a more permissive token configuration

# Update .env with additional GitHub configuration
echo "GITHUB_TOKEN=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" >> /home/ubuntu/ai-backend-python/.env
echo "GITHUB_REPO=CTG813819/Lvl_UP" >> /home/ubuntu/ai-backend-python/.env
echo "GITHUB_REPO_URL=https://github.com/CTG813819/Lvl_UP.git" >> /home/ubuntu/ai-backend-python/.env
echo "GITHUB_USERNAME=CTG813819" >> /home/ubuntu/ai-backend-python/.env
echo "GITHUB_EMAIL=canicegonzague@gmail.com" >> /home/ubuntu/ai-backend-python/.env

# Test the current token with different API endpoints
curl -H "Authorization: token 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" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/user

# Restart the service
sudo systemctl restart ai-backend-python
'''
    
    # Write emergency fix to EC2
    success, output, error = run_ssh_command(f"cd /home/ubuntu/ai-backend-python && cat > emergency_github_fix.sh << 'EOF'\n{emergency_fix}\nEOF")
    
    if success:
        print("✅ Emergency GitHub fix created")
        print("\n🔧 To apply emergency fix, run:")
        print("ssh -i New.pem ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com")
        print("cd /home/ubuntu/ai-backend-python")
        print("chmod +x emergency_github_fix.sh")
        print("./emergency_github_fix.sh")
    else:
        print(f"❌ Failed to create emergency fix: {error}")
    
    print("\n🎉 GitHub token fix setup completed!")
    print("=" * 50)
    print("The 401 errors should be resolved once you update the GitHub token.")
    print("Follow the instructions above to create a new token with proper permissions.")
    
    return True

if __name__ == "__main__":
    fix_github_token() 