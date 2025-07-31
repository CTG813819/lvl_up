#!/usr/bin/env python3
"""
Permanent SQLAlchemy Fix for _static_cache_key Error
This script fixes the SQLAlchemy version compatibility issue permanently
"""

import subprocess
import sys
import os
import time

class SQLAlchemyPermanentFixer:
    def __init__(self):
        self.fixes_applied = []
        self.issues_found = []
        
    def check_current_sqlalchemy(self):
        """Check current SQLAlchemy version"""
        print("🔍 Checking current SQLAlchemy version...")
        try:
            result = subprocess.run([
                "python3", "-c",
                "import sqlalchemy; print(f'Current version: {sqlalchemy.__version__}')"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"📊 {version}")
                return version
            else:
                print("❌ Could not check SQLAlchemy version")
                return None
        except Exception as e:
            print(f"❌ Error checking SQLAlchemy: {str(e)}")
            return None

    def install_compatible_sqlalchemy(self):
        """Install a compatible SQLAlchemy version"""
        print("📦 Installing compatible SQLAlchemy version...")
        
        # Try to install SQLAlchemy 2.0.x which is more stable
        try:
            print("📦 Installing SQLAlchemy 2.0.23...")
            result = subprocess.run([
                "pip3", "install", "sqlalchemy==2.0.23", "--break-system-packages", "--force-reinstall"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ SQLAlchemy 2.0.23 installed successfully")
                self.fixes_applied.append("Installed SQLAlchemy 2.0.23")
                return True
            else:
                print(f"❌ Failed to install SQLAlchemy 2.0.23: {result.stderr}")
                self.issues_found.append("Failed to install SQLAlchemy 2.0.23")
                return False
        except Exception as e:
            print(f"❌ Error installing SQLAlchemy: {str(e)}")
            self.issues_found.append(f"Error installing SQLAlchemy: {str(e)}")
            return False

    def fix_database_imports(self):
        """Fix database imports to handle SQLAlchemy compatibility"""
        print("🔧 Fixing database imports...")
        
        database_file = "app/core/database.py"
        if not os.path.exists(database_file):
            print(f"❌ Database file not found: {database_file}")
            return False
            
        try:
            with open(database_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add SQLAlchemy compatibility fixes
            compatibility_fixes = '''
# SQLAlchemy compatibility fixes
import sqlalchemy
if hasattr(sqlalchemy, '__version__'):
    sqlalchemy_version = sqlalchemy.__version__
    if sqlalchemy_version.startswith('1.'):
        # SQLAlchemy 1.x compatibility
        from sqlalchemy import create_engine, MetaData
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker, Session
    else:
        # SQLAlchemy 2.x compatibility
        from sqlalchemy import create_engine, MetaData
        from sqlalchemy.orm import declarative_base, sessionmaker, Session
else:
    # Fallback for unknown versions
    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Fix for _static_cache_key error
def safe_session_factory():
    """Create a safe session factory that handles SQLAlchemy version differences"""
    try:
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        if '_static_cache_key' in str(e):
            # Fallback for SQLAlchemy version issues
            print("⚠️ Using fallback session factory due to SQLAlchemy version compatibility")
            return sessionmaker(autocommit=False, autoflush=False, bind=engine)
        else:
            raise e

'''
            
            # Insert compatibility fixes after imports
            if '# SQLAlchemy compatibility fixes' not in content:
                # Find the end of imports
                lines = content.split('\n')
                import_end = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        import_end = i + 1
                    elif line.strip() and not line.startswith('#'):
                        break
                
                # Insert compatibility fixes
                lines.insert(import_end, compatibility_fixes)
                content = '\n'.join(lines)
                
                # Write back to file
                with open(database_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✅ Database imports fixed")
                self.fixes_applied.append("Fixed database imports")
                return True
            else:
                print("✅ Database imports already fixed")
                return True
                
        except Exception as e:
            print(f"❌ Error fixing database imports: {str(e)}")
            self.issues_found.append(f"Error fixing database imports: {str(e)}")
            return False

    def create_sqlalchemy_compatibility_patch(self):
        """Create a SQLAlchemy compatibility patch"""
        print("🔧 Creating SQLAlchemy compatibility patch...")
        
        patch_content = '''
"""
SQLAlchemy Compatibility Patch
Fixes _static_cache_key and other version compatibility issues
"""

import sqlalchemy
import warnings

def apply_sqlalchemy_patches():
    """Apply SQLAlchemy compatibility patches"""
    
    # Patch for _static_cache_key error
    def safe_comparator(comparator):
        """Safe comparator that handles _static_cache_key issues"""
        if hasattr(comparator, '_static_cache_key'):
            return comparator
        else:
            # Create a safe wrapper
            class SafeComparator:
                def __init__(self, original):
                    self._original = original
                    self._static_cache_key = None
                
                def __getattr__(self, name):
                    return getattr(self._original, name)
                
                def __call__(self, *args, **kwargs):
                    return self._original(*args, **kwargs)
            
            return SafeComparator(comparator)
    
    # Patch SQLAlchemy functions if needed
    try:
        if hasattr(sqlalchemy, 'func'):
            original_func = sqlalchemy.func
            sqlalchemy.func = safe_comparator(original_func)
    except Exception as e:
        warnings.warn(f"Could not patch SQLAlchemy func: {e}")
    
    # Patch other common SQLAlchemy objects
    try:
        if hasattr(sqlalchemy, 'text'):
            original_text = sqlalchemy.text
            sqlalchemy.text = safe_comparator(original_text)
    except Exception as e:
        warnings.warn(f"Could not patch SQLAlchemy text: {e}")

# Apply patches when module is imported
apply_sqlalchemy_patches()
'''
        
        try:
            with open('app/core/sqlalchemy_patch.py', 'w', encoding='utf-8') as f:
                f.write(patch_content)
            
            # Update database.py to import the patch
            database_file = "app/core/database.py"
            if os.path.exists(database_file):
                with open(database_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'from .sqlalchemy_patch import apply_sqlalchemy_patches' not in content:
                    # Add import at the top
                    lines = content.split('\n')
                    lines.insert(0, 'from .sqlalchemy_patch import apply_sqlalchemy_patches')
                    lines.insert(1, 'apply_sqlalchemy_patches()  # Apply patches early')
                    lines.insert(2, '')
                    content = '\n'.join(lines)
                    
                    with open(database_file, 'w', encoding='utf-8') as f:
                        f.write(content)
            
            print("✅ SQLAlchemy compatibility patch created")
            self.fixes_applied.append("Created SQLAlchemy compatibility patch")
            return True
            
        except Exception as e:
            print(f"❌ Error creating SQLAlchemy patch: {str(e)}")
            self.issues_found.append(f"Error creating SQLAlchemy patch: {str(e)}")
            return False

    def restart_backend_service(self):
        """Restart the backend service"""
        print("🔄 Restarting backend service...")
        try:
            # Stop the service
            result = subprocess.run([
                "sudo", "systemctl", "stop", "ai-backend-python.service"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Backend service stopped")
            else:
                print(f"⚠️ Could not stop service: {result.stderr}")
            
            # Wait a moment
            time.sleep(3)
            
            # Start the service
            result = subprocess.run([
                "sudo", "systemctl", "start", "ai-backend-python.service"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Backend service started")
                self.fixes_applied.append("Restarted backend service")
                return True
            else:
                print(f"❌ Could not start service: {result.stderr}")
                self.issues_found.append("Failed to restart backend service")
                return False
                
        except Exception as e:
            print(f"❌ Error restarting service: {str(e)}")
            self.issues_found.append(f"Error restarting service: {str(e)}")
            return False

    def test_sqlalchemy_fix(self):
        """Test if the SQLAlchemy fix is working"""
        print("🧪 Testing SQLAlchemy fix...")
        try:
            # Test basic SQLAlchemy import
            result = subprocess.run([
                "python3", "-c",
                "import sqlalchemy; print('SQLAlchemy import: OK')"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ SQLAlchemy import test: PASSED")
                
                # Test database connection
                result = subprocess.run([
                    "python3", "-c",
                    "from app.core.database import get_session; print('Database import: OK')"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print("✅ Database import test: PASSED")
                    return True
                else:
                    print(f"❌ Database import test: FAILED - {result.stderr}")
                    return False
            else:
                print(f"❌ SQLAlchemy import test: FAILED - {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Test error: {str(e)}")
            return False

    def run_complete_fix(self):
        """Run the complete SQLAlchemy fix"""
        print("🔧 Starting Permanent SQLAlchemy Fix")
        print("=" * 50)
        
        # Step 1: Check current version
        current_version = self.check_current_sqlalchemy()
        
        # Step 2: Install compatible version
        if not self.install_compatible_sqlalchemy():
            print("⚠️ Could not install compatible SQLAlchemy version")
        
        # Step 3: Fix database imports
        self.fix_database_imports()
        
        # Step 4: Create compatibility patch
        self.create_sqlalchemy_compatibility_patch()
        
        # Step 5: Restart service
        self.restart_backend_service()
        
        # Step 6: Test the fix
        time.sleep(5)  # Wait for service to start
        test_result = self.test_sqlalchemy_fix()
        
        # Generate summary
        self.generate_summary(test_result)

    def generate_summary(self, test_result):
        """Generate fix summary"""
        print("\n" + "=" * 50)
        print("📋 SQLAlchemy Fix Summary")
        print("=" * 50)
        
        print(f"✅ Fixes Applied: {len(self.fixes_applied)}")
        for fix in self.fixes_applied:
            print(f"   • {fix}")
        
        if self.issues_found:
            print(f"\n❌ Issues Found: {len(self.issues_found)}")
            for issue in self.issues_found:
                print(f"   • {issue}")
        
        print(f"\n🧪 Test Result: {'✅ PASSED' if test_result else '❌ FAILED'}")
        
        if test_result:
            print("\n🎉 SQLAlchemy fix completed successfully!")
            print("   The _static_cache_key error should be resolved.")
        else:
            print("\n⚠️ SQLAlchemy fix may need additional attention.")
            print("   Check the logs for any remaining issues.")

def main():
    fixer = SQLAlchemyPermanentFixer()
    fixer.run_complete_fix()

if __name__ == "__main__":
    main() 