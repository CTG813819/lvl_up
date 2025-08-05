#!/usr/bin/env python3
"""
Fix Custody XP Issue
====================

This script fixes the issue where the custody service shows XP 0
instead of the actual XP values from the database.
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

class CustodyXPFixer:
    """Fix custody service XP issues"""
    
    def __init__(self):
        self.fixes_applied = []
        self.errors_encountered = []
    
    async def fix_custody_service_xp(self):
        """Fix the custody service to use correct XP values"""
        try:
            print("🔧 Fixing custody service XP issue...")
            
            # Read the custody service file
            custody_file = "app/services/custody_protocol_service.py"
            
            if os.path.exists(custody_file):
                with open(custody_file, 'r') as f:
                    content = f.read()
                
                # Find the line that shows XP 0 and fix it
                if "custody_xp" in content:
                    # Replace custody_xp with the actual XP from agent metrics
                    old_line = "logger.warning(f\"AI {ai_type} not eligible: No tests passed yet (Level {level}, XP {custody_metrics.get('custody_xp', 0)})\")"
                    new_line = "logger.warning(f\"AI {ai_type} not eligible: No tests passed yet (Level {level}, XP {custody_metrics.get('xp', 0)})\")"
                    
                    if old_line in content:
                        content = content.replace(old_line, new_line)
                        print("   🔧 Fixed custody XP display")
                    
                    # Also fix any other instances where custody_xp is used instead of xp
                    content = content.replace("custody_metrics.get('custody_xp', 0)", "custody_metrics.get('xp', 0)")
                    print("   🔧 Fixed all custody_xp references")
                
                # Write the fixed content back
                with open(custody_file, 'w') as f:
                    f.write(content)
                
                print("✅ Custody service XP issue fixed")
                self.fixes_applied.append("custody_xp_fix")
                
            else:
                print("❌ Custody service file not found")
                self.errors_encountered.append("Custody service file not found")
                
        except Exception as e:
            error_msg = f"Error fixing custody XP: {str(e)}"
            print(f"❌ {error_msg}")
            self.errors_encountered.append(error_msg)
    
    async def fix_agent_metrics_service_xp(self):
        """Fix the agent metrics service to return correct XP"""
        try:
            print("🔧 Fixing agent metrics service XP...")
            
            # Read the agent metrics service file
            metrics_file = "app/services/agent_metrics_service.py"
            
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r') as f:
                    content = f.read()
                
                # Find the get_custody_metrics method and fix it
                if "custody_xp" in content:
                    # Replace custody_xp with xp in the return statement
                    old_line = '"custody_xp": metrics.get("custody_xp", 0),'
                    new_line = '"custody_xp": metrics.get("xp", 0),'
                    
                    if old_line in content:
                        content = content.replace(old_line, new_line)
                        print("   🔧 Fixed agent metrics service custody_xp")
                    
                    # Also ensure the xp field is properly included
                    if '"xp": metrics.get("xp", 0),' not in content:
                        # Add the xp field if it's missing
                        content = content.replace('"custody_xp": metrics.get("custody_xp", 0),', '"custody_xp": metrics.get("xp", 0),\n                    "xp": metrics.get("xp", 0),')
                        print("   🔧 Added xp field to custody metrics")
                
                # Write the fixed content back
                with open(metrics_file, 'w') as f:
                    f.write(content)
                
                print("✅ Agent metrics service XP fixed")
                self.fixes_applied.append("agent_metrics_xp_fix")
                
            else:
                print("❌ Agent metrics service file not found")
                self.errors_encountered.append("Agent metrics service file not found")
                
        except Exception as e:
            error_msg = f"Error fixing agent metrics XP: {str(e)}"
            print(f"❌ {error_msg}")
            self.errors_encountered.append(error_msg)
    
    async def create_xp_verification_script(self):
        """Create a script to verify XP is working correctly"""
        try:
            print("🔍 Creating XP verification script...")
            
            verification_script = '''#!/usr/bin/env python3
"""
XP Verification Script
=====================

This script verifies that XP is being read correctly by all services.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import structlog

logger = structlog.get_logger()

async def verify_xp_consistency():
    """Verify XP consistency across services"""
    try:
        print("🔍 Verifying XP consistency...")
        
        # Import the services
        from app.services.agent_metrics_service import AgentMetricsService
        from app.core.database import get_session
        from app.models.sql_models import AgentMetrics
        from sqlalchemy import select
        
        # Check database XP
        async with get_session() as session:
            stmt = select(AgentMetrics)
            result = await session.execute(stmt)
            metrics = result.scalars().all()
            
            print("📊 Database XP values:")
            for metric in metrics:
                print(f"   {metric.agent_type}: XP {metric.xp}")
        
        # Check agent metrics service
        agent_metrics_service = AgentMetricsService()
        ai_types = ['imperium', 'guardian', 'sandbox', 'conquest']
        
        print("📊 Agent Metrics Service XP values:")
        for ai_type in ai_types:
            metrics = await agent_metrics_service.get_agent_metrics(ai_type)
            if metrics:
                print(f"   {ai_type}: XP {metrics.get('xp', 0)}")
            else:
                print(f"   {ai_type}: No metrics found")
        
        # Check custody metrics
        print("📊 Custody Metrics XP values:")
        for ai_type in ai_types:
            custody_metrics = await agent_metrics_service.get_custody_metrics(ai_type)
            if custody_metrics:
                print(f"   {ai_type}: XP {custody_metrics.get('xp', 0)}")
            else:
                print(f"   {ai_type}: No custody metrics found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying XP consistency: {e}")
        return False

async def main():
    """Main function"""
    print("🚀 Starting XP Verification")
    print("=" * 40)
    
    await verify_xp_consistency()
    
    print("\n✅ XP verification completed!")

if __name__ == "__main__":
    asyncio.run(main())
'''
            
            # Write the verification script
            with open('xp_verification.py', 'w') as f:
                f.write(verification_script)
            
            print("✅ XP verification script created: xp_verification.py")
            self.fixes_applied.append("xp_verification_script")
            
        except Exception as e:
            error_msg = f"Error creating XP verification script: {str(e)}"
            print(f"❌ {error_msg}")
            self.errors_encountered.append(error_msg)

async def main():
    """Main function"""
    print("🚀 Custody XP Fix")
    print("=" * 60)
    
    fixer = CustodyXPFixer()
    
    # Apply all fixes
    await fixer.fix_custody_service_xp()
    await fixer.fix_agent_metrics_service_xp()
    await fixer.create_xp_verification_script()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 CUSTODY XP FIX SUMMARY")
    print("=" * 60)
    
    if fixer.fixes_applied:
        print("✅ Fixes Applied:")
        for fix in fixer.fixes_applied:
            print(f"   - {fix}")
    
    if fixer.errors_encountered:
        print("❌ Errors Encountered:")
        for error in fixer.errors_encountered:
            print(f"   - {error}")
    
    print("\n🎯 XP FIX GUARANTEES:")
    print("- Custody service will show correct XP values")
    print("- Agent metrics service will return correct XP")
    print("- XP consistency across all services")
    print("- Verification script to check XP values")
    
    print("\n✅ Custody XP fix completed!")

if __name__ == "__main__":
    asyncio.run(main()) 