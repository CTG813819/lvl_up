#!/usr/bin/env python3
"""
Fix all async with statements that are outside async functions
"""

def find_and_fix_async_with():
    """Find and fix all async with statements outside async functions"""
    
    # Read the file
    with open("app/services/imperium_learning_controller.py", "r") as f:
        lines = f.readlines()
    
    print(f"File has {len(lines)} lines")
    
    # Find all async with statements
    async_with_lines = []
    for i, line in enumerate(lines):
        if "async with" in line:
            async_with_lines.append(i)
            print(f"Line {i+1}: {line.strip()}")
    
    print(f"Found {len(async_with_lines)} async with statements")
    
    # For each async with, check if it's inside an async function
    fixes_needed = []
    
    for async_with_line in async_with_lines:
        # Look backwards to find the function definition
        in_async_function = False
        function_start = None
        
        for i in range(async_with_line, -1, -1):
            line = lines[i].strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            
            # Check if this is a function definition
            if line.startswith("async def "):
                in_async_function = True
                function_start = i
                break
            elif line.startswith("def "):
                # Found a regular function - this async with is outside async function
                in_async_function = False
                function_start = i
                break
        
        if not in_async_function and function_start is not None:
            fixes_needed.append((async_with_line, function_start))
            print(f"Line {async_with_line+1}: async with outside async function (function at line {function_start+1})")
    
    # Apply fixes
    for async_with_line, function_start in fixes_needed:
        # Make the function async
        function_line = lines[function_start]
        if function_line.strip().startswith("def "):
            lines[function_start] = function_line.replace("def ", "async def ", 1)
            print(f"Made function at line {function_start+1} async")
    
    # Write the fixed content back
    with open("app/services/imperium_learning_controller.py", "w") as f:
        f.writelines(lines)
    
    print(f"Applied {len(fixes_needed)} fixes")
    return len(fixes_needed) > 0

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
    print("Fixing all async with statements outside async functions...")
    
    if find_and_fix_async_with():
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
        print("No fixes needed or could not apply fixes")

if __name__ == "__main__":
    main() 