#!/usr/bin/env python3
"""
Accurate Dart Endpoint Analysis
Properly extract endpoint paths from Dart files by handling template variables
"""

import os
import re
import json
from datetime import datetime

class AccurateDartEndpointAnalyzer:
    def __init__(self):
        # Working endpoints from our previous analysis
        self.working_endpoints = [
            "/api/imperium/dashboard",
            "/api/proposals",
            "/api/conquest/deployments", 
            "/api/approval/pending",
            "/api/agents/status",
            "/api/oath-papers",
            "/api/growth/insights",
            "/api/missions/statistics",
            "/api/custody/",
            "/api/imperium/monitoring",
            "/api/learning/insights/{aiType}",
            "/api/guardian/code-review",
            "/api/growth/analysis",
            "/api/learning/data",
            "/api/terra/extensions",
            "/api/proposals?status=pending",
            "/api/imperium/status",
            "/api/imperium/improvements",
            "/api/imperium/issues",
            "/api/guardian/threat-detection",
            "/api/imperium/agents",
            "/api/imperium/trusted-sources"
        ]
        
        # Non-working endpoints from our previous analysis
        self.failed_endpoints = [
            "/api/imperium/trigger-scan",
            "/api/proposals/{id}/accept",
            "/api/terra/extensions/{extensionId}",
            "/api/proposals/{id}/apply",
            "/api/guardian/",
            "/api/learning/test",
            "/api/guardian/security-status",
            "/api/approval/stats/overview",
            "/api/error",
            "/health",
            "/api/custody/test/{aiType}/force",
            "/api/codex/",
            "/api/usage",
            "/api/imperium/agents/{agentId}/topics",
            "/api/analytics",
            "/api/conquest/force-work",
            "/api/missions/health-check",
            "/api/conquest/improve-app",
            "/api/ai/upload-training-data",
            "/api/ai/research-subject",
            "/api/codex/log",
            "/api/oath-papers/enhanced-learning",
            "/api/imperium/learning/data",
            "/api/feedback",
            "/api/notifications/ws",
            "/api/learning/effectiveness",
            "/api/notifications/send",
            "/api/missions/sync",
            "/api/proposals/quotas",
            "/api/performance",
            "/api/guardian/health-check",
            "/api/ai/learning/cross-ai"
        ]
        
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "files_analyzed": [],
            "endpoints_found": {},
            "working_endpoints_used": [],
            "failed_endpoints_used": [],
            "unknown_endpoints": [],
            "files_with_issues": [],
            "files_clean": []
        }

    def extract_endpoints_from_dart_file(self, file_path):
        """Extract all API endpoints from a Dart file with proper template handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            endpoints = []
            
            # Pattern 1: Uri.parse with template variables
            uri_pattern1 = r'Uri\.parse\([\'"]([^\'"]*?/api/[^\'"]*?)[\'"]\)'
            matches1 = re.findall(uri_pattern1, content)
            
            for match in matches1:
                # Extract just the endpoint part after /api/
                if '/api/' in match:
                    api_start = match.find('/api/')
                    endpoint = match[api_start:]
                    
                    # Clean up template variables
                    endpoint = re.sub(r'/\$\{[^}]+\}', '/{id}', endpoint)
                    endpoint = re.sub(r'/\$[a-zA-Z_][a-zA-Z0-9_]*', '/{id}', endpoint)
                    endpoint = re.sub(r'/\$[^/]+', '/{id}', endpoint)
                    
                    # Remove any remaining template variables
                    endpoint = re.sub(r'\$\{[^}]+\}', '', endpoint)
                    endpoint = re.sub(r'\$[a-zA-Z_][a-zA-Z0-9_]*', '', endpoint)
                    
                    # Clean up any double slashes or trailing slashes
                    endpoint = re.sub(r'//+', '/', endpoint)
                    endpoint = endpoint.rstrip('/')
                    
                    if endpoint.startswith('/api/'):
                        endpoints.append(endpoint)
            
            # Pattern 2: Direct API calls without Uri.parse
            api_pattern = r'[\'"]([^\'"]*?/api/[^\'"]*?)[\'"]'
            matches2 = re.findall(api_pattern, content)
            
            for match in matches2:
                if '/api/' in match and 'Uri.parse' not in match:
                    api_start = match.find('/api/')
                    endpoint = match[api_start:]
                    
                    # Clean up template variables
                    endpoint = re.sub(r'/\$\{[^}]+\}', '/{id}', endpoint)
                    endpoint = re.sub(r'/\$[a-zA-Z_][a-zA-Z0-9_]*', '/{id}', endpoint)
                    endpoint = re.sub(r'/\$[^/]+', '/{id}', endpoint)
                    
                    # Remove any remaining template variables
                    endpoint = re.sub(r'\$\{[^}]+\}', '', endpoint)
                    endpoint = re.sub(r'\$[a-zA-Z_][a-zA-Z0-9_]*', '', endpoint)
                    
                    # Clean up any double slashes or trailing slashes
                    endpoint = re.sub(r'//+', '/', endpoint)
                    endpoint = endpoint.rstrip('/')
                    
                    if endpoint.startswith('/api/'):
                        endpoints.append(endpoint)
            
            return list(set(endpoints))  # Remove duplicates
            
        except Exception as e:
            print(f"❌ Error reading {file_path}: {str(e)}")
            return []

    def analyze_dart_files(self):
        """Analyze all Dart files in the lib directory"""
        print("🔍 Analyzing Dart files for endpoint usage...")
        
        lib_dir = "../lib"
        if not os.path.exists(lib_dir):
            print(f"❌ lib directory not found: {lib_dir}")
            return
        
        # Walk through all Dart files
        for root, dirs, files in os.walk(lib_dir):
            for file in files:
                if file.endswith('.dart'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, '..')
                    
                    endpoints = self.extract_endpoints_from_dart_file(file_path)
                    
                    if endpoints:
                        print(f"📄 {relative_path} - Found {len(endpoints)} endpoints")
                        self.analysis_results["files_analyzed"].append(relative_path)
                        self.analysis_results["endpoints_found"][relative_path] = endpoints
                        
                        # Check each endpoint
                        has_issues = False
                        for endpoint in endpoints:
                            if endpoint in self.working_endpoints:
                                if endpoint not in self.analysis_results["working_endpoints_used"]:
                                    self.analysis_results["working_endpoints_used"].append(endpoint)
                            elif endpoint in self.failed_endpoints:
                                if endpoint not in self.analysis_results["failed_endpoints_used"]:
                                    self.analysis_results["failed_endpoints_used"].append(endpoint)
                                has_issues = True
                            else:
                                if endpoint not in self.analysis_results["unknown_endpoints"]:
                                    self.analysis_results["unknown_endpoints"].append(endpoint)
                                has_issues = True
                        
                        if has_issues:
                            self.analysis_results["files_with_issues"].append(relative_path)
                        else:
                            self.analysis_results["files_clean"].append(relative_path)

    def generate_analysis_report(self):
        """Generate comprehensive analysis report"""
        print("\n" + "="*60)
        print("📊 ACCURATE DART ENDPOINT ANALYSIS REPORT")
        print("="*60)
        
        print(f"📁 Files Analyzed: {len(self.analysis_results['files_analyzed'])}")
        print(f"✅ Files Using Only Working Endpoints: {len(self.analysis_results['files_clean'])}")
        print(f"❌ Files With Issues: {len(self.analysis_results['files_with_issues'])}")
        
        print(f"\n🔗 Endpoints Found:")
        print(f"   ✅ Working Endpoints Used: {len(self.analysis_results['working_endpoints_used'])}")
        print(f"   ❌ Failed Endpoints Used: {len(self.analysis_results['failed_endpoints_used'])}")
        print(f"   ❓ Unknown Endpoints: {len(self.analysis_results['unknown_endpoints'])}")
        
        # Show working endpoints being used
        if self.analysis_results['working_endpoints_used']:
            print(f"\n✅ Working Endpoints Being Used:")
            for endpoint in sorted(self.analysis_results['working_endpoints_used']):
                print(f"   • {endpoint}")
        
        # Show failed endpoints being used
        if self.analysis_results['failed_endpoints_used']:
            print(f"\n❌ Failed Endpoints Being Used:")
            for endpoint in sorted(self.analysis_results['failed_endpoints_used']):
                print(f"   • {endpoint}")
        
        # Show unknown endpoints
        if self.analysis_results['unknown_endpoints']:
            print(f"\n❓ Unknown Endpoints:")
            for endpoint in sorted(self.analysis_results['unknown_endpoints']):
                print(f"   • {endpoint}")
        
        # Show files with issues
        if self.analysis_results['files_with_issues']:
            print(f"\n🚨 Files With Endpoint Issues:")
            for file_path in sorted(self.analysis_results['files_with_issues']):
                endpoints = self.analysis_results['endpoints_found'][file_path]
                failed_in_file = [ep for ep in endpoints if ep in self.failed_endpoints]
                unknown_in_file = [ep for ep in endpoints if ep not in self.working_endpoints and ep not in self.failed_endpoints]
                
                print(f"   📄 {file_path}")
                if failed_in_file:
                    print(f"      ❌ Failed: {', '.join(failed_in_file)}")
                if unknown_in_file:
                    print(f"      ❓ Unknown: {', '.join(unknown_in_file)}")
        
        # Show clean files
        if self.analysis_results['files_clean']:
            print(f"\n✅ Files Using Only Working Endpoints:")
            for file_path in sorted(self.analysis_results['files_clean']):
                print(f"   📄 {file_path}")
        
        # Calculate compliance percentage
        total_files = len(self.analysis_results['files_analyzed'])
        clean_files = len(self.analysis_results['files_clean'])
        compliance_percentage = (clean_files / total_files * 100) if total_files > 0 else 0
        
        print(f"\n📊 COMPLIANCE SUMMARY:")
        print(f"   Overall Compliance: {compliance_percentage:.1f}%")
        print(f"   Files Using Only Working Endpoints: {clean_files}/{total_files}")
        
        if compliance_percentage >= 90:
            print("✅ EXCELLENT - Almost all files are using correct endpoints!")
        elif compliance_percentage >= 75:
            print("✅ GOOD - Most files are using correct endpoints")
        elif compliance_percentage >= 50:
            print("⚠️ FAIR - Some files need endpoint fixes")
        else:
            print("❌ POOR - Many files need endpoint fixes")
        
        # Save detailed results
        with open('accurate_dart_endpoint_analysis_report.json', 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: accurate_dart_endpoint_analysis_report.json")

    def run_analysis(self):
        """Run complete analysis"""
        print("🚀 Starting accurate Dart endpoint analysis...")
        print(f"⏰ Timestamp: {self.analysis_results['timestamp']}")
        
        self.analyze_dart_files()
        self.generate_analysis_report()

def main():
    analyzer = AccurateDartEndpointAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main() 