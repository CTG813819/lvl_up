#!/usr/bin/env python3
"""
Test script to check learning insights generation
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_database
from app.services.ai_learning_service import AILearningService
from app.services.enhanced_learning_service import enhanced_learning_service

async def test_learning_insights():
    """Test if learning insights are being generated properly"""
    try:
        print("🔧 Initializing database...")
        await init_database()
        
        print("🔧 Initializing AI Learning Service...")
        learning_service = await AILearningService.initialize()
        
        print("🔧 Testing learning insights for each AI type...")
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            print(f"\n📊 Testing {ai_type}...")
            
            # Get learning insights
            insights = await learning_service.get_learning_insights(ai_type)
            print(f"   Learning stats: {insights.get('learning_stats', {})}")
            print(f"   Recent patterns: {len(insights.get('recent_patterns', []))} patterns")
            print(f"   Failure analytics: {insights.get('failure_analytics', {})}")
            
            # Try to record a learning event
            print(f"   Recording test learning event for {ai_type}...")
            await learning_service.record_learning_event(
                ai_type, 
                "test_event", 
                {"test_data": "sample", "timestamp": "2025-08-03T11:00:00"}
            )
            
            # Get insights again to see if they changed
            updated_insights = await learning_service.get_learning_insights(ai_type)
            print(f"   Updated patterns: {len(updated_insights.get('recent_patterns', []))} patterns")
        
        print("\n🔧 Testing enhanced learning service...")
        await enhanced_learning_service.start_enhanced_learning()
        
        print("\n✅ Learning insights test completed!")
        
    except Exception as e:
        print(f"❌ Error testing learning insights: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_learning_insights()) 