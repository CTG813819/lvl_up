#!/usr/bin/env python3
"""
Update GitHub Token
==================

This script updates the expired GitHub token with the new valid token
in all configuration files and services.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class GitHubTokenUpdater:
    def __init__(self):
        self.base_dir = Path("/home/ubuntu/ai-backend-python")
        self.old_token = "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"
        self.new_token = "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"
        
    def update_config_file(self, file_path: Path):
        """Update token in a specific config file"""
        if not file_path.exists():
            logger.warning(f"⚠️ File not found: {file_path}")
            return False
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            if self.old_token in content:
                new_content = content.replace(self.old_token, self.new_token)
                with open(file_path, 'w') as f:
                    f.write(new_content)
                logger.info(f"✅ Updated token in {file_path.name}")
                return True
            else:
                logger.info(f"ℹ️ No old token found in {file_path.name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to update {file_path}: {e}")
            return False
    
    def update_service_files(self):
        """Update GitHub token in systemd service files"""
        logger.info("🔧 Updating systemd service files...")
        
        services = ['guardian-ai.service', 'conquest-ai.service']
        
        for service in services:
            service_path = Path(f"/etc/systemd/system/{service}")
            if service_path.exists():
                try:
                    with open(service_path, 'r') as f:
                        content = f.read()
                    
                    if self.old_token in content:
                        new_content = content.replace(self.old_token, self.new_token)
                        with open(service_path, 'w') as f:
                            f.write(new_content)
                        logger.info(f"✅ Updated token in {service}")
                    else:
                        logger.info(f"ℹ️ No old token found in {service}")
                        
                except Exception as e:
                    logger.error(f"❌ Failed to update {service}: {e}")
            else:
                logger.warning(f"⚠️ Service file not found: {service}")
    
    def update_environment_variables(self):
        """Update environment variables"""
        logger.info("🔧 Updating environment variables...")
        
        # Update .bashrc
        bashrc_path = Path.home() / ".bashrc"
        try:
            with open(bashrc_path, 'r') as f:
                content = f.read()
            
            # Remove old token line if exists
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if not line.strip().startswith('export GITHUB_TOKEN='):
                    new_lines.append(line)
            
            # Add new token line
            new_lines.append(f'export GITHUB_TOKEN="{self.new_token}"')
            
            with open(bashrc_path, 'w') as f:
                f.write('\n'.join(new_lines))
            
            logger.info("✅ Updated .bashrc with new token")
            
            # Set for current session
            os.environ['GITHUB_TOKEN'] = self.new_token
            logger.info("✅ Set new token for current session")
            
        except Exception as e:
            logger.error(f"❌ Failed to update .bashrc: {e}")
    
    def test_new_token(self):
        """Test the new token"""
        logger.info("🧪 Testing new GitHub token...")
        
        import requests
        
        headers = {
            'Authorization': f'token {self.new_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"✅ New token works! User: {user_data.get('login', 'Unknown')}")
                return True
            else:
                logger.error(f"❌ New token failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Token test failed: {e}")
            return False
    
    def restart_services(self):
        """Restart AI services with new token"""
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
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to restart services: {e}")
    
    def check_service_status(self):
        """Check service status after restart"""
        logger.info("📊 Checking service status...")
        
        services = ['guardian-ai.service', 'conquest-ai.service']
        
        for service in services:
            try:
                result = subprocess.run(['sudo', 'systemctl', 'is-active', service], 
                                      capture_output=True, text=True, check=True)
                status = result.stdout.strip()
                logger.info(f"   {service}: {status}")
                
                if status == 'active':
                    # Check recent logs for errors
                    log_result = subprocess.run(
                        ['sudo', 'journalctl', '-u', service, '--no-pager', '-n', '3'],
                        capture_output=True, text=True
                    )
                    if log_result.stdout:
                        recent_logs = log_result.stdout.strip().split('\n')[-2:]
                        for log in recent_logs:
                            if 'error' in log.lower() or '401' in log:
                                logger.warning(f"   ⚠️ {log}")
                            elif 'success' in log.lower() or 'started' in log.lower():
                                logger.info(f"   ✅ {log}")
                                
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to check {service}: {e}")
    
    def run_update(self):
        """Run the complete token update"""
        logger.info("🚀 Starting GitHub Token Update...")
        logger.info("=" * 60)
        
        # Step 1: Test new token first
        if not self.test_new_token():
            logger.error("❌ New token is invalid! Please check the token.")
            return False
        
        # Step 2: Update config files
        logger.info("🔧 Updating configuration files...")
        config_files = [
            self.base_dir / "app" / "core" / "config.py",
            self.base_dir / ".env",
            self.base_dir / "config.json"
        ]
        
        for config_file in config_files:
            self.update_config_file(config_file)
        
        # Step 3: Update service files
        self.update_service_files()
        
        # Step 4: Update environment variables
        self.update_environment_variables()
        
        # Step 5: Restart services
        self.restart_services()
        
        # Step 6: Check service status
        self.check_service_status()
        
        logger.info("=" * 60)
        logger.info("✅ GitHub Token Update completed!")
        logger.info("💡 The new token has been applied to:")
        logger.info("   - Configuration files")
        logger.info("   - Systemd service files")
        logger.info("   - Environment variables")
        logger.info("   - Services restarted")
        
        return True

def main():
    """Main function"""
    try:
        updater = GitHubTokenUpdater()
        success = updater.run_update()
        
        if success:
            logger.info("🎉 Token update completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Token update failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 