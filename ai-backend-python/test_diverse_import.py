#!/usr/bin/env python3
"""
Test Diverse Test Generator Import
=================================

This script tests if the diverse test generator can be imported successfully.
"""

try:
    from diverse_test_generator import DiverseTestGenerator
    print("✅ DiverseTestGenerator imported successfully")
    
    # Test creating an instance
    generator = DiverseTestGenerator()
    print("✅ DiverseTestGenerator instance created successfully")
    
    # Test generating a test
    test = generator.generate_diverse_test("custody", "imperium")
    print(f"✅ Generated test: {test['title']}")
    
    # Test generating a response
    response = generator.generate_ai_response("imperium", test)
    print(f"✅ Generated response with score: {response['score']}")
    
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 