#!/usr/bin/env python3
import sys
import os

# Add the ai-backend-python directory to the path
sys.path.insert(0, 'ai-backend-python')

try:
    print("Testing AI Agent Service availability...")
    from app.services.ai_agent_service import AIAgentService
    print("✅ AI Agent Service import successful")
    
    print("Testing AI Agent Service initialization...")
    ai_service = AIAgentService()
    print("✅ AI Agent Service instance created")
    
    print("✅ AI Agent Service is available")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 