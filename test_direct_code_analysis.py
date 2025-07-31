#!/usr/bin/env python3
"""
Direct test of code analysis methods to verify they generate meaningful code changes.
This script tests the _analyze_dart_code, _analyze_js_code, and _analyze_python_code methods directly.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_agent_service import AIAgentService

class DirectCodeAnalysisTest:
    """Test class to verify code analysis methods generate meaningful changes"""
    
    def __init__(self):
        self.agent_service = None
    
    async def initialize(self):
        """Initialize the test"""
        self.agent_service = AIAgentService()
        print("✅ Test initialized")
    
    def create_test_dart_code(self) -> str:
        """Create test Dart code with known issues"""
        return '''
import 'package:flutter/material.dart';

class TestWidget extends StatefulWidget {
  @override
  _TestWidgetState createState() => _TestWidgetState();
}

class _TestWidgetState extends State<TestWidget> {
  String data = "test";
  String unusedVar = "never used";
  
  @override
  Widget build(BuildContext context) {
    print("Debug info");
    print("More debug info");
    
    setState(() {
      data = "updated";
    });
    
    setState(() {
      data = "updated again";
    });
    
    setState(() {
      data = "and again";
    });
    
    return Container(
      child: Text(data),
    );
  }
}
'''
    
    def create_test_js_code(self) -> str:
        """Create test JavaScript code with known issues"""
        return '''
var oldVariable = "test";
var anotherVar = "something";

function testFunction() {
    console.log("Debug info");
    if (oldVariable == "test") {
        console.log("Found test");
    }
    
    var unusedVar = "never used";
    
    return oldVariable;
}

function longFunction() {
    var result = "";
    for (var i = 0; i < 100; i++) {
        result += i;
        if (i % 10 == 0) {
            console.log("Progress: " + i);
        }
    }
    return result;
}
'''
    
    def create_test_python_code(self) -> str:
        """Create test Python code with known issues"""
        return '''
import os
import sys
import unused_module

def test_function():
    print("Debug info")
    data = "test"
    result = data.format("value")
    return result

def long_function():
    result = []
    for i in range(100):
        result.append(i)
        if i % 10 == 0:
            print("Progress: {}".format(i))
    return result

def unused_function():
    pass
'''
    
    def analyze_code_changes(self, original_code: str, optimized_code: str, language: str) -> bool:
        """Analyze if the code changes are meaningful"""
        print(f"\n🔍 Analyzing {language} code changes...")
        
        lines_before = len(original_code.split('\n'))
        lines_after = len(optimized_code.split('\n'))
        chars_before = len(original_code)
        chars_after = len(optimized_code)
        
        print(f"  Original: {lines_before} lines, {chars_before} characters")
        print(f"  Optimized: {lines_after} lines, {chars_after} characters")
        
        # Check if there are meaningful changes
        if lines_before == lines_after and chars_before == chars_after:
            print(f"  ❌ No meaningful changes detected")
            return False
        else:
            print(f"  ✅ Meaningful changes detected:")
            print(f"    Lines: {lines_before} → {lines_after}")
            print(f"    Characters: {chars_before} → {chars_after}")
            
            # Show some of the changes
            if chars_after > chars_before:
                print(f"    Added {chars_after - chars_before} characters")
            elif chars_before > chars_after:
                print(f"    Removed {chars_before - chars_after} characters")
            
            return True
    
    async def test_dart_analysis(self):
        """Test Dart code analysis"""
        print("\n🏆 Testing Dart code analysis...")
        
        original_code = self.create_test_dart_code()
        file_path = "lib/test_widget.dart"
        
        try:
            analysis = await self.agent_service._analyze_dart_code(original_code, file_path)
            
            if analysis and analysis.get("optimizations"):
                print(f"✅ Found {len(analysis['optimizations'])} optimizations")
                
                original_code = analysis.get("original_code", "")
                optimized_code = analysis.get("optimized_code", "")
                
                has_changes = self.analyze_code_changes(original_code, optimized_code, "Dart")
                
                if has_changes:
                    print("  📝 Sample changes:")
                    # Show first few lines of differences
                    orig_lines = original_code.split('\n')[:5]
                    opt_lines = optimized_code.split('\n')[:5]
                    
                    for i, (orig, opt) in enumerate(zip(orig_lines, opt_lines)):
                        if orig != opt:
                            print(f"    Line {i+1}: {orig.strip()} → {opt.strip()}")
                else:
                    print("  ❌ No meaningful code changes generated")
            else:
                print("❌ No optimizations found")
                
        except Exception as e:
            print(f"❌ Dart analysis error: {str(e)}")
    
    async def test_js_analysis(self):
        """Test JavaScript code analysis"""
        print("\n🛡️ Testing JavaScript code analysis...")
        
        original_code = self.create_test_js_code()
        file_path = "src/test_script.js"
        
        try:
            analysis = await self.agent_service._analyze_js_code(original_code, file_path)
            
            if analysis and (analysis.get("optimizations") or analysis.get("warnings")):
                optimizations = len(analysis.get("optimizations", []))
                warnings = len(analysis.get("warnings", []))
                print(f"✅ Found {optimizations} optimizations and {warnings} warnings")
                
                original_code = analysis.get("original_code", "")
                optimized_code = analysis.get("optimized_code", "")
                
                has_changes = self.analyze_code_changes(original_code, optimized_code, "JavaScript")
                
                if has_changes:
                    print("  📝 Sample changes:")
                    # Show first few lines of differences
                    orig_lines = original_code.split('\n')[:5]
                    opt_lines = optimized_code.split('\n')[:5]
                    
                    for i, (orig, opt) in enumerate(zip(orig_lines, opt_lines)):
                        if orig != opt:
                            print(f"    Line {i+1}: {orig.strip()} → {opt.strip()}")
                else:
                    print("  ❌ No meaningful code changes generated")
            else:
                print("❌ No optimizations or warnings found")
                
        except Exception as e:
            print(f"❌ JavaScript analysis error: {str(e)}")
    
    async def test_python_analysis(self):
        """Test Python code analysis"""
        print("\n🧪 Testing Python code analysis...")
        
        original_code = self.create_test_python_code()
        file_path = "app/test_module.py"
        
        try:
            analysis = await self.agent_service._analyze_python_code(original_code, file_path)
            
            if analysis and analysis.get("optimizations"):
                print(f"✅ Found {len(analysis['optimizations'])} optimizations")
                
                original_code = analysis.get("original_code", "")
                optimized_code = analysis.get("optimized_code", "")
                
                has_changes = self.analyze_code_changes(original_code, optimized_code, "Python")
                
                if has_changes:
                    print("  📝 Sample changes:")
                    # Show first few lines of differences
                    orig_lines = original_code.split('\n')[:5]
                    opt_lines = optimized_code.split('\n')[:5]
                    
                    for i, (orig, opt) in enumerate(zip(orig_lines, opt_lines)):
                        if orig != opt:
                            print(f"    Line {i+1}: {orig.strip()} → {opt.strip()}")
                else:
                    print("  ❌ No meaningful code changes generated")
            else:
                print("❌ No optimizations found")
                
        except Exception as e:
            print(f"❌ Python analysis error: {str(e)}")
    
    async def run_all_tests(self):
        """Run all analysis tests"""
        print("🚀 Starting direct code analysis tests...")
        
        await self.initialize()
        
        # Test each language
        await self.test_dart_analysis()
        await self.test_js_analysis()
        await self.test_python_analysis()
        
        print("\n🎯 Test summary:")
        print("✅ All code analysis methods tested")
        print("📊 Check the output above for meaningful changes")

async def main():
    """Main test function"""
    test = DirectCodeAnalysisTest()
    await test.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 