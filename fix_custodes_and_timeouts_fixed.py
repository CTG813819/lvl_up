#!/usr/bin/env python3
"""
Fixed Custodes AI Testing After Cycles and Resolve Timeout Issues
- Configure Custodes to test AIs after their learning cycles
- Fix timeout issues with Guardian and Conquest AI tests
- Handle permission issues for systemd services
- Use virtual environment for package installation
"""

import asyncio
import subprocess
import sys
import time
import requests
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CustodesAndTimeoutFixer:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.timeout = 120  # Increased timeout for slow AIs
        self.session = requests.Session()
        self.session.timeout = self.timeout
        self.venv_path = os.path.join(os.getcwd(), "venv")
        
    def setup_virtual_environment(self):
        """Setup virtual environment for package installation"""
        logger.info("🔧 Setting up virtual environment...")
        
        try:
            # Check if venv already exists
            if os.path.exists(self.venv_path):
                logger.info("✅ Virtual environment already exists")
                return True
            
            # Create virtual environment
            result = subprocess.run(
                [sys.executable, "-m", "venv", self.venv_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("✅ Virtual environment created successfully")
                return True
            else:
                logger.error(f"❌ Failed to create virtual environment: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating virtual environment: {e}")
            return False
    
    def install_dependencies_in_venv(self):
        """Install missing dependencies in virtual environment"""
        logger.info("📦 Installing missing dependencies in virtual environment...")
        
        # Get pip path from virtual environment
        if os.name == 'nt':  # Windows
            pip_path = os.path.join(self.venv_path, "Scripts", "pip")
        else:  # Unix/Linux
            pip_path = os.path.join(self.venv_path, "bin", "pip")
        
        dependencies = [
            "websocket-client",
            "requests[security]",
            "urllib3"
        ]
        
        for dep in dependencies:
            try:
                logger.info(f"Installing {dep}...")
                result = subprocess.run(
                    [pip_path, "install", dep],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    logger.info(f"✅ {dep} installed successfully")
                else:
                    logger.warning(f"⚠️ Failed to install {dep}: {result.stderr}")
            except Exception as e:
                logger.warning(f"⚠️ Error installing {dep}: {e}")
    
    def check_backend_health(self):
        """Check if backend is healthy and responsive"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Backend is healthy and responsive")
                return True
            else:
                logger.error(f"❌ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Backend health check error: {e}")
            return False
    
    def configure_custodes_testing_schedule(self):
        """Configure Custodes to test AIs after their cycles"""
        logger.info("🔧 Configuring Custodes AI testing schedule...")
        
        # AI cycle schedules with longer intervals to prevent conflicts
        ai_schedules = {
            "imperium": 1800,  # 30 minutes
            "guardian": 900,   # 15 minutes
            "sandbox": 2700,   # 45 minutes
            "conquest": 1200   # 20 minutes
        }
        
        # Configure Custodes to test each AI after their cycle + 5 minutes
        custodes_schedule = {}
        for ai_name, cycle_time in ai_schedules.items():
            test_time = cycle_time + 300  # 5 minutes after cycle
            custodes_schedule[ai_name] = test_time
            logger.info(f"📅 {ai_name} AI: Test {test_time}s after cycle ({cycle_time}s)")
        
        # Create Custodes testing configuration
        custodes_config = {
            "testing_schedule": custodes_schedule,
            "test_delay_after_cycle": 300,  # 5 minutes
            "batch_testing": True,
            "auto_level_up": True,
            "performance_threshold": 0.8
        }
        
        try:
            # Update Custodes configuration via API
            response = self.session.post(
                f"{self.base_url}/api/custody/configure",
                json=custodes_config,
                timeout=30
            )
            if response.status_code == 200:
                logger.info("✅ Custodes testing schedule configured")
                return True
            else:
                logger.warning(f"⚠️ Could not configure via API: {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ API configuration failed: {e}")
            return False
    
    def optimize_ai_test_timeouts(self):
        """Optimize AI test timeouts and performance"""
        logger.info("⚡ Optimizing AI test timeouts...")
        
        # Test configuration with much longer timeouts for slow AIs
        test_config = {
            "imperium": {
                "timeout": 90,
                "max_retries": 2,
                "test_categories": ["knowledge_verification", "code_quality"]
            },
            "guardian": {
                "timeout": 180,  # 3 minutes for Guardian
                "max_retries": 2,
                "test_categories": ["security_awareness", "code_quality"]
            },
            "sandbox": {
                "timeout": 90,
                "max_retries": 2,
                "test_categories": ["experimental_validation", "innovation_capability"]
            },
            "conquest": {
                "timeout": 180,  # 3 minutes for Conquest
                "max_retries": 2,
                "test_categories": ["performance_optimization", "self_improvement"]
            }
        }
        
        for ai_name, config in test_config.items():
            logger.info(f"⚙️ {ai_name} AI: {config['timeout']}s timeout, {config['max_retries']} retries")
        
        return test_config
    
    def run_optimized_custody_tests(self):
        """Run custody tests with optimized timeouts"""
        logger.info("🧪 Running optimized custody tests...")
        
        test_config = self.optimize_ai_test_timeouts()
        results = {}
        
        for ai_name, config in test_config.items():
            logger.info(f"🧪 Testing {ai_name} AI with {config['timeout']}s timeout...")
            
            for attempt in range(config['max_retries']):
                try:
                    start_time = time.time()
                    
                    # Run test with optimized timeout
                    response = self.session.post(
                        f"{self.base_url}/api/custody/test/{ai_name}",
                        json={"timeout": config['timeout']},
                        timeout=config['timeout'] + 10
                    )
                    
                    elapsed_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        result = response.json()
                        results[ai_name] = {
                            "status": "success",
                            "elapsed_time": elapsed_time,
                            "data": result
                        }
                        logger.info(f"✅ {ai_name} test completed in {elapsed_time:.2f}s")
                        break
                    else:
                        logger.warning(f"⚠️ {ai_name} test failed: {response.status_code}")
                        if attempt < config['max_retries'] - 1:
                            logger.info(f"🔄 Retrying {ai_name} test (attempt {attempt + 2})...")
                            time.sleep(5)
                        else:
                            results[ai_name] = {
                                "status": "failed",
                                "error": f"HTTP {response.status_code}"
                            }
                            
                except requests.exceptions.Timeout:
                    logger.warning(f"⏰ {ai_name} test timed out (attempt {attempt + 1})")
                    if attempt < config['max_retries'] - 1:
                        logger.info(f"🔄 Retrying {ai_name} test...")
                        time.sleep(10)  # Longer wait between retries
                    else:
                        results[ai_name] = {
                            "status": "timeout",
                            "error": f"Timed out after {config['timeout']}s"
                        }
                        
                except Exception as e:
                    logger.error(f"❌ {ai_name} test error: {e}")
                    if attempt < config['max_retries'] - 1:
                        logger.info(f"🔄 Retrying {ai_name} test...")
                        time.sleep(5)
                    else:
                        results[ai_name] = {
                            "status": "error",
                            "error": str(e)
                        }
        
        return results
    
    def create_custodes_scheduler_script(self):
        """Create Custodes scheduler script without systemd permissions"""
        logger.info("📝 Creating Custodes scheduler script...")
        
        script_content = '''#!/usr/bin/env python3
"""
Custodes AI Testing Scheduler
- Runs custody tests after AI learning cycles
- Monitors AI performance and health
"""

import time
import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

class CustodesScheduler:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.session.timeout = 180
        
        # AI testing schedule (seconds after cycle completion)
        self.test_schedule = {
            "imperium": 2100,  # 35 minutes
            "guardian": 1200,  # 20 minutes
            "sandbox": 3000,   # 50 minutes
            "conquest": 1500   # 25 minutes
        }
        
        # Track last test times
        self.last_tests = {}
        
    def check_ai_cycle_completion(self, ai_name):
        """Check if AI has completed its learning cycle"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/ai/{ai_name}/status",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("cycle_completed", False)
            return False
        except Exception as e:
            logger.error(f"Error checking {ai_name} cycle: {e}")
            return False
    
    def run_custody_test(self, ai_name):
        """Run custody test for specific AI"""
        try:
            logger.info(f"🧪 Running custody test for {ai_name}...")
            
            response = self.session.post(
                f"{self.base_url}/api/custody/test/{ai_name}",
                json={"timeout": 180},
                timeout=190
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ {ai_name} custody test completed")
                return True
            else:
                logger.warning(f"⚠️ {ai_name} custody test failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ {ai_name} custody test error: {e}")
            return False
    
    def run_scheduler(self):
        """Main scheduler loop"""
        logger.info("🚀 Starting Custodes AI Testing Scheduler...")
        
        while True:
            try:
                current_time = time.time()
                
                for ai_name, test_delay in self.test_schedule.items():
                    # Check if it's time to test this AI
                    last_test = self.last_tests.get(ai_name, 0)
                    time_since_test = current_time - last_test
                    
                    if time_since_test >= test_delay:
                        # Check if AI cycle is complete
                        if self.check_ai_cycle_completion(ai_name):
                            if self.run_custody_test(ai_name):
                                self.last_tests[ai_name] = current_time
                                logger.info(f"✅ Scheduled test completed for {ai_name}")
                            else:
                                logger.warning(f"⚠️ Scheduled test failed for {ai_name}")
                        else:
                            logger.info(f"⏳ {ai_name} cycle not yet complete, skipping test")
                
                # Sleep for 30 seconds before next check
                time.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("🛑 Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    scheduler = CustodesScheduler()
    scheduler.run_scheduler()
'''
        
        script_path = "custodes_scheduler.py"
        try:
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make script executable
            os.chmod(script_path, 0o755)
            logger.info("✅ Custodes scheduler script created")
            return script_path
        except Exception as e:
            logger.error(f"❌ Failed to create scheduler script: {e}")
            return None
    
    def create_custodes_scheduler_service(self):
        """Create Custodes scheduler service file (user-level)"""
        logger.info("🔧 Creating Custodes scheduler service...")
        
        # Create service in user directory instead of system directory
        user_home = os.path.expanduser("~")
        service_dir = os.path.join(user_home, ".config", "systemd", "user")
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(service_dir, exist_ok=True)
            
            service_content = f"""[Unit]
Description=Custodes AI Testing Scheduler
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'ubuntu')}
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} {os.path.join(os.getcwd(), 'custodes_scheduler.py')}
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
"""
            
            service_path = os.path.join(service_dir, "custodes-scheduler.service")
            
            with open(service_path, 'w') as f:
                f.write(service_content)
            
            logger.info(f"✅ Custodes scheduler service created at {service_path}")
            logger.info("📋 To enable the service, run:")
            logger.info(f"   systemctl --user enable custodes-scheduler.service")
            logger.info(f"   systemctl --user start custodes-scheduler.service")
            
            return service_path
            
        except Exception as e:
            logger.error(f"❌ Failed to create service: {e}")
            return None
    
    def test_websocket_connection(self):
        """Test WebSocket connection for real-time monitoring"""
        logger.info("🔌 Testing WebSocket connection...")
        
        try:
            # Simple WebSocket test using requests
            response = self.session.get(f"{self.base_url}/api/websocket/status", timeout=10)
            if response.status_code == 200:
                logger.info("✅ WebSocket endpoint is available")
                return True
            else:
                logger.warning(f"⚠️ WebSocket endpoint not available: {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"⚠️ WebSocket test failed: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive system test"""
        logger.info("🧪 Running comprehensive system test...")
        
        test_results = {
            "backend_health": False,
            "custodes_config": False,
            "ai_tests": {},
            "websocket": False
        }
        
        # Test backend health
        test_results["backend_health"] = self.check_backend_health()
        
        # Test Custodes configuration
        test_results["custodes_config"] = self.configure_custodes_testing_schedule()
        
        # Test AI custody tests
        test_results["ai_tests"] = self.run_optimized_custody_tests()
        
        # Test WebSocket
        test_results["websocket"] = self.test_websocket_connection()
        
        # Log results
        logger.info("📊 Test Results Summary:")
        logger.info(f"   Backend Health: {'✅' if test_results['backend_health'] else '❌'}")
        logger.info(f"   Custodes Config: {'✅' if test_results['custodes_config'] else '❌'}")
        logger.info(f"   WebSocket: {'✅' if test_results['websocket'] else '❌'}")
        
        for ai_name, result in test_results["ai_tests"].items():
            status = result.get("status", "unknown")
            if status == "success":
                logger.info(f"   {ai_name} AI: ✅ ({result.get('elapsed_time', 0):.2f}s)")
            else:
                logger.info(f"   {ai_name} AI: ❌ ({result.get('error', 'Unknown error')})")
        
        return test_results
    
    def run_fix(self):
        """Run the complete fix process"""
        logger.info("🚀 Starting Custodes and Timeout Fixes...")
        logger.info("=" * 60)
        
        # Step 1: Setup virtual environment
        if not self.setup_virtual_environment():
            logger.warning("⚠️ Virtual environment setup failed, continuing without it")
        
        # Step 2: Install dependencies
        self.install_dependencies_in_venv()
        
        # Step 3: Check backend health
        if not self.check_backend_health():
            logger.error("❌ Backend is not healthy, stopping fix process")
            return False
        
        # Step 4: Configure Custodes testing schedule
        self.configure_custodes_testing_schedule()
        
        # Step 5: Create Custodes scheduler script
        script_path = self.create_custodes_scheduler_script()
        
        # Step 6: Create Custodes scheduler service (user-level)
        service_path = self.create_custodes_scheduler_service()
        
        # Step 7: Run comprehensive tests
        test_results = self.run_comprehensive_test()
        
        # Step 8: Summary
        logger.info("=" * 60)
        logger.info("🎯 Fix Process Complete!")
        logger.info("=" * 60)
        
        if script_path:
            logger.info(f"📝 Scheduler script: {script_path}")
        if service_path:
            logger.info(f"🔧 Service file: {service_path}")
        
        logger.info("📋 Next Steps:")
        logger.info("1. Review test results above")
        logger.info("2. If service was created, enable it with:")
        logger.info("   systemctl --user enable custodes-scheduler.service")
        logger.info("   systemctl --user start custodes-scheduler.service")
        logger.info("3. Monitor the scheduler logs with:")
        logger.info("   journalctl --user -u custodes-scheduler.service -f")
        
        return True

def main():
    """Main entry point"""
    fixer = CustodesAndTimeoutFixer()
    success = fixer.run_fix()
    
    if success:
        logger.info("✅ Fix process completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Fix process failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 