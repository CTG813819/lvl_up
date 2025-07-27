#!/usr/bin/env python3
"""
Test script to verify schedule module works
"""

try:
    import schedule
    print("✅ schedule module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import schedule module: {e}")
    exit(1)

print("✅ All tests passed") 