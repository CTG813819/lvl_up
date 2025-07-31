#!/usr/bin/env python3
"""
Fix indentation error in custody_protocol_service.py
"""

def fix_custody_indentation():
    """Fix indentation error in custody_protocol_service.py"""
    file_path = "ai-backend-python/app/services/custody_protocol_service.py"
    
    print(f"🔧 Fixing indentation error in {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines for easier processing
    lines = content.split('\n')
    
    # Check the specific area around line 1106
    print("Checking lines around 1106...")
    for i in range(max(0, 1100), min(len(lines), 1115)):
        print(f"Line {i+1}: {repr(lines[i])}")
    
    # Look for the specific issue - there might be a missing line or incorrect indentation
    # Let me check if there's a missing line in the _update_custody_metrics method
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Check if this is around the problematic area
        if i >= 1055 and i <= 1070:  # Around the _update_custody_metrics method
            # Check if there's a missing line after the failed test logging
            if 'Test FAILED - Updated failed:' in line:
                fixed_lines.append(line)
                # Check if the next line is properly indented
                if i + 1 < len(lines) and lines[i + 1].strip() == '':
                    # Empty line is fine
                    fixed_lines.append(lines[i + 1])
                elif i + 1 < len(lines) and not lines[i + 1].startswith('            '):
                    # Next line should be properly indented
                    if lines[i + 1].strip() != '':
                        fixed_lines.append('            ' + lines[i + 1].lstrip())
                    else:
                        fixed_lines.append(lines[i + 1])
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("✅ Fixed indentation in custody_protocol_service.py")
    
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
    fix_custody_indentation() 