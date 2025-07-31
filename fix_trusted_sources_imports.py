#!/usr/bin/env python3
"""
Patch script to fix trusted sources import issues
"""

import os

# Path to the imperium_learning.py file
IMPERIUM_LEARNING_PATH = os.path.join('app', 'routers', 'imperium_learning.py')

# Read the current file
with open(IMPERIUM_LEARNING_PATH, 'r') as f:
    content = f.read()

# Apply the fixes
# 1. Fix the import statement
content = content.replace(
    'from ..services import trusted_sources',
    'from ..services.trusted_sources import get_trusted_sources as ts_get_sources, add_trusted_source as ts_add_source, remove_trusted_source as ts_remove_source'
)

# 2. Fix the function calls
content = content.replace('trusted_sources.get_trusted_sources()', 'ts_get_sources()')
content = content.replace('trusted_sources.add_trusted_source(url)', 'ts_add_source(url)')
content = content.replace('trusted_sources.remove_trusted_source(url)', 'ts_remove_source(url)')

# Write the fixed content back
with open(IMPERIUM_LEARNING_PATH, 'w') as f:
    f.write(content)

print("✅ Fixed trusted sources import issues in imperium_learning.py")
print("Please restart the backend service:")
print("sudo systemctl restart imperium-monitoring") 