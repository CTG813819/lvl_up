#!/usr/bin/env python3
"""
AI Performance Diagnostic Tool
- Investigate Guardian and Conquest AI timeout issues
- Check backend endpoints and response times
- Analyze AI service status and health
"""

import requests
import time
import json
import logging
import subprocess
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

class AIPerformanceDiagnostic:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.session.timeout = 30
        
    def check_backend_endpoints(self):
        """Check all available backend endpoints"""
        logger.info("🔍 Checking backend endpoints...")
        
        endpoints = [
            "/api/health",
            "/api/ai/imperium/status",
            "/api/ai/guardian/status", 
            "/api/ai/sandbox/status",
            "/api/ai/conquest/status",
            "/api/custody/test/imperium",
            "/api/custody/test/guardian",
            "/api/custody/test/sandbox", 
            "/api/custody/test/conquest",
            "/api/custody/configure",
            "/api/websocket/status"
        ]
        
        results = {}
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                elapsed_time = time.time() - start_time
                
                results[endpoint] = {
                    "status_code": response.status_code,
                    "response_time": elapsed_time,
                    "available": True
                }
                
                if response.status_code == 200:
                    logger.info(f"✅ {endpoint}: {response.status_code} ({elapsed_time:.2f}s)")
                else:
                    logger.warning(f"⚠️ {endpoint}: {response.status_code} ({elapsed_time:.2f}s)")
                    
            except Exception as e:
                results[endpoint] = {
                    "status_code": None,
                    "response_time": None,
                    "available": False,
                    "error": str(e)
                }
                logger.error(f"❌ {endpoint}: {e}")
        
        return results
    
    def check_ai_service_status(self):
        """Check individual AI service status"""
        logger.info("🤖 Checking AI service status...")
        
        ai_services = ["imperium", "guardian", "sandbox", "conquest"]
        results = {}
        
        for ai_name in ai_services:
            try:
                # Check AI status endpoint
                response = self.session.get(f"{self.base_url}/api/ai/{ai_name}/status", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    results[ai_name] = {
                        "status": "available",
                        "data": data,
                        "response_time": response.elapsed.total_seconds()
                    }
                    logger.info(f"✅ {ai_name}: Available ({response.elapsed.total_seconds():.2f}s)")
                    logger.info(f"   Status: {data.get('status', 'unknown')}")
                    logger.info(f"   Cycle: {data.get('cycle_completed', 'unknown')}")
                else:
                    results[ai_name] = {
                        "status": "error",
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds()
                    }
                    logger.warning(f"⚠️ {ai_name}: HTTP {response.status_code}")
                    
            except Exception as e:
                results[ai_name] = {
                    "status": "error",
                    "error": str(e)
                }
                logger.error(f"❌ {ai_name}: {e}")
        
        return results
    
    def test_ai_response_times(self):
        """Test AI response times with different timeouts"""
        logger.info("⏱️ Testing AI response times...")
        
        ai_services = ["imperium", "guardian", "sandbox", "conquest"]
        timeouts = [10, 30, 60, 120, 180]
        results = {}
        
        for ai_name in ai_services:
            results[ai_name] = {}
            
            for timeout in timeouts:
                try:
                    logger.info(f"🧪 Testing {ai_name} with {timeout}s timeout...")
                    start_time = time.time()
                    
                    response = self.session.post(
                        f"{self.base_url}/api/custody/test/{ai_name}",
                        json={"timeout": timeout},
                        timeout=timeout + 5
                    )
                    
                    elapsed_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        results[ai_name][timeout] = {
                            "status": "success",
                            "response_time": elapsed_time,
                            "data": response.json()
                        }
                        logger.info(f"✅ {ai_name} ({timeout}s): Success in {elapsed_time:.2f}s")
                        break  # Found working timeout, stop testing
                    else:
                        results[ai_name][timeout] = {
                            "status": "error",
                            "status_code": response.status_code,
                            "response_time": elapsed_time
                        }
                        logger.warning(f"⚠️ {ai_name} ({timeout}s): HTTP {response.status_code}")
                        
                except requests.exceptions.Timeout:
                    results[ai_name][timeout] = {
                        "status": "timeout",
                        "response_time": timeout
                    }
                    logger.warning(f"⏰ {ai_name} ({timeout}s): Timed out")
                    
                except Exception as e:
                    results[ai_name][timeout] = {
                        "status": "error",
                        "error": str(e)
                    }
                    logger.error(f"❌ {ai_name} ({timeout}s): {e}")
        
        return results
    
    def check_system_resources(self):
        """Check system resources that might affect AI performance"""
        logger.info("💻 Checking system resources...")
        
        try:
            # Check CPU usage
            cpu_result = subprocess.run(
                ["top", "-bn1", "|", "grep", "Cpu(s)"],
                capture_output=True,
                text=True,
                shell=True,
                timeout=10
            )
            
            # Check memory usage
            mem_result = subprocess.run(
                ["free", "-h"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Check disk usage
            disk_result = subprocess.run(
                ["df", "-h"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            logger.info("📊 System Resources:")
            if cpu_result.stdout:
                logger.info(f"CPU: {cpu_result.stdout.strip()}")
            if mem_result.stdout:
                logger.info(f"Memory:\n{mem_result.stdout.strip()}")
            if disk_result.stdout:
                logger.info(f"Disk:\n{disk_result.stdout.strip()}")
                
        except Exception as e:
            logger.error(f"❌ Error checking system resources: {e}")
    
    def check_backend_logs(self):
        """Check recent backend logs for errors"""
        logger.info("📋 Checking recent backend logs...")
        
        try:
            # Check if there are any recent error logs
            log_result = subprocess.run(
                ["journalctl", "-u", "guardian-ai.service", "--since", "10 minutes ago", "-n", "20"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if log_result.stdout:
                logger.info("Recent Guardian AI logs:")
                for line in log_result.stdout.strip().split('\n')[-10:]:
                    if 'ERROR' in line or 'WARNING' in line:
                        logger.warning(f"   {line}")
            
            # Check conquest logs
            conquest_log_result = subprocess.run(
                ["journalctl", "-u", "conquest-ai.service", "--since", "10 minutes ago", "-n", "20"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if conquest_log_result.stdout:
                logger.info("Recent Conquest AI logs:")
                for line in conquest_log_result.stdout.strip().split('\n')[-10:]:
                    if 'ERROR' in line or 'WARNING' in line:
                        logger.warning(f"   {line}")
                        
        except Exception as e:
            logger.error(f"❌ Error checking logs: {e}")
    
    def run_diagnostic(self):
        """Run complete diagnostic"""
        logger.info("🚀 Starting AI Performance Diagnostic...")
        logger.info("=" * 60)
        
        # Step 1: Check backend endpoints
        endpoint_results = self.check_backend_endpoints()
        
        # Step 2: Check AI service status
        ai_status_results = self.check_ai_service_status()
        
        # Step 3: Test AI response times
        response_time_results = self.test_ai_response_times()
        
        # Step 4: Check system resources
        self.check_system_resources()
        
        # Step 5: Check backend logs
        self.check_backend_logs()
        
        # Step 6: Summary and recommendations
        logger.info("=" * 60)
        logger.info("📊 Diagnostic Summary:")
        logger.info("=" * 60)
        
        # Endpoint availability
        available_endpoints = sum(1 for r in endpoint_results.values() if r.get("available", False))
        total_endpoints = len(endpoint_results)
        logger.info(f"Backend Endpoints: {available_endpoints}/{total_endpoints} available")
        
        # AI service status
        working_ais = sum(1 for r in ai_status_results.values() if r.get("status") == "available")
        total_ais = len(ai_status_results)
        logger.info(f"AI Services: {working_ais}/{total_ais} working")
        
        # Response time analysis
        logger.info("Response Time Analysis:")
        for ai_name, results in response_time_results.items():
            working_timeout = None
            for timeout, result in results.items():
                if result.get("status") == "success":
                    working_timeout = timeout
                    break
            
            if working_timeout:
                logger.info(f"   {ai_name}: ✅ Works with {working_timeout}s timeout")
            else:
                logger.info(f"   {ai_name}: ❌ No working timeout found")
        
        # Recommendations
        logger.info("=" * 60)
        logger.info("💡 Recommendations:")
        logger.info("=" * 60)
        
        if response_time_results.get("guardian", {}).get(180, {}).get("status") != "success":
            logger.info("1. Guardian AI needs longer timeout or performance optimization")
            logger.info("   - Consider increasing timeout to 300s (5 minutes)")
            logger.info("   - Check Guardian AI service logs for bottlenecks")
        
        if response_time_results.get("conquest", {}).get(180, {}).get("status") != "success":
            logger.info("2. Conquest AI has connection issues")
            logger.info("   - Check Conquest AI service status")
            logger.info("   - Verify network connectivity")
            logger.info("   - Review Conquest AI logs for errors")
        
        if not endpoint_results.get("/api/custody/configure", {}).get("available", False):
            logger.info("3. Custodes configuration endpoint not available")
            logger.info("   - This is expected if Custodes service is not running")
            logger.info("   - The scheduler will work without this endpoint")
        
        return {
            "endpoints": endpoint_results,
            "ai_status": ai_status_results,
            "response_times": response_time_results
        }

def main():
    """Main entry point"""
    diagnostic = AIPerformanceDiagnostic()
    results = diagnostic.run_diagnostic()
    
    # Save results to file
    with open("ai_diagnostic_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("📄 Diagnostic results saved to ai_diagnostic_results.json")

if __name__ == "__main__":
    main() 