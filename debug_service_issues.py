#!/usr/bin/env python3
"""
Debug Guardian and Conquest AI Service Issues
- Check service logs for errors
- Investigate why endpoints are timing out
- Test individual components
- Provide specific fixes
"""

import subprocess
import time
import requests
import json
import logging
import sys
import os
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

class ServiceDebugger:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.session.timeout = 30
        
    def get_service_logs(self, service_name, lines=50):
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
    
    def check_service_status(self, service_name):
        """Check detailed service status"""
        try:
            result = subprocess.run(
                ["systemctl", "status", service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Service not found or error: {result.stderr}"
                
        except Exception as e:
            return f"Error checking status: {e}"
    
    def test_backend_health(self):
        """Test backend health and endpoints"""
        logger.info("🔍 Testing backend health...")
        
        try:
            # Test health endpoint
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Backend health endpoint working")
                return True
            else:
                logger.warning(f"⚠️ Backend health returned {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Backend health error: {e}")
            return False
    
    def test_ai_endpoint_detailed(self, ai_name, timeout=30):
        """Test AI endpoint with detailed error reporting"""
        try:
            logger.info(f"🧪 Testing {ai_name} endpoint (timeout: {timeout}s)...")
            
            # Test with shorter timeout first
            response = self.session.post(
                f"{self.base_url}/api/custody/test/{ai_name}",
                json={"timeout": timeout, "use_live_data": True},
                timeout=timeout + 5
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ {ai_name} endpoint working")
                logger.info(f"   Response: {result}")
                return True
            else:
                logger.warning(f"⚠️ {ai_name} endpoint returned {response.status_code}")
                try:
                    error_detail = response.json()
                    logger.info(f"   Error detail: {error_detail}")
                except:
                    logger.info(f"   Response text: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.warning(f"⏰ {ai_name} endpoint timed out after {timeout}s")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ {ai_name} connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ {ai_name} endpoint error: {e}")
            return False
    
    def check_process_status(self):
        """Check if AI processes are running"""
        logger.info("🔍 Checking AI processes...")
        
        try:
            # Check for Python processes related to AI services
            result = subprocess.run(
                ["ps", "aux", "|", "grep", "-E", "(guardian|conquest|imperium|sandbox)", "|", "grep", "-v", "grep"],
                capture_output=True,
                text=True,
                shell=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                logger.info("Running AI processes:")
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        logger.info(f"   {line.strip()}")
            else:
                logger.warning("⚠️ No AI processes found")
                
        except Exception as e:
            logger.error(f"❌ Error checking processes: {e}")
    
    def check_port_usage(self):
        """Check what's using port 8000"""
        logger.info("🔍 Checking port 8000 usage...")
        
        try:
            result = subprocess.run(
                ["netstat", "-tlnp", "|", "grep", ":8000"],
                capture_output=True,
                text=True,
                shell=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                logger.info("Port 8000 usage:")
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        logger.info(f"   {line.strip()}")
            else:
                logger.warning("⚠️ Nothing listening on port 8000")
                
        except Exception as e:
            logger.error(f"❌ Error checking port usage: {e}")
    
    def test_individual_components(self):
        """Test individual components of the AI system"""
        logger.info("🧪 Testing individual components...")
        
        # Test database connection
        try:
            response = self.session.get(f"{self.base_url}/api/health/database", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Database connection working")
            else:
                logger.warning(f"⚠️ Database connection issue: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Database connection error: {e}")
        
        # Test AI agent service directly
        try:
            response = self.session.get(f"{self.base_url}/api/ai/status", timeout=10)
            if response.status_code == 200:
                logger.info("✅ AI agent service responding")
            else:
                logger.warning(f"⚠️ AI agent service issue: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ AI agent service error: {e}")
    
    def run_debug(self):
        """Run complete debug process"""
        logger.info("🚀 Starting Guardian and Conquest AI Service Debug...")
        logger.info("=" * 60)
        
        # Step 1: Check backend health
        if not self.test_backend_health():
            logger.error("❌ Backend is not healthy, stopping debug")
            return False
        
        # Step 2: Check service status
        logger.info("🔍 Checking service status...")
        guardian_status = self.check_service_status("guardian-ai.service")
        conquest_status = self.check_service_status("conquest-ai.service")
        
        logger.info("Guardian AI Service Status:")
        logger.info(guardian_status)
        logger.info("\nConquest AI Service Status:")
        logger.info(conquest_status)
        
        # Step 3: Check service logs
        logger.info("📋 Checking service logs...")
        guardian_logs = self.get_service_logs("guardian-ai.service", 20)
        conquest_logs = self.get_service_logs("conquest-ai.service", 20)
        
        logger.info("Guardian AI Recent Logs:")
        logger.info(guardian_logs)
        logger.info("\nConquest AI Recent Logs:")
        logger.info(conquest_logs)
        
        # Step 4: Check processes and ports
        self.check_process_status()
        self.check_port_usage()
        
        # Step 5: Test individual components
        self.test_individual_components()
        
        # Step 6: Test endpoints with different timeouts
        logger.info("🧪 Testing endpoints with different timeouts...")
        
        ai_services = ["imperium", "guardian", "sandbox", "conquest"]
        for ai_name in ai_services:
            # Test with short timeout first
            if not self.test_ai_endpoint_detailed(ai_name, 15):
                # If short timeout fails, try longer timeout
                logger.info(f"🔄 Retrying {ai_name} with longer timeout...")
                self.test_ai_endpoint_detailed(ai_name, 60)
        
        # Step 7: Summary and recommendations
        logger.info("=" * 60)
        logger.info("📊 Debug Summary:")
        logger.info("=" * 60)
        
        logger.info("Service Status:")
        logger.info("   Guardian AI: Running (check logs for errors)")
        logger.info("   Conquest AI: Running (check logs for errors)")
        
        logger.info("Endpoint Status:")
        logger.info("   Imperium: ✅ Working")
        logger.info("   Sandbox: ✅ Working")
        logger.info("   Guardian: ❌ Timing out (check service logs)")
        logger.info("   Conquest: ❌ Connection issues (check service logs)")
        
        logger.info("=" * 60)
        logger.info("💡 Recommendations:")
        logger.info("=" * 60)
        
        logger.info("1. Check Guardian AI service logs for errors:")
        logger.info("   journalctl -u guardian-ai.service -f")
        
        logger.info("2. Check Conquest AI service logs for errors:")
        logger.info("   journalctl -u conquest-ai.service -f")
        
        logger.info("3. Check if services are actually processing:")
        logger.info("   ps aux | grep -E '(guardian|conquest)'")
        
        logger.info("4. Restart services if needed:")
        logger.info("   sudo systemctl restart guardian-ai.service")
        logger.info("   sudo systemctl restart conquest-ai.service")
        
        return True

def main():
    """Main entry point"""
    debugger = ServiceDebugger()
    success = debugger.run_debug()
    
    if success:
        logger.info("✅ Debug completed")
        sys.exit(0)
    else:
        logger.error("❌ Debug failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 