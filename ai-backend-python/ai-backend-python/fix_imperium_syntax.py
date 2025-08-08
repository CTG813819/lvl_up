#!/usr/bin/env python3
"""
Comprehensive fix for imperium_learning_controller.py syntax error
"""

def fix_imperium_syntax():
    """Fix the syntax error in imperium_learning_controller.py"""
    
    # Read the file
    with open("app/services/imperium_learning_controller.py", "r") as f:
        lines = f.readlines()
    
    print(f"File has {len(lines)} lines")
    
    # Find the _load_persisted_agent_metrics method
    method_start = None
    method_end = None
    
    for i, line in enumerate(lines):
        if "async def _load_persisted_agent_metrics" in line:
            method_start = i
            print(f"Found method definition at line {i+1}")
            break
        elif "def _load_persisted_agent_metrics" in line:
            # Fix: make it async
            lines[i] = line.replace("def _load_persisted_agent_metrics", "async def _load_persisted_agent_metrics")
            method_start = i
            print(f"Found method definition at line {i+1} and made it async")
            break
    
    if method_start is None:
        print("Could not find _load_persisted_agent_metrics method")
        return False
    
    # Find the end of the method (next method or end of class)
    for i in range(method_start + 1, len(lines)):
        if lines[i].strip().startswith("async def ") or lines[i].strip().startswith("def "):
            if lines[i].strip().startswith("async def _load_persisted_agent_metrics"):
                continue  # Skip if it's the same method
            method_end = i
            break
    
    if method_end is None:
        method_end = len(lines)
    
    print(f"Method spans lines {method_start+1} to {method_end}")
    
    # Check for the async with line
    async_with_line = None
    for i in range(method_start, method_end):
        if "async with get_session()" in lines[i]:
            async_with_line = i
            print(f"Found async with at line {i+1}: {lines[i].strip()}")
            break
    
    if async_with_line is None:
        print("Could not find async with line in method")
        return False
    
    # Check indentation of the async with line
    async_with_indent = len(lines[async_with_line]) - len(lines[async_with_line].lstrip())
    method_indent = len(lines[method_start]) - len(lines[method_start].lstrip())
    
    print(f"Method indent: {method_indent}, async with indent: {async_with_indent}")
    
    # Fix indentation if needed
    if async_with_indent <= method_indent:
        # The async with line is not properly indented inside the method
        correct_indent = " " * (method_indent + 4)  # 4 spaces more than method
        lines[async_with_line] = correct_indent + lines[async_with_line].lstrip()
        print(f"Fixed indentation of line {async_with_line+1}")
    
    # Write the fixed content back
    with open("app/services/imperium_learning_controller.py", "w") as f:
        f.writelines(lines)
    
    print("Applied fixes to the file")
    return True

def test_syntax():
    """Test if the file has valid syntax"""
    try:
        with open("app/services/imperium_learning_controller.py", "r") as f:
            content = f.read()
        
        compile(content, "imperium_learning_controller.py", "exec")
        print("✓ File compiles successfully")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        print(f"Line {e.lineno}: {e.text}")
        return False

def test_import():
    """Test if the module can be imported"""
    try:
        import sys
        sys.path.insert(0, ".")
        
        from app.services.imperium_learning_controller import ImperiumLearningController
        print("✓ Module imports successfully")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def main():
    """Main function"""
    print("Fixing imperium_learning_controller.py syntax error...")
    
    if fix_imperium_syntax():
        print("\nApplied fixes. Testing...")
        
        if test_syntax():
            print("✓ Syntax is valid")
            
            if test_import():
                print("✓ Module can be imported")
                print("\n🎉 All fixes successful! The backend should now start properly.")
            else:
                print("✗ Module import failed")
        else:
            print("✗ Syntax still invalid")
    else:
        print("Could not apply fixes")

if __name__ == "__main__":
    main() 