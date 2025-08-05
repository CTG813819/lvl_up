#!/usr/bin/env python3
"""
Comprehensive Component Testing Script
=====================================

This script will test all AI agents and the Custody Protocol to ensure they're running properly.
"""

import pytest
import requests
import json
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

@pytest.mark.parametrize("endpoint,description", [
    ("/api/custody", "Custody Protocol Overview"),
    ("/api/custody/health", "Custody Protocol Health"),
    ("/api/custody/tests", "Custody Protocol Tests"),
    ("/api/custody/analytics", "Custody Protocol Analytics"),
    ("/api/imperium", "Imperium Overview"),
    ("/api/imperium/learning", "Imperium Learning"),
    ("/api/imperium/status", "Imperium Status"),
    ("/api/imperium/analytics", "Imperium Analytics"),
    ("/api/guardian", "Guardian Overview"),
    ("/api/guardian/health-check", "Guardian Health Check"),
    ("/api/guardian/health-status", "Guardian Health Status"),
    ("/api/guardian/suggestions", "Guardian Suggestions"),
    ("/api/sandbox", "Sandbox Overview"),
    ("/api/sandbox/experiments", "Sandbox Experiments"),
])
def test_endpoint(endpoint, description):
    response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
    assert response.status_code == 200, f"{description} failed with status {response.status_code}: {response.text}"

def test_custody_protocol():
    """Test Custody Protocol functionality"""
    logger.info("🔒 Testing Custody Protocol...")
    
    # Test custody protocol overview
    test_endpoint("/api/custody", "Custody Protocol Overview")
    
    # Test custody protocol health
    test_endpoint("/api/custody/health", "Custody Protocol Health")
    
    # Test custody protocol tests
    test_endpoint("/api/custody/tests", "Custody Protocol Tests")
    
    # Test custody protocol analytics
    test_endpoint("/api/custody/analytics", "Custody Protocol Analytics")
    
    return True

def test_imperium():
    """Test Imperium AI agent"""
    logger.info("👑 Testing Imperium AI...")
    
    # Test imperium overview
    test_endpoint("/api/imperium", "Imperium Overview")
    
    # Test imperium learning
    test_endpoint("/api/imperium/learning", "Imperium Learning")
    
    # Test imperium status
    test_endpoint("/api/imperium/status", "Imperium Status")
    
    # Test imperium analytics
    test_endpoint("/api/imperium/analytics", "Imperium Analytics")
    
    return True

def test_guardian():
    """Test Guardian AI agent"""
    logger.info("🛡️ Testing Guardian AI...")
    
    # Test guardian overview
    test_endpoint("/api/guardian", "Guardian Overview")
    
    # Test guardian health check
    test_endpoint("/api/guardian/health-check", "Guardian Health Check")
    
    # Test guardian health status
    test_endpoint("/api/guardian/health-status", "Guardian Health Status")
    
    # Test guardian suggestions
    test_endpoint("/api/guardian/suggestions", "Guardian Suggestions")
    
    return True

def test_sandbox():
    """Test Sandbox AI agent"""
    logger.info("🧪 Testing Sandbox AI...")
    
    # Test sandbox overview
    test_endpoint("/api/sandbox", "Sandbox Overview")
    
    # Test sandbox experiments
    test_endpoint("/api/sandbox/experiments", "Sandbox Experiments")
    
    # Test sandbox status
    test_endpoint("/api/sandbox/status", "Sandbox Status")
    
    return True

def test_agents_status():
    """Test overall agents status"""
    logger.info("🤖 Testing Overall Agents Status...")
    
    # Test agents status
    test_endpoint("/api/agents/status", "Agents Status")
    
    # Test AI status
    test_endpoint("/api/proposals/ai-status", "AI Status")
    
    return True

def test_enhanced_learning():
    """Test Enhanced Learning system"""
    logger.info("🧠 Testing Enhanced Learning...")
    
    # Test enhanced learning health
    test_endpoint("/api/enhanced-learning/health", "Enhanced Learning Health")
    
    # Test enhanced learning status
    test_endpoint("/api/enhanced-learning/status", "Enhanced Learning Status")
    
    return True

def test_optimized_services():
    """Test Optimized Services"""
    logger.info("⚡ Testing Optimized Services...")
    
    # Test optimized services health
    test_endpoint("/optimized/health", "Optimized Services Health")
    
    # Test cache stats
    test_endpoint("/optimized/cache/stats", "Cache Statistics")
    
    return True

def test_proposals():
    """Test Proposals system"""
    logger.info("📋 Testing Proposals System...")
    
    # Test proposals overview
    test_endpoint("/api/proposals", "Proposals Overview")
    
    # Test proposals stats
    test_endpoint("/api/proposals/stats", "Proposals Statistics")
    
    return True

def test_monitoring():
    """Test Monitoring system"""
    logger.info("📊 Testing Monitoring System...")
    
    # Test monitoring status
    test_endpoint("/api/monitoring", "Monitoring Status")
    
    return True

def test_websocket_connections():
    """Test WebSocket connections"""
    logger.info("🔌 Testing WebSocket Connections...")
    
    # Test imperium learning analytics websocket
    try:
        import websocket
        ws = websocket.create_connection("ws://localhost:8000/ws/imperium/learning-analytics", timeout=5)
        ws.send("test")
        response = ws.recv()
        ws.close()
        logger.info("✅ WebSocket connection working")
        return True
    except Exception as e:
        logger.warning(f"⚠️ WebSocket test failed: {str(e)}")
        return False

# Add additional test functions for other features as needed, using pytest style. 