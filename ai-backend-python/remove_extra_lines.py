#!/usr/bin/env python3
"""
Remove extra lines causing indentation error in ai_learning_service.py
"""

def remove_extra_lines():
    """Remove the extra lines causing the indentation error"""
    file_path = "app/services/ai_learning_service.py"
    
    print(f"🔧 Removing extra lines in {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Skip the problematic lines 1682-1683 (0-indexed: 1681-1682)
        if i == 1681 or i == 1682:  # These are the extra lines
            print(f"Skipping problematic line {i+1}: {repr(line)}")
            continue
        else:
            fixed_lines.append(line)
    
    # Join the lines back together
    content = '\n'.join(fixed_lines)
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Removed extra lines successfully")
    
    # Test syntax
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', file_path], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Syntax check passed")
        return True
    else:
        print(f"❌ Syntax check failed: {result.stderr}")
        return False

if __name__ == "__main__":
    remove_extra_lines() 