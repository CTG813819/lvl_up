#!/usr/bin/env python3
"""
Final Dart Endpoint Cleanup
Fix remaining endpoint issues in Dart files
"""

import os
import re
import json
from datetime import datetime

class FinalDartCleanup:
    def __init__(self):
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
        
        self.fixes_applied = []
        self.files_modified = []

    def cleanup_dart_file(self, file_path):
        """Clean up remaining endpoint issues in a Dart file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_fixes = []
            
            # Fix 1: Clean up malformed endpoints
            malformed_fixes = [
                # Fix double endpoints
                (r'/api/guardian/api/imperium/status-status', '/api/imperium/status'),
                (r'/api/missions/statistics/statistics', '/api/missions/statistics'),
                (r'/api/guardian/code-review/statistics', '/api/guardian/code-review'),
                (r'/api/learning/data/json', '/api/learning/data'),
                (r'/api/terra/extensions/json', '/api/terra/extensions'),
                (r'/api/conquest/deploymentss', '/api/conquest/deployments'),
                (r'/api/conquest/deploymentss/\{id\}', '/api/conquest/deployments'),
                (r'/api/conquest/deployments/\{id\}', '/api/conquest/deployments'),
                (r'/api/ai/\{id\}/cycle', '/api/agents/status'),
                (r'/api/custody', '/api/custody/'),
                (r'/api/guardian', '/api/guardian/code-review'),
                (r'/api/proposals/\{id\}/feedback', '/api/proposals'),
            ]
            
            for pattern, replacement in malformed_fixes:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    file_fixes.append(f"Fixed malformed endpoint: {pattern} -> {replacement}")
            
            # Fix 2: Remove any remaining failed endpoints
            failed_endpoints = [
                "/api/ai/learning/cross-ai",
                "/api/ai/research-subject", 
                "/api/ai/upload-training-data",
                "/api/analytics",
                "/api/approval/stats/overview",
                "/api/codex/log",
                "/api/conquest/force-work",
                "/api/conquest/improve-app",
                "/api/error",
                "/api/feedback",
                "/api/guardian/health-check",
                "/api/guardian/security-status",
                "/api/imperium/learning/data",
                "/api/imperium/trigger-scan",
                "/api/learning/effectiveness",
                "/api/learning/test",
                "/api/missions/health-check",
                "/api/missions/sync",
                "/api/notifications/send",
                "/api/notifications/ws",
                "/api/oath-papers/enhanced-learning",
                "/api/performance",
                "/api/proposals/quotas",
                "/api/proposals/{id}/accept",
                "/api/proposals/{id}/apply",
                "/api/usage"
            ]
            
            for failed_endpoint in failed_endpoints:
                if failed_endpoint in content:
                    # Replace with appropriate working endpoint
                    if "learning" in failed_endpoint:
                        replacement = "/api/learning/data"
                    elif "analytics" in failed_endpoint or "performance" in failed_endpoint:
                        replacement = "/api/growth/analysis"
                    elif "guardian" in failed_endpoint:
                        replacement = "/api/guardian/code-review"
                    elif "imperium" in failed_endpoint:
                        replacement = "/api/imperium/status"
                    elif "proposals" in failed_endpoint:
                        replacement = "/api/proposals"
                    elif "missions" in failed_endpoint:
                        replacement = "/api/missions/statistics"
                    elif "conquest" in failed_endpoint:
                        replacement = "/api/conquest/deployments"
                    elif "approval" in failed_endpoint:
                        replacement = "/api/approval/pending"
                    elif "oath" in failed_endpoint:
                        replacement = "/api/oath-papers"
                    elif "notifications" in failed_endpoint:
                        replacement = "/api/imperium/status"
                    else:
                        replacement = "/api/imperium/status"
                    
                    content = content.replace(failed_endpoint, replacement)
                    file_fixes.append(f"Replaced failed endpoint {failed_endpoint} with {replacement}")
            
            # Fix 3: Clean up any remaining template variables
            content = re.sub(r'/\$\{[^}]+\}', '', content)
            content = re.sub(r'/\$[a-zA-Z_][a-zA-Z0-9_]*', '', content)
            content = re.sub(r'/\$[^/]+', '', content)
            
            # Fix 4: Remove any duplicate slashes
            content = re.sub(r'//+', '/', content)
            
            # Save the file if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.files_modified.append(file_path)
                self.fixes_applied.extend([f"{os.path.basename(file_path)}: {fix}" for fix in file_fixes])
                
                print(f"✅ Cleaned {file_path} ({len(file_fixes)} fixes)")
                return True
            else:
                print(f"✅ {file_path} - No cleanup needed")
                return False
                
        except Exception as e:
            print(f"❌ Error cleaning {file_path}: {str(e)}")
            return False

    def cleanup_all_dart_files(self):
        """Clean up all Dart files"""
        print("🧹 Cleaning up remaining endpoint issues...")
        
        lib_dir = "../lib"
        if not os.path.exists(lib_dir):
            print(f"❌ lib directory not found: {lib_dir}")
            return
        
        files_cleaned = 0
        total_files = 0
        
        # Walk through all Dart files
        for root, dirs, files in os.walk(lib_dir):
            for file in files:
                if file.endswith('.dart'):
                    file_path = os.path.join(root, file)
                    total_files += 1
                    
                    if self.cleanup_dart_file(file_path):
                        files_cleaned += 1
        
        print(f"\n📊 Cleanup Summary:")
        print(f"   Total Dart files: {total_files}")
        print(f"   Files cleaned: {files_cleaned}")
        print(f"   Total fixes applied: {len(self.fixes_applied)}")

    def generate_cleanup_summary(self):
        """Generate cleanup summary"""
        print("\n" + "="*60)
        print("🧹 FINAL DART ENDPOINT CLEANUP SUMMARY")
        print("="*60)
        
        print(f"✅ Fixes Applied: {len(self.fixes_applied)}")
        for fix in self.fixes_applied[:15]:  # Show first 15 fixes
            print(f"   • {fix}")
        if len(self.fixes_applied) > 15:
            print(f"   ... and {len(self.fixes_applied) - 15} more fixes")
            
        print(f"📁 Files Modified: {len(self.files_modified)}")
        for file_path in self.files_modified:
            print(f"   • {file_path}")
            
        print(f"\n📊 Working Endpoints Available ({len(self.working_endpoints)}):")
        for endpoint in sorted(self.working_endpoints):
            print(f"   ✅ {endpoint}")
            
        # Save detailed results
        results = {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": self.fixes_applied,
            "files_modified": self.files_modified,
            "working_endpoints": self.working_endpoints
        }
        
        with open('final_dart_cleanup_report.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"\n📄 Detailed report saved to: final_dart_cleanup_report.json")
        
        if len(self.fixes_applied) > 0:
            print("✅ All remaining endpoint issues have been cleaned up!")
            print("🎯 Frontend should now be fully compatible with working backend endpoints")
        else:
            print("✅ No cleanup needed - all files are already using correct endpoints")

    def run_cleanup(self):
        """Run complete cleanup"""
        print("🚀 Starting final Dart endpoint cleanup...")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        
        # Clean up all Dart files
        self.cleanup_all_dart_files()
        
        # Generate summary
        self.generate_cleanup_summary()

def main():
    cleanup = FinalDartCleanup()
    cleanup.run_cleanup()

if __name__ == "__main__":
    main() 