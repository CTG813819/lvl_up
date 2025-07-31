#!/usr/bin/env python3
"""
Direct Database.py Fix
======================
This script directly examines and fixes the database.py file by reading
the actual content and fixing the specific indentation error.
"""

import os

def read_and_fix_database():
    """Read the database file and fix the indentation error"""
    database_file = "/home/ubuntu/ai-backend-python/app/core/database.py"
    
    if not os.path.exists(database_file):
        print(f"❌ Database file not found: {database_file}")
        return False
    
    print("📖 Reading database.py...")
    
    # Read the current content
    with open(database_file, 'r') as f:
        lines = f.readlines()
    
    print(f"📄 File has {len(lines)} lines")
    
    # Find the problematic area around line 47-49
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        line_num = i + 1
        
        # Look for the problematic 'with' statement
        if 'with' in line and 'get_session' in line:
            print(f"🔍 Found 'with' statement at line {line_num}: {line.strip()}")
            
            # Add the 'with' line
            fixed_lines.append(line)
            
            # Check the next line
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                next_line_num = i + 2
                
                print(f"🔍 Next line ({next_line_num}): {next_line.strip()}")
                
                # If the next line is the docstring without proper indentation
                if '"""Get database connection"""' in next_line:
                    if not next_line.startswith('    """'):
                        print(f"🔧 Fixing indentation for line {next_line_num}")
                        # Fix the indentation
                        fixed_lines.append('    """Get database connection"""\n')
                        i += 1  # Skip the original line
                    else:
                        fixed_lines.append(next_line)
                        i += 1
                else:
                    # Add the missing indented block
                    print(f"🔧 Adding missing indented block after line {line_num}")
                    fixed_lines.append('    """Get database connection"""\n')
            else:
                # Add the missing indented block at the end
                print(f"🔧 Adding missing indented block at end")
                fixed_lines.append('    """Get database connection"""\n')
        else:
            fixed_lines.append(line)
        
        i += 1
    
    # Create backup
    backup_file = database_file + '.backup'
    with open(backup_file, 'w') as f:
        f.writelines(lines)
    print(f"📝 Backup created: {backup_file}")
    
    # Write the fixed content
    with open(database_file, 'w') as f:
        f.writelines(fixed_lines)
    
    print("✅ Database.py fixed")
    return True

def test_database_import():
    """Test if the database can be imported"""
    print("\n🧪 Testing database import...")
    
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
    
    test_file = "/home/ubuntu/test_database_direct.py"
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

def show_database_content():
    """Show the content around the problematic area"""
    database_file = "/home/ubuntu/ai-backend-python/app/core/database.py"
    
    if not os.path.exists(database_file):
        print(f"❌ Database file not found: {database_file}")
        return
    
    print("\n📄 Current database.py content around line 47-49:")
    print("=" * 50)
    
    with open(database_file, 'r') as f:
        lines = f.readlines()
    
    # Show lines around 47-49
    start = max(0, 45)
    end = min(len(lines), 55)
    
    for i in range(start, end):
        marker = ">>> " if i == 46 else "    "  # Line 47 is index 46
        print(f"{marker}{i+1:2d}: {lines[i].rstrip()}")
    
    print("=" * 50)

def main():
    print("🔧 Direct Database.py Fix")
    print("=" * 30)
    
    # Show current content
    show_database_content()
    
    # Fix the database file
    if not read_and_fix_database():
        return False
    
    # Show fixed content
    print("\n📄 Fixed database.py content around line 47-49:")
    show_database_content()
    
    # Test the fix
    if test_database_import():
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