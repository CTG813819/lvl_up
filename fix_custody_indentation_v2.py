#!/usr/bin/env python3
"""
Fix specific indentation error in custody_protocol_service.py around line 1105-1106
"""

def fix_custody_indentation_v2():
    """Fix specific indentation error in custody_protocol_service.py"""
    file_path = "ai-backend-python/app/services/custody_protocol_service.py"
    
    print(f"🔧 Fixing specific indentation error in {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines for easier processing
    lines = content.split('\n')
    
    # Check the specific area around line 1105-1106
    print("Checking lines around 1105-1106...")
    for i in range(max(0, 1100), min(len(lines), 1110)):
        print(f"Line {i+1}: {repr(lines[i])}")
    
    # Look for the specific issue - there might be a missing colon or incorrect indentation
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Check if this is the function definition line
        if 'async def _persist_custody_metrics_to_database(self, ai_type: str, metrics: Dict):' in line:
            print(f"Found function definition at line {i+1}")
            # Make sure the function definition has proper indentation
            if not line.startswith('    '):
                fixed_line = '    ' + line.lstrip()
                fixed_lines.append(fixed_line)
                print(f"Fixed function definition indentation")
            else:
                fixed_lines.append(line)
        # Check if this is the docstring line
        elif '"""Persist custody metrics to the database"""' in line:
            print(f"Found docstring at line {i+1}")
            # Make sure the docstring has proper indentation
            if not line.startswith('        '):
                fixed_line = '        ' + line.lstrip()
                fixed_lines.append(fixed_line)
                print(f"Fixed docstring indentation")
            else:
                fixed_lines.append(line)
        # Check if this is the try line
        elif 'try:' in line and i > 1100 and i < 1110:
            print(f"Found try statement at line {i+1}")
            # Make sure the try has proper indentation
            if not line.startswith('        '):
                fixed_line = '        ' + line.lstrip()
                fixed_lines.append(fixed_line)
                print(f"Fixed try statement indentation")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("✅ Fixed specific indentation in custody_protocol_service.py")
    
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
    fix_custody_indentation_v2() 