#!/usr/bin/env python3
"""
Fix the specific indentation error on line 242
"""

def fix_line_242():
    """Fix the indentation error on line 242"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Fix the specific problematic section around line 242
    # The issue is that the actual code is after the except blocks instead of inside the try block
    
    # Find the problematic section and fix it
    for i in range(len(lines)):
        if 'async def _load_test_models(self):' in lines[i]:
            # Found the method, now fix the try-except block
            j = i + 1
            while j < len(lines) and 'try:' not in lines[j]:
                j += 1
            
            if j < len(lines):
                # Found the try block, now fix it
                # The pattern is: try: pass except AttributeError ... except Exception ... actual_code
                # We need to move the actual code into the try block
                
                # Find where the actual code starts (after the except blocks)
                k = j + 1
                while k < len(lines) and 'pass' in lines[k]:
                    k += 1
                
                # Skip the except blocks
                while k < len(lines) and ('except AttributeError' in lines[k] or 'except Exception' in lines[k] or 'logger.warning' in lines[k] or '# Continue with fallback behavior' in lines[k]):
                    k += 1
                
                # Now k points to the actual code that should be in the try block
                # Collect all the actual code
                actual_code = []
                while k < len(lines) and not lines[k].strip().startswith('except Exception as e:') and not lines[k].strip().startswith('except Exception as e:'):
                    if lines[k].strip() and not lines[k].strip().startswith('except'):
                        actual_code.append(lines[k])
                    k += 1
                
                # Now fix the structure
                # Replace the try block with the actual code inside it
                lines[j] = '        try:\n'
                lines[j+1] = '            model_path = f"{settings.ml_model_path}/custody"\n'
                lines[j+2] = '            \n'
                lines[j+3] = '            for ai_type in ["imperium", "guardian", "sandbox", "conquest"]:\n'
                lines[j+4] = '                for difficulty in TestDifficulty:\n'
                lines[j+5] = '                    model_file = f"{model_path}/{ai_type}_{difficulty.value}_test_model.pkl"\n'
                lines[j+6] = '                    if os.path.exists(model_file):\n'
                lines[j+7] = '                        self.test_models[f"{ai_type}_{difficulty.value}"] = joblib.load(model_file)\n'
                lines[j+8] = '                        logger.info(f"Loaded test model for {ai_type} {difficulty.value}")\n'
                lines[j+9] = '        except AttributeError as e:\n'
                lines[j+10] = '            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")\n'
                lines[j+11] = '            # Continue with fallback behavior\n'
                lines[j+12] = '        except Exception as e:\n'
                lines[j+13] = '            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")\n'
                lines[j+14] = '            # Continue with fallback behavior\n'
                lines[j+15] = '        except Exception as e:\n'
                lines[j+16] = '            logger.error(f"Error loading test models: {str(e)}")\n'
                break
    
    # Write the fixed content back
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("Fixed the indentation error on line 242")

if __name__ == "__main__":
    fix_line_242()