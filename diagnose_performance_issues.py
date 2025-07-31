#!/usr/bin/env python3
"""
Performance Diagnostic Script
Identifies current performance bottlenecks on EC2
"""

import asyncio
import os
import sys
import subprocess
import time
import psutil
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-backend-python/logs/performance_diagnosis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PerformanceDiagnostic:
    def __init__(self):
        self.base_path = "/home/ubuntu/ai-backend-python"
        self.logs_path = f"{self.base_path}/logs"
        
    async def run_comprehensive_diagnosis(self):
        """Run comprehensive performance diagnosis"""
        logger.info("Starting comprehensive performance diagnosis")
        
        try:
            # 1. System resource analysis
            await self.analyze_system_resources()
            
            # 2. Database performance analysis
            await self.analyze_database_performance()
            
            # 3. Application performance analysis
            await self.analyze_application_performance()
            
            # 4. Service status analysis
            await self.analyze_service_status()
            
            # 5. Network and connectivity analysis
            await self.analyze_network_performance()
            
            # 6. Generate performance report
            await self.generate_performance_report()
            
            logger.info("Performance diagnosis completed successfully")
            
        except Exception as e:
            logger.error(f"Performance diagnosis failed: {str(e)}")
            raise
    
    async def analyze_system_resources(self):
        """Analyze system resource usage"""
        logger.info("Analyzing system resources")
        
        try:
            # CPU analysis
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory analysis
            memory = psutil.virtual_memory()
            
            # Disk analysis
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network analysis
            network = psutil.net_io_counters()
            
            # Load average
            load_avg = os.getloadavg()
            
            logger.info(f"System Resources:")
            logger.info(f"  CPU: {cpu_percent}% usage, {cpu_count} cores, {cpu_freq.current:.1f}MHz")
            logger.info(f"  Memory: {memory.percent}% used, {memory.available / 1024 / 1024 / 1024:.1f}GB available")
            logger.info(f"  Disk: {disk.percent}% used, {disk.free / 1024 / 1024 / 1024:.1f}GB free")
            logger.info(f"  Load Average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
            
            # Check for resource bottlenecks
            bottlenecks = []
            if cpu_percent > 80:
                bottlenecks.append(f"High CPU usage: {cpu_percent}%")
            if memory.percent > 85:
                bottlenecks.append(f"High memory usage: {memory.percent}%")
            if disk.percent > 90:
                bottlenecks.append(f"High disk usage: {disk.percent}%")
            if load_avg[0] > cpu_count * 2:
                bottlenecks.append(f"High load average: {load_avg[0]:.2f}")
            
            if bottlenecks:
                logger.warning(f"Resource bottlenecks detected: {', '.join(bottlenecks)}")
            else:
                logger.info("No resource bottlenecks detected")
                
        except Exception as e:
            logger.error(f"System resource analysis failed: {str(e)}")
    
    async def analyze_database_performance(self):
        """Analyze database performance"""
        logger.info("Analyzing database performance")
        
        try:
            # Check PostgreSQL status
            result = subprocess.run(
                ["sudo", "systemctl", "status", "postgresql"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                logger.info("PostgreSQL is running")
                
                # Check PostgreSQL configuration
                pg_config_commands = [
                    "sudo -u postgres psql -c 'SHOW max_connections;'",
                    "sudo -u postgres psql -c 'SHOW shared_buffers;'",
                    "sudo -u postgres psql -c 'SHOW effective_cache_size;'",
                    "sudo -u postgres psql -c 'SHOW work_mem;'",
                    "sudo -u postgres psql -c 'SHOW maintenance_work_mem;'",
                ]
                
                for cmd in pg_config_commands:
                    try:
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            logger.info(f"PostgreSQL config: {result.stdout.strip()}")
                    except Exception as e:
                        logger.warning(f"Failed to check PostgreSQL config: {str(e)}")
            else:
                logger.warning("PostgreSQL is not running or not accessible")
                
        except Exception as e:
            logger.error(f"Database performance analysis failed: {str(e)}")
    
    async def analyze_application_performance(self):
        """Analyze application performance"""
        logger.info("Analyzing application performance")
        
        try:
            # Check Python processes
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    if 'python' in proc.info['name'].lower():
                        python_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_mb': proc.info['memory_info'].rss / 1024 / 1024
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if python_processes:
                logger.info(f"Found {len(python_processes)} Python processes:")
                for proc in python_processes:
                    logger.info(f"  PID {proc['pid']}: {proc['name']} - CPU: {proc['cpu_percent']}%, Memory: {proc['memory_mb']:.1f}MB")
            else:
                logger.warning("No Python processes found")
            
            # Check application logs
            log_files = [
                f"{self.logs_path}/performance_optimization.log",
                f"{self.logs_path}/performance_monitor.log",
                f"{self.base_path}/logs/app.log",
            ]
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    try:
                        # Get last 10 lines of log
                        result = subprocess.run(
                            ["tail", "-10", log_file],
                            capture_output=True, text=True, timeout=10
                        )
                        if result.returncode == 0:
                            logger.info(f"Recent logs from {log_file}:")
                            for line in result.stdout.strip().split('\n'):
                                if line.strip():
                                    logger.info(f"  {line}")
                    except Exception as e:
                        logger.warning(f"Failed to read log file {log_file}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Application performance analysis failed: {str(e)}")
    
    async def analyze_service_status(self):
        """Analyze systemd service status"""
        logger.info("Analyzing service status")
        
        try:
            services = [
                "ai-backend-optimized.service",
                "guardian-ai.service",
                "main.service",
                "postgresql.service",
            ]
            
            for service in services:
                try:
                    result = subprocess.run(
                        ["sudo", "systemctl", "status", service],
                        capture_output=True, text=True, timeout=30
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"{service} is active")
                        
                        # Check for recent errors
                        if "error" in result.stdout.lower() or "failed" in result.stdout.lower():
                            logger.warning(f"{service} has errors in status")
                    else:
                        logger.warning(f"{service} is not active or not found")
                        
                except Exception as e:
                    logger.warning(f"Failed to check {service}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Service status analysis failed: {str(e)}")
    
    async def analyze_network_performance(self):
        """Analyze network performance"""
        logger.info("Analyzing network performance")
        
        try:
            # Test local connectivity
            local_endpoints = [
                "http://localhost:4000/health",
                "http://localhost:4000/api/health",
                "http://127.0.0.1:4000/health",
            ]
            
            for endpoint in local_endpoints:
                try:
                    start_time = time.time()
                    response = requests.get(endpoint, timeout=10)
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        logger.info(f"{endpoint} - OK (Response time: {response_time:.1f}ms)")
                    else:
                        logger.warning(f"{endpoint} - HTTP {response.status_code} (Response time: {response_time:.1f}ms)")
                        
                except requests.exceptions.RequestException as e:
                    logger.warning(f"{endpoint} - Connection failed: {str(e)}")
            
            # Check network interfaces
            network_interfaces = psutil.net_if_addrs()
            for interface, addresses in network_interfaces.items():
                for addr in addresses:
                    if addr.family == psutil.AF_INET:  # IPv4
                        logger.info(f"Network interface {interface}: {addr.address}")
                        
        except Exception as e:
            logger.error(f"Network performance analysis failed: {str(e)}")
    
    async def generate_performance_report(self):
        """Generate comprehensive performance report"""
        logger.info("Generating performance report")
        
        try:
            report = {
                "timestamp": datetime.utcnow().isoformat(),
                "system_info": {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage('/').percent,
                    "load_average": os.getloadavg(),
                },
                "services": {},
                "recommendations": []
            }
            
            # Check service status for report
            services = ["ai-backend-optimized.service", "guardian-ai.service", "postgresql.service"]
            for service in services:
                try:
                    result = subprocess.run(
                        ["sudo", "systemctl", "is-active", service],
                        capture_output=True, text=True, timeout=10
                    )
                    report["services"][service] = result.stdout.strip()
                except:
                    report["services"][service] = "unknown"
            
            # Generate recommendations
            if report["system_info"]["cpu_percent"] > 80:
                report["recommendations"].append("High CPU usage detected - consider optimizing queries or scaling")
            
            if report["system_info"]["memory_percent"] > 85:
                report["recommendations"].append("High memory usage detected - consider reducing memory footprint")
            
            if report["system_info"]["disk_percent"] > 90:
                report["recommendations"].append("High disk usage detected - consider cleanup or storage expansion")
            
            # Save report
            report_path = f"{self.logs_path}/performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w') as f:
                import json
                json.dump(report, f, indent=2)
            
            logger.info(f"Performance report saved to: {report_path}")
            
            # Print summary
            logger.info("=== PERFORMANCE DIAGNOSIS SUMMARY ===")
            logger.info(f"CPU Usage: {report['system_info']['cpu_percent']}%")
            logger.info(f"Memory Usage: {report['system_info']['memory_percent']}%")
            logger.info(f"Disk Usage: {report['system_info']['disk_percent']}%")
            logger.info(f"Load Average: {report['system_info']['load_average'][0]:.2f}")
            
            for service, status in report["services"].items():
                logger.info(f"{service}: {status}")
            
            if report["recommendations"]:
                logger.info("Recommendations:")
                for rec in report["recommendations"]:
                    logger.info(f"  - {rec}")
            else:
                logger.info("No immediate performance issues detected")
                
        except Exception as e:
            logger.error(f"Failed to generate performance report: {str(e)}")

async def main():
    """Main diagnostic function"""
    diagnostic = PerformanceDiagnostic()
    await diagnostic.run_comprehensive_diagnosis()

if __name__ == "__main__":
    asyncio.run(main()) 