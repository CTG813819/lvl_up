#!/usr/bin/env python3
"""
Enhanced Automatic Custodes Testing Service
Ensures ALL AIs get tested with proper fallback handling
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
        logging.FileHandler('/home/ubuntu/ai-backend-python/enhanced_custodes_service.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = "http://localhost:8000"
REGULAR_TEST_INTERVAL = 1 * 60 * 60  # 1 hour in seconds
AI_TYPES = ["imperium", "guardian", "conquest", "sandbox"]

def check_backend_status():
    """Check if the backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/custody/", timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Backend status check failed: {e}")
        return False

def force_test_for_ai(ai_type: str):
    """Force test for a specific AI with enhanced error handling"""
    try:
        logger.info(f"🧪 Testing {ai_type} AI...")
        
        # Try the main test endpoint first
        response = requests.post(
            f"{BACKEND_URL}/api/custody/test/{ai_type}/force",
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ {ai_type} test completed: {result.get('status', 'unknown')}")
            return {"status": "success", "ai_type": ai_type, "result": result}
        else:
            logger.warning(f"⚠️ {ai_type} main test failed: {response.status_code}, trying fallback...")
            
            # Try fallback endpoint
            fallback_response = requests.post(
                f"{BACKEND_URL}/api/custody/fallback/test/{ai_type}",
                timeout=60
            )
            
            if fallback_response.status_code == 200:
                fallback_result = fallback_response.json()
                logger.info(f"✅ {ai_type} fallback test completed: {fallback_result.get('status', 'unknown')}")
                return {"status": "success", "ai_type": ai_type, "result": fallback_result, "method": "fallback"}
            else:
                logger.error(f"❌ {ai_type} both main and fallback tests failed")
                return {"status": "failed", "ai_type": ai_type, "error": f"HTTP {response.status_code}"}
                
    except Exception as e:
        logger.error(f"❌ Error testing {ai_type}: {str(e)}")
        return {"status": "error", "ai_type": ai_type, "error": str(e)}

def force_tests_for_all_ais():
    """Force tests for ALL AIs with comprehensive error handling"""
    logger.info("🚀 Starting comprehensive tests for ALL AIs...")
    
    results = {}
    success_count = 0
    
    for ai_type in AI_TYPES:
        result = force_test_for_ai(ai_type)
        results[ai_type] = result
        
        if result.get('status') == 'success':
            success_count += 1
    
    logger.info(f"📊 Test Results Summary:")
    logger.info(f"   Total AIs: {len(AI_TYPES)}")
    logger.info(f"   Successful: {success_count}")
    logger.info(f"   Failed: {len(AI_TYPES) - success_count}")
    
    # Log individual results
    for ai_type, result in results.items():
        status_icon = "✅" if result.get('status') == 'success' else "❌"
        logger.info(f"   {status_icon} {ai_type}: {result.get('status', 'unknown')}")
    
    return results

def main():
    """Main service loop"""
    logger.info("🛡️ Starting Enhanced Automatic Custodes Testing Service")
    
    last_test_time = datetime.now() - timedelta(hours=5)  # Force immediate test
    
    while True:
        try:
            current_time = datetime.now()
            
            # Check if backend is running
            if not check_backend_status():
                logger.warning("Backend is not running, waiting...")
                time.sleep(60)
                continue
            
            # Run tests every hour
            if current_time - last_test_time >= timedelta(hours=1):
                logger.info("🕐 Running comprehensive tests for ALL AIs...")
                results = force_tests_for_all_ais()
                last_test_time = current_time
                
                # Log summary
                success_count = sum(1 for r in results.values() if r.get('status') == 'success')
                logger.info(f"🎯 Hourly test cycle completed: {success_count}/{len(AI_TYPES)} AIs tested successfully")
            
            # Sleep for 5 minutes before next check
            time.sleep(300)
            
        except KeyboardInterrupt:
            logger.info("Service stopped by user")
            break
        except Exception as e:
            logger.error(f"Service error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main() 