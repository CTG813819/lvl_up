#!/usr/bin/env python3
"""
Custody Protocol Testing Script
===============================

This script specifically tests the Custody Protocol functionality to ensure
it's running tests and performing comprehensive validation.
"""

import pytest
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

@pytest.mark.parametrize("endpoint,description", [
    ("/api/custody", "Custody Protocol Overview"),
    ("/api/custody/health", "Custody Protocol Health"),
    ("/api/custody/tests", "Custody Protocol Tests"),
    ("/api/custody/analytics", "Custody Protocol Analytics"),
])
def test_custody_endpoint(endpoint, description):
    response = requests.get(f"{BASE_URL}{endpoint}", timeout=15)
    assert response.status_code == 200, f"{description} failed with status {response.status_code}: {response.text}"

def test_custody_protocol_overview():
    """Test custody protocol overview"""
    logger.info("🔒 Testing Custody Protocol Overview...")
    success, data = test_custody_endpoint("/api/custody", "Custody Protocol Overview")
    
    if success and data:
        logger.info(f"   Status: {data.get('status', 'unknown')}")
        logger.info(f"   Message: {data.get('message', 'No message')}")
        
        # Check features
        features = data.get('features', [])
        logger.info(f"   Features: {len(features)} features available")
        for feature in features:
            logger.info(f"     - {feature}")
        
        # Check analytics
        analytics = data.get('analytics', {})
        if analytics:
            logger.info(f"   Analytics: {analytics}")
    
    return success

def test_custody_health():
    """Test custody protocol health"""
    logger.info("🏥 Testing Custody Protocol Health...")
    success, data = test_custody_endpoint("/api/custody/health", "Custody Protocol Health")
    
    if success and data:
        logger.info(f"   Health Status: {data.get('status', 'unknown')}")
        logger.info(f"   Components: {data.get('components', {})}")
    
    return success

def test_custody_tests():
    """Test custody protocol tests"""
    logger.info("🧪 Testing Custody Protocol Tests...")
    success, data = test_custody_endpoint("/api/custody/tests", "Custody Protocol Tests")
    
    if success and data:
        logger.info(f"   Tests Status: {data.get('status', 'unknown')}")
        tests = data.get('tests', [])
        logger.info(f"   Available Tests: {len(tests)}")
        for test in tests:
            logger.info(f"     - {test.get('name', 'Unknown')}: {test.get('status', 'unknown')}")
    
    return success

def test_custody_analytics():
    """Test custody protocol analytics"""
    logger.info("📊 Testing Custody Protocol Analytics...")
    success, data = test_custody_endpoint("/api/custody/analytics", "Custody Protocol Analytics")
    
    if success and data:
        logger.info(f"   Analytics Status: {data.get('status', 'unknown')}")
        analytics_data = data.get('data', {})
        logger.info(f"   Analytics Data: {analytics_data}")
    
    return success

def test_custody_run_test():
    """Test running a custody protocol test"""
    logger.info("🚀 Testing Custody Protocol Test Execution...")
    
    # Test data for running a test
    test_data = {
        "test_type": "comprehensive",
        "ai_type": "Imperium",
        "difficulty": "medium"
    }
    
    success, data = test_custody_endpoint("/api/custody/run-test", "Run Custody Protocol Test")
    
    if success and data:
        logger.info(f"   Test Execution Status: {data.get('status', 'unknown')}")
        logger.info(f"   Test Results: {data.get('results', {})}")
    
    return success

def test_custody_ai_status():
    """Test custody protocol AI status"""
    logger.info("🤖 Testing Custody Protocol AI Status...")
    success, data = test_custody_endpoint("/api/custody/ai-status", "Custody Protocol AI Status")
    
    if success and data:
        logger.info(f"   AI Status: {data.get('status', 'unknown')}")
        ai_status = data.get('ai_status', {})
        for ai_type, status in ai_status.items():
            logger.info(f"     {ai_type}: {status}")
    
    return success

def test_custody_test_history():
    """Test custody protocol test history"""
    logger.info("📜 Testing Custody Protocol Test History...")
    success, data = test_custody_endpoint("/api/custody/test-history", "Custody Protocol Test History")
    
    if success and data:
        logger.info(f"   History Status: {data.get('status', 'unknown')}")
        history = data.get('history', [])
        logger.info(f"   Test History: {len(history)} entries")
        for entry in history[:5]:  # Show first 5 entries
            logger.info(f"     - {entry.get('test_type', 'Unknown')}: {entry.get('result', 'Unknown')}")
    
    return success

# The run_custody_comprehensive_test function is removed as it's not directly used in pytest collection.
# The test functions themselves can be run individually or via pytest collection.
# For example:
# pytest test_custody_protocol.py -v
# pytest test_custody_protocol.py::test_custody_protocol_overview -v
# pytest test_custody_protocol.py::test_custody_health -v
# etc. 