#!/usr/bin/env python3
"""
Fix Guardian and Conquest AI Service Issues
- Diagnose why Guardian and Conquest AI services are not responding
- Check service status and logs
- Restart services if needed
- Fix configuration issues
"""

import subprocess
import time
import requests
import json
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class GuardianConquestFixer:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.session.timeout = 30
        
    def check_service_status(self, service_name):
        """Check if a systemd service is running"""
        try:
            result = subprocess.run(
                ["systemctl", "status", service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Service exists and is active
                if "Active: active (running)" in result.stdout:
                    return "running"
                elif "Active: inactive" in result.stdout:
                    return "stopped"
                elif "Active: failed" in result.stdout:
                    return "failed"
                else:
                    return "unknown"
            else:
                # Service doesn't exist
                return "not_found"
                
        except Exception as e:
            logger.error(f"Error checking {service_name}: {e}")
            return "error"
    
    def get_service_logs(self, service_name, lines=20):
        """Get recent logs for a service"""
        try:
            result = subprocess.run(
                ["journalctl", "-u", service_name, "-n", str(lines), "--no-pager"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error getting logs: {result.stderr}"
                
        except Exception as e:
            return f"Error getting logs: {e}"
    
    def restart_service(self, service_name):
        """Restart a systemd service"""
        try:
            logger.info(f"🔄 Restarting {service_name}...")
            
            # Stop the service
            stop_result = subprocess.run(
                ["systemctl", "stop", service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if stop_result.returncode != 0:
                logger.warning(f"⚠️ Could not stop {service_name}: {stop_result.stderr}")
            
            # Wait a moment
            time.sleep(5)
            
            # Start the service
            start_result = subprocess.run(
                ["systemctl", "start", service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if start_result.returncode == 0:
                logger.info(f"✅ {service_name} restarted successfully")
                return True
            else:
                logger.error(f"❌ Failed to start {service_name}: {start_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error restarting {service_name}: {e}")
            return False
    
    def check_system_resources(self):
        """Check system resources"""
        logger.info("💻 Checking system resources...")
        
        try:
            # Check memory usage
            mem_result = subprocess.run(
                ["free", "-h"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if mem_result.returncode == 0:
                logger.info("Memory Usage:")
                logger.info(mem_result.stdout.strip())
            
            # Check disk usage
            disk_result = subprocess.run(
                ["df", "-h"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if disk_result.returncode == 0:
                logger.info("Disk Usage:")
                logger.info(disk_result.stdout.strip())
            
            # Check running processes
            ps_result = subprocess.run(
                ["ps", "aux", "--sort=-%cpu", "|", "head", "-10"],
                capture_output=True,
                text=True,
                shell=True,
                timeout=10
            )
            
            if ps_result.returncode == 0:
                logger.info("Top CPU Processes:")
                logger.info(ps_result.stdout.strip())
                
        except Exception as e:
            logger.error(f"❌ Error checking system resources: {e}")
    
    def test_ai_endpoint(self, ai_name, timeout=30):
        """Test AI endpoint with POST request"""
        try:
            logger.info(f"🧪 Testing {ai_name} endpoint...")
            
            response = self.session.post(
                f"{self.base_url}/api/custody/test/{ai_name}",
                json={"timeout": timeout},
                timeout=timeout + 5
            )
            
            if response.status_code == 200:
                logger.info(f"✅ {ai_name} endpoint working")
                return True
            else:
                logger.warning(f"⚠️ {ai_name} endpoint returned {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.warning(f"⏰ {ai_name} endpoint timed out")
            return False
        except Exception as e:
            logger.error(f"❌ {ai_name} endpoint error: {e}")
            return False
    
    def fix_service_configuration(self, service_name):
        """Fix common service configuration issues"""
        logger.info(f"🔧 Checking {service_name} configuration...")
        
        try:
            # Check if service file exists
            service_file = f"/etc/systemd/system/{service_name}"
            
            result = subprocess.run(
                ["test", "-f", service_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.warning(f"⚠️ {service_name} service file not found")
                return False
            
            # Check service file permissions
            perm_result = subprocess.run(
                ["ls", "-la", service_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if perm_result.returncode == 0:
                logger.info(f"Service file permissions: {perm_result.stdout.strip()}")
            
            # Reload systemd daemon
            reload_result = subprocess.run(
                ["systemctl", "daemon-reload"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if reload_result.returncode == 0:
                logger.info("✅ Systemd daemon reloaded")
                return True
            else:
                logger.error(f"❌ Failed to reload systemd: {reload_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error fixing {service_name} configuration: {e}")
            return False
    
    def run_comprehensive_fix(self):
        """Run comprehensive fix for Guardian and Conquest AI services"""
        logger.info("🚀 Starting Guardian and Conquest AI Service Fix...")
        logger.info("=" * 60)
        
        # Step 1: Check system resources
        self.check_system_resources()
        
        # Step 2: Check service status
        services = ["guardian-ai.service", "conquest-ai.service"]
        service_status = {}
        
        for service in services:
            logger.info(f"🔍 Checking {service}...")
            status = self.check_service_status(service)
            service_status[service] = status
            logger.info(f"   Status: {status}")
            
            # Get recent logs
            logs = self.get_service_logs(service, 10)
            if logs and "No journal files found" not in logs:
                logger.info(f"   Recent logs:")
                for line in logs.split('\n')[-5:]:  # Last 5 lines
                    if line.strip():
                        logger.info(f"     {line.strip()}")
        
        # Step 3: Fix services based on status
        for service, status in service_status.items():
            ai_name = service.replace("-ai.service", "")
            
            if status == "not_found":
                logger.warning(f"⚠️ {service} not found - service may not be installed")
                continue
            elif status == "failed":
                logger.info(f"🔄 {service} failed - attempting restart...")
                if self.restart_service(service):
                    # Wait for service to start
                    time.sleep(10)
                    # Test the endpoint
                    self.test_ai_endpoint(ai_name, 60)
            elif status == "stopped":
                logger.info(f"🔄 {service} stopped - attempting start...")
                if self.restart_service(service):
                    # Wait for service to start
                    time.sleep(10)
                    # Test the endpoint
                    self.test_ai_endpoint(ai_name, 60)
            elif status == "running":
                logger.info(f"✅ {service} is running - testing endpoint...")
                # Test the endpoint
                self.test_ai_endpoint(ai_name, 60)
            else:
                logger.warning(f"⚠️ {service} has unknown status: {status}")
        
        # Step 4: Test all AI endpoints
        logger.info("🧪 Testing all AI endpoints...")
        ai_services = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_name in ai_services:
            self.test_ai_endpoint(ai_name, 60)
        
        # Step 5: Summary
        logger.info("=" * 60)
        logger.info("📊 Fix Summary:")
        logger.info("=" * 60)
        
        for service, status in service_status.items():
            ai_name = service.replace("-ai.service", "")
            logger.info(f"{ai_name}: {status}")
        
        logger.info("=" * 60)
        logger.info("💡 Next Steps:")
        logger.info("=" * 60)
        
        if service_status.get("guardian-ai.service") != "running":
            logger.info("1. Guardian AI service needs attention")
            logger.info("   - Check service logs for errors")
            logger.info("   - Verify service configuration")
        
        if service_status.get("conquest-ai.service") != "running":
            logger.info("2. Conquest AI service needs attention")
            logger.info("   - Check service logs for errors")
            logger.info("   - Verify service configuration")
        
        logger.info("3. Monitor services with:")
        logger.info("   journalctl -u guardian-ai.service -f")
        logger.info("   journalctl -u conquest-ai.service -f")
        
        return service_status

def main():
    """Main entry point"""
    fixer = GuardianConquestFixer()
    results = fixer.run_comprehensive_fix()
    
    # Save results to file
    with open("guardian_conquest_fix_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("📄 Fix results saved to guardian_conquest_fix_results.json")

if __name__ == "__main__":
    main() 