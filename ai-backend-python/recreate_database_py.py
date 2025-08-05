#!/usr/bin/env python3
"""
Recreate Database.py
===================
This script completely recreates the database.py file with the correct
content to fix the indentation error.
"""

import os

def recreate_database_py():
    """Recreate the database.py file with correct content"""
    database_file = "/home/ubuntu/ai-backend-python/app/core/database.py"
    
    print("🔧 Recreating database.py...")
    
    # Create backup of existing file
    if os.path.exists(database_file):
        backup_file = database_file + '.backup'
        with open(database_file, 'r') as f:
            content = f.read()
        with open(backup_file, 'w') as f:
            f.write(content)
        print(f"📝 Backup created: {backup_file}")
    
    # Correct database.py content
    correct_content = '''"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_backend.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
else:
    engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_session():
    """Get database connection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
    
    # Write the correct content
    with open(database_file, 'w') as f:
        f.write(correct_content)
    
    print("✅ Database.py recreated with correct content")
    return True

def test_database_import():
    """Test if the database can be imported"""
    print("\n🧪 Testing database import...")
    
    test_script = """
import sys
sys.path.insert(0, '/home/ubuntu/ai-backend-python')

try:
    from app.core.database import get_session, get_db, init_db
    print("✅ Database import successful")
    print("✅ All database functions imported")
except Exception as e:
    print(f"❌ Database import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
    
    test_file = "/home/ubuntu/test_recreated_database.py"
    with open(test_file, 'w') as f:
        f.write(test_script)
    
    import subprocess
    result = subprocess.run(['python3', test_file], capture_output=True, text=True)
    
    os.remove(test_file)
    
    if result.returncode == 0:
        print("✅ Database import test passed")
        return True
    else:
        print(f"❌ Database import test failed: {result.stderr}")
        return False

def test_main_app_import():
    """Test if the main app can be imported"""
    print("\n🧪 Testing main app import...")
    
    test_script = """
import sys
sys.path.insert(0, '/home/ubuntu/ai-backend-python')

try:
    from app.main import app
    print("✅ Main app import successful")
except Exception as e:
    print(f"❌ Main app import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
    
    test_file = "/home/ubuntu/test_main_app.py"
    with open(test_file, 'w') as f:
        f.write(test_script)
    
    import subprocess
    result = subprocess.run(['python3', test_file], capture_output=True, text=True)
    
    os.remove(test_file)
    
    if result.returncode == 0:
        print("✅ Main app import test passed")
        return True
    else:
        print(f"❌ Main app import test failed: {result.stderr}")
        return False

def main():
    print("🔧 Recreate Database.py")
    print("=" * 30)
    
    # Recreate the database file
    if not recreate_database_py():
        return False
    
    # Test the database import
    if not test_database_import():
        return False
    
    # Test the main app import
    if not test_main_app_import():
        return False
    
    print("\n✅ Database.py recreation completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Database.py recreation failed!")
        exit(1) 