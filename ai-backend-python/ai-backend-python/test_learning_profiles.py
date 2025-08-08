#!/usr/bin/env python3
"""
Test Learning Profile Creation
See what subjects and patterns are being extracted from the database
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_database
from app.services.custodes_fallback_testing import CustodesFallbackTesting

async def test_learning_profiles():
    """Test learning profile creation"""
    print("🧪 Testing learning profile creation...")
    
    # Initialize database
    await init_database()
    
    # Initialize fallback service
    fallback_service = CustodesFallbackTesting()
    
    # Test learning from all AIs
    print("🔄 Learning from all AIs...")
    profiles = await fallback_service.learn_from_all_ais()
    
    print(f"\n📊 Learning Profiles Created: {len(profiles)}")
    
    for ai_type, profile in profiles.items():
        print(f"\n🤖 {ai_type.upper()} Profile:")
        print(f"   Subjects learned: {len(profile.subjects_learned)}")
        if profile.subjects_learned:
            print(f"   Subjects: {profile.subjects_learned[:10]}...")  # Show first 10
        print(f"   Code patterns: {len(profile.code_patterns)}")
        if profile.code_patterns:
            print(f"   Patterns: {profile.code_patterns}")
        print(f"   Improvement types: {len(profile.improvement_types)}")
        if profile.improvement_types:
            print(f"   Types: {profile.improvement_types}")
        print(f"   File types: {len(profile.file_types_worked)}")
        if profile.file_types_worked:
            print(f"   Files: {profile.file_types_worked}")
        print(f"   Learning score: {profile.learning_score}")
        print(f"   Level: {profile.level}")
        print(f"   XP: {profile.xp}")

if __name__ == "__main__":
    asyncio.run(test_learning_profiles()) 