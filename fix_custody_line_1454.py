#!/usr/bin/env python3
"""
Fix for the syntax error on line 1454 in custody_protocol_service.py
"""

def fix_custody_line_1454():
    """Fix the syntax error on line 1454"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The exact problematic pattern from the current file
    old_pattern = '''            except Exception as e:
                return max(0, min(100, score))
# Removed orphaned else block

return 75

        except AttributeError as e:'''
    
    # The corrected pattern - fix the indentation and structure
    new_pattern = '''            except Exception as e:
                return max(0, min(100, score))
        except AttributeError as e:'''
    
    # Apply the fix
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("Fixed syntax error on line 1454")
    else:
        print("Pattern not found. Trying alternative approach...")
        
        # Alternative approach: find the specific lines and fix them manually
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Look for the problematic pattern: orphaned return statement
            if (line.strip() == 'return 75' and 
                i > 0 and '# Removed orphaned else block' in lines[i-1]):
                
                # Found the problematic pattern, remove the orphaned return
                # Skip this line and the comment above it
                i += 1
                continue
            else:
                fixed_lines.append(line)
            
            i += 1
        
        # Write the fixed content back to the file
        with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        print("Fixed syntax error using line-by-line approach")
        return
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_custody_line_1454()