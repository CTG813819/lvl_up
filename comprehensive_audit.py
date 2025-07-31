#!/usr/bin/env python3
"""
Comprehensive Audit Script
Checks for mock/stub data and ensures live data usage across all AI services
"""

import os
import subprocess
import sys
import re
import json
from datetime import datetime

def run_ssh_command(command):
    """Run SSH command on EC2 instance"""
    try:
        ssh_cmd = [
            "ssh", "-i", "New.pem", 
            "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com",
            command
        ]
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def audit_mock_data():
    """Audit for mock/stub data in the codebase"""
    print("🔍 AUDITING FOR MOCK/STUB DATA")
    print("=" * 60)
    
    # Check for mock data patterns in key files
    mock_patterns = [
        r'mock_',
        r'_mock',
        r'stub_',
        r'_stub',
        r'fake_',
        r'_fake',
        r'test_',
        r'_test',
        r'simulate',
        r'simulation',
        r'placeholder',
        r'# TODO:',
        r'# FIXME:',
        r'NotImplementedError',
        r'raise NotImplementedError',
        r'return \{\}',  # Empty dict returns
        r'return \[\]',  # Empty list returns
        r'return None',  # None returns
        r'return ""',    # Empty string returns
        r'return 0',     # Zero returns
        r'return False', # False returns
    ]
    
    # Files to audit
    audit_files = [
        "app/services/imperium_ai_service.py",
        "app/services/imperium_learning_controller.py", 
        "app/services/ai_learning_service.py",
        "app/services/testing_service.py",
        "app/services/ai_agent_service.py",
        "app/services/guardian_ai_service.py",
        "app/services/sandbox_ai_service.py",
        "app/services/conquest_ai_service.py",
        "app/routers/imperium_learning.py",
        "app/routers/proposals.py"
    ]
    
    mock_findings = []
    
    for file_path in audit_files:
        print(f"\n📄 Checking {file_path}...")
        
        # Read file content
        success, output, error = run_ssh_command(f"cd /home/ubuntu/ai-backend-python && cat {file_path}")
        
        if not success:
            print(f"❌ Could not read {file_path}: {error}")
            continue
        
        file_content = output
        file_issues = []
        
        # Check for mock patterns
        for pattern in mock_patterns:
            matches = re.finditer(pattern, file_content, re.IGNORECASE)
            for match in matches:
                line_num = file_content[:match.start()].count('\n') + 1
                line_content = file_content.split('\n')[line_num - 1].strip()
                file_issues.append({
                    'pattern': pattern,
                    'line': line_num,
                    'content': line_content[:100] + '...' if len(line_content) > 100 else line_content
                })
        
        if file_issues:
            mock_findings.append({
                'file': file_path,
                'issues': file_issues
            })
            print(f"⚠️  Found {len(file_issues)} potential mock/stub issues")
        else:
            print(f"✅ No mock/stub issues found")
    
    return mock_findings

def audit_live_data_usage():
    """Audit for live data usage patterns"""
    print("\n🔍 AUDITING LIVE DATA USAGE")
    print("=" * 60)
    
    # Check for live data patterns
    live_patterns = [
        r'async def.*get.*',
        r'async def.*fetch.*',
        r'async def.*load.*',
        r'async def.*retrieve.*',
        r'await.*get.*',
        r'await.*fetch.*',
        r'await.*load.*',
        r'await.*retrieve.*',
        r'requests\.get',
        r'aiohttp\.ClientSession',
        r'get_session\(\)',
        r'select.*from',
        r'insert.*into',
        r'update.*set',
        r'delete.*from'
    ]
    
    # Check specific live data endpoints
    live_endpoints = [
        "app/services/github_service.py",
        "app/services/ai_learning_service.py",
        "app/routers/imperium_learning.py"
    ]
    
    live_findings = []
    
    for file_path in live_endpoints:
        print(f"\n📄 Checking live data in {file_path}...")
        
        success, output, error = run_ssh_command(f"cd /home/ubuntu/ai-backend-python && cat {file_path}")
        
        if not success:
            print(f"❌ Could not read {file_path}: {error}")
            continue
        
        file_content = output
        live_usage = []
        
        # Check for live data patterns
        for pattern in live_patterns:
            matches = re.finditer(pattern, file_content, re.IGNORECASE)
            for match in matches:
                line_num = file_content[:match.start()].count('\n') + 1
                line_content = file_content.split('\n')[line_num - 1].strip()
                live_usage.append({
                    'pattern': pattern,
                    'line': line_num,
                    'content': line_content[:100] + '...' if len(line_content) > 100 else line_content
                })
        
        if live_usage:
            live_findings.append({
                'file': file_path,
                'usage': live_usage
            })
            print(f"✅ Found {len(live_usage)} live data usage patterns")
        else:
            print(f"⚠️  No live data usage patterns found")
    
    return live_findings

