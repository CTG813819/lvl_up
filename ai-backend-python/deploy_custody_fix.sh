#!/bin/bash

# Fix custody protocol service indentation errors
echo "Fixing custody protocol service indentation errors..."

# Navigate to the project directory
cd /home/ubuntu/ai-backend-python

# Create a backup of the original file
cp app/services/custody_protocol_service.py app/services/custody_protocol_service.py.backup

# Fix the malformed try-except blocks
# The pattern is: try: pass except AttributeError as e: ... except Exception as e: ... actual_code
# We need to move the actual code into the try block and fix the indentation

python3 -c "
import re

# Read the file
with open('app/services/custody_protocol_service.py', 'r') as f:
    content = f.read()

# Pattern to find malformed try-except blocks
# This pattern matches:
# try:
#         pass
# except AttributeError as e:
#         logger.warning(...)
#         # Continue with fallback behavior
#     except Exception as e:
#         logger.warning(...)
#         # Continue with fallback behavior
#     actual_code_here

pattern = r'try:\s*\n\s+pass\s*\nexcept AttributeError as e:\s*\n\s+logger\.warning\(f\"⚠️ EnhancedTestGenerator method not available: \{e\}\"\)\s*\n\s+# Continue with fallback behavior\s*\nexcept Exception as e:\s*\n\s+logger\.warning\(f\"⚠️ EnhancedTestGenerator method not available: \{e\}\"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+(.*?)(?=\n\s+except Exception as e:|$)'

def fix_try_except_blocks(match):
    actual_code = match.group(1)
    # Remove the extra indentation from the actual code
    actual_code = re.sub(r'^\s+', '', actual_code, flags=re.MULTILINE)
    
    # Create the fixed try-except block
    fixed_block = f'''try:
    {actual_code}
except AttributeError as e:
    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {{e}}")
    # Continue with fallback behavior
except Exception as e:
    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {{e}}")
    # Continue with fallback behavior'''
    
    return fixed_block

# Apply the fix
content = re.sub(pattern, fix_try_except_blocks, content, flags=re.DOTALL)

# Write the fixed content back
with open('app/services/custody_protocol_service.py', 'w') as f:
    f.write(content)

print('Fixed custody protocol service indentation errors')
"

# Restart the service
echo "Restarting AI backend service..."
sudo systemctl restart ai-backend-python

# Check service status
echo "Checking service status..."
sleep 5
sudo systemctl status ai-backend-python --no-pager

echo "Custody protocol fix deployment completed!"