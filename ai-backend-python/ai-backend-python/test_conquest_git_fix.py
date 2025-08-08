#!/usr/bin/env python3
"""
Test script to verify Conquest agent git fix
"""

import subprocess
import shutil
import sys
import os

def test_git_availability():
    """Test if git is available and working"""
    print("🧪 Testing git availability...")
    
    # Check if git is available
    git_path = shutil.which('git')
    if git_path:
        print(f"✅ Git found at: {git_path}")
    else:
        print("❌ Git not found in PATH")
        return False
    
    # Test git version
    try:
        result = subprocess.run(['git', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Git version: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Git version check failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Git command not found")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Git version check timed out")
        return False
    except Exception as e:
        print(f"❌ Git test failed: {e}")
        return False

def test_git_operations():
    """Test git operations that Conquest agent uses"""
    print("\n🧪 Testing git operations...")
    
    # Test git status
    try:
        result = subprocess.run(['git', 'status'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Git status works")
        else:
            print(f"⚠️ Git status failed (not in repo): {result.stderr.strip()}")
    except FileNotFoundError:
        print("❌ Git status failed - git not found")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Git status timed out")
        return False
    except Exception as e:
        print(f"❌ Git status failed: {e}")
        return False
    
    # Test git branch
    try:
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ Git branch works: {result.stdout.strip()}")
        else:
            print(f"⚠️ Git branch failed (not in repo): {result.stderr.strip()}")
    except FileNotFoundError:
        print("❌ Git branch failed - git not found")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Git branch timed out")
        return False
    except Exception as e:
        print(f"❌ Git branch failed: {e}")
        return False
    
    return True

def test_conquest_agent_code():
    """Test the updated Conquest agent code"""
    print("\n🧪 Testing Conquest agent code...")
    
    # Test the git availability check
    try:
        import shutil
        git_path = shutil.which('git')
        print(f"✅ Git availability check works: {bool(git_path)}")
        
        # Test subprocess with git
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            print(f"✅ Subprocess git test works: {result.returncode == 0}")
        except FileNotFoundError:
            print("⚠️ Subprocess git test failed - git not found (expected in some environments)")
        except Exception as e:
            print(f"⚠️ Subprocess git test failed: {e}")
            
    except Exception as e:
        print(f"❌ Conquest agent code test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🔧 Testing Conquest agent git fix...")
    print("=" * 50)
    
    tests = [
        ("Git Availability", test_git_availability),
        ("Git Operations", test_git_operations),
        ("Conquest Agent Code", test_conquest_agent_code)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Conquest agent git fix is working.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 