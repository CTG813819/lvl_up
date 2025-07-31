#!/usr/bin/env python3
"""
Script to fix syntax errors in custody_protocol_service.py
The file has malformed try-except blocks with empty try statements.
"""

import re

def fix_custody_syntax():
    """Fix malformed try-except blocks in custody_protocol_service.py"""
    
    file_path = "app/services/custody_protocol_service.py"
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match empty try blocks followed by except
    # This matches: try:\n followed by except (with optional whitespace)
    pattern = r'try:\s*\nexcept'
    
    # Replace with try: pass\n except
    fixed_content = re.sub(pattern, 'try:\n            pass\nexcept', content)
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"Fixed syntax errors in {file_path}")

if __name__ == "__main__":
    fix_custody_syntax()