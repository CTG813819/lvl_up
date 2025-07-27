#!/usr/bin/env python3
"""
Comprehensive System Audit Script for LVL_UP AI Backend
This script performs a full audit of all AI systems, schedules, tasks, and implementations.
"""

import os
import sys
import json
import time
import requests
import subprocess
import psycopg2
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_audit.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SystemAuditor:
    def __init__(self):
        self.audit_results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'PENDING',
            'checks': {},
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        self.base_url = "http://localhost:8000"
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'lvl_up'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }

    def run_comprehensive_audit(self):
        """Run all audit checks"""
        logger.info("Starting comprehensive system audit...")
        
        try:
            # System Health Checks
            self.check_system_health()
            
            # Database Checks
            self.check_database_connectivity()
            self.check_database_schema()
            self.check_database_performance()
            
            # Service Checks
            self.check_backend_services()
            self.check_ai_services()
            self.check_guardian_services()
            self.check_imperium_services()
            
            # API Endpoint Checks
            self.check_api_endpoints()
            self.check_websocket_connections()
            
            # Schedule and Task Checks
            self.check_scheduled_tasks()
            self.check_ai_learning_systems()
            self.check_autonomous_agents()
            
            # Performance and Resource Checks
            self.check_system_resources()
            self.check_token_usage()
            self.check_error_logs()
            
            # Security Checks
            self.check_security_configuration()
            
            # Generate final report
            self.generate_audit_report()
            
        except Exception as e:
            logger.error(f"Critical error during audit: {str(e)}")
            self.audit_results['errors'].append(f"Critical audit error: {str(e)}")
            self.audit_results['overall_status'] = 'FAILED'

    def check_system_health(self):
        """Check basic system health"""
        logger.info("Checking system health...")
        check_name = "system_health"
        
        try:
            # Check if backend is running
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                self.audit_results['checks'][check_name] = {
                    'status': 'PASS',
                    'details': 'Backend service is running and healthy'
                }
            else:
                self.audit_results['checks'][check_name] = {
                    'status': 'FAIL',
                    'details': f'Backend health check failed with status {response.status_code}'
                }
                self.audit_results['errors'].append(f"Backend health check failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'Cannot connect to backend: {str(e)}'
            }
            self.audit_results['errors'].append(f"Backend connection failed: {str(e)}")

    def check_database_connectivity(self):
        """Check database connectivity and basic operations"""
        logger.info("Checking database connectivity...")
        check_name = "database_connectivity"
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            # Check if key tables exist
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('proposals', 'agents', 'ai_learning_summaries', 'guardian_suggestions')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            self.audit_results['checks'][check_name] = {
                'status': 'PASS',
                'details': f'Database connected successfully. PostgreSQL version: {version[0]}. Found tables: {tables}'
            }
            
        except Exception as e:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'Database connection failed: {str(e)}'
            }
            self.audit_results['errors'].append(f"Database connection failed: {str(e)}")

    def check_database_schema(self):
        """Check database schema integrity"""
        logger.info("Checking database schema...")
        check_name = "database_schema"
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check key table structures
            schema_checks = {}
            
            # Check proposals table
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'proposals' 
                ORDER BY ordinal_position
            """)
            proposals_columns = cursor.fetchall()
            schema_checks['proposals'] = proposals_columns
            
            # Check agents table
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'agents' 
                ORDER BY ordinal_position
            """)
            agents_columns = cursor.fetchall()
            schema_checks['agents'] = agents_columns
            
            # Check for required columns
            required_columns = {
                'proposals': ['id', 'title', 'description', 'status', 'created_at'],
                'agents': ['id', 'name', 'type', 'status', 'created_at']
            }
            
            missing_columns = []
            for table, columns in required_columns.items():
                existing_columns = [col[0] for col in schema_checks.get(table, [])]
                for required_col in columns:
                    if required_col not in existing_columns:
                        missing_columns.append(f"{table}.{required_col}")
            
            cursor.close()
            conn.close()
            
            if missing_columns:
                self.audit_results['checks'][check_name] = {
                    'status': 'FAIL',
                    'details': f'Missing required columns: {missing_columns}'
                }
                self.audit_results['errors'].append(f"Missing database columns: {missing_columns}")
            else:
                self.audit_results['checks'][check_name] = {
                    'status': 'PASS',
                    'details': 'Database schema is valid with all required columns'
                }
                
        except Exception as e:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'Schema check failed: {str(e)}'
            }
            self.audit_results['errors'].append(f"Schema check failed: {str(e)}")

    def check_database_performance(self):
        """Check database performance metrics"""
        logger.info("Checking database performance...")
        check_name = "database_performance"
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check table sizes
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE schemaname = 'public' 
                AND tablename IN ('proposals', 'agents', 'ai_learning_summaries')
                ORDER BY tablename, attname
            """)
            stats = cursor.fetchall()
            
            # Check for slow queries
            cursor.execute("""
                SELECT query, calls, total_time, mean_time
                FROM pg_stat_statements 
                WHERE mean_time > 1000
                ORDER BY mean_time DESC 
                LIMIT 5
            """)
            slow_queries = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            performance_issues = []
            if slow_queries:
                performance_issues.append(f"Found {len(slow_queries)} slow queries")
            
            if performance_issues:
                self.audit_results['checks'][check_name] = {
                    'status': 'WARNING',
                    'details': f'Performance issues detected: {performance_issues}'
                }
                self.audit_results['warnings'].extend(performance_issues)
            else:
                self.audit_results['checks'][check_name] = {
                    'status': 'PASS',
                    'details': 'Database performance is acceptable'
                }
                
        except Exception as e:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'Performance check failed: {str(e)}'
            }
            self.audit_results['errors'].append(f"Performance check failed: {str(e)}")

    def check_backend_services(self):
        """Check if all backend services are running"""
        logger.info("Checking backend services...")
        check_name = "backend_services"
        
        try:
            # Check if main backend process is running
            result = subprocess.run(['pgrep', '-f', 'uvicorn'], capture_output=True, text=True)
            
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                self.audit_results['checks'][check_name] = {
                    'status': 'PASS',
                    'details': f'Backend service is running with PIDs: {pids}'
                }
            else:
                self.audit_results['checks'][check_name] = {
                    'status': 'FAIL',
                    'details': 'Backend service is not running'
                }
                self.audit_results['errors'].append("Backend service is not running")
                
        except Exception as e:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'Service check failed: {str(e)}'
            }
            self.audit_results['errors'].append(f"Service check failed: {str(e)}")

    def check_ai_services(self):
        """Check AI-specific services and endpoints"""
        logger.info("Checking AI services...")
        check_name = "ai_services"
        
        ai_endpoints = [
            "/ai/agents",
            "/ai/learning",
            "/ai/growth",
            "/ai/proposals",
            "/ai/analytics"
        ]
        
        failed_endpoints = []
        working_endpoints = []
        
        for endpoint in ai_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code in [200, 401, 403]:  # Accept auth errors as "working"
                    working_endpoints.append(endpoint)
                else:
                    failed_endpoints.append(f"{endpoint} (status: {response.status_code})")
            except Exception as e:
                failed_endpoints.append(f"{endpoint} (error: {str(e)})")
        
        if failed_endpoints:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'Failed endpoints: {failed_endpoints}. Working: {working_endpoints}'
            }
            self.audit_results['errors'].append(f"AI service endpoints failed: {failed_endpoints}")
        else:
            self.audit_results['checks'][check_name] = {
                'status': 'PASS',
                'details': f'All AI endpoints working: {working_endpoints}'
            }

    def check_guardian_services(self):
        """Check Guardian AI services"""
        logger.info("Checking Guardian services...")
        check_name = "guardian_services"
        
        guardian_endpoints = [
            "/guardian/status",
            "/guardian/suggestions",
            "/guardian/analytics"
        ]
        
        failed_endpoints = []
        working_endpoints = []
        
        for endpoint in guardian_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code in [200, 401, 403]:
                    working_endpoints.append(endpoint)
                else:
                    failed_endpoints.append(f"{endpoint} (status: {response.status_code})")
            except Exception as e:
                failed_endpoints.append(f"{endpoint} (error: {str(e)})")
        
        if failed_endpoints:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'Failed Guardian endpoints: {failed_endpoints}. Working: {working_endpoints}'
            }
            self.audit_results['errors'].append(f"Guardian endpoints failed: {failed_endpoints}")
        else:
            self.audit_results['checks'][check_name] = {
                'status': 'PASS',
                'details': f'All Guardian endpoints working: {working_endpoints}'
            }

    def check_imperium_services(self):
        """Check Imperium monitoring services"""
        logger.info("Checking Imperium services...")
        check_name = "imperium_services"
        
        try:
            # Check if Imperium service is running
            result = subprocess.run(['pgrep', '-f', 'imperium'], capture_output=True, text=True)
            
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                self.audit_results['checks'][check_name] = {
                    'status': 'PASS',
                    'details': f'Imperium service is running with PIDs: {pids}'
                }
            else:
                self.audit_results['checks'][check_name] = {
                    'status': 'WARNING',
                    'details': 'Imperium service is not running'
                }
                self.audit_results['warnings'].append("Imperium service is not running")
                
        except Exception as e:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'Imperium check failed: {str(e)}'
            }
            self.audit_results['errors'].append(f"Imperium check failed: {str(e)}")

    def check_api_endpoints(self):
        """Check all API endpoints"""
        logger.info("Checking API endpoints...")
        check_name = "api_endpoints"
        
        critical_endpoints = [
            "/",
            "/docs",
            "/health",
            "/api/v1/status"
        ]
        
        failed_endpoints = []
        working_endpoints = []
        
        for endpoint in critical_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code in [200, 401, 403]:
                    working_endpoints.append(endpoint)
                else:
                    failed_endpoints.append(f"{endpoint} (status: {response.status_code})")
            except Exception as e:
                failed_endpoints.append(f"{endpoint} (error: {str(e)})")
        
        if failed_endpoints:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'Failed critical endpoints: {failed_endpoints}. Working: {working_endpoints}'
            }
            self.audit_results['errors'].append(f"Critical endpoints failed: {failed_endpoints}")
        else:
            self.audit_results['checks'][check_name] = {
                'status': 'PASS',
                'details': f'All critical endpoints working: {working_endpoints}'
            }

    def check_websocket_connections(self):
        """Check WebSocket connectivity"""
        logger.info("Checking WebSocket connections...")
        check_name = "websocket_connections"
        
        try:
            import websocket
            ws = websocket.create_connection(f"ws://localhost:8000/ws", timeout=5)
            ws.close()
            
            self.audit_results['checks'][check_name] = {
                'status': 'PASS',
                'details': 'WebSocket connection successful'
            }
            
        except ImportError:
            self.audit_results['checks'][check_name] = {
                'status': 'WARNING',
                'details': 'WebSocket library not available for testing'
            }
            self.audit_results['warnings'].append("WebSocket library not available")
        except Exception as e:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'WebSocket connection failed: {str(e)}'
            }
            self.audit_results['errors'].append(f"WebSocket connection failed: {str(e)}")

    def check_scheduled_tasks(self):
        """Check scheduled tasks and cron jobs"""
        logger.info("Checking scheduled tasks...")
        check_name = "scheduled_tasks"
        
        try:
            # Check if cron is running
            result = subprocess.run(['pgrep', 'cron'], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Check for AI-related cron jobs
                result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
                if result.returncode == 0:
                    cron_jobs = result.stdout
                    ai_jobs = [line for line in cron_jobs.split('\n') if 'ai' in line.lower() or 'guardian' in line.lower()]
                    
                    if ai_jobs:
                        self.audit_results['checks'][check_name] = {
                            'status': 'PASS',
                            'details': f'Found {len(ai_jobs)} AI-related scheduled tasks'
                        }
                    else:
                        self.audit_results['checks'][check_name] = {
                            'status': 'WARNING',
                            'details': 'No AI-related scheduled tasks found'
                        }
                        self.audit_results['warnings'].append("No AI scheduled tasks found")
                else:
                    self.audit_results['checks'][check_name] = {
                        'status': 'WARNING',
                        'details': 'Cannot read crontab'
                    }
                    self.audit_results['warnings'].append("Cannot read crontab")
            else:
                self.audit_results['checks'][check_name] = {
                    'status': 'FAIL',
                    'details': 'Cron service is not running'
                }
                self.audit_results['errors'].append("Cron service is not running")
                
        except Exception as e:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'Scheduled task check failed: {str(e)}'
            }
            self.audit_results['errors'].append(f"Scheduled task check failed: {str(e)}")

    def check_ai_learning_systems(self):
        """Check AI learning and growth systems"""
        logger.info("Checking AI learning systems...")
        check_name = "ai_learning_systems"
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check for recent learning activities
            cursor.execute("""
                SELECT COUNT(*) FROM ai_learning_summaries 
                WHERE created_at > NOW() - INTERVAL '24 hours'
            """)
            recent_learning = cursor.fetchone()[0]
            
            # Check for active learning proposals
            cursor.execute("""
                SELECT COUNT(*) FROM proposals 
                WHERE status = 'learning' AND created_at > NOW() - INTERVAL '7 days'
            """)
            active_learning = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            if recent_learning > 0 or active_learning > 0:
                self.audit_results['checks'][check_name] = {
                    'status': 'PASS',
                    'details': f'AI learning active: {recent_learning} recent summaries, {active_learning} active learning proposals'
                }
            else:
                self.audit_results['checks'][check_name] = {
                    'status': 'WARNING',
                    'details': 'No recent AI learning activity detected'
                }
                self.audit_results['warnings'].append("No recent AI learning activity")
                
        except Exception as e:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'AI learning check failed: {str(e)}'
            }
            self.audit_results['errors'].append(f"AI learning check failed: {str(e)}")

    def check_autonomous_agents(self):
        """Check autonomous AI agents"""
        logger.info("Checking autonomous agents...")
        check_name = "autonomous_agents"
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check for active agents
            cursor.execute("""
                SELECT type, COUNT(*) FROM agents 
                WHERE status = 'active' 
                GROUP BY type
            """)
            active_agents = cursor.fetchall()
            
            # Check for recent agent activities
            cursor.execute("""
                SELECT COUNT(*) FROM proposals 
                WHERE created_at > NOW() - INTERVAL '24 hours' 
                AND created_by LIKE '%agent%'
            """)
            recent_agent_activity = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            if active_agents:
                agent_summary = ", ".join([f"{agent_type}: {count}" for agent_type, count in active_agents])
                self.audit_results['checks'][check_name] = {
                    'status': 'PASS',
                    'details': f'Active agents: {agent_summary}. Recent activity: {recent_agent_activity} proposals'
                }
            else:
                self.audit_results['checks'][check_name] = {
                    'status': 'WARNING',
                    'details': 'No active autonomous agents found'
                }
                self.audit_results['warnings'].append("No active autonomous agents")
                
        except Exception as e:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'Autonomous agents check failed: {str(e)}'
            }
            self.audit_results['errors'].append(f"Autonomous agents check failed: {str(e)}")

    def check_system_resources(self):
        """Check system resources and performance"""
        logger.info("Checking system resources...")
        check_name = "system_resources"
        
        try:
            # Check CPU usage
            result = subprocess.run(['top', '-bn1'], capture_output=True, text=True)
            cpu_line = [line for line in result.stdout.split('\n') if 'Cpu(s)' in line]
            
            # Check memory usage
            result = subprocess.run(['free', '-h'], capture_output=True, text=True)
            memory_info = result.stdout
            
            # Check disk usage
            result = subprocess.run(['df', '-h'], capture_output=True, text=True)
            disk_info = result.stdout
            
            # Check if any resource is critically low
            warnings = []
            
            # Parse disk usage for critical thresholds
            disk_lines = disk_info.split('\n')[1:]  # Skip header
            for line in disk_lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 5:
                        usage = parts[4].replace('%', '')
                        if usage.isdigit() and int(usage) > 90:
                            warnings.append(f"Disk usage critical: {parts[5]} at {parts[4]}")
            
            if warnings:
                self.audit_results['checks'][check_name] = {
                    'status': 'WARNING',
                    'details': f'Resource warnings: {warnings}'
                }
                self.audit_results['warnings'].extend(warnings)
            else:
                self.audit_results['checks'][check_name] = {
                    'status': 'PASS',
                    'details': 'System resources are within acceptable limits'
                }
                
        except Exception as e:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'Resource check failed: {str(e)}'
            }
            self.audit_results['errors'].append(f"Resource check failed: {str(e)}")

    def check_token_usage(self):
        """Check AI token usage and limits"""
        logger.info("Checking token usage...")
        check_name = "token_usage"
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check recent token usage
            cursor.execute("""
                SELECT SUM(tokens_used) FROM token_usage 
                WHERE created_at > NOW() - INTERVAL '24 hours'
            """)
            daily_usage = cursor.fetchone()[0] or 0
            
            # Check monthly usage
            cursor.execute("""
                SELECT SUM(tokens_used) FROM token_usage 
                WHERE created_at > NOW() - INTERVAL '30 days'
            """)
            monthly_usage = cursor.fetchone()[0] or 0
            
            cursor.close()
            conn.close()
            
            # Define thresholds (adjust as needed)
            daily_limit = 100000
            monthly_limit = 2000000
            
            warnings = []
            if daily_usage > daily_limit:
                warnings.append(f"Daily token usage ({daily_usage}) exceeds limit ({daily_limit})")
            if monthly_usage > monthly_limit:
                warnings.append(f"Monthly token usage ({monthly_usage}) exceeds limit ({monthly_limit})")
            
            if warnings:
                self.audit_results['checks'][check_name] = {
                    'status': 'WARNING',
                    'details': f'Token usage warnings: {warnings}. Daily: {daily_usage}, Monthly: {monthly_usage}'
                }
                self.audit_results['warnings'].extend(warnings)
            else:
                self.audit_results['checks'][check_name] = {
                    'status': 'PASS',
                    'details': f'Token usage within limits. Daily: {daily_usage}, Monthly: {monthly_usage}'
                }
                
        except Exception as e:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'Token usage check failed: {str(e)}'
            }
            self.audit_results['errors'].append(f"Token usage check failed: {str(e)}")

    def check_error_logs(self):
        """Check for recent errors in logs"""
        logger.info("Checking error logs...")
        check_name = "error_logs"
        
        try:
            # Check for recent errors in application logs
            log_files = [
                '/var/log/syslog',
                '/var/log/messages',
                'system_audit.log'
            ]
            
            recent_errors = []
            for log_file in log_files:
                if os.path.exists(log_file):
                    result = subprocess.run([
                        'grep', '-i', 'error', log_file
                    ], capture_output=True, text=True)
                    
                    if result.stdout:
                        error_lines = result.stdout.split('\n')[-10:]  # Last 10 errors
                        recent_errors.extend(error_lines)
            
            if recent_errors:
                self.audit_results['checks'][check_name] = {
                    'status': 'WARNING',
                    'details': f'Found {len(recent_errors)} recent errors in logs'
                }
                self.audit_results['warnings'].append(f"Recent errors found: {len(recent_errors)}")
            else:
                self.audit_results['checks'][check_name] = {
                    'status': 'PASS',
                    'details': 'No recent errors found in logs'
                }
                
        except Exception as e:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'Error log check failed: {str(e)}'
            }
            self.audit_results['errors'].append(f"Error log check failed: {str(e)}")

    def check_security_configuration(self):
        """Check security configuration"""
        logger.info("Checking security configuration...")
        check_name = "security_configuration"
        
        try:
            # Check if environment variables are set
            required_env_vars = [
                'DB_PASSWORD',
                'OPENAI_API_KEY',
                'GITHUB_TOKEN'
            ]
            
            missing_vars = []
            for var in required_env_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            # Check file permissions
            critical_files = [
                '/etc/passwd',
                '/etc/shadow'
            ]
            
            permission_issues = []
            for file_path in critical_files:
                if os.path.exists(file_path):
                    stat = os.stat(file_path)
                    if stat.st_mode & 0o777 != 0o644:  # Should be 644
                        permission_issues.append(f"{file_path} has incorrect permissions")
            
            issues = []
            if missing_vars:
                issues.append(f"Missing environment variables: {missing_vars}")
            if permission_issues:
                issues.append(f"Permission issues: {permission_issues}")
            
            if issues:
                self.audit_results['checks'][check_name] = {
                    'status': 'WARNING',
                    'details': f'Security issues found: {issues}'
                }
                self.audit_results['warnings'].extend(issues)
            else:
                self.audit_results['checks'][check_name] = {
                    'status': 'PASS',
                    'details': 'Security configuration appears secure'
                }
                
        except Exception as e:
            self.audit_results['checks'][check_name] = {
                'status': 'FAIL',
                'details': f'Security check failed: {str(e)}'
            }
            self.audit_results['errors'].append(f"Security check failed: {str(e)}")

    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        logger.info("Generating audit report...")
        
        # Determine overall status
        failed_checks = [check for check, data in self.audit_results['checks'].items() 
                        if data['status'] == 'FAIL']
        warning_checks = [check for check, data in self.audit_results['checks'].items() 
                         if data['status'] == 'WARNING']
        
        if failed_checks:
            self.audit_results['overall_status'] = 'FAILED'
        elif warning_checks:
            self.audit_results['overall_status'] = 'WARNING'
        else:
            self.audit_results['overall_status'] = 'PASSED'
        
        # Generate recommendations
        if failed_checks:
            self.audit_results['recommendations'].append(
                f"Critical: Fix {len(failed_checks)} failed checks: {failed_checks}"
            )
        
        if warning_checks:
            self.audit_results['recommendations'].append(
                f"Review {len(warning_checks)} warning checks: {warning_checks}"
            )
        
        if not self.audit_results['errors'] and not self.audit_results['warnings']:
            self.audit_results['recommendations'].append(
                "System is healthy. Continue monitoring and maintenance."
            )
        
        # Save detailed report
        with open('comprehensive_audit_report.json', 'w') as f:
            json.dump(self.audit_results, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*80)
        print("COMPREHENSIVE SYSTEM AUDIT REPORT")
        print("="*80)
        print(f"Timestamp: {self.audit_results['timestamp']}")
        print(f"Overall Status: {self.audit_results['overall_status']}")
        print(f"Total Checks: {len(self.audit_results['checks'])}")
        print(f"Passed: {len([c for c, d in self.audit_results['checks'].items() if d['status'] == 'PASS'])}")
        print(f"Warnings: {len([c for c, d in self.audit_results['checks'].items() if d['status'] == 'WARNING'])}")
        print(f"Failed: {len([c for c, d in self.audit_results['checks'].items() if d['status'] == 'FAIL'])}")
        print(f"Errors: {len(self.audit_results['errors'])}")
        print(f"Warnings: {len(self.audit_results['warnings'])}")
        
        print("\nCHECK RESULTS:")
        print("-"*80)
        for check_name, check_data in self.audit_results['checks'].items():
            status_icon = {
                'PASS': '✅',
                'WARNING': '⚠️',
                'FAIL': '❌'
            }.get(check_data['status'], '❓')
            print(f"{status_icon} {check_name}: {check_data['status']}")
            print(f"   {check_data['details']}")
            print()
        
        if self.audit_results['errors']:
            print("ERRORS:")
            print("-"*80)
            for error in self.audit_results['errors']:
                print(f"❌ {error}")
            print()
        
        if self.audit_results['warnings']:
            print("WARNINGS:")
            print("-"*80)
            for warning in self.audit_results['warnings']:
                print(f"⚠️ {warning}")
            print()
        
        if self.audit_results['recommendations']:
            print("RECOMMENDATIONS:")
            print("-"*80)
            for rec in self.audit_results['recommendations']:
                print(f"💡 {rec}")
            print()
        
        print("="*80)
        print(f"Detailed report saved to: comprehensive_audit_report.json")
        print("="*80)

def main():
    """Main function to run the comprehensive audit"""
    print("Starting Comprehensive System Audit...")
    print("This may take several minutes to complete...")
    
    auditor = SystemAuditor()
    auditor.run_comprehensive_audit()
    
    print("\nAudit completed!")
    return auditor.audit_results['overall_status']

if __name__ == "__main__":
    try:
        status = main()
        sys.exit(0 if status in ['PASSED', 'WARNING'] else 1)
    except KeyboardInterrupt:
        print("\nAudit interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nCritical error: {str(e)}")
        traceback.print_exc()
        sys.exit(1) 