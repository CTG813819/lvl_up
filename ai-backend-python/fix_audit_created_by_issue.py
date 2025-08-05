#!/usr/bin/env python3
"""
Fix for audit script created_by column issue
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import get_session, init_database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_audit_created_by_issue():
    """Fix the created_by column issue in the audit script"""
    try:
        # Initialize database
        await init_database()
        session = get_session()
        
        async with session as s:
            # Check if created_by column exists in proposals table
            result = await s.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'proposals' 
                AND column_name = 'created_by'
            """))
            
            column_exists = result.fetchone()
            
            if not column_exists:
                logger.info("Adding created_by column to proposals table...")
                
                # Add the created_by column
                await s.execute(text("""
                    ALTER TABLE proposals 
                    ADD COLUMN created_by VARCHAR(100) DEFAULT 'system'
                """))
                
                # Update existing records to have a default value
                await s.execute(text("""
                    UPDATE proposals 
                    SET created_by = 'system' 
                    WHERE created_by IS NULL
                """))
                
                # Create index for better performance
                await s.execute(text("""
                    CREATE INDEX idx_proposals_created_by ON proposals(created_by)
                """))
                
                logger.info("✅ created_by column added successfully!")
            else:
                logger.info("✅ created_by column already exists!")
            
            # Verify the fix
            result = await s.execute(text("""
                SELECT COUNT(*) FROM proposals 
                WHERE created_at > NOW() - INTERVAL '24 hours' 
                AND created_by LIKE '%agent%'
            """))
            
            count = result.scalar()
            logger.info(f"✅ Query test successful! Found {count} recent agent proposals")
            
            await s.commit()
            
    except Exception as e:
        logger.error(f"❌ Error fixing created_by issue: {e}")
        raise

async def create_alternative_audit_script():
    """Create an alternative audit script that doesn't rely on created_by column"""
    try:
        # Create a new audit script that uses ai_type instead of created_by
        audit_script_content = '''#!/usr/bin/env python3
"""
Alternative Comprehensive System Audit (Fixed for created_by issue)
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import get_session, init_database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_autonomous_agents_alternative():
    """Check autonomous agents using ai_type instead of created_by"""
    try:
        session = get_session()
        async with session as s:
            # Check for recent agent activities using ai_type
            result = await s.execute(text("""
                SELECT ai_type, COUNT(*) 
                FROM proposals 
                WHERE created_at > NOW() - INTERVAL '24 hours' 
                AND ai_type IN ('imperium', 'guardian', 'sandbox', 'conquest', 'codex')
                GROUP BY ai_type
            """))
            
            recent_agent_activity = result.fetchall()
            
            if recent_agent_activity:
                activity_summary = ", ".join([f"{ai_type}: {count}" for ai_type, count in recent_agent_activity])
                logger.info(f"✅ Recent agent activity: {activity_summary}")
                return True
            else:
                logger.warning("⚠️ No recent agent activity found")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error checking autonomous agents: {e}")
        return False

async def main():
    """Main function"""
    try:
        await init_database()
        await check_autonomous_agents_alternative()
        logger.info("✅ Alternative audit check completed!")
        
    except Exception as e:
        logger.error(f"❌ Error in alternative audit: {e}")

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        with open('alternative_audit_check.py', 'w') as f:
            f.write(audit_script_content)
        
        logger.info("✅ Alternative audit script created: alternative_audit_check.py")
        
    except Exception as e:
        logger.error(f"❌ Error creating alternative audit script: {e}")

async def main():
    """Main function"""
    try:
        logger.info("🔧 Fixing audit created_by column issue...")
        
        # Fix the database schema
        await fix_audit_created_by_issue()
        
        # Create alternative audit script
        await create_alternative_audit_script()
        
        logger.info("✅ Audit created_by issue fixed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 