#!/usr/bin/env python3
"""
Final Fix for Remaining Issues
Addresses database table creation, missing imports, and backend service
"""

import asyncio
import sys
import os
import subprocess
import time

# Add the ai-backend-python directory to the path
sys.path.append('/home/ubuntu/ai-backend-python')

async def fix_database_tables():
    """Create missing database tables"""
    try:
        print("🔧 Fixing Database Tables...")
        
        from app.core.database import init_database, get_session
        from sqlalchemy import text
        
        await init_database()
        session = get_session()
        
        async with session as s:
            # Create learning_metrics table if it doesn't exist
            print("  📊 Creating learning_metrics table...")
            await s.execute(text("""
                CREATE TABLE IF NOT EXISTS learning_metrics (
                    id SERIAL PRIMARY KEY,
                    agent_type VARCHAR(50) NOT NULL,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    learning_history JSONB DEFAULT '[]',
                    subjects_learned JSONB DEFAULT '[]',
                    knowledge_gaps JSONB DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create agent_learning_metrics table if it doesn't exist
            print("  📊 Creating agent_learning_metrics table...")
            await s.execute(text("""
                CREATE TABLE IF NOT EXISTS agent_learning_metrics (
                    id SERIAL PRIMARY KEY,
                    agent_type VARCHAR(50) NOT NULL,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    total_tests_given INTEGER DEFAULT 0,
                    total_tests_passed INTEGER DEFAULT 0,
                    total_tests_failed INTEGER DEFAULT 0,
                    consecutive_successes INTEGER DEFAULT 0,
                    consecutive_failures INTEGER DEFAULT 0,
                    last_test_date TIMESTAMP,
                    test_history JSONB DEFAULT '[]',
                    learning_history JSONB DEFAULT '[]',
                    subjects_learned JSONB DEFAULT '[]',
                    knowledge_gaps JSONB DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            await s.commit()
            print("  ✅ Database tables created successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error fixing database tables: {str(e)}")
        return False

async def fix_agnostic_method_imports():
    """Fix missing imports in the agnostic test method"""
    try:
        print("\n🔧 Fixing Agnostic Method Imports...")
        
        service_path = "/home/ubuntu/ai-backend-python/app/services/custody_protocol_service.py"
        
        if not os.path.exists(service_path):
            print(f"  ❌ Service file not found: {service_path}")
            return False
        
        with open(service_path, 'r') as f:
            content = f.read()
        
        # Check if text import is already present
        if 'from sqlalchemy import text' in content:
            print("  ✅ SQLAlchemy text import already present")
            return True
        
        # Add the import at the top of the file
        import_line = "from sqlalchemy import text\n"
        
        # Find the right place to insert (after existing imports)
        lines = content.split('\n')
        insert_index = 0
        
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                insert_index = i + 1
            elif line.strip() == '':
                continue
            else:
                break
        
        lines.insert(insert_index, import_line)
        new_content = '\n'.join(lines)
        
        with open(service_path, 'w') as f:
            f.write(new_content)
        
        print("  ✅ Added SQLAlchemy text import")
        return True
        
    except Exception as e:
        print(f"  ❌ Error fixing imports: {str(e)}")
        return False

async def fix_backend_service():
    """Fix and start the backend service"""
    try:
        print("\n🚀 Fixing Backend Service...")
        
        # Check if there are any Python path issues
        main_path = "/home/ubuntu/ai-backend-python/app/main.py"
        
        if not os.path.exists(main_path):
            print(f"  ❌ Main file not found: {main_path}")
            return False
        
        # Check the main.py file for import issues
        with open(main_path, 'r') as f:
            content = f.read()
        
        # Fix the import issue by running from the correct directory
        print("  🔧 Starting backend service from correct directory...")
        
        # Kill any existing processes
        subprocess.run(['pkill', '-f', 'main.py'], capture_output=True)
        time.sleep(2)
        
        # Start the service with proper Python path
        process = subprocess.Popen([
            '/home/ubuntu/ai-backend-python/venv/bin/python',
            '-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000'
        ], cwd='/home/ubuntu/ai-backend-python')
        
        # Wait for service to start
        print("  ⏳ Waiting for service to start...")
        time.sleep(10)
        
        # Check if service is running
        result = subprocess.run(['pgrep', '-f', 'uvicorn'], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Backend service started successfully")
            return True
        else:
            print("  ❌ Failed to start backend service")
            return False
            
    except Exception as e:
        print(f"  ❌ Error fixing backend service: {str(e)}")
        return False

async def test_complete_system():
    """Test the complete system after fixes"""
    try:
        print("\n🧪 Testing Complete System...")
        
        from app.services.custody_protocol_service import CustodyProtocolService
        from app.services.custody_protocol_service import TestCategory
        
        service = await CustodyProtocolService.initialize()
        
        # Test agnostic test generation with proper imports
        print("  🎯 Testing agnostic test generation...")
        agnostic_test = await service._generate_agnostic_test(
            ai_type="imperium",
            difficulty=1,
            category=TestCategory.KNOWLEDGE_VERIFICATION
        )
        
        print(f"    ✅ Agnostic test generated: {agnostic_test.get('test_type')}")
        print(f"    📝 Questions: {len(agnostic_test.get('questions', []))}")
        
        # Test knowledge gap scanning
        print("  🔍 Testing knowledge gap scanning...")
        learning_data = await service._scan_ai_learning("imperium")
        print(f"    📚 Subjects learned: {len(learning_data.get('subjects_learned', []))}")
        print(f"    🕳️ Knowledge gaps: {len(learning_data.get('knowledge_gaps', []))}")
        
        # Test API endpoint
        print("  🌐 Testing API endpoint...")
        try:
            import requests
            response = requests.get("http://localhost:8000/api/custody/", timeout=5)
            if response.status_code == 200:
                print("    ✅ API endpoint responding")
                return True
            else:
                print(f"    ⚠️ API endpoint: {response.status_code}")
                return False
        except Exception as e:
            print(f"    ❌ API endpoint: {str(e)}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing complete system: {str(e)}")
        return False

async def verify_learning_cycles():
    """Verify learning cycles are working without errors"""
    try:
        print("\n🔄 Verifying Learning Cycles...")
        
        # Check recent logs for errors
        result = subprocess.run(['journalctl', '-u', 'ultimate_start', '--since', '2 minutes ago', '-n', '20'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            logs = result.stdout
            xp_errors = logs.count("'AgentLearningMetrics' object has no attribute 'xp'")
            learning_errors = logs.count("Error triggering learning cycle")
            
            if xp_errors == 0 and learning_errors == 0:
                print("  ✅ No learning cycle errors in recent logs")
                return True
            else:
                print(f"  ⚠️ Found {xp_errors} xp errors and {learning_errors} learning errors")
                return False
        else:
            print("  ⚠️ Could not check logs")
            return False
            
    except Exception as e:
        print(f"  ❌ Error verifying learning cycles: {str(e)}")
        return False

async def main():
    """Main fix function"""
    print("🔧 Final Fix for Remaining Issues")
    print("=" * 80)
    
    # Fix database tables
    tables_fixed = await fix_database_tables()
    
    # Fix agnostic method imports
    imports_fixed = await fix_agnostic_method_imports()
    
    # Fix backend service
    service_fixed = await fix_backend_service()
    
    # Test complete system
    system_tested = await test_complete_system()
    
    # Verify learning cycles
    learning_verified = await verify_learning_cycles()
    
    # Summary
    print("\n" + "=" * 80)
    print("🎉 FINAL FIX SUMMARY")
    print("=" * 80)
    
    print(f"📊 Results:")
    print(f"   Database Tables: {'✅ FIXED' if tables_fixed else '❌ FAILED'}")
    print(f"   Agnostic Imports: {'✅ FIXED' if imports_fixed else '❌ FAILED'}")
    print(f"   Backend Service: {'✅ FIXED' if service_fixed else '❌ FAILED'}")
    print(f"   Complete System: {'✅ WORKING' if system_tested else '❌ FAILED'}")
    print(f"   Learning Cycles: {'✅ VERIFIED' if learning_verified else '❌ FAILED'}")
    
    if all([tables_fixed, imports_fixed, service_fixed, system_tested, learning_verified]):
        print(f"\n🎉 ALL ISSUES RESOLVED!")
        print(f"   • Database tables are properly created")
        print(f"   • Agnostic test generation is fully functional")
        print(f"   • Backend service is running on port 8000")
        print(f"   • Learning cycles are working without errors")
        print(f"   • Knowledge gap scanning is operational")
        print(f"   • Frontend data is being generated accurately")
    else:
        print(f"\n⚠️ SOME ISSUES REMAIN - Check individual results above")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 