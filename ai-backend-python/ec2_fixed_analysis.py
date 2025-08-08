#!/usr/bin/env python3
"""
Fixed Comprehensive System Analysis Script for EC2
Analyzes every function, data structure, AI function, tool, and component in the LVL_UP system on EC2
"""

import os
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class FixedComprehensiveAnalyzer:
    def __init__(self):
        self.project_root = Path('/home/ubuntu/ai-backend-python')
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'backend_analysis': {},
            'frontend_analysis': {},
            'summary': {}
        }
    
    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                'file_path': str(file_path.relative_to(self.project_root)),
                'file_size': len(content),
                'lines': len(content.split('\n')),
                'classes': [],
                'functions': [],
                'imports': [],
                'ai_functions': [],
                'endpoints': [],
                'errors': []
            }
            
            try:
                tree = ast.parse(content)
                
                # Extract imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis['imports'].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        for alias in node.names:
                            analysis['imports'].append(f'{module}.{alias.name}')
                
                # Extract classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_info = {
                            'name': node.name,
                            'bases': [base.id for base in node.bases if isinstance(base, ast.Name)],
                            'methods': []
                        }
                        
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                class_info['methods'].append({
                                    'name': item.name,
                                    'args': [arg.arg for arg in item.args.args],
                                    'is_async': isinstance(item, ast.AsyncFunctionDef)
                                })
                        
                        analysis['classes'].append(class_info)
                
                # Extract functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if hasattr(parent, 'body') and node in parent.body):
                        func_info = {
                            'name': node.name,
                            'args': [arg.arg for arg in node.args.args],
                            'is_async': isinstance(node, ast.AsyncFunctionDef)
                        }
                        analysis['functions'].append(func_info)
                
                # Identify AI-related functions
                ai_keywords = ['ai_', 'AI', 'guardian', 'brain', 'learning', 'analytics', 'intelligence', 'custodes', 'imperium']
                for func in analysis['functions']:
                    if any(keyword.lower() in func['name'].lower() for keyword in ai_keywords):
                        analysis['ai_functions'].append(func)
                
                # Identify FastAPI endpoints
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if hasattr(node, 'decorator_list'):
                            for decorator in node.decorator_list:
                                if isinstance(decorator, ast.Call):
                                    if isinstance(decorator.func, ast.Attribute):
                                        if decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                                            analysis['endpoints'].append({
                                                'name': node.name,
                                                'method': decorator.func.attr.upper(),
                                                'path': self._extract_path_from_decorator(decorator)
                                            })
                
            except SyntaxError as e:
                analysis['errors'].append(f'Syntax error: {e}')
            
            return analysis
            
        except Exception as e:
            return {
                'file_path': str(file_path.relative_to(self.project_root)),
                'error': str(e)
            }
    
    def _extract_path_from_decorator(self, decorator: ast.Call) -> str:
        try:
            if decorator.args:
                if isinstance(decorator.args[0], ast.Constant):
                    return decorator.args[0].value
                elif isinstance(decorator.args[0], ast.Str):
                    return decorator.args[0].s
        except:
            pass
        return '/'
    
    def analyze_backend(self) -> Dict[str, Any]:
        print('🔍 Analyzing Python backend...')
        
        backend_analysis = {
            'total_files': 0,
            'total_lines': 0,
            'total_classes': 0,
            'total_functions': 0,
            'total_ai_functions': 0,
            'total_endpoints': 0,
            'files': [],
            'services': [],
            'models': [],
            'routers': [],
            'ai_components': [],
            'endpoints': []
        }
        
        # Analyze all Python files in the current directory and subdirectories
        python_files = [f for f in self.project_root.rglob('*.py') 
                       if f.is_file() and not f.name.startswith('__')]
        print(f'🐍 Found {len(python_files)} Python files to analyze')
        
        for python_file in python_files:
            print(f'   Analyzing: {python_file.relative_to(self.project_root)}')
            analysis = self.analyze_python_file(python_file)
            backend_analysis['files'].append(analysis)
            
            backend_analysis['total_files'] += 1
            backend_analysis['total_lines'] += analysis.get('lines', 0)
            backend_analysis['total_classes'] += len(analysis.get('classes', []))
            backend_analysis['total_functions'] += len(analysis.get('functions', []))
            backend_analysis['total_ai_functions'] += len(analysis.get('ai_functions', []))
            backend_analysis['total_endpoints'] += len(analysis.get('endpoints', []))
            
            # Categorize components
            if 'service' in python_file.name.lower():
                backend_analysis['services'].append(analysis)
            if 'model' in python_file.name.lower() or python_file.parent.name == 'models':
                backend_analysis['models'].append(analysis)
            if 'router' in python_file.name.lower() or python_file.parent.name == 'routers':
                backend_analysis['routers'].append(analysis)
            if analysis.get('ai_functions'):
                backend_analysis['ai_components'].append(analysis)
            if analysis.get('endpoints'):
                backend_analysis['endpoints'].extend(analysis.get('endpoints', []))
        
        return backend_analysis
    
    def analyze_frontend(self) -> Dict[str, Any]:
        print('🔍 Analyzing Flutter/Dart frontend...')
        
        frontend_analysis = {
            'total_files': 0,
            'total_lines': 0,
            'total_classes': 0,
            'total_functions': 0,
            'total_ai_functions': 0,
            'files': [],
            'services': [],
            'providers': [],
            'widgets': [],
            'models': [],
            'ai_components': []
        }
        
        lib_path = self.project_root / 'lib'
        if not lib_path.exists():
            print(f'❌ Frontend path not found: {lib_path}')
            return frontend_analysis
        
        # Analyze all Dart files
        dart_files = list(lib_path.rglob('*.dart'))
        print(f'📱 Found {len(dart_files)} Dart files to analyze')
        
        for dart_file in dart_files:
            if dart_file.is_file():
                print(f'   Analyzing: {dart_file.relative_to(self.project_root)}')
                analysis = self.analyze_dart_file(dart_file)
                frontend_analysis['files'].append(analysis)
                
                frontend_analysis['total_files'] += 1
                frontend_analysis['total_lines'] += analysis.get('lines', 0)
                frontend_analysis['total_classes'] += len(analysis.get('classes', []))
                frontend_analysis['total_functions'] += len(analysis.get('functions', []))
                frontend_analysis['total_ai_functions'] += len(analysis.get('ai_functions', []))
                
                # Categorize components
                if analysis.get('services'):
                    frontend_analysis['services'].append(analysis)
                if analysis.get('providers'):
                    frontend_analysis['providers'].append(analysis)
                if analysis.get('widgets'):
                    frontend_analysis['widgets'].append(analysis)
                if analysis.get('models'):
                    frontend_analysis['models'].append(analysis)
                if analysis.get('ai_functions'):
                    frontend_analysis['ai_components'].append(analysis)
        
        return frontend_analysis
    
    def analyze_dart_file(self, file_path: Path) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                'file_path': str(file_path.relative_to(self.project_root)),
                'file_size': len(content),
                'lines': len(content.split('\n')),
                'classes': [],
                'functions': [],
                'imports': [],
                'ai_functions': [],
                'services': [],
                'providers': [],
                'widgets': [],
                'models': [],
                'errors': []
            }
            
            # Extract imports
            import_pattern = r'import\s+[\'"]([^\'"]+)[\'"]'
            analysis['imports'] = re.findall(import_pattern, content)
            
            # Extract class definitions
            class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?(?:\s+with\s+([^{]+))?\s*{'
            classes = re.findall(class_pattern, content)
            for class_match in classes:
                class_name = class_match[0]
                extends = class_match[1] if class_match[1] else None
                implements = class_match[2] if class_match[2] else None
                with_mixin = class_match[3] if class_match[3] else None
                
                analysis['classes'].append({
                    'name': class_name,
                    'extends': extends,
                    'implements': implements,
                    'with_mixin': with_mixin
                })
            
            # Extract function definitions
            function_pattern = r'(?:static\s+)?(?:Future<[^>]+>\s+)?(\w+)\s+(\w+)\s*\([^)]*\)\s*(?:async\s*)?(?:=>\s*[^{]+|{[^}]*})'
            functions = re.findall(function_pattern, content)
            for return_type, func_name in functions:
                analysis['functions'].append({
                    'name': func_name,
                    'return_type': return_type,
                    'is_async': 'async' in content[content.find(f'{return_type} {func_name}'):content.find(f'{return_type} {func_name}')+100]
                })
            
            # Identify AI-related functions
            ai_keywords = ['ai_', 'AI', 'guardian', 'brain', 'learning', 'analytics', 'intelligence']
            for func in analysis['functions']:
                if any(keyword.lower() in func['name'].lower() for keyword in ai_keywords):
                    analysis['ai_functions'].append(func)
            
            # Identify services
            if 'service' in file_path.name.lower():
                analysis['services'] = analysis['functions']
            
            # Identify providers
            if 'provider' in file_path.name.lower():
                analysis['providers'] = analysis['functions']
            
            # Identify widgets
            if 'widget' in file_path.name.lower() or 'screen' in file_path.name.lower():
                analysis['widgets'] = analysis['functions']
            
            # Identify models
            if 'model' in file_path.name.lower() or file_path.parent.name == 'models':
                analysis['models'] = analysis['classes']
            
            return analysis
            
        except Exception as e:
            return {
                'file_path': str(file_path.relative_to(self.project_root)),
                'error': str(e)
            }
    
    def generate_summary(self) -> Dict[str, Any]:
        print('📊 Generating comprehensive summary...')
        
        frontend = self.analysis_results['frontend_analysis']
        backend = self.analysis_results['backend_analysis']
        
        summary = {
            'system_overview': {
                'total_files': frontend['total_files'] + backend['total_files'],
                'total_lines': frontend['total_lines'] + backend['total_lines'],
                'frontend_files': frontend['total_files'],
                'backend_files': backend['total_files'],
                'frontend_lines': frontend['total_lines'],
                'backend_lines': backend['total_lines']
            },
            'ai_components': {
                'frontend_ai_functions': frontend['total_ai_functions'],
                'backend_ai_functions': backend['total_ai_functions'],
                'total_ai_functions': frontend['total_ai_functions'] + backend['total_ai_functions']
            },
            'architecture': {
                'frontend_services': len(frontend['services']),
                'frontend_providers': len(frontend['providers']),
                'frontend_widgets': len(frontend['widgets']),
                'frontend_models': len(frontend['models']),
                'backend_services': len(backend['services']),
                'backend_models': len(backend['models']),
                'backend_routers': len(backend['routers']),
                'backend_endpoints': backend['total_endpoints']
            },
            'key_findings': []
        }
        
        # Add key findings
        if frontend['total_ai_functions'] > 0:
            summary['key_findings'].append(f'Frontend has {frontend["total_ai_functions"]} AI-related functions')
        
        if backend['total_ai_functions'] > 0:
            summary['key_findings'].append(f'Backend has {backend["total_ai_functions"]} AI-related functions')
        
        if backend['total_endpoints'] > 0:
            summary['key_findings'].append(f'Backend exposes {backend["total_endpoints"]} API endpoints')
        
        if len(frontend['services']) > 0:
            summary['key_findings'].append(f'Frontend has {len(frontend["services"])} service files')
        
        if len(backend['services']) > 0:
            summary['key_findings'].append(f'Backend has {len(backend["services"])} service files')
        
        return summary
    
    def run_analysis(self) -> Dict[str, Any]:
        print('🚀 Starting comprehensive system analysis on EC2...')
        print(f'📁 Project root: {self.project_root}')
        
        # Analyze backend
        self.analysis_results['backend_analysis'] = self.analyze_backend()
        
        # Analyze frontend
        self.analysis_results['frontend_analysis'] = self.analyze_frontend()
        
        # Generate summary
        self.analysis_results['summary'] = self.generate_summary()
        
        print('✅ Comprehensive analysis completed!')
        return self.analysis_results
    
    def save_report(self, output_file: str = 'fixed_comprehensive_analysis_report.json'):
        output_path = self.project_root / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f'📄 Analysis report saved to: {output_path}')
        return output_path
    
    def print_summary(self):
        summary = self.analysis_results['summary']
        
        print('\n' + '='*80)
        print('🎯 COMPREHENSIVE SYSTEM ANALYSIS SUMMARY (EC2 FIXED)')
        print('='*80)
        
        print(f'\n📊 SYSTEM OVERVIEW:')
        print(f'   Total Files: {summary["system_overview"]["total_files"]}')
        print(f'   Total Lines: {summary["system_overview"]["total_lines"]:,}')
        print(f'   Frontend: {summary["system_overview"]["frontend_files"]} files, {summary["system_overview"]["frontend_lines"]:,} lines')
        print(f'   Backend: {summary["system_overview"]["backend_files"]} files, {summary["system_overview"]["backend_lines"]:,} lines')
        
        print(f'\n🤖 AI COMPONENTS:')
        print(f'   Total AI Functions: {summary["ai_components"]["total_ai_functions"]}')
        print(f'   Frontend AI Functions: {summary["ai_components"]["frontend_ai_functions"]}')
        print(f'   Backend AI Functions: {summary["ai_components"]["backend_ai_functions"]}')
        
        print(f'\n🏗️  ARCHITECTURE:')
        print(f'   Frontend Services: {summary["architecture"]["frontend_services"]}')
        print(f'   Frontend Providers: {summary["architecture"]["frontend_providers"]}')
        print(f'   Frontend Widgets: {summary["architecture"]["frontend_widgets"]}')
        print(f'   Frontend Models: {summary["architecture"]["frontend_models"]}')
        print(f'   Backend Services: {summary["architecture"]["backend_services"]}')
        print(f'   Backend Models: {summary["architecture"]["backend_models"]}')
        print(f'   Backend Routers: {summary["architecture"]["backend_routers"]}')
        print(f'   Backend Endpoints: {summary["architecture"]["backend_endpoints"]}')
        
        print(f'\n🔍 KEY FINDINGS:')
        for finding in summary['key_findings']:
            print(f'   • {finding}')
        
        print('\n' + '='*80)

def main():
    analyzer = FixedComprehensiveAnalyzer()
    results = analyzer.run_analysis()
    report_path = analyzer.save_report()
    analyzer.print_summary()
    print(f'\n📋 Detailed analysis saved to: {report_path}')

if __name__ == '__main__':
    main() 