def audit_imperium_service():
    """Specific audit of Imperium AI service"""
    print("\n🔍 AUDITING IMPERIUM AI SERVICE")
    print("=" * 60)
    
    imperium_audit = {
        'ml_models': False,
        'live_learning': False,
        'real_optimizations': False,
        'live_testing': False,
        'github_integration': False
    }
    
    # Check Imperium service
    success, output, error = run_ssh_command("cd /home/ubuntu/ai-backend-python && cat app/services/imperium_ai_service.py")
    
    if success:
        content = output
        
        # Check for ML models
        if 'RandomForestRegressor' in content or 'GradientBoostingRegressor' in content:
            imperium_audit['ml_models'] = True
            print("✅ ML models found")
        
        # Check for live learning
        if 'async def.*learn' in content or 'await.*learn' in content:
            imperium_audit['live_learning'] = True
            print("✅ Live learning methods found")
        
        # Check for real optimizations
        if 'optimize_code' in content or 'optimization' in content:
            imperium_audit['real_optimizations'] = True
            print("✅ Real optimization methods found")
        
        # Check for live testing
        if 'test_proposal' in content or 'testing_service' in content:
            imperium_audit['live_testing'] = True
            print("✅ Live testing integration found")
        
        # Check for GitHub integration
        if 'github_service' in content or 'get_repo_content' in content:
            imperium_audit['github_integration'] = True
            print("✅ GitHub integration found")
    
    return imperium_audit

def audit_database_usage():
    """Audit database usage for live data"""
    print("\n🔍 AUDITING DATABASE USAGE")
    print("=" * 60)
    
    # Check database connection and tables
    db_checks = {
        'connection': False,
        'tables': False,
        'live_queries': False,
        'proposals': False,
        'learning_data': False
    }
    
    # Test database connection
    success, output, error = run_ssh_command("cd /home/ubuntu/ai-backend-python && python3 -c \"from app.core.database import get_session; import asyncio; async def test(): async with get_session() as session: print('Database connection OK'); asyncio.run(test())\"")
    
    if success and 'Database connection OK' in output:
        db_checks['connection'] = True
        print("✅ Database connection working")
    
    # Check for database tables
    success, output, error = run_ssh_command("cd /home/ubuntu/ai-backend-python && psql 'postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require' -c '\\dt'")
    
    if success:
        db_checks['tables'] = True
        print("✅ Database tables accessible")
        print(f"Tables found: {output}")
    
    # Check for live queries in code
    success, output, error = run_ssh_command("cd /home/ubuntu/ai-backend-python && grep -r 'select.*from' app/ --include='*.py' | head -5")
    
    if success and output.strip():
        db_checks['live_queries'] = True
        print("✅ Live database queries found")
    
    return db_checks

def audit_current_logs():
    """Audit current system logs for live data usage"""
    print("\n🔍 AUDITING CURRENT SYSTEM LOGS")
    print("=" * 60)
    
    # Get recent logs
    success, output, error = run_ssh_command("sudo journalctl -u ai-backend-python --no-pager -n 50")
    
    if success:
        logs = output
        
        # Check for live data indicators
        live_indicators = {
            'database_queries': 'Database health check passed' in logs,
            'github_access': 'GitHub service initialized' in logs,
            'ai_learning': 'Learning insights' in logs,
            'proposal_generation': 'Generating proposal' in logs,
            'live_testing': 'Running LIVE testing' in logs,
            'ml_models': 'ML models' in logs,
            'real_errors': 'Failed to get repo content' in logs or 'Database session error' in logs
        }
        
        for indicator, found in live_indicators.items():
            status = "✅" if found else "❌"
            print(f"{status} {indicator}: {'Found' if found else 'Not found'}")
        
        return live_indicators
    
    return {}

def audit_github_integration():
    """Audit GitHub integration for live data"""
    print("\n🔍 AUDITING GITHUB INTEGRATION")
    print("=" * 60)
    
    # Test GitHub API access
    test_script = '''
import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def test_github():
    token = os.getenv('GITHUB_TOKEN')
    repo = os.getenv('GITHUB_REPO')
    
    if not token or not repo:
        print("❌ GitHub configuration missing")
        return False
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test repository access
            url = f"https://api.github.com/repos/{repo}"
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Repository access: {data.get('name', 'Unknown')}")
                    
                    # Test content access
                    content_url = f"https://api.github.com/repos/{repo}/contents"
                    async with session.get(content_url, headers=headers) as content_response:
                        if content_response.status == 200:
                            contents = await content_response.json()
                            print(f"✅ Content access: {len(contents)} items")
                            return True
                        else:
                            print(f"❌ Content access failed: {content_response.status}")
                            return False
                else:
                    print(f"❌ Repository access failed: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ GitHub test error: {e}")
        return False

asyncio.run(test_github())
'''
    
    success, output, error = run_ssh_command(f"cd /home/ubuntu/ai-backend-python && cat > test_github_live.py << 'EOF'\n{test_script}\nEOF")
    
    if success:
        success, output, error = run_ssh_command("cd /home/ubuntu/ai-backend-python && python3 test_github_live.py")
        if success:
            print(output)
            return 'GitHub integration working' in output
        else:
            print(f"❌ GitHub test failed: {error}")
            return False
    
    return False

