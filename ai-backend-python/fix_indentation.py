#!/usr/bin/env python3
"""
Fix indentation errors in ai_learning_service.py
"""

def fix_indentation_errors():
    """Fix indentation errors in the file"""
    file_path = "app/services/ai_learning_service.py"
    
    print(f"🔧 Fixing indentation errors in {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines for easier processing
    lines = content.split('\n')
    fixed_lines = []
    
    # Check the specific area around line 1682
    print("Checking lines around 1682...")
    for i in range(max(0, 1675), min(len(lines), 1690)):
        print(f"Line {i+1}: {repr(lines[i])}")
    
    # Fix indentation issues
    for i, line in enumerate(lines):
        # Check for lines that might have incorrect indentation
        if i >= 1675 and i <= 1690:  # Around the problematic area
            # If this is a line that should be properly indented
            if 'logger.info(' in line and not line.startswith('                    '):
                # Fix indentation
                fixed_line = '                    ' + line.lstrip()
                fixed_lines.append(fixed_line)
                print(f"Fixed indentation for line {i+1}")
            elif 'f"' in line and not line.startswith('                        '):
                # Fix indentation for f-string lines
                fixed_line = '                        ' + line.lstrip()
                fixed_lines.append(fixed_line)
                print(f"Fixed indentation for line {i+1}")
            elif ')' in line and not line.startswith('                    '):
                # Fix indentation for closing parenthesis
                fixed_line = '                    ' + line.lstrip()
                fixed_lines.append(fixed_line)
                print(f"Fixed indentation for line {i+1}")
            else:
                fixed_lines.append(line)
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
        
        # If still failing, let's try a complete rewrite of the problematic section
        print("🔄 Trying complete rewrite of problematic section...")
        return rewrite_problematic_section(file_path)

def rewrite_problematic_section(file_path):
    """Completely rewrite the problematic section"""
    print("🔧 Rewriting problematic section...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for the problematic logger.info section
        if 'logger.info(' in line and 'Updated existing learning pattern' in line:
            print(f"Found problematic section at line {i+1}")
            
            # Replace with correct format
            fixed_lines.append('                    logger.info(')
            fixed_lines.append('                        f"Updated existing learning pattern: pattern={pattern}, success_rate={existing.success_rate}, applied_count={existing.applied_count}"')
            fixed_lines.append('                    )')
            
            # Skip the problematic lines
            i += 1
            while i < len(lines) and ('learning_data=' in lines[i] or 'success_rate=' in lines[i] or 'applied_count=' in lines[i] or ')' in lines[i]):
                i += 1
            continue
            
        elif 'logger.info(' in line and 'Created new learning pattern' in line:
            print(f"Found problematic section at line {i+1}")
            
            # Replace with correct format
            fixed_lines.append('                    logger.info(')
            fixed_lines.append('                        f"Created new learning pattern: pattern={pattern}, ai_type={proposal.ai_type}"')
            fixed_lines.append('                    )')
            
            # Skip the problematic lines
            i += 1
            while i < len(lines) and ('pattern=' in lines[i] or 'ai_type=' in lines[i] or ')' in lines[i]):
                i += 1
            continue
        
        else:
            fixed_lines.append(line)
        
        i += 1
    
    # Join the lines back together
    content = '\n'.join(fixed_lines)
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Rewrote problematic section")
    
    # Test syntax again
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', file_path], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Syntax check passed after rewrite")
        return True
    else:
        print(f"❌ Syntax check still failed: {result.stderr}")
        return False

if __name__ == "__main__":
    fix_indentation_errors() 