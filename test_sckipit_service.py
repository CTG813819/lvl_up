#!/usr/bin/env python3
"""
Test SckipitService to verify it's working properly
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.sckipit_service import SckipitService

async def test_sckipit_service():
    """Test the SckipitService"""
    print("🔍 Testing SckipitService")
    print("=" * 40)
    
    try:
        # Initialize SckipitService
        print("🔧 Initializing SckipitService...")
        sckipit = await SckipitService.initialize()
        print("✅ SckipitService initialized successfully")
        
        # Test if the service has the generate_answer_with_llm method
        print("🔧 Checking for generate_answer_with_llm method...")
        if hasattr(sckipit, 'generate_answer_with_llm'):
            print("✅ generate_answer_with_llm method found")
            
            # Test the method
            print("🔧 Testing generate_answer_with_llm...")
            test_prompt = "Generate a simple test scenario for AI competition"
            result = await sckipit.generate_answer_with_llm(test_prompt)
            print(f"✅ Method executed successfully")
            print(f"📊 Result type: {type(result)}")
            print(f"📊 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        else:
            print("❌ generate_answer_with_llm method not found")
            print(f"📊 Available methods: {[method for method in dir(sckipit) if not method.startswith('_')]}")
        
        # Test other methods
        print("\n🔧 Testing other methods...")
        
        # Test get_sckipit_status
        if hasattr(sckipit, 'get_sckipit_status'):
            status = await sckipit.get_sckipit_status()
            print(f"✅ get_sckipit_status: {status}")
        
        # Test generate_dart_code_from_description_async
        if hasattr(sckipit, 'generate_dart_code_from_description_async'):
            code = await sckipit.generate_dart_code_from_description_async("Create a simple button widget")
            print(f"✅ generate_dart_code_from_description_async: Generated {len(code)} characters")
        
        print("\n🎉 SckipitService test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing SckipitService: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main function"""
    try:
        await test_sckipit_service()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 