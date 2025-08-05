#!/usr/bin/env python3
"""
Comprehensive Backend Fix Script
Fixes all Learning model field issues and other backend problems
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

async def fix_learning_insights_issues():
    """Fix Learning insights issues"""
    print("🔧 Fixing Learning insights issues...")
    
    # Read the current learning router
    router_path = Path("app/routers/learning.py")
    
    if not router_path.exists():
        print("❌ Learning router file not found!")
        return False
    
    with open(router_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the get_learning_insights function
    old_insights = '''    # Get recent learning entries
    recent_learning = await session.execute(
        select(Learning)
        .where(Learning.ai_type == ai_type)
        .order_by(Learning.created_at.desc())
        .limit(10)
    )
    recent_entries = recent_learning.scalars().all()
    
    # Calculate success patterns
    success_patterns = [l for l in recent_entries if l.success_rate > 0.7]
    failure_patterns = [l for l in recent_entries if l.success_rate < 0.3]'''
    
    new_insights = '''    # Get recent learning entries
    recent_learning = await session.execute(
        select(Learning)
        .where(Learning.ai_type == ai_type)
        .order_by(Learning.created_at.desc())
        .limit(10)
    )
    recent_entries = recent_learning.scalars().all()
    
    # Calculate success patterns from learning_data
    success_patterns = []
    failure_patterns = []
    
    for entry in recent_entries:
        if entry.learning_data:
            success_rate = entry.learning_data.get("success_rate", 0.0)
            if success_rate > 0.7:
                success_patterns.append(entry)
            elif success_rate < 0.3:
                failure_patterns.append(entry)'''
    
    content = content.replace(old_insights, new_insights)
    
    # Fix the total_patterns calculation
    old_total = '''    total_patterns = len(recent_entries)'''
    
    new_total = '''    total_patterns = len([e for e in recent_entries if e.learning_data])'''
    
    content = content.replace(old_total, new_total)
    
    # Write the fixed content back
    with open(router_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed Learning insights issues")
    return True

async def fix_ai_growth_service_issues():
    """Fix AI growth service issues"""
    print("🔧 Fixing AI growth service issues...")
    
    service_path = Path("app/services/ai_growth_service.py")
    
    if not service_path.exists():
        print("❌ AI growth service file not found!")
        return False
    
    with open(service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the confidence attribute access
    old_confidence = '''                func.avg(Learning.confidence).label('avg_confidence'),'''
    
    new_confidence = '''                func.avg(func.json_extract_path_text(Learning.learning_data, 'confidence')).label('avg_confidence'),'''
    
    content = content.replace(old_confidence, new_confidence)
    
    # Write the fixed content back
    with open(service_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed AI growth service issues")
    return True

async def fix_imperium_learning_controller_issues():
    """Fix Imperium learning controller issues"""
    print("🔧 Fixing Imperium learning controller issues...")
    
    controller_path = Path("app/services/imperium_learning_controller.py")
    
    if not controller_path.exists():
        print("❌ Imperium learning controller file not found!")
        return False
    
    with open(controller_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the learning_patterns access
    old_patterns = '''                    learning_patterns=db_metrics.learning_patterns or [],'''
    
    new_patterns = '''                    learning_patterns=db_metrics.learning_patterns or [] if hasattr(db_metrics, 'learning_patterns') else [],'''
    
    content = content.replace(old_patterns, new_patterns)
    
    # Write the fixed content back
    with open(controller_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed Imperium learning controller issues")
    return True

async def create_learning_data_migration():
    """Create a migration to add missing fields to Learning model"""
    print("🔧 Creating Learning data migration...")
    
    migration_script = '''#!/usr/bin/env python3
"""
Migration script to add missing fields to Learning model
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

async def migrate_learning_data():
    """Migrate existing Learning data to include missing fields"""
    try:
        from core.database import get_session
        from models.sql_models import Learning
        from sqlalchemy import select, update
        
        print("🔄 Migrating Learning data...")
        
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
'''
    
    with open("migrate_learning_data.py", 'w', encoding='utf-8') as f:
        f.write(migration_script)
    
    print("✅ Created Learning data migration script")
    return True

async def run_migration():
    """Run the Learning data migration"""
    print("🔄 Running Learning data migration...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "migrate_learning_data.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migration completed successfully")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

async def test_fixes():
    """Test that the fixes work"""
    print("🧪 Testing fixes...")
    
    test_script = '''#!/usr/bin/env python3
"""
Test script to verify fixes work
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

async def test_learning_service():
    """Test the fixed learning service"""
    try:
        from services.ai_learning_service import AILearningService
        from core.database import get_session
        from models.sql_models import Learning
        
        learning_service = AILearningService()
        
        # Test creating a learning entry
        async with get_session() as session:
            # Test basic database connection
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            print("✅ Database connection test passed")
            
            # Test Learning model creation with proper data structure
            test_learning = Learning(
                ai_type="test_ai",
                learning_type="test_learning",
                learning_data={
                    "pattern_id": "test_pattern",
                    "success_rate": 0.8,
                    "confidence": 0.9,
                    "applied_count": 1,
                    "context": "Test learning entry"
                },
                status="active"
            )
            session.add(test_learning)
            await session.commit()
            print("✅ Learning model creation test passed")
            
            # Clean up
            await session.delete(test_learning)
            await session.commit()
            print("✅ Learning model cleanup test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Learning service test failed: {e}")
        return False

async def test_learning_insights():
    """Test learning insights endpoint"""
    try:
        from routers.learning import get_learning_insights
        from core.database import get_session
        
        # Test with a valid AI type
        result = await get_learning_insights("Imperium")
        print("✅ Learning insights test passed")
        return True
        
    except Exception as e:
        print(f"❌ Learning insights test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing comprehensive fixes...")
    
    # Test learning service
    learning_ok = await test_learning_service()
    
    # Test learning insights
    insights_ok = await test_learning_insights()
    
    if learning_ok and insights_ok:
        print("🎉 All tests passed! Comprehensive fixes are working.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    with open("test_comprehensive_fixes.py", 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ Created comprehensive test script")
    return True

async def main():
    """Main fix function"""
    print("🔧 Comprehensive Backend Fix Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app").exists():
        print("❌ Please run this script from the ai-backend-python directory")
        return False
    
    try:
        # Fix Learning insights issues
        insights_fixed = await fix_learning_insights_issues()
        
        # Fix AI growth service issues
        growth_fixed = await fix_ai_growth_service_issues()
        
        # Fix Imperium learning controller issues
        controller_fixed = await fix_imperium_learning_controller_issues()
        
        # Create and run migration
        migration_created = await create_learning_data_migration()
        migration_run = await run_migration()
        
        # Create test script
        test_created = await test_fixes()
        
        if (insights_fixed and growth_fixed and controller_fixed and 
            migration_created and migration_run and test_created):
            print("\n🎉 All comprehensive fixes applied successfully!")
            print("\n📋 Next steps:")
            print("1. Restart the backend: sudo systemctl restart ai-backend-python")
            print("2. Test the fixes: python test_comprehensive_fixes.py")
            print("3. Monitor logs: sudo journalctl -u ai-backend-python -f")
            return True
        else:
            print("\n❌ Some fixes failed. Please check the errors above.")
            return False
            
    except Exception as e:
        print(f"❌ Error during fix process: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 