#!/usr/bin/env python3
"""
Fix PostgreSQL syntax error in guardian_ai_service.py
"""

def fix_postgresql_syntax():
    """Fix PostgreSQL syntax error in the file"""
    file_path = "app/services/guardian_ai_service.py"
    
    print(f"🔧 Fixing PostgreSQL syntax error in {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Search for PostgreSQL-specific syntax that's not valid Python
    problematic_patterns = [
        (r'func\.json_extract_path_text\([^)]+\)::float', 'func.json_extract_path_text(...)'),  # Remove ::float
        (r'func\.json_extract_path_text\([^)]+\)::int', 'func.json_extract_path_text(...)'),    # Remove ::int
        (r'func\.json_extract_path_text\([^)]+\)::text', 'func.json_extract_path_text(...)'),   # Remove ::text
        (r'::float', ''),  # Remove any remaining ::float
        (r'::int', ''),    # Remove any remaining ::int
        (r'::text', ''),   # Remove any remaining ::text
    ]
    
    import re
    
    for pattern, replacement in problematic_patterns:
        if re.search(pattern, content):
            print(f"Found problematic pattern: {pattern}")
            content = re.sub(pattern, replacement, content)
            print(f"Fixed pattern: {pattern}")
    
    # Also check for any other PostgreSQL-specific syntax
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Check for PostgreSQL type casting syntax
        if '::' in line and ('func.' in line or 'Learning.' in line or 'Mission.' in line):
            print(f"Found PostgreSQL syntax on line {i+1}: {line}")
            # Remove the type casting
            fixed_line = re.sub(r'::[a-zA-Z]+', '', line)
            fixed_lines.append(fixed_line)
            print(f"Fixed line {i+1}")
        else:
            fixed_lines.append(line)
    
    # Join the lines back together
    content = '\n'.join(fixed_lines)
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ File updated successfully")
    
    # Test syntax
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', file_path], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Syntax check passed")
        return True
    else:
        print(f"❌ Syntax check failed: {result.stderr}")
        
        # If still failing, let's search for the exact line
        print("🔍 Searching for the exact problematic line...")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '::' in line:
                print(f"Line {i+1}: {line}")
        return False

if __name__ == "__main__":
    fix_postgresql_syntax() 