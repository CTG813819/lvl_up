#!/usr/bin/env python3
"""
Test script to verify SckipitService initialization and method availability
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_sckipit_service():
    """Test SckipitService initialization and method availability"""
    try:
        print("🔍 Testing SckipitService initialization...")
        
        # Import and initialize SckipitService
        from app.services.sckipit_service import SckipitService
        sckipit = await SckipitService.initialize()
        print("✅ SckipitService initialized successfully")
        
        # Test if the generate_answer_with_llm method exists
        print("🔧 Testing generate_answer_with_llm method...")
        if hasattr(sckipit, 'generate_answer_with_llm'):
            print("✅ generate_answer_with_llm method found")
            
            # Test the method
            result = await sckipit.generate_answer_with_llm("Test prompt for adversarial testing")
            print("✅ generate_answer_with_llm method works:", result)
        else:
            print("❌ generate_answer_with_llm method not found")
            
        print("\n🎉 SckipitService test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing SckipitService: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sckipit_service()) 