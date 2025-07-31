#!/usr/bin/env python3
"""
Complete fix for imperium_learning.py file
"""

import os

# Path to the imperium_learning.py file
IMPERIUM_LEARNING_PATH = os.path.join('app', 'routers', 'imperium_learning.py')

# Read the current file
with open(IMPERIUM_LEARNING_PATH, 'r') as f:
    content = f.read()

print("🔍 Current file content analysis:")
print(f"File size: {len(content)} characters")
print(f"Contains 'trusted_sources.get_trusted_sources': {'trusted_sources.get_trusted_sources' in content}")
print(f"Contains 'from ..services import trusted_sources': {'from ..services import trusted_sources' in content}")
print(f"Contains 'ts_get_sources': {'ts_get_sources' in content}")

# Apply comprehensive fixes
print("\n🔧 Applying fixes...")

# 1. Fix the import statement
if 'from ..services import trusted_sources' in content:
    content = content.replace(
        'from ..services import trusted_sources',
        'from ..services.trusted_sources import get_trusted_sources as ts_get_sources, add_trusted_source as ts_add_source, remove_trusted_source as ts_remove_source'
    )
    print("✅ Fixed import statement")

# 2. Fix all function calls
if 'trusted_sources.get_trusted_sources()' in content:
    content = content.replace('trusted_sources.get_trusted_sources()', 'ts_get_sources()')
    print("✅ Fixed get_trusted_sources call")

if 'trusted_sources.add_trusted_source(' in content:
    content = content.replace('trusted_sources.add_trusted_source(', 'ts_add_source(')
    print("✅ Fixed add_trusted_source call")

if 'trusted_sources.remove_trusted_source(' in content:
    content = content.replace('trusted_sources.remove_trusted_source(', 'ts_remove_source(')
    print("✅ Fixed remove_trusted_source call")

# Write the fixed content back
with open(IMPERIUM_LEARNING_PATH, 'w') as f:
    f.write(content)

print(f"\n✅ Fixed imperium_learning.py")
print(f"New file size: {len(content)} characters")

# Verify the fixes
print("\n🔍 Verification:")
print(f"Contains 'trusted_sources.get_trusted_sources': {'trusted_sources.get_trusted_sources' in content}")
print(f"Contains 'from ..services import trusted_sources': {'from ..services import trusted_sources' in content}")
print(f"Contains 'ts_get_sources': {'ts_get_sources' in content}")

print("\n📋 Next steps:")
print("1. Clear Python cache: rm -rf ~/ai-backend-python/__pycache__ ~/ai-backend-python/app/__pycache__ ~/ai-backend-python/app/services/__pycache__ ~/ai-backend-python/app/routers/__pycache__")
print("2. Restart service: sudo systemctl restart imperium-monitoring")
print("3. Test endpoints") 