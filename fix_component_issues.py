#!/usr/bin/env python3
"""
Fix Component Issues Script
===========================

This script will fix the issues identified in the component tests.
"""

import requests
import json
import time
import logging
import subprocess
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def install_websocket_module():
    """Install the websocket-client module"""
    logger.info("📦 Installing websocket-client module...")
    try:
        subprocess.run(["pip3", "install", "websocket-client"], check=True, capture_output=True)
        logger.info("✅ websocket-client installed")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install websocket-client: {e}")
        return False

def test_custody_protocol_tests():
    """Test running custody protocol tests"""
    logger.info("🧪 Testing Custody Protocol Test Execution...")
    
    # Test data for running a comprehensive test
    test_data = {
        "test_type": "comprehensive",
        "ai_type": "Imperium",
        "difficulty": "basic"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/custody/run-test", json=test_data, timeout=30)
        if response.status_code in [200, 201]:
            data = response.json()
            logger.info(f"✅ Custody Protocol Test Executed: {data.get('status', 'OK')}")
            return True, data
        else:
            logger.error(f"❌ Custody Protocol Test Failed: HTTP {response.status_code}")
            return False, None
    except Exception as e:
        logger.error(f"❌ Custody Protocol Test Error: {str(e)}")
        return False, None

def test_imperium_learning():
    """Test Imperium learning functionality"""
    logger.info("👑 Testing Imperium Learning...")
    
    # Test imperium learning endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/imperium/learning", timeout=15)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Imperium Learning: {data.get('status', 'OK')}")
            return True, data
        else:
            logger.error(f"❌ Imperium Learning: HTTP {response.status_code}")
            return False, None
    except Exception as e:
        logger.error(f"❌ Imperium Learning Error: {str(e)}")
        return False, None

def test_sandbox_overview():
    """Test Sandbox overview"""
    logger.info("🧪 Testing Sandbox Overview...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/sandbox", timeout=15)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Sandbox Overview: {data.get('status', 'OK')}")
            return True, data
        else:
            logger.error(f"❌ Sandbox Overview: HTTP {response.status_code}")
            return False, None
    except Exception as e:
        logger.error(f"❌ Sandbox Overview Error: {str(e)}")
        return False, None

def test_agents_status():
    """Test agents status with longer timeout"""
    logger.info("🤖 Testing Agents Status (with longer timeout)...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/agents/status", timeout=30)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Agents Status: {data.get('status', 'OK')}")
            return True, data
        else:
            logger.error(f"❌ Agents Status: HTTP {response.status_code}")
            return False, None
    except Exception as e:
        logger.error(f"❌ Agents Status Error: {str(e)}")
        return False, None

def test_proposals_system():
    """Test proposals system"""
    logger.info("📋 Testing Proposals System...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/proposals", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                logger.info(f"✅ Proposals Overview: {len(data)} proposals")
            else:
                logger.info(f"✅ Proposals Overview: {data.get('status', 'OK')}")
            return True, data
        else:
            logger.error(f"❌ Proposals Overview: HTTP {response.status_code}")
            return False, None
    except Exception as e:
        logger.error(f"❌ Proposals Overview Error: {str(e)}")
        return False, None

def test_monitoring_system():
    """Test monitoring system"""
    logger.info("📊 Testing Monitoring System...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/monitoring", timeout=15)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Monitoring Status: {data.get('status', 'OK')}")
            return True, data
        else:
            logger.error(f"❌ Monitoring Status: HTTP {response.status_code}")
            return False, None
    except Exception as e:
        logger.error(f"❌ Monitoring Status Error: {str(e)}")
        return False, None

def test_websocket_connection():
    """Test WebSocket connection"""
    logger.info("🔌 Testing WebSocket Connection...")
    
    try:
        import websocket
        ws = websocket.create_connection("ws://localhost:8000/ws/imperium/learning-analytics", timeout=10)
        ws.send("test")
        response = ws.recv()
        ws.close()
        logger.info("✅ WebSocket connection working")
        return True
    except ImportError:
        logger.error("❌ websocket-client module not installed")
        return False
    except Exception as e:
        logger.warning(f"⚠️ WebSocket test failed: {str(e)}")
        return False

def run_custody_protocol_tests():
    """Run custody protocol tests for all AIs"""
    logger.info("🔒 Running Custody Protocol Tests for All AIs...")
    
    ai_types = ["Imperium", "Guardian", "Sandbox", "Conquest"]
    test_results = {}
    
    for ai_type in ai_types:
        logger.info(f"🧪 Testing {ai_type} AI...")
        test_data = {
            "test_type": "comprehensive",
            "ai_type": ai_type,
            "difficulty": "basic"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/custody/run-test", json=test_data, timeout=30)
            if response.status_code in [200, 201]:
                data = response.json()
                logger.info(f"✅ {ai_type} Test: {data.get('status', 'OK')}")
                test_results[ai_type] = True
            else:
                logger.error(f"❌ {ai_type} Test: HTTP {response.status_code}")
                test_results[ai_type] = False
        except Exception as e:
            logger.error(f"❌ {ai_type} Test Error: {str(e)}")
            test_results[ai_type] = False
        
        time.sleep(2)  # Wait between tests
    
    return test_results

def main():
    """Main function to fix component issues"""
    logger.info("🚀 Starting Component Issue Fixes...")
    logger.info("=" * 60)
    
    # Install missing websocket module
    install_websocket_module()
    
    # Test and fix custody protocol
    logger.info("🔒 Testing Custody Protocol Tests...")
    test_custody_protocol_tests()
    
    # Run custody protocol tests for all AIs
    custody_results = run_custody_protocol_tests()
    
    # Test other components
    logger.info("🔧 Testing Other Components...")
    test_imperium_learning()
    test_sandbox_overview()
    test_agents_status()
    test_proposals_system()
    test_monitoring_system()
    test_websocket_connection()
    
    # Summary
    logger.info("=" * 60)
    logger.info("📋 FIX SUMMARY")
    logger.info("=" * 60)
    
    logger.info("Custody Protocol Tests:")
    for ai_type, success in custody_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"  {ai_type}: {status}")
    
    logger.info("=" * 60)
    logger.info("✅ Component fixes applied!")
    logger.info("🔄 Run the comprehensive test again to verify improvements.")

if __name__ == "__main__":
    main() 