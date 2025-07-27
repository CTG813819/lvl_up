#!/usr/bin/env python3
"""
Simple script to check database schema
"""

import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

from app.core.database import init_database
from sqlalchemy import text

async def check_schema():
    """Check if required columns exist"""
    try:
        await init_database()
        
        # Import engine after initialization
        from app.core.database import engine
        
        if not engine:
            print("❌ Database engine is None after initialization")
            return False
        
        async with engine.begin() as conn:
            # Check for ai_learning_summary column
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'proposals' 
                AND column_name = 'ai_learning_summary'
            """))
            
            ai_learning_summary_exists = result.scalar() is not None
            print(f"ai_learning_summary column exists: {ai_learning_summary_exists}")
            
            # Check for other critical columns
            critical_columns = [
                'change_type', 'change_scope', 'affected_components', 
                'learning_sources', 'expected_impact', 'risk_assessment',
                'application_response', 'application_timestamp', 
                'application_result', 'post_application_analysis'
            ]
            
            missing_columns = []
            for column in critical_columns:
                result = await conn.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'proposals' 
                    AND column_name = '{column}'
                """))
                if result.scalar() is None:
                    missing_columns.append(column)
            
            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
                return False
            else:
                print("✅ All critical columns are present")
                return True
                
    except Exception as e:
        print(f"❌ Error checking schema: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(check_schema())
    sys.exit(0 if success else 1) 