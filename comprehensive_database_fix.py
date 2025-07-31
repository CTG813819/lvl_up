#!/usr/bin/env python3
"""
Comprehensive Database.py Fix
============================
This script reads the actual database.py file, identifies the specific
indentation error, and fixes it properly.
"""

import os
import re

def read_database_file():
    """Read the database.py file and return its content"""
    database_file = "/home/ubuntu/ai-backend-python/app/core/database.py"
    
    if not os.path.exists(database_file):
        print(f"❌ Database file not found: {database_file}")
        return None
    
    with open(database_file, 'r') as f:
        return f.read()

def analyze_database_file(content):
    """Analyze the database file and find the indentation error"""
    print("🔍 Analyzing database.py...")
    
    lines = content.split('\n')
    
    # Look for the problematic area around line 47-49
    for i, line in enumerate(lines):
        if 'with' in line and 'get_session' in line:
            print(f"📍 Found 'with' statement at line {i+1}: {line.strip()}")
            
            # Check the next few lines
            for j in range(i+1, min(i+5, len(lines))):
                print(f"   Line {j+1}: {lines[j]}")
            
            return i, lines
    
    return None, lines

def fix_database_content(content):
    """Fix the database content by correcting indentation issues"""
    print("🔧 Fixing database content...")
    
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for the problematic pattern: 'with' followed by docstring without proper indentation
        if ('with' in line and 'get_session' in line and 
            i + 1 < len(lines) and 
            '"""Get database connection"""' in lines[i + 1]):
            
            print(f"🔧 Fixing indentation at line {i+1}")
            
            # Add the 'with' line as is
            fixed_lines.append(line)
            
            # Fix the docstring indentation
            docstring_line = lines[i + 1]
            if not docstring_line.startswith('    """'):
                # Fix the indentation
                fixed_lines.append('    """Get database connection"""')
            else:
                fixed_lines.append(docstring_line)
            
            i += 1  # Skip the next line since we've handled it
            
        else:
            fixed_lines.append(line)
        
        i += 1
    
    return '\n'.join(fixed_lines)

def test_fixed_database():
    """Test if the fixed database can be imported"""
    print("\n🧪 Testing fixed database import...")
    
    test_script = """
import sys
sys.path.insert(0, '/home/ubuntu/ai-backend-python')

try:
    from app.core.database import get_session
    print("✅ Database import successful")
    print("✅ get_session function imported")
except Exception as e:
    print(f"❌ Database import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
    
    test_file = "/home/ubuntu/test_fixed_database.py"
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
    print("🔧 Comprehensive Database.py Fix")
    print("=" * 40)
    
    # Read the current database file
    content = read_database_file()
    if content is None:
        return False
    
    # Analyze the file to understand the issue
    problem_line, lines = analyze_database_file(content)
    
    if problem_line is None:
        print("⚠️  Could not find the specific problematic area")
        print("🔧 Attempting general fix...")
    
    # Fix the content
    fixed_content = fix_database_content(content)
    
    # Create backup
    database_file = "/home/ubuntu/ai-backend-python/app/core/database.py"
    backup_file = database_file + '.backup'
    with open(backup_file, 'w') as f:
        f.write(content)
    print(f"📝 Backup created: {backup_file}")
    
    # Write the fixed content
    with open(database_file, 'w') as f:
        f.write(fixed_content)
    
    print("✅ Database.py content fixed")
    
    # Test the fix
    if test_fixed_database():
        print("\n✅ Database.py fix completed successfully!")
        return True
    else:
        print("\n❌ Database.py fix failed!")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Database.py fix failed!")
        exit(1) 