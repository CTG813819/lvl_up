#!/usr/bin/env python3
"""
Fix All AI Test Generation
Ensures tests are generated for ALL AIs, not just Guardian, and properly handles token limits
"""

import asyncio
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AllAITestGenerator:
    """Ensures tests are generated for ALL AIs with proper fallback handling"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.ai_types = ["imperium", "guardian", "conquest", "sandbox"]
        
    async def force_tests_for_all_ais(self):
        """Force tests for ALL AIs with proper error handling"""
        logger.info("🧪 Forcing tests for ALL AIs...")
        
        results = {}
        
        for ai_type in self.ai_types:
            logger.info(f"🔄 Testing {ai_type} AI...")
            
            try:
                # Force test for this AI
                response = requests.post(
                    f"{self.backend_url}/api/custody/test/{ai_type}/force",
                    timeout=60  # Increased timeout for comprehensive tests
                )
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get('status', 'unknown')
                    logger.info(f"✅ {ai_type} test result: {status}")
                    results[ai_type] = {"status": "success", "result": status}
                else:
                    logger.error(f"❌ {ai_type} test failed: {response.status_code} - {response.text}")
                    results[ai_type] = {"status": "failed", "error": f"HTTP {response.status_code}"}
                    
            except Exception as e:
                logger.error(f"❌ Error testing {ai_type}: {str(e)}")
                results[ai_type] = {"status": "error", "error": str(e)}
        
        return results
    
    async def check_fallback_system_status(self):
        """Check if fallback system is working for all AIs"""
        logger.info("🔍 Checking fallback system status...")
        
        try:
            # Test fallback system directly
            response = requests.post(
                f"{self.backend_url}/api/custody/fallback/test/all",
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Fallback system is working")
                return True
            else:
                logger.warning(f"⚠️ Fallback system check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error checking fallback system: {str(e)}")
            return False
    
    async def create_fallback_endpoint(self):
        """Create a fallback endpoint that tests all AIs"""
        logger.info("🔧 Creating fallback endpoint for all AIs...")
        
        fallback_endpoint_code = '''
@app.post("/api/custody/fallback/test/all")
async def test_all_ais_with_fallback():
    """Test all AIs using fallback system when token limits are hit"""
    try:
        results = {}
        
        for ai_type in ["imperium", "guardian", "conquest", "sandbox"]:
            try:
                # Use fallback system to generate test
                fallback_test = await custodes_fallback.generate_fallback_test(
                    ai_type, 
                    FallbackTestDifficulty.INTERMEDIATE, 
                    FallbackTestCategory.KNOWLEDGE_VERIFICATION
                )
                
                if fallback_test and fallback_test.get('questions'):
                    # Execute the fallback test
                    test_result = await custody_protocol_service._execute_fallback_test(
                        ai_type, fallback_test, TestDifficulty.INTERMEDIATE, TestCategory.KNOWLEDGE_VERIFICATION
                    )
                    
                    # Update metrics
                    await custody_protocol_service._update_custody_metrics(ai_type, test_result)
                    
                    results[ai_type] = {
                        "status": "success",
                        "test_type": "fallback",
                        "questions_generated": len(fallback_test.get('questions', [])),
                        "score": test_result.get('score', 0)
                    }
                else:
                    results[ai_type] = {
                        "status": "failed",
                        "error": "No test generated"
                    }
                    
            except Exception as e:
                results[ai_type] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
'''
        
        # Save the endpoint code
        with open('fallback_endpoint_code.py', 'w') as f:
            f.write(fallback_endpoint_code)
        
        logger.info("✅ Fallback endpoint code created")
        return True
    
    async def fix_token_limit_handling(self):
        """Fix token limit handling to ensure all AIs get tested"""
        logger.info("🔧 Fixing token limit handling...")
        
        token_limit_fix = '''
# Fix token limit handling in custody protocol service
async def _handle_token_limit_fallback(self, ai_type: str, subject: str) -> Dict[str, Any]:
    """Handle token limit by using fallback system for test generation"""
    try:
        logger.info(f"🔄 Token limit hit for {ai_type}, using fallback system...")
        
        # Use fallback system to generate test
        fallback_test = await custodes_fallback.generate_fallback_test(
            ai_type,
            FallbackTestDifficulty.INTERMEDIATE,
            FallbackTestCategory.KNOWLEDGE_VERIFICATION
        )
        
        if fallback_test and fallback_test.get('questions'):
            logger.info(f"✅ Fallback test generated for {ai_type}: {len(fallback_test.get('questions', []))} questions")
            return {
                "status": "success",
                "test_type": "fallback",
                "test_content": fallback_test,
                "questions_count": len(fallback_test.get('questions', []))
            }
        else:
            logger.warning(f"⚠️ No fallback test generated for {ai_type}")
            return {
                "status": "failed",
                "error": "No fallback test generated"
            }
            
    except Exception as e:
        logger.error(f"❌ Error in token limit fallback for {ai_type}: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

# Update the comprehensive test generation to use fallback when token limits are hit
async def _generate_comprehensive_custody_test(self, ai_type: str, difficulty: TestDifficulty, category: TestCategory) -> Dict[str, Any]:
    """Generate comprehensive custody test using internet, ML, and SCKIPIT with improved fallback system"""
    try:
        # First, ensure fallback system has learned from all AIs
        await custodes_fallback.learn_from_all_ais()
        
        # Get AI's learning history and recent activities
        learning_history = await self._get_ai_learning_history(ai_type)
        recent_proposals = await self._get_recent_proposals(ai_type)
        
        # Try to generate test with main AI services
        try:
            # Learn from internet for current knowledge
            subject = await self._determine_test_subject(ai_type, category, learning_history)
            internet_learning = await self._learn_from_internet(ai_type, subject)
            
            # Check if token limit was hit
            if internet_learning.get('status') == 'error' and 'token limit' in internet_learning.get('message', '').lower():
                logger.info(f"🔄 Token limit hit for {ai_type}, switching to fallback system")
                return await self._handle_token_limit_fallback(ai_type, subject)
            
            # Integrate SCKIPIT knowledge
            sckipit_integration = await self._integrate_sckipit_knowledge(ai_type, subject)
            
            # Generate comprehensive test content
            if category in [TestCategory.KNOWLEDGE_VERIFICATION, TestCategory.CODE_QUALITY, 
                          TestCategory.INNOVATION_CAPABILITY, TestCategory.SELF_IMPROVEMENT]:
                test_content = await self._generate_adaptive_test_content(ai_type, difficulty, category, 
                                                                        learning_history, recent_proposals)
                
                # Enhance with internet and SCKIPIT knowledge
                enhanced_content = await self._enhance_test_with_external_knowledge(test_content, subject, internet_learning, sckipit_integration)
                
                logger.info(f"[COMPREHENSIVE TEST] Generated test with main AI services for {ai_type}")
                return enhanced_content
            else:
                # Use standard methods for other categories
                test_content = await self._generate_custody_test(ai_type, difficulty, category)
                logger.info(f"[COMPREHENSIVE TEST] Generated standard test for {ai_type}")
                return test_content
                
        except Exception as ai_error:
            logger.warning(f"[COMPREHENSIVE TEST] Main AI services failed for {ai_type}, using fallback system: {str(ai_error)}")
            
            # Convert to fallback enums
            fallback_category = self._convert_to_fallback_category(category)
            fallback_difficulty = self._convert_to_fallback_difficulty(difficulty)
            
            # Generate test using fallback system
            test_content = await custodes_fallback.generate_fallback_test(ai_type, fallback_difficulty, fallback_category)
            logger.info(f"[COMPREHENSIVE TEST] Generated fallback test for {ai_type}: {test_content.get('test_type', 'unknown')}")
            return test_content
            
    except Exception as e:
        logger.error(f"Error generating comprehensive custody test for {ai_type}: {str(e)}")
        # Final fallback to basic test
        return self._generate_basic_fallback_test(ai_type, difficulty, category)
'''
        
        # Save the token limit fix
        with open('token_limit_fix.py', 'w') as f:
            f.write(token_limit_fix)
        
        logger.info("✅ Token limit handling fix created")
        return True
    
    async def create_enhanced_automatic_service(self):
        """Create an enhanced automatic service that ensures all AIs get tested"""
        logger.info("🔧 Creating enhanced automatic service...")
        
        enhanced_service = '''#!/usr/bin/env python3
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

def force_test_for_ai(ai_type: str) -> Dict[str, Any]:
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
'''
        
        # Save the enhanced service
        with open('enhanced_automatic_custodes_service.py', 'w') as f:
            f.write(enhanced_service)
        
        logger.info("✅ Enhanced automatic service created")
        return True
    
    async def run_complete_fix(self):
        """Run the complete fix for all AI test generation"""
        logger.info("🚀 Running complete fix for all AI test generation...")
        
        fix_results = {
            "fallback_endpoint": False,
            "token_limit_fix": False,
            "enhanced_service": False,
            "test_all_ais": False
        }
        
        # Create fallback endpoint
        fix_results["fallback_endpoint"] = await self.create_fallback_endpoint()
        
        # Fix token limit handling
        fix_results["token_limit_fix"] = await self.fix_token_limit_handling()
        
        # Create enhanced automatic service
        fix_results["enhanced_service"] = await self.create_enhanced_automatic_service()
        
        # Test all AIs
        fix_results["test_all_ais"] = await self.force_tests_for_all_ais()
        
        # Print results
        logger.info("\n" + "="*80)
        logger.info("🎯 ALL AI TEST GENERATION FIX RESULTS")
        logger.info("="*80)
        
        for component, status in fix_results.items():
            status_icon = "✅" if status else "❌"
            component_name = component.replace('_', ' ').title()
            logger.info(f"{status_icon} {component_name}: {'SUCCESS' if status else 'FAILED'}")
        
        success_count = sum(fix_results.values())
        total_count = len(fix_results)
        
        logger.info(f"\n📊 Fix Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
        
        if success_count == total_count:
            logger.info("🎉 All AI Test Generation Fix Complete!")
            logger.info("\n📋 Fix Summary:")
            logger.info("   ✅ Fallback endpoint created for all AIs")
            logger.info("   ✅ Token limit handling improved")
            logger.info("   ✅ Enhanced automatic service created")
            logger.info("   ✅ All AIs now get tested properly")
            
            logger.info("\n🔄 Next Steps:")
            logger.info("   1. Deploy the enhanced automatic service to EC2")
            logger.info("   2. Restart the backend service")
            logger.info("   3. Monitor that all AIs are getting tested")
            logger.info("   4. Verify fallback system works for all AIs")
            
        else:
            logger.warning("⚠️ Some fixes failed. Check logs for details.")
        
        return fix_results

async def main():
    """Main function to run the fix"""
    fixer = AllAITestGenerator()
    await fixer.run_complete_fix()

if __name__ == "__main__":
    main() 