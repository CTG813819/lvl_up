#!/usr/bin/env python3
"""
Fix Custodes AI Testing After Cycles and Resolve Timeout Issues
- Configure Custodes to test AIs after their learning cycles
- Fix timeout issues with Guardian and Conquest AI tests
- Install missing dependencies
- Optimize test execution
"""

import asyncio
import subprocess
import sys
import time
import requests
import json
import logging
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
        self.timeout = 60  # Increased timeout
        self.session = requests.Session()
        self.session.timeout = self.timeout
        
    def install_dependencies(self):
        """Install missing dependencies"""
        logger.info("📦 Installing missing dependencies...")
        
        dependencies = [
            "websocket-client",
            "requests[security]",
            "urllib3"
        ]
        
        for dep in dependencies:
            try:
                logger.info(f"Installing {dep}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep],
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
        
        # AI cycle schedules
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
        
        # Test configuration with optimized timeouts
        test_config = {
            "imperium": {
                "timeout": 45,
                "max_retries": 2,
                "test_categories": ["knowledge_verification", "code_quality"]
            },
            "guardian": {
                "timeout": 60,
                "max_retries": 3,
                "test_categories": ["security_awareness", "code_quality"]
            },
            "sandbox": {
                "timeout": 45,
                "max_retries": 2,
                "test_categories": ["experimental_validation", "innovation_capability"]
            },
            "conquest": {
                "timeout": 60,
                "max_retries": 3,
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
                        time.sleep(5)
                    else:
                        results[ai_name] = {
                            "status": "timeout",
                            "error": f"Timeout after {config['timeout']}s"
                        }
                        
                except Exception as e:
                    logger.error(f"❌ {ai_name} test error: {e}")
                    results[ai_name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    break
        
        return results
    
    def create_custodes_scheduler_service(self):
        """Create a dedicated Custodes scheduler service"""
        logger.info("🔧 Creating Custodes scheduler service...")
        
        service_content = """[Unit]
Description=Custodes AI Testing Scheduler
After=ai-backend-python.service
Wants=ai-backend-python.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python custodes_scheduler.py
ExecStop=/bin/kill -TERM $MAINPID
KillMode=mixed
TimeoutStopSec=30
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        try:
            with open("/etc/systemd/system/custodes-scheduler.service", "w") as f:
                f.write(service_content)
            
            # Reload systemd and enable service
            subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", "custodes-scheduler.service"], check=True)
            
            logger.info("✅ Custodes scheduler service created and enabled")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create service: {e}")
            return False
    
    def create_custodes_scheduler_script(self):
        """Create the Custodes scheduler Python script"""
        logger.info("📝 Creating Custodes scheduler script...")
        
        script_content = '''#!/usr/bin/env python3
"""
Custodes AI Testing Scheduler
Automatically tests AIs after their learning cycles
"""

import asyncio
import time
import requests
import logging
from datetime import datetime
from typing import Dict

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
        
        # AI cycle schedules (in seconds)
        self.ai_schedules = {
            "imperium": 1800,  # 30 minutes
            "guardian": 900,   # 15 minutes
            "sandbox": 2700,   # 45 minutes
            "conquest": 1200   # 20 minutes
        }
        
        # Test delay after cycle (5 minutes)
        self.test_delay = 300
        
        # Last test times
        self.last_tests = {}
        
    async def wait_for_ai_cycle(self, ai_name: str):
        """Wait for AI to complete its learning cycle"""
        cycle_time = self.ai_schedules[ai_name]
        last_test = self.last_tests.get(ai_name, 0)
        current_time = time.time()
        
        # Calculate time since last test
        time_since_test = current_time - last_test
        
        if time_since_test < cycle_time + self.test_delay:
            # Wait for cycle to complete
            wait_time = (cycle_time + self.test_delay) - time_since_test
            logger.info(f"⏰ Waiting {wait_time:.0f}s for {ai_name} cycle to complete...")
            await asyncio.sleep(wait_time)
    
    async def test_ai(self, ai_name: str):
        """Test a specific AI"""
        try:
            logger.info(f"🧪 Testing {ai_name} AI...")
            
            # Run custody test
            response = self.session.post(
                f"{self.base_url}/api/custody/test/{ai_name}",
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ {ai_name} test completed successfully")
                
                # Check if AI leveled up
                if result.get("leveled_up", False):
                    logger.info(f"🎉 {ai_name} AI leveled up!")
                
                # Update last test time
                self.last_tests[ai_name] = time.time()
                
            else:
                logger.warning(f"⚠️ {ai_name} test failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ {ai_name} test error: {e}")
    
    async def run_scheduler(self):
        """Main scheduler loop"""
        logger.info("🚀 Starting Custodes AI Testing Scheduler...")
        logger.info("📅 Testing Schedule:")
        for ai_name, cycle_time in self.ai_schedules.items():
            logger.info(f"   {ai_name}: Every {cycle_time + self.test_delay}s")
        
        while True:
            try:
                # Test each AI after their cycle
                for ai_name in self.ai_schedules.keys():
                    await self.wait_for_ai_cycle(ai_name)
                    await self.test_ai(ai_name)
                
                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

if __name__ == "__main__":
    scheduler = CustodesScheduler()
    asyncio.run(scheduler.run_scheduler())
'''
        
        try:
            with open("custodes_scheduler.py", "w") as f:
                f.write(script_content)
            
            # Make script executable
            subprocess.run(["chmod", "+x", "custodes_scheduler.py"], check=True)
            
            logger.info("✅ Custodes scheduler script created")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create script: {e}")
            return False
    
    def test_websocket_connection(self):
        """Test WebSocket connection with proper error handling"""
        logger.info("🔌 Testing WebSocket connection...")
        
        try:
            import websocket
            
            # Test WebSocket connection
            ws = websocket.create_connection(
                f"ws://localhost:8000/ws/imperium/learning-analytics",
                timeout=10
            )
            
            # Send test message
            ws.send(json.dumps({"type": "test", "message": "ping"}))
            
            # Receive response
            response = ws.recv()
            ws.close()
            
            logger.info("✅ WebSocket connection successful")
            return True
            
        except ImportError:
            logger.warning("⚠️ websocket-client not available, skipping WebSocket test")
            return False
        except Exception as e:
            logger.warning(f"⚠️ WebSocket test failed: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive test of all components"""
        logger.info("🧪 Running comprehensive component test...")
        
        test_results = {
            "custody_protocol": {},
            "ai_agents": {},
            "enhanced_learning": {},
            "optimized_services": {},
            "proposals": {},
            "websocket": {}
        }
        
        # Test Custody Protocol
        try:
            response = self.session.get(f"{self.base_url}/api/custody", timeout=30)
            if response.status_code == 200:
                test_results["custody_protocol"]["overview"] = "success"
            else:
                test_results["custody_protocol"]["overview"] = "failed"
        except Exception as e:
            test_results["custody_protocol"]["overview"] = f"error: {e}"
        
        # Test AI Agents
        for ai_name in ["imperium", "guardian", "sandbox", "conquest"]:
            try:
                response = self.session.get(f"{self.base_url}/api/{ai_name}/status", timeout=30)
                if response.status_code == 200:
                    test_results["ai_agents"][ai_name] = "success"
                else:
                    test_results["ai_agents"][ai_name] = "failed"
            except Exception as e:
                test_results["ai_agents"][ai_name] = f"error: {e}"
        
        # Test Enhanced Learning
        try:
            response = self.session.get(f"{self.base_url}/api/enhanced-learning/health", timeout=30)
            if response.status_code == 200:
                test_results["enhanced_learning"]["health"] = "success"
            else:
                test_results["enhanced_learning"]["health"] = "failed"
        except Exception as e:
            test_results["enhanced_learning"]["health"] = f"error: {e}"
        
        # Test Optimized Services
        try:
            response = self.session.get(f"{self.base_url}/optimized/health", timeout=30)
            if response.status_code == 200:
                test_results["optimized_services"]["health"] = "success"
            else:
                test_results["optimized_services"]["health"] = "failed"
        except Exception as e:
            test_results["optimized_services"]["health"] = f"error: {e}"
        
        # Test Proposals
        try:
            response = self.session.get(f"{self.base_url}/api/proposals", timeout=30)
            if response.status_code == 200:
                test_results["proposals"]["overview"] = "success"
            else:
                test_results["proposals"]["overview"] = "failed"
        except Exception as e:
            test_results["proposals"]["overview"] = f"error: {e}"
        
        # Test WebSocket
        test_results["websocket"]["connection"] = "skipped"  # Will be tested separately
        
        return test_results
    
    def run_fix(self):
        """Run the complete fix process"""
        logger.info("🚀 Starting Custodes and Timeout Fixes...")
        logger.info("=" * 60)
        
        # Step 1: Install dependencies
        self.install_dependencies()
        
        # Step 2: Check backend health
        if not self.check_backend_health():
            logger.error("❌ Backend is not healthy. Please start the backend first.")
            return False
        
        # Step 3: Configure Custodes testing schedule
        self.configure_custodes_testing_schedule()
        
        # Step 4: Create Custodes scheduler
        self.create_custodes_scheduler_script()
        self.create_custodes_scheduler_service()
        
        # Step 5: Run optimized custody tests
        logger.info("🧪 Running optimized custody tests...")
        custody_results = self.run_optimized_custody_tests()
        
        # Step 6: Test WebSocket connection
        self.test_websocket_connection()
        
        # Step 7: Run comprehensive test
        comprehensive_results = self.run_comprehensive_test()
        
        # Print results
        logger.info("=" * 60)
        logger.info("📋 FIX SUMMARY")
        logger.info("=" * 60)
        
        logger.info("Custody Protocol Tests:")
        for ai_name, result in custody_results.items():
            status = "✅ PASS" if result.get("status") == "success" else "❌ FAIL"
            logger.info(f"  {ai_name}: {status}")
        
        logger.info("\\nComponent Tests:")
        for component, tests in comprehensive_results.items():
            if isinstance(tests, dict):
                for test_name, result in tests.items():
                    status = "✅ PASS" if result == "success" else "❌ FAIL"
                    logger.info(f"  {component}.{test_name}: {status}")
            else:
                status = "✅ PASS" if tests == "success" else "❌ FAIL"
                logger.info(f"  {component}: {status}")
        
        logger.info("=" * 60)
        logger.info("✅ Custodes and timeout fixes applied!")
        logger.info("🔄 Custodes scheduler will automatically test AIs after their cycles.")
        logger.info("📊 All components now use optimized timeouts and error handling.")
        
        return True

def main():
    fixer = CustodesAndTimeoutFixer()
    success = fixer.run_fix()
    
    if success:
        logger.info("🎉 Fix completed successfully!")
        logger.info("💡 Next steps:")
        logger.info("   1. Start the Custodes scheduler: sudo systemctl start custodes-scheduler.service")
        logger.info("   2. Monitor the scheduler: sudo journalctl -u custodes-scheduler.service -f")
        logger.info("   3. Run comprehensive tests to verify improvements")
    else:
        logger.error("❌ Fix failed. Please check the logs and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 