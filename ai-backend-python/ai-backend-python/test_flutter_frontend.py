#!/usr/bin/env python3
"""
Flutter Frontend Test
Tests the Flutter frontend application and its integration with the backend.
"""

import requests
import json
import sys
import subprocess
import time
from datetime import datetime

def check_flutter_installation():
    """Check if Flutter is installed and working"""
    print("🔍 Checking Flutter installation...")
    
    try:
        result = subprocess.run(["flutter", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Flutter is installed")
            print(f"Version info: {result.stdout.split('Flutter')[1].split('•')[0].strip()}")
            return True
        else:
            print("❌ Flutter is not working properly")
            return False
    except Exception as e:
        print(f"❌ Flutter is not installed or not in PATH: {e}")
        return False

def check_flutter_dependencies():
    """Check if Flutter dependencies are installed"""
    print("\n📦 Checking Flutter dependencies...")
    
    try:
        result = subprocess.run(["flutter", "pub", "get"], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Flutter dependencies are up to date")
            return True
        else:
            print("❌ Flutter dependencies need updating")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Could not check Flutter dependencies: {e}")
        return False

def run_flutter_analyze():
    """Run Flutter analyze to check for issues"""
    print("\n🔍 Running Flutter analyze...")
    
    try:
        result = subprocess.run(["flutter", "analyze"], capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Flutter analyze passed - no issues found")
            return True
        else:
            print("⚠️ Flutter analyze found issues:")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Could not run Flutter analyze: {e}")
        return False

def run_flutter_tests():
    """Run Flutter tests"""
    print("\n🧪 Running Flutter tests...")
    
    try:
        result = subprocess.run(["flutter", "test"], capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅ Flutter tests passed")
            # Extract test summary
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if "All tests passed" in line or "test passed" in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print("❌ Flutter tests failed")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Could not run Flutter tests: {e}")
        return False

def start_flutter_web():
    """Start Flutter web server"""
    print("\n🌐 Starting Flutter web server...")
    
    try:
        # Start Flutter web in background
        process = subprocess.Popen(
            ["flutter", "run", "-d", "web-server", "--web-port", "3000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for server to start
        time.sleep(10)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Flutter web server started on port 3000")
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ Flutter web server failed to start")
            print(f"Error: {stderr}")
            return None
    except Exception as e:
        print(f"❌ Could not start Flutter web server: {e}")
        return None

def test_flutter_web_endpoints():
    """Test Flutter web endpoints"""
    print("\n🌐 Testing Flutter web endpoints...")
    
    base_url = "http://localhost:3000"
    endpoints = [
        ("/", "Main App"),
        ("/conquest", "Conquest Screen"),
        ("/analytics", "Analytics Screen"),
        ("/settings", "Settings Screen")
    ]
    
    results = {}
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {description} endpoint working")
                results[endpoint] = True
            else:
                print(f"❌ {description} endpoint failed (Status: {response.status_code})")
                results[endpoint] = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {description} endpoint failed: {e}")
            results[endpoint] = False
    
    return results

def test_flutter_backend_integration():
    """Test Flutter integration with backend"""
    print("\n🔗 Testing Flutter-Backend integration...")
    
    backend_url = "http://ec2-34-202-215-209.compute-1.amazonaws.com:4000"
    endpoints = [
        ("/health", "Backend Health"),
        ("/api/conquest/statistics", "Conquest Statistics"),
        ("/api/conquest/enhanced-statistics", "Enhanced Statistics"),
        ("/api/conquest/status", "Conquest Status")
    ]
    
    results = {}
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{backend_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {description} integration working")
                results[endpoint] = True
            else:
                print(f"❌ {description} integration failed (Status: {response.status_code})")
                results[endpoint] = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {description} integration failed: {e}")
            results[endpoint] = False
    
    return results

def check_flutter_build():
    """Check if Flutter can build the app"""
    print("\n🏗️ Checking Flutter build...")
    
    try:
        # Try building for web
        result = subprocess.run(["flutter", "build", "web"], capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅ Flutter web build successful")
            return True
        else:
            print("❌ Flutter web build failed")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Could not build Flutter app: {e}")
        return False

def generate_flutter_report(results):
    """Generate Flutter test report"""
    print("\n" + "="*60)
    print("📊 FLUTTER FRONTEND TEST REPORT")
    print("="*60)
    
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
    if passed_tests / total_tests >= 0.8:
        print("   🚀 Flutter frontend is ready for production use")
    elif passed_tests / total_tests >= 0.6:
        print("   ⚠️ Flutter frontend needs some attention but is mostly functional")
    else:
        print("   🔧 Flutter frontend needs significant work")
    
    return passed_tests / total_tests if total_tests > 0 else 0

def main():
    """Main Flutter test function"""
    print("🚀 FLUTTER FRONTEND COMPREHENSIVE TEST")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = {}
    
    # Check Flutter installation
    results["flutter_installation"] = check_flutter_installation()
    
    if results["flutter_installation"]:
        # Check dependencies
        results["dependencies"] = check_flutter_dependencies()
        
        # Run Flutter analyze
        results["analyze"] = run_flutter_analyze()
        
        # Run Flutter tests
        results["tests"] = run_flutter_tests()
        
        # Check build
        results["build"] = check_flutter_build()
        
        # Start Flutter web server
        web_process = start_flutter_web()
        
        if web_process:
            # Test web endpoints
            web_results = test_flutter_web_endpoints()
            for endpoint, result in web_results.items():
                results[f"web_{endpoint}"] = result
            
            # Test backend integration
            integration_results = test_flutter_backend_integration()
            for endpoint, result in integration_results.items():
                results[f"integration_{endpoint}"] = result
            
            # Stop web server
            web_process.terminate()
            web_process.wait()
        else:
            results["web_server"] = False
            results["backend_integration"] = False
    else:
        # Skip other tests if Flutter is not installed
        results["dependencies"] = False
        results["analyze"] = False
        results["tests"] = False
        results["build"] = False
        results["web_server"] = False
        results["backend_integration"] = False
    
    # Generate report
    success_rate = generate_flutter_report(results)
    
    print(f"\n🎉 FLUTTER TEST COMPLETE!")
    print(f"Overall Success Rate: {success_rate*100:.1f}%")
    
    if success_rate >= 0.8:
        print("✅ Flutter frontend is ready for production use!")
        return 0
    elif success_rate >= 0.6:
        print("⚠️ Flutter frontend needs some attention but is mostly functional")
        return 1
    else:
        print("❌ Flutter frontend needs significant work")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 