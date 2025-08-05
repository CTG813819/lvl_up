#!/usr/bin/env python3
"""
Comprehensive Frontend Test Suite for Flutter App
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime

def check_flutter_installation():
    """Check if Flutter is properly installed"""
    print("🔍 Checking Flutter installation...")
    
    try:
        # Check Flutter version using shell=True for Windows
        result = subprocess.run('flutter --version', shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Flutter is installed")
            # Extract version info
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'Flutter' in line and 'channel' in line:
                    print(f"Version info: {line.strip()}")
                    break
            return True
        else:
            print("❌ Flutter installation check failed")
            return False
    except FileNotFoundError:
        print("❌ Flutter not found in PATH")
        return False
    except Exception as e:
        print(f"❌ Error checking Flutter: {e}")
        return False

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    try:
        result = subprocess.run('flutter pub get', shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print("❌ Failed to install dependencies")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def run_flutter_analyze():
    """Run Flutter analyze to check for issues"""
    print("\n🔍 Running Flutter analyze...")
    
    try:
        result = subprocess.run('flutter analyze', shell=True, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅ Flutter analyze passed - no issues found")
            return True
        else:
            print("❌ Flutter analyze found issues:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running Flutter analyze: {e}")
        return False

def run_flutter_tests():
    """Run Flutter unit tests"""
    print("\n🧪 Running Flutter unit tests...")
    
    try:
        result = subprocess.run('flutter test', shell=True, capture_output=True, text=True, timeout=180)
        if result.returncode == 0:
            print("✅ Flutter unit tests passed")
            # Extract test summary
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'All tests passed' in line:
                    print(f"Test summary: {line}")
                    break
            return True
        else:
            print("❌ Flutter unit tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Flutter tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running Flutter tests: {e}")
        return False

def run_integration_tests():
    """Run Flutter integration tests"""
    print("\n🔗 Running Flutter integration tests...")
    
    try:
        result = subprocess.run('flutter test integration_test', shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ Flutter integration tests passed")
            return True
        else:
            print("❌ Flutter integration tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Flutter integration tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running Flutter integration tests: {e}")
        return False

def check_code_formatting():
    """Check if code is properly formatted"""
    print("\n🎨 Checking code formatting...")
    
    try:
        result = subprocess.run('dart format --set-exit-if-changed .', shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Code formatting is correct")
            return True
        else:
            print("❌ Code formatting issues found:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error checking code formatting: {e}")
        return False

def build_web_version():
    """Build web version to check for build issues"""
    print("\n🌐 Building web version...")
    
    try:
        result = subprocess.run('flutter build web', shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ Web build successful")
            return True
        else:
            print("❌ Web build failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Web build timed out")
        return False
    except Exception as e:
        print(f"❌ Error building web version: {e}")
        return False

def build_android_apk():
    """Build Android APK to check for build issues"""
    print("\n📱 Building Android APK...")
    
    try:
        result = subprocess.run('flutter build apk --debug', shell=True, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            print("✅ Android APK build successful")
            return True
        else:
            print("❌ Android APK build failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Android APK build timed out")
        return False
    except Exception as e:
        print(f"❌ Error building Android APK: {e}")
        return False

def check_widget_tree():
    """Check if main widgets can be instantiated"""
    print("\n🌳 Checking widget tree...")
    
    try:
        # Try to run a simple widget test
        test_code = '''
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lvl_up/main.dart' as app;

void main() {
  testWidgets('App should start without crashing', (WidgetTester tester) async {
    app.main();
    await tester.pumpAndSettle();
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
'''
        
        with open('test_widget_tree.dart', 'w') as f:
            f.write(test_code)
        
        result = subprocess.run('flutter test test_widget_tree.dart', shell=True, capture_output=True, text=True, timeout=60)
        
        # Clean up
        if os.path.exists('test_widget_tree.dart'):
            os.remove('test_widget_tree.dart')
        
        if result.returncode == 0:
            print("✅ Widget tree check passed")
            return True
        else:
            print("❌ Widget tree check failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error checking widget tree: {e}")
        return False

def check_assets():
    """Check if all assets are properly configured"""
    print("\n🖼️ Checking assets...")
    
    try:
        # Check if pubspec.yaml has assets section
        with open('pubspec.yaml', 'r') as f:
            content = f.read()
            
        if 'assets:' in content:
            print("✅ Assets section found in pubspec.yaml")
            
            # Check if assets directory exists
            if os.path.exists('assets'):
                print("✅ Assets directory exists")
                return True
            else:
                print("⚠️ Assets directory not found")
                return False
        else:
            print("⚠️ No assets section in pubspec.yaml")
            return True  # Not critical
    except Exception as e:
        print(f"❌ Error checking assets: {e}")
        return False

def check_permissions():
    """Check if required permissions are configured"""
    print("\n🔐 Checking permissions...")
    
    try:
        # Check Android permissions
        if os.path.exists('android/app/src/main/AndroidManifest.xml'):
            with open('android/app/src/main/AndroidManifest.xml', 'r') as f:
                content = f.read()
                
            required_permissions = [
                'android.permission.INTERNET',
                'android.permission.ACCESS_NETWORK_STATE'
            ]
            
            missing_permissions = []
            for permission in required_permissions:
                if permission not in content:
                    missing_permissions.append(permission)
            
            if not missing_permissions:
                print("✅ All required Android permissions configured")
                return True
            else:
                print(f"⚠️ Missing Android permissions: {missing_permissions}")
                return False
        else:
            print("⚠️ AndroidManifest.xml not found")
            return True  # Not critical for web testing
    except Exception as e:
        print(f"❌ Error checking permissions: {e}")
        return False

def generate_frontend_report(results):
    """Generate a comprehensive frontend test report"""
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE FRONTEND TEST REPORT")
    print("="*80)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"\n📈 TEST SUMMARY:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    print(f"   📊 Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
    
    print(f"\n🔍 DETAILED RESULTS:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    if passed_tests / total_tests >= 0.9:
        print("   🚀 Frontend is highly stable - ready for production")
    elif passed_tests / total_tests >= 0.7:
        print("   ⚠️ Frontend is mostly stable - some issues need attention")
    else:
        print("   🔧 Frontend needs significant work - focus on core functionality")
    
    return passed_tests / total_tests if total_tests > 0 else 0

def main():
    """Main frontend test function"""
    print("🚀 COMPREHENSIVE FRONTEND TEST")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = {}
    
    # Run all frontend tests
    results["Flutter Installation"] = check_flutter_installation()
    results["Dependencies"] = check_dependencies()
    results["Code Analysis"] = run_flutter_analyze()
    results["Unit Tests"] = run_flutter_tests()
    results["Integration Tests"] = run_integration_tests()
    results["Code Formatting"] = check_code_formatting()
    results["Web Build"] = build_web_version()
    results["Android Build"] = build_android_apk()
    results["Widget Tree"] = check_widget_tree()
    results["Assets"] = check_assets()
    results["Permissions"] = check_permissions()
    
    # Generate comprehensive report
    success_rate = generate_frontend_report(results)
    
    print(f"\n🎉 FRONTEND TEST COMPLETE!")
    print(f"Overall Success Rate: {success_rate*100:.1f}%")
    
    if success_rate >= 0.9:
        print("✅ Frontend is ready for production!")
        return 0
    elif success_rate >= 0.7:
        print("⚠️ Frontend needs some attention but is mostly functional")
        return 1
    else:
        print("❌ Frontend needs significant work")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Frontend testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 