import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

async def migrate_learning_data():
    """Migrate existing Learning data to include missing fields"""
    try:
        from core.database import get_session, init_database
        from models.sql_models import Learning
        from sqlalchemy import select, update

        print("🔄 Migrating Learning data...")

        await init_database()  # Ensure DB is initialized

        async with get_session() as session:
            # Get all Learning entries
            result = await session.execute(select(Learning))
            learning_entries = result.scalars().all()
            
            migrated_count = 0
            
            for entry in learning_entries:
                # Check if learning_data exists and has required fields
                if not entry.learning_data:
                    # Create default learning_data structure
                    entry.learning_data = {
                        "pattern_id": f"legacy_{entry.id}",
                        "success_rate": 0.5,
                        "confidence": 0.5,
                        "applied_count": 1,
                        "context": f"Migrated from legacy entry {entry.id}"
                    }
                    migrated_count += 1
                elif isinstance(entry.learning_data, dict):
                    # Ensure all required fields exist
                    if "success_rate" not in entry.learning_data:
                        entry.learning_data["success_rate"] = 0.5
                    if "confidence" not in entry.learning_data:
                        entry.learning_data["confidence"] = 0.5
                    if "applied_count" not in entry.learning_data:
                        entry.learning_data["applied_count"] = 1
                    if "pattern_id" not in entry.learning_data:
                        entry.learning_data["pattern_id"] = f"legacy_{entry.id}"
                    migrated_count += 1
            
            # Commit changes
            await session.commit()
            
            print(f"✅ Migrated {migrated_count} Learning entries")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(migrate_learning_data())
    sys.exit(0 if success else 1) 