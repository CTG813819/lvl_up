#!/usr/bin/env python3
"""
Fix all syntax errors in ai_learning_service.py
"""

def fix_all_syntax_errors():
    """Fix all syntax errors in the file"""
    file_path = "app/services/ai_learning_service.py"
    
    print(f"🔧 Fixing all syntax errors in {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines for easier processing
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for problematic logger.info calls
        if 'logger.info(' in line and 'learning_data={' in line:
            print(f"Found problematic logger.info call at line {i+1}")
            
            # Replace with proper f-string format
            fixed_lines.append('                    logger.info(')
            fixed_lines.append('                        f"Updated existing learning pattern: pattern={pattern}, success_rate={existing.success_rate}, applied_count={existing.applied_count}"')
            fixed_lines.append('                    )')
            
            # Skip the next few lines that are part of the problematic call
            i += 1
            while i < len(lines) and ('learning_data=' in lines[i] or 'success_rate=' in lines[i] or 'applied_count=' in lines[i]):
                i += 1
            continue
            
        elif 'logger.info("Created new learning pattern"' in line:
            print(f"Found problematic logger.info call at line {i+1}")
            
            # Replace with proper f-string format
            fixed_lines.append('                    logger.info(')
            fixed_lines.append('                        f"Created new learning pattern: pattern={pattern}, ai_type={proposal.ai_type}"')
            fixed_lines.append('                    )')
            
            # Skip the next few lines that are part of the problematic call
            i += 1
            while i < len(lines) and ('pattern=' in lines[i] or 'ai_type=' in lines[i]):
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
        
        # If still failing, let's try a more aggressive fix
        print("🔄 Trying more aggressive fix...")
        return fix_aggressive_syntax_error(file_path)

def fix_aggressive_syntax_error(file_path):
    """More aggressive fix for syntax errors"""
    print("🔧 Applying aggressive syntax fix...")
    
    # Read the file again
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace all problematic logger.info patterns
    import re
    
    # Pattern 1: logger.info with learning_data
    pattern1 = r'logger\.info\("Updated existing learning pattern",\s*learning_data=\{.*?\}\)'
    replacement1 = '''logger.info(
                        f"Updated existing learning pattern: pattern={pattern}, success_rate={existing.success_rate}, applied_count={existing.applied_count}"
                    )'''
    
    content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)
    
    # Pattern 2: logger.info with pattern and ai_type
    pattern2 = r'logger\.info\("Created new learning pattern",\s*pattern=.*?ai_type=.*?\)'
    replacement2 = '''logger.info(
                        f"Created new learning pattern: pattern={pattern}, ai_type={proposal.ai_type}"
                    )'''
    
    content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Applied aggressive fix")
    
    # Test syntax again
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', file_path], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Syntax check passed after aggressive fix")
        return True
    else:
        print(f"❌ Syntax check still failed: {result.stderr}")
        return False

if __name__ == "__main__":
    fix_all_syntax_errors() 