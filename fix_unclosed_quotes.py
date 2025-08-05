#!/usr/bin/env python3
"""
Fix unclosed quotes in imperium_learning_controller.py
"""

import re
import os

def find_unclosed_quotes():
    """Find lines with unclosed quotes"""
    
    with open("app/services/imperium_learning_controller.py", "r") as f:
        lines = f.readlines()
    
    issues = []
    
    for i, line in enumerate(lines, 1):
        # Count single quotes
        single_quotes = line.count("'")
        if single_quotes % 2 != 0:
            issues.append(f"Line {i}: Unclosed single quotes - {line.strip()}")
        
        # Count double quotes
        double_quotes = line.count('"')
        if double_quotes % 2 != 0:
            issues.append(f"Line {i}: Unclosed double quotes - {line.strip()}")
    
    return issues

def fix_unclosed_quotes():
    """Fix unclosed quotes in the file"""
    
    with open("app/services/imperium_learning_controller.py", "r") as f:
        content = f.read()
    
    # Common patterns that might need fixing
    fixes = [
        # Fix common patterns
        (r"(\w+)\s*=\s*'([^']*)$", r"\1 = '\2'"),  # Unclosed single quote at end of line
        (r"(\w+)\s*=\s*"([^"]*)$", r'\1 = "\2"'),  # Unclosed double quote at end of line
        (r"logger\.(error|info|warning|debug)\s*\(\s*'([^']*)$", r"logger.\1('\2')"),  # Logger calls
        (r"logger\.(error|info|warning|debug)\s*\(\s*"([^"]*)$", r'logger.\1("\2")'),  # Logger calls with double quotes
    ]
    
    original_content = content
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Write back if changes were made
    if content != original_content:
        with open("app/services/imperium_learning_controller.py", "w") as f:
            f.write(content)
        print("Applied fixes to the file")
        return True
    else:
        print("No automatic fixes applied")
        return False

def main():
    """Main function"""
    print("Finding unclosed quotes in imperium_learning_controller.py...")
    
    # Find issues
    issues = find_unclosed_quotes()
    
    if issues:
        print(f"Found {len(issues)} potential quote issues:")
        for issue in issues[:10]:  # Show first 10 issues
            print(f"  {issue}")
        
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
        
        # Try to fix automatically
        print("\nAttempting automatic fixes...")
        if fix_unclosed_quotes():
            print("Automatic fixes applied. Checking again...")
            issues_after = find_unclosed_quotes()
            if issues_after:
                print(f"Still have {len(issues_after)} issues after automatic fix:")
                for issue in issues_after[:5]:
                    print(f"  {issue}")
            else:
                print("✓ All quote issues fixed!")
        else:
            print("Automatic fixes could not be applied. Manual intervention required.")
    else:
        print("✓ No unclosed quote issues found")

if __name__ == "__main__":
    main() 