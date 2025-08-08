#!/usr/bin/env python3
"""
Comprehensive System Analysis Script
Analyzes every function, data structure, AI function, tool, and component in the LVL_UP system
"""

import os
import json
import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime
import importlib.util
import inspect

class ComprehensiveSystemAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.lib_path = self.project_root / "lib"
        self.backend_path = self.project_root / "ai-backend-python"
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "frontend_analysis": {},
            "backend_analysis": {},
            "integration_analysis": {},
            "summary": {}
        }
        
        # Ensure paths exist
        if not self.lib_path.exists():
            print(f"⚠️  Warning: Frontend path not found: {self.lib_path}")
        if not self.backend_path.exists():
            print(f"⚠️  Warning: Backend path not found: {self.backend_path}")
        
    def analyze_dart_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Dart file for functions, classes, and data structures"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                "file_path": str(file_path.relative_to(self.project_root)),
                "file_size": len(content),
                "lines": len(content.split('\n')),
                "classes": [],
                "functions": [],
                "variables": [],
                "imports": [],
                "ai_functions": [],
                "services": [],
                "providers": [],
                "widgets": [],
                "models": [],
                "errors": []
            }
            
            # Extract imports
            import_pattern = r'import\s+[\'"]([^\'"]+)[\'"]'
            analysis["imports"] = re.findall(import_pattern, content)
            
            # Extract class definitions
            class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?(?:\s+with\s+([^{]+))?\s*{'
            classes = re.findall(class_pattern, content)
            for class_match in classes:
                class_name = class_match[0]
                extends = class_match[1] if class_match[1] else None
                implements = class_match[2] if class_match[2] else None
                with_mixin = class_match[3] if class_match[3] else None
                
                analysis["classes"].append({
                    "name": class_name,
                    "extends": extends,
                    "implements": implements,
                    "with_mixin": with_mixin
                })
            
            # Extract function definitions
            function_pattern = r'(?:static\s+)?(?:Future<[^>]+>\s+)?(\w+)\s+(\w+)\s*\([^)]*\)\s*(?:async\s*)?(?:=>\s*[^{]+|{[^}]*})'
            functions = re.findall(function_pattern, content)
            for return_type, func_name in functions:
                analysis["functions"].append({
                    "name": func_name,
                    "return_type": return_type,
                    "is_async": "async" in content[content.find(f"{return_type} {func_name}"):content.find(f"{return_type} {func_name}")+100]
                })
            
            # Identify AI-related functions
            ai_keywords = ['ai_', 'AI', 'guardian', 'brain', 'learning', 'analytics', 'intelligence']
            for func in analysis["functions"]:
                if any(keyword.lower() in func["name"].lower() for keyword in ai_keywords):
                    analysis["ai_functions"].append(func)
            
            # Identify services
            if "service" in file_path.name.lower():
                analysis["services"] = analysis["functions"]
            
            # Identify providers
            if "provider" in file_path.name.lower():
                analysis["providers"] = analysis["functions"]
            
            # Identify widgets
            if "widget" in file_path.name.lower() or "screen" in file_path.name.lower():
                analysis["widgets"] = analysis["functions"]
            
            # Identify models
            if "model" in file_path.name.lower() or file_path.parent.name == "models":
                analysis["models"] = analysis["classes"]
            
            return analysis
            
        except Exception as e:
            return {
                "file_path": str(file_path.relative_to(self.project_root)),
                "error": str(e)
            }
    
    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file for functions, classes, and data structures"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                "file_path": str(file_path.relative_to(self.project_root)),
                "file_size": len(content),
                "lines": len(content.split('\n')),
                "classes": [],
                "functions": [],
                "variables": [],
                "imports": [],
                "ai_functions": [],
                "services": [],
                "models": [],
                "routers": [],
                "endpoints": [],
                "errors": []
            }
            
            try:
                tree = ast.parse(content)
                
                # Extract imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis["imports"].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            analysis["imports"].append(f"{module}.{alias.name}")
                
                # Extract classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_info = {
                            "name": node.name,
                            "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
                            "methods": [],
                            "attributes": []
                        }
                        
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                class_info["methods"].append({
                                    "name": item.name,
                                    "args": [arg.arg for arg in item.args.args],
                                    "is_async": isinstance(item, ast.AsyncFunctionDef)
                                })
                            elif isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        class_info["attributes"].append(target.id)
                        
                        analysis["classes"].append(class_info)
                
                # Extract functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if hasattr(parent, 'body') and node in parent.body):
                        func_info = {
                            "name": node.name,
                            "args": [arg.arg for arg in node.args.args],
                            "is_async": isinstance(node, ast.AsyncFunctionDef)
                        }
                        analysis["functions"].append(func_info)
                
                # Identify AI-related functions
                ai_keywords = ['ai_', 'AI', 'guardian', 'brain', 'learning', 'analytics', 'intelligence', 'custodes', 'imperium']
                for func in analysis["functions"]:
                    if any(keyword.lower() in func["name"].lower() for keyword in ai_keywords):
                        analysis["ai_functions"].append(func)
                
                # Identify FastAPI endpoints
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check for FastAPI decorators
                        if hasattr(node, 'decorator_list'):
                            for decorator in node.decorator_list:
                                if isinstance(decorator, ast.Call):
                                    if isinstance(decorator.func, ast.Attribute):
                                        if decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                                            analysis["endpoints"].append({
                                                "name": node.name,
                                                "method": decorator.func.attr.upper(),
                                                "path": self._extract_path_from_decorator(decorator)
                                            })
                
                # Identify services
                if "service" in file_path.name.lower():
                    analysis["services"] = analysis["functions"]
                
                # Identify models
                if "model" in file_path.name.lower() or file_path.parent.name == "models":
                    analysis["models"] = analysis["classes"]
                
                # Identify routers
                if "router" in file_path.name.lower() or file_path.parent.name == "routers":
                    analysis["routers"] = analysis["functions"]
                
            except SyntaxError as e:
                analysis["errors"].append(f"Syntax error: {e}")
            
            return analysis
            
        except Exception as e:
            return {
                "file_path": str(file_path.relative_to(self.project_root)),
                "error": str(e)
            }
    
    def _extract_path_from_decorator(self, decorator: ast.Call) -> str:
        """Extract path from FastAPI decorator"""
        try:
            if decorator.args:
                if isinstance(decorator.args[0], ast.Constant):
                    return decorator.args[0].value
                elif isinstance(decorator.args[0], ast.Str):
                    return decorator.args[0].s
        except:
            pass
        return "/"
    
    def analyze_frontend(self) -> Dict[str, Any]:
        """Analyze the entire Flutter/Dart frontend"""
        print("🔍 Analyzing Flutter/Dart frontend...")
        
        frontend_analysis = {
            "total_files": 0,
            "total_lines": 0,
            "total_classes": 0,
            "total_functions": 0,
            "total_ai_functions": 0,
            "files": [],
            "services": [],
            "providers": [],
            "widgets": [],
            "models": [],
            "ai_components": []
        }
        
        # Check if frontend path exists
        if not self.lib_path.exists():
            print(f"❌ Frontend path not found: {self.lib_path}")
            return frontend_analysis
        
        # Analyze all Dart files
        dart_files = list(self.lib_path.rglob("*.dart"))
        print(f"📱 Found {len(dart_files)} Dart files to analyze")
        
        for dart_file in dart_files:
            if dart_file.is_file():
                print(f"   Analyzing: {dart_file.relative_to(self.project_root)}")
                analysis = self.analyze_dart_file(dart_file)
                frontend_analysis["files"].append(analysis)
                
                frontend_analysis["total_files"] += 1
                frontend_analysis["total_lines"] += analysis.get("lines", 0)
                frontend_analysis["total_classes"] += len(analysis.get("classes", []))
                frontend_analysis["total_functions"] += len(analysis.get("functions", []))
                frontend_analysis["total_ai_functions"] += len(analysis.get("ai_functions", []))
                
                # Categorize components
                if analysis.get("services"):
                    frontend_analysis["services"].append(analysis)
                if analysis.get("providers"):
                    frontend_analysis["providers"].append(analysis)
                if analysis.get("widgets"):
                    frontend_analysis["widgets"].append(analysis)
                if analysis.get("models"):
                    frontend_analysis["models"].append(analysis)
                if analysis.get("ai_functions"):
                    frontend_analysis["ai_components"].append(analysis)
        
        return frontend_analysis
    
    def analyze_backend(self) -> Dict[str, Any]:
        """Analyze the entire Python backend"""
        print("🔍 Analyzing Python backend...")
        
        backend_analysis = {
            "total_files": 0,
            "total_lines": 0,
            "total_classes": 0,
            "total_functions": 0,
            "total_ai_functions": 0,
            "total_endpoints": 0,
            "files": [],
            "services": [],
            "models": [],
            "routers": [],
            "ai_components": [],
            "endpoints": []
        }
        
        # Check if backend path exists
        if not self.backend_path.exists():
            print(f"❌ Backend path not found: {self.backend_path}")
            return backend_analysis
        
        # Analyze all Python files
        python_files = [f for f in self.backend_path.rglob("*.py") 
                       if f.is_file() and not f.name.startswith("__")]
        print(f"🐍 Found {len(python_files)} Python files to analyze")
        
        for python_file in python_files:
            print(f"   Analyzing: {python_file.relative_to(self.project_root)}")
            analysis = self.analyze_python_file(python_file)
            backend_analysis["files"].append(analysis)
            
            backend_analysis["total_files"] += 1
            backend_analysis["total_lines"] += analysis.get("lines", 0)
            backend_analysis["total_classes"] += len(analysis.get("classes", []))
            backend_analysis["total_functions"] += len(analysis.get("functions", []))
            backend_analysis["total_ai_functions"] += len(analysis.get("ai_functions", []))
            backend_analysis["total_endpoints"] += len(analysis.get("endpoints", []))
            
            # Categorize components
            if analysis.get("services"):
                backend_analysis["services"].append(analysis)
            if analysis.get("models"):
                backend_analysis["models"].append(analysis)
            if analysis.get("routers"):
                backend_analysis["routers"].append(analysis)
            if analysis.get("ai_functions"):
                backend_analysis["ai_components"].append(analysis)
            if analysis.get("endpoints"):
                backend_analysis["endpoints"].extend(analysis.get("endpoints", []))
        
        return backend_analysis
    
    def analyze_integration(self) -> Dict[str, Any]:
        """Analyze integration between frontend and backend"""
        print("🔍 Analyzing frontend-backend integration...")
        
        integration_analysis = {
            "api_endpoints": [],
            "data_models": [],
            "shared_concepts": [],
            "potential_issues": []
        }
        
        # Extract API endpoints from backend
        backend_endpoints = []
        for file_analysis in self.analysis_results["backend_analysis"].get("files", []):
            for endpoint in file_analysis.get("endpoints", []):
                backend_endpoints.append(endpoint)
        
        # Extract API calls from frontend
        frontend_api_calls = []
        for file_analysis in self.analysis_results["frontend_analysis"].get("files", []):
            content = ""
            try:
                with open(self.project_root / file_analysis["file_path"], 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                continue
            
            # Look for HTTP calls
            http_patterns = [
                r'http\.(get|post|put|delete|patch)\s*\([^)]+\)',
                r'HttpClient\(\)\.(get|post|put|delete|patch)\s*\([^)]+\)',
                r'Dio\(\)\.(get|post|put|delete|patch)\s*\([^)]+\)'
            ]
            
            for pattern in http_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    frontend_api_calls.append({
                        "method": match.upper(),
                        "file": file_analysis["file_path"]
                    })
        
        integration_analysis["api_endpoints"] = {
            "backend": backend_endpoints,
            "frontend_calls": frontend_api_calls
        }
        
        # Check for shared data models
        backend_models = []
        frontend_models = []
        
        for file_analysis in self.analysis_results["backend_analysis"].get("models", []):
            for class_info in file_analysis.get("classes", []):
                backend_models.append(class_info["name"])
        
        for file_analysis in self.analysis_results["frontend_analysis"].get("models", []):
            for class_info in file_analysis.get("classes", []):
                frontend_models.append(class_info["name"])
        
        integration_analysis["data_models"] = {
            "backend": backend_models,
            "frontend": frontend_models
        }
        
        return integration_analysis
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive summary of the analysis"""
        print("📊 Generating comprehensive summary...")
        
        frontend = self.analysis_results["frontend_analysis"]
        backend = self.analysis_results["backend_analysis"]
        integration = self.analysis_results["integration_analysis"]
        
        summary = {
            "system_overview": {
                "total_files": frontend["total_files"] + backend["total_files"],
                "total_lines": frontend["total_lines"] + backend["total_lines"],
                "frontend_files": frontend["total_files"],
                "backend_files": backend["total_files"],
                "frontend_lines": frontend["total_lines"],
                "backend_lines": backend["total_lines"]
            },
            "ai_components": {
                "frontend_ai_functions": frontend["total_ai_functions"],
                "backend_ai_functions": backend["total_ai_functions"],
                "total_ai_functions": frontend["total_ai_functions"] + backend["total_ai_functions"]
            },
            "architecture": {
                "frontend_services": len(frontend["services"]),
                "frontend_providers": len(frontend["providers"]),
                "frontend_widgets": len(frontend["widgets"]),
                "frontend_models": len(frontend["models"]),
                "backend_services": len(backend["services"]),
                "backend_models": len(backend["models"]),
                "backend_routers": len(backend["routers"]),
                "backend_endpoints": backend["total_endpoints"]
            },
            "integration": {
                "api_endpoints": len(integration["api_endpoints"]["backend"]),
                "frontend_api_calls": len(integration["api_endpoints"]["frontend_calls"]),
                "backend_models": len(integration["data_models"]["backend"]),
                "frontend_models": len(integration["data_models"]["frontend"])
            },
            "key_findings": []
        }
        
        # Add key findings
        if frontend["total_ai_functions"] > 0:
            summary["key_findings"].append(f"Frontend has {frontend['total_ai_functions']} AI-related functions")
        
        if backend["total_ai_functions"] > 0:
            summary["key_findings"].append(f"Backend has {backend['total_ai_functions']} AI-related functions")
        
        if backend["total_endpoints"] > 0:
            summary["key_findings"].append(f"Backend exposes {backend['total_endpoints']} API endpoints")
        
        if len(frontend["services"]) > 0:
            summary["key_findings"].append(f"Frontend has {len(frontend['services'])} service files")
        
        if len(backend["services"]) > 0:
            summary["key_findings"].append(f"Backend has {len(backend['services'])} service files")
        
        return summary
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run the complete comprehensive analysis"""
        print("🚀 Starting comprehensive system analysis...")
        print(f"📁 Project root: {self.project_root}")
        print(f"📱 Frontend path: {self.lib_path}")
        print(f"🐍 Backend path: {self.backend_path}")
        
        # Analyze frontend
        self.analysis_results["frontend_analysis"] = self.analyze_frontend()
        
        # Analyze backend
        self.analysis_results["backend_analysis"] = self.analyze_backend()
        
        # Analyze integration
        self.analysis_results["integration_analysis"] = self.analyze_integration()
        
        # Generate summary
        self.analysis_results["summary"] = self.generate_summary()
        
        print("✅ Comprehensive analysis completed!")
        return self.analysis_results
    
    def save_analysis_report(self, output_file: str = "comprehensive_system_analysis_report.json"):
        """Save the analysis results to a JSON file"""
        output_path = self.project_root / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Analysis report saved to: {output_path}")
        return output_path
    
    def print_summary(self):
        """Print a human-readable summary of the analysis"""
        summary = self.analysis_results["summary"]
        
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE SYSTEM ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"\n📊 SYSTEM OVERVIEW:")
        print(f"   Total Files: {summary['system_overview']['total_files']}")
        print(f"   Total Lines: {summary['system_overview']['total_lines']:,}")
        print(f"   Frontend: {summary['system_overview']['frontend_files']} files, {summary['system_overview']['frontend_lines']:,} lines")
        print(f"   Backend: {summary['system_overview']['backend_files']} files, {summary['system_overview']['backend_lines']:,} lines")
        
        print(f"\n🤖 AI COMPONENTS:")
        print(f"   Total AI Functions: {summary['ai_components']['total_ai_functions']}")
        print(f"   Frontend AI Functions: {summary['ai_components']['frontend_ai_functions']}")
        print(f"   Backend AI Functions: {summary['ai_components']['backend_ai_functions']}")
        
        print(f"\n🏗️  ARCHITECTURE:")
        print(f"   Frontend Services: {summary['architecture']['frontend_services']}")
        print(f"   Frontend Providers: {summary['architecture']['frontend_providers']}")
        print(f"   Frontend Widgets: {summary['architecture']['frontend_widgets']}")
        print(f"   Frontend Models: {summary['architecture']['frontend_models']}")
        print(f"   Backend Services: {summary['architecture']['backend_services']}")
        print(f"   Backend Models: {summary['architecture']['backend_models']}")
        print(f"   Backend Routers: {summary['architecture']['backend_routers']}")
        print(f"   Backend Endpoints: {summary['architecture']['backend_endpoints']}")
        
        print(f"\n🔗 INTEGRATION:")
        print(f"   API Endpoints: {summary['integration']['api_endpoints']}")
        print(f"   Frontend API Calls: {summary['integration']['frontend_api_calls']}")
        print(f"   Backend Models: {summary['integration']['backend_models']}")
        print(f"   Frontend Models: {summary['integration']['frontend_models']}")
        
        print(f"\n🔍 KEY FINDINGS:")
        for finding in summary['key_findings']:
            print(f"   • {finding}")
        
        print("\n" + "="*80)

def main():
    """Main function to run the comprehensive analysis"""
    # Get the project root (assuming script is run from project root)
    project_root = Path.cwd()
    
    # Create analyzer
    analyzer = ComprehensiveSystemAnalyzer(project_root)
    
    # Run comprehensive analysis
    results = analyzer.run_comprehensive_analysis()
    
    # Save report
    report_path = analyzer.save_analysis_report()
    
    # Print summary
    analyzer.print_summary()
    
    print(f"\n📋 Detailed analysis saved to: {report_path}")
    print("🎉 Analysis complete! Check the JSON report for detailed information.")

if __name__ == "__main__":
    main() 