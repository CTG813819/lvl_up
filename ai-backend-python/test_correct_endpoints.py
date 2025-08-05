#!/usr/bin/env python3
"""
Test Correct AI Endpoints
=========================

This script tests the correct AI endpoints based on the actual API routes.
"""

import os
import sys
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class CorrectEndpointsTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        
    def test_custody_endpoints(self):
        """Test the custody test endpoints"""
        logger.info("🧪 Testing custody test endpoints...")
        
        ai_types = ['guardian', 'conquest', 'imperium', 'sandbox']
        
        for ai_type in ai_types:
            try:
                url = f"{self.base_url}/api/custody/test/{ai_type}"
                logger.info(f"🧪 Testing {ai_type} custody endpoint: {url}")
                
                response = requests.post(url, json={
                    'test_difficulty': 'basic',
                    'test_category': 'knowledge_verification'
                }, timeout=30)
                
                if response.status_code == 200:
                    logger.info(f"✅ {ai_type} custody endpoint working")
                    data = response.json()
                    logger.info(f"   Response: {data}")
                elif response.status_code == 404:
                    logger.warning(f"⚠️ {ai_type} custody endpoint not found (404)")
                elif response.status_code == 405:
                    logger.warning(f"⚠️ {ai_type} custody endpoint method not allowed (405)")
                else:
                    logger.warning(f"⚠️ {ai_type} custody endpoint returned {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ {ai_type} custody endpoint timed out")
            except requests.exceptions.ConnectionError:
                logger.error(f"❌ {ai_type} custody endpoint connection error")
            except Exception as e:
                logger.error(f"❌ {ai_type} custody endpoint test failed: {e}")
    
    def test_enhanced_ai_endpoints(self):
        """Test the enhanced AI endpoints"""
        logger.info("🧪 Testing enhanced AI endpoints...")
        
        ai_types = ['guardian', 'conquest', 'imperium', 'sandbox']
        
        for ai_type in ai_types:
            try:
                url = f"{self.base_url}/api/enhanced-ai/run-ai/{ai_type}"
                logger.info(f"🧪 Testing {ai_type} enhanced AI endpoint: {url}")
                
                response = requests.post(url, json={
                    'test_difficulty': 'basic',
                    'test_category': 'knowledge_verification'
                }, timeout=30)
                
                if response.status_code == 200:
                    logger.info(f"✅ {ai_type} enhanced AI endpoint working")
                    data = response.json()
                    logger.info(f"   Response: {data}")
                elif response.status_code == 404:
                    logger.warning(f"⚠️ {ai_type} enhanced AI endpoint not found (404)")
                elif response.status_code == 405:
                    logger.warning(f"⚠️ {ai_type} enhanced AI endpoint method not allowed (405)")
                else:
                    logger.warning(f"⚠️ {ai_type} enhanced AI endpoint returned {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ {ai_type} enhanced AI endpoint timed out")
            except requests.exceptions.ConnectionError:
                logger.error(f"❌ {ai_type} enhanced AI endpoint connection error")
            except Exception as e:
                logger.error(f"❌ {ai_type} enhanced AI endpoint test failed: {e}")
    
    def test_other_ai_endpoints(self):
        """Test other AI-related endpoints"""
        logger.info("🧪 Testing other AI endpoints...")
        
        endpoints_to_test = [
            ('conquest_build_failure', f"{self.base_url}/api/conquest/build-failure"),
            ('conquest_test_code_gen', f"{self.base_url}/api/conquest/test-ai-code-generation"),
            ('sandbox_test_code_gen', f"{self.base_url}/api/agents/sandbox/test-ai-code-generation"),
            ('sandbox_run_experiments', f"{self.base_url}/api/agents/sandbox/run-ai-experiments"),
            ('sandbox_capabilities', f"{self.base_url}/api/agents/sandbox/ai-capabilities"),
            ('enhanced_ai_status', f"{self.base_url}/api/enhanced-ai/status"),
            ('enhanced_ai_run_cycle', f"{self.base_url}/api/enhanced-ai/run-cycle"),
        ]
        
        for name, url in endpoints_to_test:
            try:
                logger.info(f"🧪 Testing {name} endpoint: {url}")
                
                # Try GET first, then POST if needed
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    logger.info(f"✅ {name} endpoint working (GET)")
                    data = response.json()
                    logger.info(f"   Response: {data}")
                elif response.status_code == 405:
                    # Try POST if GET not allowed
                    response = requests.post(url, json={}, timeout=30)
                    if response.status_code == 200:
                        logger.info(f"✅ {name} endpoint working (POST)")
                        data = response.json()
                        logger.info(f"   Response: {data}")
                    else:
                        logger.warning(f"⚠️ {name} endpoint returned {response.status_code}")
                elif response.status_code == 404:
                    logger.warning(f"⚠️ {name} endpoint not found (404)")
                else:
                    logger.warning(f"⚠️ {name} endpoint returned {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⏰ {name} endpoint timed out")
            except requests.exceptions.ConnectionError:
                logger.error(f"❌ {name} endpoint connection error")
            except Exception as e:
                logger.error(f"❌ {name} endpoint test failed: {e}")
    
    def test_health_endpoints(self):
        """Test health and status endpoints"""
        logger.info("🧪 Testing health and status endpoints...")
        
        health_endpoints = [
            ('health', f"{self.base_url}/health"),
            ('docs', f"{self.base_url}/docs"),
            ('openapi', f"{self.base_url}/openapi.json"),
        ]
        
        for name, url in health_endpoints:
            try:
                logger.info(f"🧪 Testing {name} endpoint: {url}")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    logger.info(f"✅ {name} endpoint working")
                else:
                    logger.warning(f"⚠️ {name} endpoint returned {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ {name} endpoint test failed: {e}")
    
    def run_tests(self):
        """Run all endpoint tests"""
        logger.info("🚀 Starting Correct Endpoints Test...")
        logger.info("=" * 60)
        
        # Test health endpoints first
        self.test_health_endpoints()
        
        # Test the correct AI endpoints
        self.test_custody_endpoints()
        self.test_enhanced_ai_endpoints()
        self.test_other_ai_endpoints()
        
        logger.info("=" * 60)
        logger.info("✅ Correct endpoints test completed!")
        logger.info("💡 The correct AI test endpoints are:")
        logger.info("   - /api/custody/test/{ai_type}")
        logger.info("   - /api/enhanced-ai/run-ai/{ai_type}")
        logger.info("   - /api/conquest/test-ai-code-generation")
        logger.info("   - /api/agents/sandbox/test-ai-code-generation")

def main():
    """Main function"""
    try:
        tester = CorrectEndpointsTester()
        tester.run_tests()
        
        logger.info("🎉 Correct endpoints test completed successfully!")
        sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 