def generate_audit_report(mock_findings, live_findings, imperium_audit, db_checks, log_indicators, github_working):
    """Generate comprehensive audit report"""
    print("\n📊 COMPREHENSIVE AUDIT REPORT")
    print("=" * 60)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'mock_data_found': len(mock_findings) > 0,
        'live_data_usage': len(live_findings) > 0,
        'imperium_service_status': imperium_audit,
        'database_status': db_checks,
        'log_indicators': log_indicators,
        'github_integration': github_working,
        'recommendations': []
    }
    
    # Mock data analysis
    if mock_findings:
        print("⚠️  MOCK/STUB DATA FOUND:")
        for finding in mock_findings:
            print(f"   📄 {finding['file']}: {len(finding['issues'])} issues")
            for issue in finding['issues'][:3]:  # Show first 3 issues
                print(f"      Line {issue['line']}: {issue['content']}")
        report['recommendations'].append("Remove mock/stub data implementations")
    else:
        print("✅ No mock/stub data found")
    
    # Live data analysis
    if live_findings:
        print("\n✅ LIVE DATA USAGE FOUND:")
        for finding in live_findings:
            print(f"   📄 {finding['file']}: {len(finding['usage'])} live patterns")
    else:
        print("\n⚠️  Limited live data usage found")
        report['recommendations'].append("Implement more live data fetching")
    
    # Imperium service analysis
    print(f"\n🤖 IMPERIUM SERVICE STATUS:")
    for feature, status in imperium_audit.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {feature}: {'Working' if status else 'Not working'}")
    
    # Database analysis
    print(f"\n🗄️  DATABASE STATUS:")
    for check, status in db_checks.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {check}: {'Working' if status else 'Not working'}")
    
    # Log analysis
    print(f"\n📋 LOG INDICATORS:")
    for indicator, status in log_indicators.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {indicator}: {'Found' if status else 'Not found'}")
    
    # GitHub analysis
    print(f"\n🔗 GITHUB INTEGRATION:")
    icon = "✅" if github_working else "❌"
    print(f"   {icon} GitHub integration: {'Working' if github_working else 'Not working'}")
    
    # Overall assessment
    print(f"\n🎯 OVERALL ASSESSMENT:")
    
    live_data_score = sum([
        len(live_findings) > 0,
        sum(imperium_audit.values()) >= 3,
        sum(db_checks.values()) >= 3,
        sum(log_indicators.values()) >= 4,
        github_working
    ]) / 5 * 100
    
    mock_data_score = 100 if len(mock_findings) == 0 else max(0, 100 - len(mock_findings) * 10)
    
    overall_score = (live_data_score + mock_data_score) / 2
    
    print(f"   Live Data Usage: {live_data_score:.1f}%")
    print(f"   Mock Data Clean: {mock_data_score:.1f}%")
    print(f"   Overall Score: {overall_score:.1f}%")
    
    if overall_score >= 80:
        print("   🎉 System is using live data effectively!")
    elif overall_score >= 60:
        print("   ⚠️  System has some live data but needs improvement")
    else:
        print("   ❌ System needs significant work to use live data")
    
    # Recommendations
    if report['recommendations']:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"   • {rec}")
    
    return report

def main():
    """Run comprehensive audit"""
    print("🔍 COMPREHENSIVE AI SYSTEM AUDIT")
    print("Checking for mock/stub data and live data usage")
    print("=" * 60)
    
    # Run all audits
    mock_findings = audit_mock_data()
    live_findings = audit_live_data_usage()
    imperium_audit = audit_imperium_service()
    db_checks = audit_database_usage()
    log_indicators = audit_current_logs()
    github_working = audit_github_integration()
    
    # Generate report
    report = generate_audit_report(
        mock_findings, live_findings, imperium_audit, 
        db_checks, log_indicators, github_working
    )
    
    # Save report
    report_json = json.dumps(report, indent=2)
    success, output, error = run_ssh_command(f"cd /home/ubuntu/ai-backend-python && echo '{report_json}' > audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    if success:
        print(f"\n📄 Audit report saved to EC2 instance")
    
    print(f"\n🎯 AUDIT COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main() 