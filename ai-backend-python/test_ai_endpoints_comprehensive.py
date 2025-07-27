#!/usr/bin/env python3
"""
Comprehensive AI Endpoints Test
===============================

This script tests all AI endpoints and diagnoses issues including 404 errors.
"""

import os
import sys
import requests
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

class AIEndpointsTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        
    def check_backend_health(self):
        """Check if the backend is running and healthy"""
        logger.info("🔍 Checking backend health...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Backend health endpoint working")
                return True
            else:
                logger.warning(f"⚠️ Backend health returned {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error("❌ Backend not accessible")
            return False
        except Exception as e:
            logger.error(f"❌ Backend health check failed: {e}")
            return False
    
    def check_backend_routes(self):
        """Check available backend routes"""
        logger.info("🔍 Checking backend routes...")
        
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Backend docs endpoint accessible")
                # Try to get OpenAPI spec
                try:
                    openapi_response = requests.get(f"{self.base_url}/openapi.json", timeout=10)
                    if openapi_response.status_code == 200:
                        openapi_data = openapi_response.json()
                        paths = openapi_data.get('paths', {})
                        ai_routes = [path for path in paths.keys() if 'ai' in path.lower()]
                        logger.info(f"✅ Found {len(ai_routes)} AI-related routes:")
                        for route in ai_routes:
                            logger.info(f"   - {route}")
                        return ai_routes
                except Exception as e:
                    logger.warning(f"⚠️ Could not get OpenAPI spec: {e}")
            else:
                logger.warning(f"⚠️ Backend docs returned {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Could not check backend routes: {e}")
        
        return []
    
    def test_ai_endpoints(self):
        """Test all AI endpoints"""
        logger.info("🧪 Testing AI endpoints...")
        
        # Test different endpoint patterns
        endpoints_to_test = [
            # Standard AI endpoints
            ('guardian', f"{self.base_url}/api/ai/guardian/test"),
            ('conquest', f"{self.base_url}/api/ai/conquest/test"),
            ('imperium', f"{self.base_url}/api/ai/imperium/test"),
            ('sandbox', f"{self.base_url}/api/ai/sandbox/test"),
            
            # Alternative endpoint patterns
            ('guardian_alt1', f"{self.base_url}/ai/guardian/test"),
            ('conquest_alt1', f"{self.base_url}/ai/conquest/test"),
            ('guardian_alt2', f"{self.base_url}/api/guardian/test"),
            ('conquest_alt2', f"{self.base_url}/api/conquest/test"),
            
            # Direct service endpoints
            ('guardian_direct', f"{self.base_url}/guardian/test"),
            ('conquest_direct', f"{self.base_url}/conquest/test"),
        ]
        
        working_endpoints = []
        
        for name, url in endpoints_to_test:
            try:
                logger.info(f"🧪 Testing {name} endpoint: {url}")
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
                        logger.warning(f"⚠️ {name} has authentication issues")
                    else:
                        logger.info(f"✅ {name} working properly")
                    working_endpoints.append((name, url))
                elif response.status_code == 404:
                    logger.warning(f"⚠️ {name} endpoint not found (404)")
                elif response.status_code == 405:
                    logger.warning(f"⚠️ {name} method not allowed (405)")
                else:
                    logger.warning(f"⚠️ {name} returned {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ {name} endpoint timed out")
            except requests.exceptions.ConnectionError:
                logger.error(f"❌ {name} endpoint connection error")
            except Exception as e:
                logger.error(f"❌ {name} endpoint test failed: {e}")
        
        return working_endpoints
    
    def check_service_logs(self):
        """Check recent service logs for errors"""
        logger.info("📋 Checking service logs...")
        
        services = ['guardian-ai.service', 'conquest-ai.service']
        
        for service in services:
            try:
                logger.info(f"📋 Checking {service} logs...")
                result = subprocess.run(
                    ['sudo', 'journalctl', '-u', service, '--no-pager', '-n', '10'],
                    capture_output=True, text=True, check=True
                )
                
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'error' in line.lower() or '401' in line or 'failed' in line.lower():
                            logger.warning(f"   ⚠️ {line}")
                        elif 'success' in line.lower() or 'started' in line.lower():
                            logger.info(f"   ✅ {line}")
                            
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Could not check {service} logs: {e}")
    
    def check_backend_process(self):
        """Check if backend process is running"""
        logger.info("🔍 Checking backend process...")
        
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, check=True)
            lines = result.stdout.split('\n')
            
            backend_processes = []
            for line in lines:
                if 'uvicorn' in line or 'main.py' in line or 'fastapi' in line:
                    backend_processes.append(line)
            
            if backend_processes:
                logger.info("✅ Backend process found:")
                for process in backend_processes:
                    logger.info(f"   {process}")
            else:
                logger.warning("⚠️ No backend process found")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Could not check processes: {e}")
    
    def check_port_usage(self):
        """Check what's using port 8000"""
        logger.info("🔍 Checking port 8000 usage...")
        
        try:
            result = subprocess.run(['sudo', 'netstat', '-tlnp'], capture_output=True, text=True, check=True)
            lines = result.stdout.split('\n')
            
            port_8000_processes = []
            for line in lines:
                if ':8000' in line:
                    port_8000_processes.append(line)
            
            if port_8000_processes:
                logger.info("✅ Port 8000 is in use:")
                for process in port_8000_processes:
                    logger.info(f"   {process}")
            else:
                logger.warning("⚠️ Nothing listening on port 8000")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Could not check port usage: {e}")
    
    def start_backend_if_needed(self):
        """Start backend if it's not running"""
        logger.info("🚀 Checking if backend needs to be started...")
        
        try:
            # Check if backend is responding
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Backend is already running")
                return True
        except:
            pass
        
        logger.info("🔧 Backend not responding, attempting to start...")
        
        try:
            # Try to start the backend
            backend_dir = Path("/home/ubuntu/ai-backend-python")
            if (backend_dir / "main.py").exists():
                logger.info("✅ Found main.py, starting backend...")
                subprocess.run([
                    'cd', str(backend_dir), '&&',
                    'source', 'venv/bin/activate', '&&',
                    'python', 'main.py'
                ], shell=True, check=True)
                return True
            else:
                logger.warning("⚠️ main.py not found")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to start backend: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive AI endpoints test"""
        logger.info("🚀 Starting Comprehensive AI Endpoints Test...")
        logger.info("=" * 60)
        
        # Step 1: Check backend health
        if not self.check_backend_health():
            logger.warning("⚠️ Backend health check failed, trying to start backend...")
            self.start_backend_if_needed()
        
        # Step 2: Check backend routes
        ai_routes = self.check_backend_routes()
        
        # Step 3: Check backend process
        self.check_backend_process()
        
        # Step 4: Check port usage
        self.check_port_usage()
        
        # Step 5: Test AI endpoints
        working_endpoints = self.test_ai_endpoints()
        
        # Step 6: Check service logs
        self.check_service_logs()
        
        # Summary
        logger.info("=" * 60)
        logger.info("📊 Test Summary:")
        logger.info(f"   - AI routes found: {len(ai_routes)}")
        logger.info(f"   - Working endpoints: {len(working_endpoints)}")
        
        if working_endpoints:
            logger.info("✅ Working endpoints:")
            for name, url in working_endpoints:
                logger.info(f"   - {name}: {url}")
        else:
            logger.warning("⚠️ No working AI endpoints found")
            logger.info("💡 Possible issues:")
            logger.info("   1. Backend not running on port 8000")
            logger.info("   2. AI routes not properly configured")
            logger.info("   3. Endpoint paths are different")
            logger.info("   4. Services need to be restarted")
        
        return working_endpoints

def main():
    """Main function"""
    try:
        tester = AIEndpointsTester()
        working_endpoints = tester.run_comprehensive_test()
        
        if working_endpoints:
            logger.info("🎉 AI endpoints test completed successfully!")
            sys.exit(0)
        else:
            logger.warning("⚠️ No working AI endpoints found")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 