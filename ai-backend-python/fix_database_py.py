#!/usr/bin/env python3
"""
Fix Database.py Indentation Error
================================
This script fixes the indentation error in database.py that's preventing
the main application from importing.
"""

import os
import re

def fix_database_py():
    """Fix the indentation error in database.py"""
    print("🔧 Fixing database.py indentation error...")
    
    database_file = "/home/ubuntu/ai-backend-python/app/core/database.py"
    
    if not os.path.exists(database_file):
        print(f"❌ Database file not found: {database_file}")
        return False
    
    # Read the current file
    with open(database_file, 'r') as f:
        content = f.read()
    
    print("📖 Reading database.py...")
    
    # Fix the specific indentation error around line 47-49
    # The issue is likely a missing indented block after a 'with' statement
    
    # Let's look for the problematic area and fix it
    lines = content.split('\n')
    
    # Find the problematic 'with' statement around line 47
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this is the problematic 'with' statement
        if 'with' in line and 'get_session' in line and i + 1 < len(lines):
            # This is likely the problematic area
            fixed_lines.append(line)
            
            # Check if the next line has proper indentation
            next_line = lines[i + 1]
            if next_line.strip().startswith('"""Get database connection"""'):
                # Fix the indentation
                fixed_lines.append('    """Get database connection"""')
                i += 1
            else:
                # Add the missing indented block
                fixed_lines.append('    """Get database connection"""')
        else:
            fixed_lines.append(line)
        
        i += 1
    
    # Write the fixed content back
    fixed_content = '\n'.join(fixed_lines)
    
    # Create a backup
    backup_file = database_file + '.backup'
    with open(backup_file, 'w') as f:
        f.write(content)
    print(f"📝 Backup created: {backup_file}")
    
    # Write the fixed content
    with open(database_file, 'w') as f:
        f.write(fixed_content)
    
    print("✅ Database.py fixed")
    return True

def test_database_import():
    """Test if database.py can be imported"""
    print("\n🧪 Testing database import...")
    
    test_script = """
import sys
sys.path.insert(0, '/home/ubuntu/ai-backend-python')

try:
    from app.core.database import get_session
    print("✅ Database import successful")
except Exception as e:
    print(f"❌ Database import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
    
    test_file = "/home/ubuntu/test_database_import.py"
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

def main():
    print("🔧 Database.py Fix")
    print("=" * 30)
    
    # Fix the database file
    if not fix_database_py():
        return False
    
    # Test the fix
    if not test_database_import():
        return False
    
    print("\n✅ Database.py fix completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Database.py fix failed!")
        exit(1) 