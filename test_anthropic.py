#!/usr/bin/env python3

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.services.anthropic_service import call_claude
    print("Testing Claude integration...")
    response = call_claude("Say hello from Claude!")
    print(f"Claude response: {response}")
except Exception as e:
    print(f"Error testing Claude: {e}")
    import traceback
    traceback.print_exc() 