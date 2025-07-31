#!/usr/bin/env python3
"""
Check Conquest Deployments in Database
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

async def check_deployments():
    """Check conquest deployments in database"""
    try:
        from app.core.database import init_database, get_session
        from app.models.sql_models import ConquestDeployment
        from sqlalchemy import select
        
        print("🔍 Checking conquest deployments in database...")
        
        # Initialize database
        await init_database()
        
        # Get session
        session = get_session()
        
        try:
            # Query all deployments
            stmt = select(ConquestDeployment).order_by(ConquestDeployment.created_at.desc())
            result = await session.execute(stmt)
            deployments = result.scalars().all()
            
            print(f"📊 Total deployments found: {len(deployments)}")
            print("=" * 50)
            
            if len(deployments) == 0:
                print("❌ No deployments found in database")
                print("This explains why the frontend only shows 1 progress log")
            else:
                for i, deployment in enumerate(deployments, 1):
                    print(f"{i}. {deployment.app_name}")
                    print(f"   Status: {deployment.status}")
                    print(f"   Created: {deployment.created_at}")
                    print(f"   ID: {deployment.id}")
                    if deployment.error_message:
                        print(f"   Error: {deployment.error_message}")
                    print()
            
            # Check if tables exist
            print("🔍 Checking if conquest_deployments table exists...")
            from sqlalchemy import text
            result = await session.execute(text("SELECT COUNT(*) FROM conquest_deployments"))
            count = result.scalar()
            print(f"✅ Table exists with {count} records")
            
        finally:
            await session.close()
            
    except Exception as e:
        print(f"❌ Error checking deployments: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_deployments()) 