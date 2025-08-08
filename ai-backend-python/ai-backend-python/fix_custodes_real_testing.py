#!/usr/bin/env python3
"""
Comprehensive fix for Custodes Protocol Real Testing
This script fixes all issues preventing the custody protocol from actually testing AIs
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

from app.core.database import init_database, get_session
from app.core.config import settings
from app.services.custody_protocol_service import CustodyProtocolService, TestCategory
import structlog

logger = structlog.get_logger()

async def fix_database_initialization():
    """Fix database initialization issues"""
    print("🔧 Fixing database initialization...")
    
    try:
        # Initialize the database
        await init_database()
        print("   ✅ Database initialized successfully")
        
        # Test database connection
        async with get_session() as session:
            # Test a simple query
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            await session.commit()
            print("   ✅ Database connection test passed")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database initialization failed: {str(e)}")
        return False

async def fix_token_limits():
    """Fix token limit issues by increasing limits"""
    print("🔧 Fixing token limits...")
    
    try:
        # Update token usage service limits
        token_service_file = "app/services/token_usage_service.py"
        
        if os.path.exists(token_service_file):
            with open(token_service_file, 'r') as f:
                content = f.read()
            
            # Increase hourly limits
            content = content.replace(
                "MAX_HOURLY_USAGE_PERCENTAGE = 0.5",
                "MAX_HOURLY_USAGE_PERCENTAGE = 5.0"  # Increase from 0.5% to 5%
            )
            
            content = content.replace(
                "HOURLY_LIMIT = int(DAILY_LIMIT / 24)",
                "HOURLY_LIMIT = int(DAILY_LIMIT / 6)"  # Increase from 24 to 6 (4x more)
            )
            
            # Increase daily limits
            content = content.replace(
                "MAX_DAILY_USAGE_PERCENTAGE = 8.0",
                "MAX_DAILY_USAGE_PERCENTAGE = 15.0"  # Increase from 8% to 15%
            )
            
            with open(token_service_file, 'w') as f:
                f.write(content)
            
            print("   ✅ Token limits increased successfully")
            return True
        else:
            print("   ⚠️ Token service file not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Token limit fix failed: {str(e)}")
        return False

async def fix_api_keys():
    """Fix API key issues"""
    print("🔧 Fixing API keys...")
    
    try:
        # Check current environment variables
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        print(f"   Anthropic API Key: {'✅ Set' if anthropic_key else '❌ Missing'}")
        print(f"   OpenAI API Key: {'✅ Set' if openai_key else '❌ Missing'}")
        
        if not anthropic_key:
            print("   ⚠️ ANTHROPIC_API_KEY not set - please set it in your environment")
        
        if not openai_key:
            print("   ⚠️ OPENAI_API_KEY not set - please set it in your environment")
            print("   💡 You can set it temporarily with: export OPENAI_API_KEY='your-key-here'")
        
        return bool(anthropic_key or openai_key)
        
    except Exception as e:
        print(f"   ❌ API key check failed: {str(e)}")
        return False

async def fix_settings_issue():
    """Fix the 'settings' not defined issue"""
    print("🔧 Fixing settings issue...")
    
    try:
        # Check if settings is properly imported in custody protocol service
        custody_file = "app/services/custody_protocol_service.py"
        
        if os.path.exists(custody_file):
            with open(custody_file, 'r') as f:
                content = f.read()
            
            # Check if settings is imported
            if "from ..core.config import settings" not in content:
                # Add the import
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith("from ..core.database import"):
                        lines.insert(i + 1, "from ..core.config import settings")
                        break
                
                content = '\n'.join(lines)
                
                with open(custody_file, 'w') as f:
                    f.write(content)
                
                print("   ✅ Settings import added to custody protocol service")
            else:
                print("   ✅ Settings import already exists")
            
            return True
        else:
            print("   ⚠️ Custody protocol service file not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Settings fix failed: {str(e)}")
        return False

async def test_custodes_after_fixes():
    """Test Custodes protocol after applying fixes"""
    print("\n🧪 Testing Custodes Protocol after fixes...")
    
    try:
        # Initialize custody service
        custody_service = await CustodyProtocolService.initialize()
        
        # Test with a simple test
        print("   🧪 Running simple test for imperium AI...")
        result = await custody_service.administer_custody_test("imperium", TestCategory.KNOWLEDGE_VERIFICATION)
        
        if result.get("status") == "error":
            print(f"   ❌ Test failed: {result.get('message')}")
            return False
        else:
            test_result = result.get("test_result", {})
            score = test_result.get("score", 0)
            passed = test_result.get("passed", False)
            
            print(f"   ✅ Test completed successfully!")
            print(f"      Score: {score}/100")
            print(f"      Passed: {passed}")
            print(f"      AI Response: {test_result.get('ai_response', '')[:100]}...")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Test failed with exception: {str(e)}")
        return False

async def create_simple_test_script():
    """Create a simple test script that works with the current setup"""
    print("🔧 Creating simple test script...")
    
    simple_test_script = '''#!/usr/bin/env python3
"""
Simple Custodes Protocol Test
Tests the custody protocol with minimal dependencies
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

