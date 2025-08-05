#!/usr/bin/env python3
"""
Android Launcher Icon Verification Script
Verifies that all required Android launcher icons are present and properly configured.
"""

import os
import sys
from pathlib import Path

def check_android_icons():
    """Check if all required Android launcher icons are present."""
    
    # Base path for Android resources
    android_res_path = Path("android/app/src/main/res")
    
    # Required mipmap directories
    mipmap_dirs = [
        "mipmap-mdpi",
        "mipmap-hdpi", 
        "mipmap-xhdpi",
        "mipmap-xxhdpi",
        "mipmap-xxxhdpi",
        "mipmap-anydpi-v26"
    ]
    
    # Required icon files
    required_icons = [
        "ic_launcher.png",
        "ic_launcher.xml"  # Only in mipmap-anydpi-v26
    ]
    
    print("🔍 Checking Android launcher icons...")
    
    all_good = True
    
    # Check each mipmap directory
    for mipmap_dir in mipmap_dirs:
        dir_path = android_res_path / mipmap_dir
        if not dir_path.exists():
            print(f"❌ Missing directory: {mipmap_dir}")
            all_good = False
            continue
            
        print(f"📁 Checking {mipmap_dir}...")
        
        # Check for ic_launcher.png in all directories
        if mipmap_dir != "mipmap-anydpi-v26":
            icon_file = dir_path / "ic_launcher.png"
            if not icon_file.exists():
                print(f"  ❌ Missing: ic_launcher.png")
                all_good = False
            else:
                print(f"  ✅ Found: ic_launcher.png")
        else:
            # Check for ic_launcher.xml in mipmap-anydpi-v26
            icon_file = dir_path / "ic_launcher.xml"
            if not icon_file.exists():
                print(f"  ❌ Missing: ic_launcher.xml")
                all_good = False
            else:
                print(f"  ✅ Found: ic_launcher.xml")
    
    # Check for required drawable resources
    drawable_path = android_res_path / "drawable"
    required_drawables = [
        "ic_launcher_foreground.xml"
    ]
    
    print(f"📁 Checking drawable resources...")
    for drawable in required_drawables:
        drawable_file = drawable_path / drawable
        if not drawable_file.exists():
            print(f"  ❌ Missing: {drawable}")
            all_good = False
        else:
            print(f"  ✅ Found: {drawable}")
    
    # Check for color resources
    values_path = android_res_path / "values"
    color_file = values_path / "ic_launcher_background.xml"
    
    print(f"📁 Checking color resources...")
    if not color_file.exists():
        print(f"  ❌ Missing: ic_launcher_background.xml")
        all_good = False
    else:
        print(f"  ✅ Found: ic_launcher_background.xml")
    
    # Check AndroidManifest.xml
    manifest_path = Path("android/app/src/main/AndroidManifest.xml")
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            content = f.read()
            if 'android:icon="@mipmap/ic_launcher"' in content:
                print("✅ AndroidManifest.xml correctly references ic_launcher")
            else:
                print("❌ AndroidManifest.xml does not reference ic_launcher")
                all_good = False
    else:
        print("❌ AndroidManifest.xml not found")
        all_good = False
    
    if all_good:
        print("\n🎉 All Android launcher icons are properly configured!")
        print("📱 The app should display the correct launcher icon on Android devices.")
    else:
        print("\n⚠️  Some Android launcher icons are missing or misconfigured.")
        print("🔧 Please ensure all required icon files are present.")
    
    return all_good

if __name__ == "__main__":
    success = check_android_icons()
    sys.exit(0 if success else 1) 