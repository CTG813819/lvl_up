#!/usr/bin/env python3
"""
Fix Learning Model - Add missing fields to resolve 'context' error
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import get_session, init_database
from app.models.sql_models import Learning
from sqlalchemy import select, update
import structlog

logger = structlog.get_logger()


async def fix_learning_model():
    """Fix the Learning model by adding missing fields"""
    try:
        print("🔧 Fixing Learning model...")
        
        # Initialize database first
        print("📊 Initializing database...")
        await init_database()
        print("✅ Database initialized successfully")
        
        # First, let's check the current Learning model structure
        async with get_session() as session:
            # Get a sample Learning entry to see current structure
            result = await session.execute(select(Learning).limit(1))
            sample = result.scalars().first()
            
            if sample:
                print(f"Current Learning model fields: {[col.name for col in Learning.__table__.columns]}")
            else:
                print("No Learning entries found")
        
        # Create a migration script to add missing fields
        migration_script = '''
-- Migration to add missing fields to Learning model
-- Run this in your PostgreSQL database

-- Add missing fields if they don't exist
DO $$ 
BEGIN
    -- Add context field if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'learning' AND column_name = 'context'
    ) THEN
        ALTER TABLE learning ADD COLUMN context TEXT;
    END IF;
    
    -- Add pattern field if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'learning' AND column_name = 'pattern'
    ) THEN
        ALTER TABLE learning ADD COLUMN pattern TEXT;
    END IF;
    
    -- Add feedback field if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'learning' AND column_name = 'feedback'
    ) THEN
        ALTER TABLE learning ADD COLUMN feedback TEXT;
    END IF;
    
    -- Add applied_count field if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'learning' AND column_name = 'applied_count'
    ) THEN
        ALTER TABLE learning ADD COLUMN applied_count INTEGER DEFAULT 0;
    END IF;
    
    -- Add success_rate field if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'learning' AND column_name = 'success_rate'
    ) THEN
        ALTER TABLE learning ADD COLUMN success_rate FLOAT DEFAULT 0.0;
    END IF;
    
    -- Add confidence field if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'learning' AND column_name = 'confidence'
    ) THEN
        ALTER TABLE learning ADD COLUMN confidence FLOAT DEFAULT 0.5;
    END IF;
    
    RAISE NOTICE 'Learning table migration completed successfully';
END $$;
'''
        
        # Save migration script
        with open('fix_learning_model_migration.sql', 'w') as f:
            f.write(migration_script)
        
        print("✅ Created migration script: fix_learning_model_migration.sql")
        
        # Also create a Python patch for the model
        model_patch = '''
# Add these properties to the Learning class in app/models/sql_models.py

@property
def context(self) -> str:
    """Get context from learning data or return default"""
    try:
        if hasattr(self, 'context') and self.context:
            return self.context
        if self.learning_data and isinstance(self.learning_data, dict):
            return self.learning_data.get('context', '')
        return ''
    except Exception:
        return ''

@property
def pattern(self) -> str:
    """Get pattern from learning data or return default"""
    try:
        if hasattr(self, 'pattern') and self.pattern:
            return self.pattern
        if self.learning_data and isinstance(self.learning_data, dict):
            return self.learning_data.get('pattern', '')
        return ''
    except Exception:
        return ''

@property
def feedback(self) -> str:
    """Get feedback from learning data or return default"""
    try:
        if hasattr(self, 'feedback') and self.feedback:
            return self.feedback
        if self.learning_data and isinstance(self.learning_data, dict):
            return self.learning_data.get('feedback', '')
        return ''
    except Exception:
        return ''

@property
def applied_count(self) -> int:
    """Get applied count from learning data or return default"""
    try:
        if hasattr(self, 'applied_count') and self.applied_count is not None:
            return self.applied_count
        if self.learning_data and isinstance(self.learning_data, dict):
            return self.learning_data.get('applied_count', 0)
        return 0
    except Exception:
        return 0

@property
def success_rate(self) -> float:
    """Get success rate from learning data or return default"""
    try:
        if hasattr(self, 'success_rate') and self.success_rate is not None:
            return self.success_rate
        if self.learning_data and isinstance(self.learning_data, dict):
            return self.learning_data.get('success_rate', 0.0)
        return 0.0
    except Exception:
        return 0.0

@property
def confidence(self) -> float:
    """Get confidence from learning data or return default"""
    try:
        if hasattr(self, 'confidence') and self.confidence is not None:
            return self.confidence
        if self.learning_data and isinstance(self.learning_data, dict):
            return self.learning_data.get('confidence', 0.5)
        return 0.5
    except Exception:
        return 0.5
'''
        
        # Save model patch
        with open('learning_model_patch.py', 'w') as f:
            f.write(model_patch)
        
        print("✅ Created model patch: learning_model_patch.py")
        
        # Update existing Learning entries to have proper learning_data structure
        async with get_session() as session:
            result = await session.execute(select(Learning))
            learning_entries = result.scalars().all()
            
            updated_count = 0
            for entry in learning_entries:
                if not entry.learning_data:
                    # Create default learning_data structure
                    entry.learning_data = {
                        "pattern": f"legacy_pattern_{entry.id}",
                        "context": f"Migrated from legacy entry {entry.id}",
                        "feedback": "Legacy entry migration",
                        "applied_count": 1,
                        "success_rate": 0.5,
                        "confidence": 0.5
                    }
                    updated_count += 1
                elif isinstance(entry.learning_data, dict):
                    # Ensure all required fields exist
                    if "pattern" not in entry.learning_data:
                        entry.learning_data["pattern"] = f"pattern_{entry.id}"
                    if "context" not in entry.learning_data:
                        entry.learning_data["context"] = f"context_{entry.id}"
                    if "feedback" not in entry.learning_data:
                        entry.learning_data["feedback"] = "Default feedback"
                    if "applied_count" not in entry.learning_data:
                        entry.learning_data["applied_count"] = 1
                    if "success_rate" not in entry.learning_data:
                        entry.learning_data["success_rate"] = 0.5
                    if "confidence" not in entry.learning_data:
                        entry.learning_data["confidence"] = 0.5
                    updated_count += 1
            
            await session.commit()
            print(f"✅ Updated {updated_count} Learning entries with proper data structure")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing Learning model: {str(e)}")
        logger.error("Learning model fix failed", error=str(e))
        return False


async def main():
    """Main function to fix Learning model"""
    try:
        print("🔧 Learning Model Fix")
        print("====================")
        
        success = await fix_learning_model()
        
        if success:
            print("\n✅ Learning model fix completed successfully!")
            print("\n📋 Next Steps:")
            print("1. Run the SQL migration: psql -d your_database -f fix_learning_model_migration.sql")
            print("2. Apply the model patch to app/models/sql_models.py")
            print("3. Restart the backend service")
            print("4. Test the Learning functionality")
        else:
            print("\n❌ Learning model fix failed!")
            print("Please check the logs for detailed error information.")
        
    except Exception as e:
        print(f"\n❌ Error in main execution: {str(e)}")
        logger.error("Main execution error", error=str(e))


if __name__ == "__main__":
    asyncio.run(main()) 