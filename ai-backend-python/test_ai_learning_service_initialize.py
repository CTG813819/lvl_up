#!/usr/bin/env python3
"""
Test script to verify AILearningService initialize method works
"""

import asyncio
import sys
import os

# Add the ai-backend-python directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

from app.services.ai_learning_service import AILearningService

async def test_initialize():
    """Test the AILearningService initialize method"""
    try:
        print("Testing AILearningService.initialize()...")
        
        # Test the initialize method
        instance = await AILearningService.initialize()
        
        if instance is not None:
            print("✅ AILearningService.initialize() works correctly!")
            print(f"Instance type: {type(instance)}")
            print(f"Instance initialized: {instance._initialized}")
            return True
        else:
            print("❌ AILearningService.initialize() returned None")
            return False
            
    except Exception as e:
        print(f"❌ Error testing AILearningService.initialize(): {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_initialize())
    sys.exit(0 if result else 1) 