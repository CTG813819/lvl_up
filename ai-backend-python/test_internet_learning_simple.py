#!/usr/bin/env python3
"""
Simple test for internet learning capabilities
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_internet_learning():
    """Test internet learning functionality"""
    try:
        print("🧠 Testing Internet Learning...")
        
        # Import the service
        from app.services.project_horus_service import ProjectHorusService
        
        # Initialize service
        project_horus = ProjectHorusService()
        
        # Test internet learning
        print("📚 Learning from internet sources...")
        result = await project_horus.learn_from_internet()
        
        print(f"✅ Learning completed!")
        print(f"📊 Status: {result.get('status', 'unknown')}")
        print(f"📚 Topics researched: {len(result.get('topics_researched', []))}")
        print(f"🧠 Learning progress: {result.get('learning_progress', 0)}")
        print(f"⚛️ Chaos complexity: {result.get('chaos_complexity', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_internet_learning()) 