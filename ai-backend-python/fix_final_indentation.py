#!/usr/bin/env python3
"""
Fix final indentation error in ai_learning_service.py
"""

def fix_final_indentation():
    """Fix the final indentation error"""
    file_path = "app/services/ai_learning_service.py"
    
    print(f"🔧 Fixing final indentation error in {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines
    lines = content.split('\n')
    
    # Check the area around line 1685
    print("Checking lines around 1685...")
    for i in range(max(0, 1680), min(len(lines), 1690)):
        print(f"Line {i+1}: {repr(lines[i])}")
    
    # Fix indentation issues
    fixed_lines = []
    for i, line in enumerate(lines):
        # Check for lines that should have proper indentation
        if i >= 1680 and i <= 1690:  # Around the problematic area
            stripped = line.lstrip()
            
            # Fix specific indentation patterns
            if stripped.startswith('# Update proposal'):
                fixed_line = '                ' + stripped
                fixed_lines.append(fixed_line)
                print(f"Fixed indentation for line {i+1}")
            elif stripped.startswith('proposal.ai_learning_applied'):
                fixed_line = '                ' + stripped
                fixed_lines.append(fixed_line)
                print(f"Fixed indentation for line {i+1}")
            elif stripped.startswith('proposal.updated_at'):
                fixed_line = '                ' + stripped
                fixed_lines.append(fixed_line)
                print(f"Fixed indentation for line {i+1}")
            elif stripped.startswith('await session.commit'):
                fixed_line = '                ' + stripped
                fixed_lines.append(fixed_line)
                print(f"Fixed indentation for line {i+1}")
            elif stripped.startswith('return {'):
                fixed_line = '                ' + stripped
                fixed_lines.append(fixed_line)
                print(f"Fixed indentation for line {i+1}")
            elif stripped.startswith('"status":'):
                fixed_line = '                    ' + stripped
                fixed_lines.append(fixed_line)
                print(f"Fixed indentation for line {i+1}")
            elif stripped.startswith('"pattern":'):
                fixed_line = '                    ' + stripped
                fixed_lines.append(fixed_line)
                print(f"Fixed indentation for line {i+1}")
            elif stripped.startswith('"ai_type":'):
                fixed_line = '                    ' + stripped
                fixed_lines.append(fixed_line)
                print(f"Fixed indentation for line {i+1}")
            elif stripped.startswith('"learning_applied":'):
                fixed_line = '                    ' + stripped
                fixed_lines.append(fixed_line)
                print(f"Fixed indentation for line {i+1}")
            elif stripped.startswith('}'):
                fixed_line = '                ' + stripped
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
        
        # If still failing, let's try a more comprehensive fix
        print("🔄 Trying comprehensive fix...")
        return comprehensive_fix(file_path)

def comprehensive_fix(file_path):
    """Comprehensive fix for all indentation issues"""
    print("🔧 Applying comprehensive fix...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines
    lines = content.split('\n')
    fixed_lines = []
    
    # Define the correct structure for the problematic section
    correct_section = [
        '                # Update proposal with learning applied',
        '                proposal.ai_learning_applied = True  # type: ignore',
        '                proposal.updated_at = datetime.utcnow()  # type: ignore',
        '',
        '                await session.commit()',
        '',
        '                return {',
        '                    "status": "success",',
        '                    "pattern": pattern,',
        '                    "ai_type": proposal.ai_type,',
        '                    "learning_applied": True',
        '                }',
        '',
        '        except Exception as e:',
        '            logger.error(f"Error learning from proposal: {str(e)} | proposal_id={proposal_id}")',
        '            return {"status": "error", "message": str(e)}'
    ]
    
    # Find the start of the problematic section and replace it
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for the start of the problematic section
        if 'Update proposal with learning applied' in line:
            print(f"Found problematic section at line {i+1}")
            
            # Add the correct section
            fixed_lines.extend(correct_section)
            
            # Skip the problematic lines
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('async def get_learning_stats'):
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
    
    print("✅ Applied comprehensive fix")
    
    # Test syntax again
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', file_path], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Syntax check passed after comprehensive fix")
        return True
    else:
        print(f"❌ Syntax check still failed: {result.stderr}")
        return False

if __name__ == "__main__":
    fix_final_indentation() 