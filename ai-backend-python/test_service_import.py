#!/usr/bin/env python3
import sys
import os

# Add the ai-backend-python directory to the path
sys.path.insert(0, 'ai-backend-python')

try:
    print("Testing import of enhanced adversarial testing service...")
    from app.services.enhanced_adversarial_testing_service import EnhancedAdversarialTestingService
    print("✅ Import successful")
    
    print("Testing service initialization...")
    service = EnhancedAdversarialTestingService()
    print("✅ Service instance created")
    
    print("✅ All tests passed - service should be able to start")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 