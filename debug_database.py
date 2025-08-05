#!/usr/bin/env python3
"""
Debug script to test database connection
"""

import os
import sys

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

print("Environment variables loaded")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')[:50] + '...' if os.getenv('DATABASE_URL') else 'None'}")

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python/app'))

try:
    from app.core.database import engine, init_database
    print(f"Engine imported: {engine}")
    
    if engine is None:
        print("Engine is None - this is the problem!")
    else:
        print("Engine is not None - should work")
        
except Exception as e:
    print(f"Error importing database: {e}") 