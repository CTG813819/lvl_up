#!/usr/bin/env python3
"""
Test script to verify fixes work
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

async def test_learning_service():
    """Test the fixed learning service"""
    try:
        from services.ai_learning_service import AILearningService
        from core.database import get_session
        from models.sql_models import Learning
        
        learning_service = AILearningService()
        
        # Test creating a learning entry
        async with get_session() as session:
            # Test basic database connection
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            print("✅ Database connection test passed")
            
            # Test Learning model creation with proper data structure
            test_learning = Learning(
                ai_type="test_ai",
                learning_type="test_learning",
                learning_data={
                    "pattern_id": "test_pattern",
                    "success_rate": 0.8,
                    "confidence": 0.9,
                    "applied_count": 1,
                    "context": "Test learning entry"
                },
                status="active"
            )
            session.add(test_learning)
            await session.commit()
            print("✅ Learning model creation test passed")
            
            # Clean up
            await session.delete(test_learning)
            await session.commit()
            print("✅ Learning model cleanup test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Learning service test failed: {e}")
        return False

async def test_learning_insights():
    """Test learning insights endpoint"""
    try:
        from routers.learning import get_learning_insights
        from core.database import get_session
        
        # Test with a valid AI type
        result = await get_learning_insights("Imperium")
        print("✅ Learning insights test passed")
        return True
        
    except Exception as e:
        print(f"❌ Learning insights test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing comprehensive fixes...")
    
    # Test learning service
    learning_ok = await test_learning_service()
    
    # Test learning insights
    insights_ok = await test_learning_insights()
    
    if learning_ok and insights_ok:
        print("🎉 All tests passed! Comprehensive fixes are working.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    asyncio.run(main())
