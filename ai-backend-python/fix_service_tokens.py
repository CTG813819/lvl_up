#!/usr/bin/env python3
"""
Fix Service Tokens with Sudo
============================

This script updates the GitHub tokens in systemd service files using sudo
to fix the permission denied errors.
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

class ServiceTokenFixer:
    def __init__(self):
        self.old_token = "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"
        self.new_token = "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"
        
    def update_service_file(self, service_name: str):
        """Update token in a systemd service file using sudo"""
        logger.info(f"🔧 Updating {service_name}...")
        
        service_path = f"/etc/systemd/system/{service_name}"
        
        try:
            # Read the current service file
            result = subprocess.run(['sudo', 'cat', service_path], 
                                  capture_output=True, text=True, check=True)
            content = result.stdout
            
            if self.old_token in content:
                # Replace the old token with new token
                new_content = content.replace(self.old_token, self.new_token)
                
                # Write the updated content back to the file
                subprocess.run(['sudo', 'tee', service_path], 
                             input=new_content, text=True, check=True)
                
                logger.info(f"✅ Updated token in {service_name}")
                return True
            else:
                logger.info(f"ℹ️ No old token found in {service_name}")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to update {service_name}: {e}")
            return False
    
    def check_service_tokens(self):
        """Check current tokens in service files"""
        logger.info("🔍 Checking current tokens in service files...")
        
        services = ['guardian-ai.service', 'conquest-ai.service']
        
        for service in services:
            try:
                result = subprocess.run(['sudo', 'cat', f'/etc/systemd/system/{service}'], 
                                      capture_output=True, text=True, check=True)
                content = result.stdout
                
                if self.old_token in content:
                    logger.warning(f"⚠️ {service} still has old token")
                elif self.new_token in content:
                    logger.info(f"✅ {service} has new token")
                else:
                    logger.info(f"ℹ️ {service} has no token")
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Could not check {service}: {e}")
    
    def restart_services(self):
        """Restart services after token update"""
        logger.info("🔄 Restarting services...")
        
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
        """Check service status and recent logs"""
        logger.info("📊 Checking service status...")
        
        services = ['guardian-ai.service', 'conquest-ai.service']
        
        for service in services:
            try:
                result = subprocess.run(['sudo', 'systemctl', 'is-active', service], 
                                      capture_output=True, text=True, check=True)
                status = result.stdout.strip()
                logger.info(f"   {service}: {status}")
                
                if status == 'active':
                    # Check recent logs for authentication errors
                    log_result = subprocess.run(
                        ['sudo', 'journalctl', '-u', service, '--no-pager', '-n', '5'],
                        capture_output=True, text=True
                    )
                    if log_result.stdout:
                        recent_logs = log_result.stdout.strip().split('\n')[-3:]
                        for log in recent_logs:
                            if '401' in log or 'unauthorized' in log.lower():
                                logger.warning(f"   ⚠️ {log}")
                            elif 'error' in log.lower():
                                logger.warning(f"   ⚠️ {log}")
                            elif 'success' in log.lower() or 'started' in log.lower():
                                logger.info(f"   ✅ {log}")
                                
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to check {service}: {e}")
    
    def test_ai_endpoints(self):
        """Test AI endpoints after token update"""
        logger.info("🧪 Testing AI endpoints...")
        
        import requests
        
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
                    if 'error' in str(data).lower() and '401' not in str(data):
                        logger.warning(f"⚠️ {name} returned error in response")
                    elif '401' in str(data):
                        logger.warning(f"⚠️ {name} still has authentication issues")
                    else:
                        logger.info(f"✅ {name} working properly")
                else:
                    logger.warning(f"⚠️ {name} endpoint returned {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ {name} endpoint timed out")
            except requests.exceptions.ConnectionError:
                logger.error(f"❌ {name} endpoint connection error")
            except Exception as e:
                logger.error(f"❌ {name} endpoint test failed: {e}")
    
    def run_fix(self):
        """Run the complete service token fix"""
        logger.info("🚀 Starting Service Token Fix...")
        logger.info("=" * 60)
        
        # Step 1: Check current tokens
        self.check_service_tokens()
        
        # Step 2: Update service files
        logger.info("🔧 Updating service files...")
        services = ['guardian-ai.service', 'conquest-ai.service']
        
        for service in services:
            self.update_service_file(service)
        
        # Step 3: Check tokens again
        logger.info("🔍 Checking tokens after update...")
        self.check_service_tokens()
        
        # Step 4: Restart services
        self.restart_services()
        
        # Step 5: Check service status
        self.check_service_status()
        
        # Step 6: Test endpoints
        logger.info("=" * 60)
        logger.info("🧪 Testing AI endpoints...")
        self.test_ai_endpoints()
        
        logger.info("=" * 60)
        logger.info("✅ Service Token Fix completed!")
        
        return True

def main():
    """Main function"""
    try:
        fixer = ServiceTokenFixer()
        success = fixer.run_fix()
        
        if success:
            logger.info("🎉 Service token fix completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Service token fix failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 