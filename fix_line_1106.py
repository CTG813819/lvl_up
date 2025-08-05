#!/usr/bin/env python3
"""
Fix line 1106 indentation
"""

def fix_line_1106():
    """Fix the specific indentation on line 1106"""
    file_path = "ai-backend-python/app/services/custody_protocol_service.py"
    
    print(f"🔧 Fixing line 1106 in {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Fix line 1106 (index 1105)
    if len(lines) > 1105:
        # Replace the problematic line
        lines[1105] = '        """Persist custody metrics to the database"""\n'
        print("✅ Fixed line 1106 indentation")
    
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
    fix_line_1106() 