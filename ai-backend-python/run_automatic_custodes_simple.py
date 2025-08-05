#!/usr/bin/env python3
"""
Simplified Automatic Custodes Testing Service
Runs Custodes tests for all AIs on a regular schedule without external dependencies
"""

import time
import requests
import json
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-backend-python/custodes_service.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = "http://localhost:8000"
REGULAR_TEST_INTERVAL = 1 * 60 * 60  # 1 hour in seconds (reduced from 4 hours)
COMPREHENSIVE_TEST_INTERVAL = 24 * 60 * 60  # 24 hours in seconds
ELIGIBILITY_CHECK_INTERVAL = 2 * 60 * 60  # 2 hours in seconds

def check_backend_status():
    """Check if the backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/custody/", timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Backend status check failed: {e}")
        return False

def force_custodes_tests():
    """Force Custodes tests for all AIs using correct custody protocol endpoints"""
    try:
        logger.info("🧪 Forcing Custodes tests for all AIs...")
        
        # Test imperium AI
        logger.info("Testing imperium AI...")
        response = requests.post(
            f"{BACKEND_URL}/api/custody/test/imperium/force",
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Imperium test result: {result.get('status', 'unknown')}")
        else:
            logger.error(f"Imperium test failed: {response.status_code} - {response.text}")
        
        # Test guardian AI
        logger.info("Testing guardian AI...")
        response = requests.post(
            f"{BACKEND_URL}/api/custody/test/guardian/force",
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Guardian test result: {result.get('status', 'unknown')}")
        else:
            logger.error(f"Guardian test failed: {response.status_code} - {response.text}")
        
        # Test conquest AI
        logger.info("Testing conquest AI...")
        response = requests.post(
            f"{BACKEND_URL}/api/custody/test/conquest/force",
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Conquest test result: {result.get('status', 'unknown')}")
        else:
            logger.error(f"Conquest test failed: {response.status_code} - {response.text}")
        
        # Test sandbox AI
        logger.info("Testing sandbox AI...")
        response = requests.post(
            f"{BACKEND_URL}/api/custody/test/sandbox/force",
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Sandbox test result: {result.get('status', 'unknown')}")
        else:
            logger.error(f"Sandbox test failed: {response.status_code} - {response.text}")
        
        logger.info("✅ Custodes tests completed")
        
    except Exception as e:
        logger.error(f"Error forcing Custodes tests: {e}")

def check_eligibility():
    """Check if AIs are eligible for tests using correct custody protocol endpoints"""
    try:
        logger.info("🔍 Checking AI eligibility for tests...")
        
        for ai_type in ["imperium", "guardian", "conquest", "sandbox"]:
            response = requests.get(f"{BACKEND_URL}/api/custody/eligibility/{ai_type}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                ai_data = data.get('data', {})
                can_create_proposals = ai_data.get('can_create_proposals', False)
                can_level_up = ai_data.get('can_level_up', False)
                current_status = ai_data.get('current_status', {})
                
                if can_create_proposals:
                    logger.info(f"✅ {ai_type} is eligible for proposals")
                else:
                    logger.info(f"❌ {ai_type} is not eligible for proposals")
                
                logger.info(f"📊 {ai_type} status: XP={current_status.get('custody_xp', 0)}, "
                          f"Tests passed={current_status.get('total_tests_passed', 0)}, "
                          f"Can level up={can_level_up}")
            else:
                logger.error(f"Failed to check eligibility for {ai_type}: {response.status_code}")
                
    except Exception as e:
        logger.error(f"Error checking eligibility: {e}")

def get_custody_analytics():
    """Get custody analytics to monitor system status"""
    try:
        logger.info("📈 Getting custody analytics...")
        response = requests.get(f"{BACKEND_URL}/api/custody/analytics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            analytics = data.get('data', {})
            
            # Log summary statistics
            total_tests = analytics.get('total_tests_administered', 0)
            total_passed = analytics.get('total_tests_passed', 0)
            total_failed = analytics.get('total_tests_failed', 0)
            
            logger.info(f"📊 Custody Analytics Summary:")
            logger.info(f"   Total tests administered: {total_tests}")
            logger.info(f"   Total tests passed: {total_passed}")
            logger.info(f"   Total tests failed: {total_failed}")
            logger.info(f"   Overall pass rate: {(total_passed/total_tests*100) if total_tests > 0 else 0:.1f}%")
            
            # Log AI-specific metrics
            ai_metrics = analytics.get('ai_specific_metrics', {})
            for ai_type, metrics in ai_metrics.items():
                xp = metrics.get('custody_xp', 0)
                level = metrics.get('custody_level', 1)
                tests_passed = metrics.get('total_tests_passed', 0)
                logger.info(f"   {ai_type}: Level {level}, XP {xp}, Tests passed {tests_passed}")
                
        else:
            logger.error(f"Failed to get analytics: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")

def main():
    """Main service loop"""
    logger.info("🛡️ Starting Simplified Automatic Custodes Testing Service")
    
    last_regular_test = datetime.now() - timedelta(hours=5)  # Force immediate test
    last_comprehensive_test = datetime.now() - timedelta(days=1)  # Start with immediate test
    last_eligibility_check = datetime.now() - timedelta(hours=3)  # Delay eligibility check
    last_analytics_check = datetime.now() - timedelta(hours=1)  # Start with immediate analytics
    
    while True:
        try:
            current_time = datetime.now()
            
            # Check if backend is running
            if not check_backend_status():
                logger.warning("Backend is not running, waiting...")
                time.sleep(60)  # Wait 1 minute before retrying
                continue
            
            # Run regular tests every 1 hour
            if current_time - last_regular_test >= timedelta(hours=1):
                logger.info("🕐 Running regular Custodes tests...")
                force_custodes_tests()
                last_regular_test = current_time
            
            # Run comprehensive tests daily at 6 AM
            if (current_time.hour == 6 and 
                current_time - last_comprehensive_test >= timedelta(days=1)):
                logger.info("🌅 Running comprehensive Custodes tests...")
                force_custodes_tests()
                last_comprehensive_test = current_time
            
            # Check eligibility every 2 hours
            if current_time - last_eligibility_check >= timedelta(hours=2):
                logger.info("🔍 Running eligibility check...")
                check_eligibility()
                last_eligibility_check = current_time
            
            # Get analytics every hour
            if current_time - last_analytics_check >= timedelta(hours=1):
                logger.info("📈 Getting custody analytics...")
                get_custody_analytics()
                last_analytics_check = current_time
            
            # Sleep for 5 minutes before next check
            time.sleep(300)
            
        except KeyboardInterrupt:
            logger.info("Service stopped by user")
            break
        except Exception as e:
            logger.error(f"Service error: {e}")
            time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    main() 