#!/usr/bin/env python3
"""
Fix AI Authentication Issues
============================

This script fixes authentication issues with Guardian and Conquest AI services
that are getting 401 Unauthorized errors when accessing the repository.

Issues identified:
- Guardian AI: "Failed to get repo content path= status=401"
- Conquest AI: "Failed to get repo content path= status=401"

Solutions:
1. Check and fix GitHub token configuration
2. Verify repository access permissions
3. Update service configurations with proper authentication
4. Test authentication before restarting services
"""

import os
import sys
import json
import subprocess
import requests
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class AIAuthenticationFixer:
    def __init__(self):
        self.base_dir = Path("/home/ubuntu/ai-backend-python")
        self.config_dir = self.base_dir / "app" / "core"
        self.services_dir = self.base_dir / "app" / "services"
        
    def check_github_token(self) -> Optional[str]:
        """Check if GitHub token is properly configured"""
        logger.info("🔍 Checking GitHub token configuration...")
        
        # Check environment variables
        token = os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_ACCESS_TOKEN')
        if token:
            logger.info("✅ GitHub token found in environment variables")
            return token
            
        # Check config files
        config_files = [
            self.config_dir / "config.py",
            self.base_dir / ".env",
            self.base_dir / "config.json"
        ]
        
        for config_file in config_files:
            if config_file.exists():
                logger.info(f"🔍 Checking {config_file}")
                try:
                    with open(config_file, 'r') as f:
                        content = f.read()
                        if 'GITHUB_TOKEN' in content or 'github_token' in content:
                            logger.info(f"✅ GitHub token reference found in {config_file}")
                            # Extract token if possible
                            lines = content.split('\n')
                            for line in lines:
                                if 'GITHUB_TOKEN' in line and '=' in line:
                                    token = line.split('=')[1].strip().strip('"\'')
                                    if token and len(token) > 10:
                                        logger.info("✅ GitHub token extracted from config")
                                        return token
                except Exception as e:
                    logger.warning(f"⚠️ Could not read {config_file}: {e}")
        
        logger.warning("⚠️ No GitHub token found in environment or config files")
        return None
    
    def test_github_access(self, token: str) -> bool:
        """Test GitHub API access with the token"""
        logger.info("🧪 Testing GitHub API access...")
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            # Test user endpoint
            response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"✅ GitHub access successful - User: {user_data.get('login', 'Unknown')}")
                return True
            else:
                logger.error(f"❌ GitHub API error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ GitHub API test failed: {e}")
            return False
    
    def check_repository_access(self, token: str, repo_name: str = "lvl_up") -> bool:
        """Check access to specific repository"""
        logger.info(f"🔍 Checking access to repository: {repo_name}")
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            # Try to get repository info
            response = requests.get(f'https://api.github.com/repos/{repo_name}', headers=headers, timeout=10)
            if response.status_code == 200:
                repo_data = response.json()
                logger.info(f"✅ Repository access successful: {repo_data.get('full_name', repo_name)}")
                return True
            else:
                logger.warning(f"⚠️ Repository access failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Repository access test failed: {e}")
            return False
    
    def fix_environment_variables(self, token: str):
        """Set GitHub token in environment variables"""
        logger.info("🔧 Setting GitHub token in environment...")
        
        # Add to .bashrc for persistence
        bashrc_path = Path.home() / ".bashrc"
        token_line = f'export GITHUB_TOKEN="{token}"'
        
        try:
            with open(bashrc_path, 'r') as f:
                content = f.read()
            
            if 'GITHUB_TOKEN' not in content:
                with open(bashrc_path, 'a') as f:
                    f.write(f'\n# GitHub Token for AI Services\n{token_line}\n')
                logger.info("✅ Added GitHub token to .bashrc")
            else:
                logger.info("✅ GitHub token already in .bashrc")
                
            # Set for current session
            os.environ['GITHUB_TOKEN'] = token
            logger.info("✅ Set GitHub token for current session")
            
        except Exception as e:
            logger.error(f"❌ Failed to set environment variable: {e}")
    
    def update_service_configs(self, token: str):
        """Update service configurations with proper authentication"""
        logger.info("🔧 Updating service configurations...")
        
        # Update Guardian AI service
        guardian_service = Path("/etc/systemd/system/guardian-ai.service")
        if guardian_service.exists():
            try:
                with open(guardian_service, 'r') as f:
                    content = f.read()
                
                # Add environment variable to service
                if 'Environment=' not in content:
                    # Find the [Service] section and add environment
                    lines = content.split('\n')
                    new_lines = []
                    for line in lines:
                        new_lines.append(line)
                        if '[Service]' in line:
                            new_lines.append(f'Environment="GITHUB_TOKEN={token}"')
                    
                    with open(guardian_service, 'w') as f:
                        f.write('\n'.join(new_lines))
                    
                    logger.info("✅ Updated Guardian AI service with GitHub token")
                else:
                    logger.info("✅ Guardian AI service already has environment variables")
                    
            except Exception as e:
                logger.error(f"❌ Failed to update Guardian AI service: {e}")
        
        # Update Conquest AI service
        conquest_service = Path("/etc/systemd/system/conquest-ai.service")
        if conquest_service.exists():
            try:
                with open(conquest_service, 'r') as f:
                    content = f.read()
                
                # Add environment variable to service
                if 'Environment=' not in content:
                    # Find the [Service] section and add environment
                    lines = content.split('\n')
                    new_lines = []
                    for line in lines:
                        new_lines.append(line)
                        if '[Service]' in line:
                            new_lines.append(f'Environment="GITHUB_TOKEN={token}"')
                    
                    with open(conquest_service, 'w') as f:
                        f.write('\n'.join(new_lines))
                    
                    logger.info("✅ Updated Conquest AI service with GitHub token")
                else:
                    logger.info("✅ Conquest AI service already has environment variables")
                    
            except Exception as e:
                logger.error(f"❌ Failed to update Conquest AI service: {e}")
    
    def check_ai_service_configs(self):
        """Check AI service configurations for authentication settings"""
        logger.info("🔍 Checking AI service configurations...")
        
        service_files = [
            self.services_dir / "guardian_ai_service.py",
            self.services_dir / "conquest_ai_service.py"
        ]
        
        for service_file in service_files:
            if service_file.exists():
                logger.info(f"🔍 Checking {service_file.name}")
                try:
                    with open(service_file, 'r') as f:
                        content = f.read()
                    
                    if 'GITHUB_TOKEN' in content or 'github_token' in content:
                        logger.info(f"✅ {service_file.name} has GitHub token configuration")
                    else:
                        logger.warning(f"⚠️ {service_file.name} missing GitHub token configuration")
                        
                except Exception as e:
                    logger.error(f"❌ Could not read {service_file}: {e}")
    
    def restart_services(self):
        """Restart AI services with new configuration"""
        logger.info("🔄 Restarting AI services...")
        
        try:
            # Reload systemd
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            logger.info("✅ Systemd daemon reloaded")
            
            # Restart Guardian AI
            subprocess.run(['sudo', 'systemctl', 'restart', 'guardian-ai.service'], check=True)
            logger.info("✅ Guardian AI service restarted")
            
            # Restart Conquest AI
            subprocess.run(['sudo', 'systemctl', 'restart', 'conquest-ai.service'], check=True)
            logger.info("✅ Conquest AI service restarted")
            
            # Wait a moment for services to start
            import time
            time.sleep(5)
            
            # Check service status
            self.check_service_status()
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to restart services: {e}")
    
    def check_service_status(self):
        """Check the status of AI services"""
        logger.info("📊 Checking service status...")
        
        services = ['guardian-ai.service', 'conquest-ai.service']
        
        for service in services:
            try:
                result = subprocess.run(['sudo', 'systemctl', 'is-active', service], 
                                      capture_output=True, text=True, check=True)
                status = result.stdout.strip()
                logger.info(f"   {service}: {status}")
                
                if status == 'active':
                    # Check recent logs
                    log_result = subprocess.run(
                        ['sudo', 'journalctl', '-u', service, '--no-pager', '-n', '5'],
                        capture_output=True, text=True
                    )
                    if log_result.stdout:
                        recent_logs = log_result.stdout.strip().split('\n')[-3:]
                        for log in recent_logs:
                            if 'error' in log.lower() or '401' in log:
                                logger.warning(f"   ⚠️ {log}")
                            elif 'success' in log.lower() or 'started' in log.lower():
                                logger.info(f"   ✅ {log}")
                                
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to check {service}: {e}")
    
    def test_ai_endpoints(self):
        """Test AI endpoints after fixes"""
        logger.info("🧪 Testing AI endpoints...")
        
        endpoints = [
            ('guardian', 'http://localhost:8000/api/ai/guardian/test'),
            ('conquest', 'http://localhost:8000/api/ai/conquest/test')
        ]
        
        for name, url in endpoints:
            try:
                logger.info(f"🧪 Testing {name} endpoint...")
                response = requests.post(url, json={
                    'test_difficulty': 'basic',
                    'test_category': 'knowledge_verification'
                }, timeout=30)
                
                if response.status_code == 200:
                    logger.info(f"✅ {name} endpoint working")
                    data = response.json()
                    if 'error' in str(data).lower():
                        logger.warning(f"⚠️ {name} returned error in response")
                else:
                    logger.warning(f"⚠️ {name} endpoint returned {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ {name} endpoint timed out")
            except requests.exceptions.ConnectionError:
                logger.error(f"❌ {name} endpoint connection error")
            except Exception as e:
                logger.error(f"❌ {name} endpoint test failed: {e}")
    
    def run_fix(self):
        """Run the complete authentication fix"""
        logger.info("🚀 Starting AI Authentication Fix...")
        logger.info("=" * 60)
        
        # Step 1: Check current GitHub token
        token = self.check_github_token()
        
        if not token:
            logger.error("❌ No GitHub token found. Please provide a valid GitHub token.")
            logger.info("💡 To get a GitHub token:")
            logger.info("   1. Go to GitHub.com → Settings → Developer settings → Personal access tokens")
            logger.info("   2. Generate a new token with 'repo' and 'read:user' permissions")
            logger.info("   3. Set it as GITHUB_TOKEN environment variable")
            return False
        
        # Step 2: Test GitHub access
        if not self.test_github_access(token):
            logger.error("❌ GitHub token is invalid or expired")
            return False
        
        # Step 3: Check repository access
        self.check_repository_access(token)
        
        # Step 4: Fix environment variables
        self.fix_environment_variables(token)
        
        # Step 5: Update service configurations
        self.update_service_configs(token)
        
        # Step 6: Check AI service configs
        self.check_ai_service_configs()
        
        # Step 7: Restart services
        self.restart_services()
        
        # Step 8: Test endpoints
        logger.info("=" * 60)
        logger.info("🧪 Testing AI endpoints after fixes...")
        self.test_ai_endpoints()
        
        logger.info("=" * 60)
        logger.info("✅ AI Authentication Fix completed!")
        logger.info("💡 If issues persist, check:")
        logger.info("   1. GitHub token permissions (needs 'repo' access)")
        logger.info("   2. Repository visibility and access")
        logger.info("   3. Service logs: journalctl -u guardian-ai.service -f")
        logger.info("   4. Service logs: journalctl -u conquest-ai.service -f")
        
        return True

def main():
    """Main function"""
    try:
        fixer = AIAuthenticationFixer()
        success = fixer.run_fix()
        
        if success:
            logger.info("🎉 Authentication fix completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Authentication fix failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 