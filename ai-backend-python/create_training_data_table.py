#!/usr/bin/env python3
"""
Script to create the training_data table for the Book of Lorgar feature.
This table stores user-uploaded training data for AI model improvement.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import text
from app.core.database import init_database
from app.models.training_data import TrainingData
from app.core.database import Base

async def create_training_data_table():
    """Create the training_data table if it doesn't exist."""
    
    try:
        # Initialize database connection
        await init_database()
        
        # Get the engine after initialization
        from app.core.database import engine
        
        if engine is None:
            print("❌ Database engine not initialized")
            return False
        
        # Create all tables (this will create training_data table)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Training data table created successfully")
        
        # Verify the table exists
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'training_data'
            """))
            
            if result.fetchone():
                print("✅ Training data table verified in database")
            else:
                print("❌ Training data table not found in database")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Error creating training data table: {e}")
        return False

async def main():
    """Main function to create the training data table."""
    print("📚 Creating Book of Lorgar training data table...")
    
    success = await create_training_data_table()
    
    if success:
        print("\n🎉 Training data table setup complete!")
        print("📝 The Book of Lorgar feature is now ready to receive training data.")
        print("🔗 API endpoint: POST /api/ai/upload-training-data")
    else:
        print("\n❌ Failed to create training data table")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 