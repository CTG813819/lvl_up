#!/usr/bin/env python3
"""
Test script to verify the Learning model fix
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import get_session, init_database
from app.models.sql_models import Learning
from sqlalchemy import select
import structlog

logger = structlog.get_logger()

async def test_learning_model_fix():
    """Test that the Learning model works correctly with the new structure"""
    try:
        print("🧪 Testing Learning model fix...")
        
        # Initialize database
        await init_database()
        print("✅ Database initialized")
        
        async with get_session() as session:
            # Test creating a new Learning entry with the correct structure
            test_learning = Learning(
                ai_type="test_ai",
                learning_type="proposal_outcome",
                learning_data={
                    'pattern': 'test_pattern',
                    'context': 'Test context',
                    'feedback': 'Test feedback',
                    'confidence': 0.8,
                    'applied_count': 1,
                    'success_rate': 1.0
                }
            )
            
            session.add(test_learning)
            await session.commit()
            print("✅ Successfully created Learning entry with new structure")
            
            # Test retrieving the learning entry
            result = await session.execute(
                select(Learning).where(Learning.ai_type == "test_ai")
            )
            retrieved_learning = result.scalar_one_or_none()
            
            if retrieved_learning:
                print(f"✅ Retrieved Learning entry: {retrieved_learning.id}")
                print(f"   AI Type: {retrieved_learning.ai_type}")
                print(f"   Learning Type: {retrieved_learning.learning_type}")
                print(f"   Learning Data: {retrieved_learning.learning_data}")
                
                # Test accessing data from learning_data
                learning_data = retrieved_learning.learning_data or {}
                pattern = learning_data.get('pattern', '')
                context = learning_data.get('context', '')
                success_rate = learning_data.get('success_rate', 0.0)
                
                print(f"   Pattern: {pattern}")
                print(f"   Context: {context}")
                print(f"   Success Rate: {success_rate}")
                
                print("✅ All Learning model operations working correctly!")
                return True
            else:
                print("❌ Failed to retrieve Learning entry")
                return False
                
    except Exception as e:
        print(f"❌ Error testing Learning model: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_learning_model_fix())
    if success:
        print("🎉 Learning model fix test passed!")
    else:
        print("💥 Learning model fix test failed!")
        sys.exit(1) 