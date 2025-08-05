#!/usr/bin/env python3
"""
Fix the TRUSTED_SOURCES import issue in imperium_learning_controller.py
"""

import os

# Path to the imperium_learning_controller.py file
CONTROLLER_PATH = os.path.join('app', 'services', 'imperium_learning_controller.py')

# Read the current file
with open(CONTROLLER_PATH, 'r') as f:
    content = f.read()

print("🔍 Current file content analysis:")
print(f"File size: {len(content)} characters")
print(f"Contains 'TRUSTED_SOURCES': {'TRUSTED_SOURCES' in content}")
print(f"Contains 'from .trusted_sources import TRUSTED_SOURCES': {'from .trusted_sources import TRUSTED_SOURCES' in content}")

# Apply fixes
print("\n🔧 Applying fixes...")

# Fix the import statement - remove TRUSTED_SOURCES from the import
if 'from .trusted_sources import TRUSTED_SOURCES, is_trusted_source' in content:
    content = content.replace(
        'from .trusted_sources import TRUSTED_SOURCES, is_trusted_source',
        'from .trusted_sources import is_trusted_source'
    )
    print("✅ Fixed import statement - removed TRUSTED_SOURCES")

# Also fix any other variations
if 'from .trusted_sources import TRUSTED_SOURCES' in content:
    content = content.replace(
        'from .trusted_sources import TRUSTED_SOURCES',
        'from .trusted_sources import is_trusted_source'
    )
    print("✅ Fixed import statement - removed TRUSTED_SOURCES (variation)")

# Remove any direct usage of TRUSTED_SOURCES variable
if 'TRUSTED_SOURCES' in content:
    # Replace with DEFAULT_TRUSTED_SOURCES if needed, or remove
    content = content.replace('TRUSTED_SOURCES', 'DEFAULT_TRUSTED_SOURCES')
    print("✅ Replaced TRUSTED_SOURCES with DEFAULT_TRUSTED_SOURCES")

# Write the fixed content back
with open(CONTROLLER_PATH, 'w') as f:
    f.write(content)

print(f"\n✅ Fixed imperium_learning_controller.py")
print(f"New file size: {len(content)} characters")

# Verify the fixes
print("\n🔍 Verification:")
print(f"Contains 'TRUSTED_SOURCES': {'TRUSTED_SOURCES' in content}")
print(f"Contains 'from .trusted_sources import TRUSTED_SOURCES': {'from .trusted_sources import TRUSTED_SOURCES' in content}")
print(f"Contains 'from .trusted_sources import is_trusted_source': {'from .trusted_sources import is_trusted_source' in content}")

print("\n📋 Next steps:")
print("1. Clear Python cache: rm -rf ~/ai-backend-python/__pycache__ ~/ai-backend-python/app/__pycache__ ~/ai-backend-python/app/services/__pycache__ ~/ai-backend-python/app/routers/__pycache__")
print("2. Restart service: sudo systemctl restart imperium-monitoring")
print("3. Test endpoints") 