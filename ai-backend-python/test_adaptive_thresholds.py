#!/usr/bin/env python3
"""
Test script for adaptive threshold system
"""

import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.adaptive_threshold_service import AdaptiveThresholdService, TestType, TestComplexity

async def test_adaptive_thresholds():
    """Test the adaptive threshold system"""
    
    print("🧪 Testing Adaptive Threshold System...")
    
    try:
        # Initialize the service
        threshold_service = await AdaptiveThresholdService.initialize()
        print("✅ Adaptive Threshold Service initialized")
        
        # Test base thresholds
        print("\n📊 Testing base thresholds:")
        for test_type in TestType:
            for complexity in TestComplexity:
                base_min, base_max = threshold_service.get_base_thresholds(test_type, complexity)
                print(f"  {test_type.value} {complexity.value}: {base_min}-{base_max}")
        
        # Test adaptive thresholds
        print("\n🎯 Testing adaptive thresholds:")
        for test_type in TestType:
            for complexity in TestComplexity:
                threshold = await threshold_service.get_adaptive_threshold(test_type, complexity)
                print(f"  {test_type.value} {complexity.value}: {threshold}")
        
        # Test AI-specific thresholds
        print("\n🤖 Testing AI-specific thresholds:")
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        for ai_type in ai_types:
            for test_type in TestType:
                for complexity in TestComplexity:
                    threshold = await threshold_service.get_ai_specific_threshold(test_type, complexity, ai_type)
                    print(f"  {ai_type} {test_type.value} {complexity.value}: {threshold}")
        
        # Test threshold analytics
        print("\n📈 Testing threshold analytics:")
        analytics = await threshold_service.get_threshold_analytics()
        print(f"  Analytics keys: {list(analytics.keys())}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing adaptive thresholds: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_adaptive_thresholds()) 