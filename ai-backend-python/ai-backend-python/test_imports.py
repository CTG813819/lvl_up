#!/usr/bin/env python3
"""
Test script to check imports
"""
import sys
import os

# Add the ai-backend-python directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

try:
    print("Testing imports...")
    
    # Test database imports
    from app.core.database import init_database, SessionLocal
    print("✅ Database imports successful")
    
    # Test proposal cycle service
    from app.services.proposal_cycle_service import ProposalCycleService
    print("✅ Proposal cycle service import successful")
    
    # Test models
    from app.models.sql_models import Proposal
    print("✅ Models import successful")
    
    print("✅ All imports successful!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc() 