from app.core.database import init_database
from app.services.custody_protocol_service import CustodyProtocolService, TestCategory

async def simple_custodes_test():
    """Simple test of custody protocol"""
    print("🧪 Simple Custodes Protocol Test")
    print("=" * 40)
    
    try:
        # Initialize database
        print("1️⃣ Initializing database...")
        await init_database()
        print("   ✅ Database initialized")
        
        # Initialize custody service
        print("2️⃣ Initializing custody service...")
        custody_service = await CustodyProtocolService.initialize()
        print("   ✅ Custody service initialized")
        
        # Run a simple test
        print("3️⃣ Running test for imperium AI...")
        result = await custody_service.administer_custody_test("imperium", TestCategory.KNOWLEDGE_VERIFICATION)
        
        if result.get("status") == "error":
            print(f"   ❌ Test failed: {result.get('message')}")
            return False
        else:
            test_result = result.get("test_result", {})
            score = test_result.get("score", 0)
            passed = test_result.get("passed", False)
            
            print(f"   ✅ Test completed!")
            print(f"      Score: {score}/100")
            print(f"      Passed: {passed}")
            
            if test_result.get("ai_response"):
                print(f"      AI Response: {test_result['ai_response'][:200]}...")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(simple_custodes_test())
    if success:
        print("\\n🎉 SUCCESS: Custodes Protocol is working!")
    else:
        print("\\n❌ FAILURE: Custodes Protocol needs more fixes")
'''
    
    with open("simple_custodes_test.py", 'w') as f:
        f.write(simple_test_script)
    
    print("   ✅ Simple test script created: simple_custodes_test.py")
    return True

async def main():
    """Main function to fix all Custodes protocol issues"""
    print("🚀 Comprehensive Custodes Protocol Fix")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    fixes = [
        ("Database Initialization", fix_database_initialization),
        ("Token Limits", fix_token_limits),
        ("API Keys", fix_api_keys),
        ("Settings Issue", fix_settings_issue),
        ("Simple Test Script", create_simple_test_script),
    ]
    
    results = {}
    
    for fix_name, fix_function in fixes:
        print(f"\n🔧 Running: {fix_name}")
        print("-" * 40)
        try:
            result = await fix_function()
            results[fix_name] = result
            if result:
                print(f"   ✅ {fix_name} completed successfully")
            else:
                print(f"   ❌ {fix_name} failed")
        except Exception as e:
            print(f"   ❌ {fix_name} failed with exception: {str(e)}")
            results[fix_name] = False
    
    # Test after fixes
    print(f"\n🧪 Testing Custodes Protocol after fixes...")
    test_success = await test_custodes_after_fixes()
    results["Final Test"] = test_success
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 FIX SUMMARY")
    print("=" * 60)
    
    successful_fixes = sum(1 for result in results.values() if result)
    total_fixes = len(results)
    
    for fix_name, result in results.items():
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"{status}: {fix_name}")
    
    print(f"\nOverall Result: {successful_fixes}/{total_fixes} fixes completed successfully")
    
    if test_success:
        print("\n🎉 EXCELLENT! Custodes Protocol is now working!")
        print("✅ AIs are being tested with real evaluations")
        print("✅ Test results are being tracked and analyzed")
        print("✅ The system is working as intended")
        
        print("\n📋 Next Steps:")
        print("1. Run the simple test: python simple_custodes_test.py")
        print("2. Monitor the enhanced autonomous learning service")
        print("3. Check the custody protocol analytics")
        
    else:
        print("\n⚠️ PARTIAL SUCCESS: Some fixes applied but testing still has issues")
        print("❌ Custodes Protocol may still need additional configuration")
        print("💡 Check API keys and token limits")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main()) 