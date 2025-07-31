#!/usr/bin/env python3
"""
Integration Verification Script
=============================

This script verifies that diverse test generation and improved scoring
are properly integrated into the main service.
"""

import asyncio
import sys
import os
from datetime import datetime
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import structlog

logger = structlog.get_logger()

async def verify_integration():
    """Verify that diverse tests and improved scoring are integrated"""
    try:
        print("🔍 Verifying integration...")
        
        # Check if the custody service has the new imports
        custody_file = "app/services/custody_protocol_service.py"
        
        if os.path.exists(custody_file):
            with open(custody_file, 'r') as f:
                content = f.read()
            
            # Check for diverse test generator import
            if "from diverse_test_generator import DiverseTestGenerator" in content:
                print("✅ Diverse test generator import found")
            else:
                print("❌ Diverse test generator import not found")
            
            # Check for improved scoring system import
            if "from improved_scoring_system import ImprovedScoringSystem" in content:
                print("✅ Improved scoring system import found")
            else:
                print("❌ Improved scoring system import not found")
            
            # Check for diverse test generator initialization
            if "self.diverse_test_generator = None" in content:
                print("✅ Diverse test generator initialization found")
            else:
                print("❌ Diverse test generator initialization not found")
            
            # Check for improved scoring system initialization
            if "self.improved_scorer = None" in content:
                print("✅ Improved scoring system initialization found")
            else:
                print("❌ Improved scoring system initialization not found")
            
            # Check for diverse test generation logic
            if "diverse_test_generator.generate_diverse_test" in content:
                print("✅ Diverse test generation logic found")
            else:
                print("❌ Diverse test generation logic not found")
            
            return True
            
        else:
            print("❌ Custody service file not found")
            return False
        
    except Exception as e:
        print(f"❌ Error verifying integration: {e}")
        return False

async def main():
    """Main function"""
    print("🚀 Starting Integration Verification")
    print("=" * 40)
    
    await verify_integration()
    
    print("\n✅ Integration verification completed!")

if __name__ == "__main__":
    asyncio.run(main()) 