#!/usr/bin/env python3
"""
Fix specific indentation issue on line 1106
"""

def fix_indentation_specific():
    """Fix the specific indentation issue"""
    file_path = "ai-backend-python/app/services/custody_protocol_service.py"
    
    print(f"🔧 Fixing specific indentation in {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Fix line 1106 (index 1105)
    if len(lines) > 1105:
        # Check if this is the problematic line
        if '"""Persist custody metrics to the database"""' in lines[1105]:
            # Fix the indentation - should be 8 spaces (2 levels)
            lines[1105] = '        """Persist custody metrics to the database"""\n'
            print("✅ Fixed docstring indentation on line 1106")
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Fixed indentation")
    
    # Test the syntax
    try:
        import ast
        with open(file_path, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ Syntax check passed!")
    except SyntaxError as e:
        print(f"❌ Syntax check failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    fix_indentation_specific() 