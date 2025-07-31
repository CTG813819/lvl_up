#!/usr/bin/env python3
"""
Performance Monitoring Script
=============================
Monitors system performance after critical performance fix
"""

import asyncio
import os
import sys
import subprocess
import json
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-backend-python/logs/performance_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self):
        self.base_path = "/home/ubuntu/ai-backend-python"
        self.logs_path = f"{self.base_path}/logs"
        self.monitoring_data = []
        
    async def run_performance_monitoring(self, duration_minutes: int = 60):
        """Run performance monitoring for specified duration"""
        logger.info(f"📊 Starting performance monitoring for {duration_minutes} minutes")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        try:
            while datetime.now() < end_time:
                # Collect performance metrics
                metrics = await self.collect_performance_metrics()
                self.monitoring_data.append(metrics)
                
                # Log current status
                await self.log_performance_status(metrics)
                
                # Check for performance issues
                await self.check_performance_issues(metrics)
                
                # Wait 30 seconds before next check
                await asyncio.sleep(30)
            
            # Generate performance report
            await self.generate_performance_report()
            
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Performance monitoring failed: {str(e)}")
            raise
    
    async def collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive performance metrics"""
        timestamp = datetime.now()
        
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Process metrics
            python_processes = []
            total_cpu_percent = 0
            total_memory_mb = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    if 'python' in proc.info['name'].lower():
                        python_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_mb': proc.info['memory_info'].rss / 1024 / 1024
                        })
                        total_cpu_percent += proc.info['cpu_percent']
                        total_memory_mb += proc.info['memory_info'].rss / 1024 / 1024
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Service status
            service_status = await self.check_service_status()
            
            # Database connections
            db_connections = await self.check_database_connections()
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Load average
            load_avg = os.getloadavg()
            
            return {
                'timestamp': timestamp.isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': memory.available / 1024 / 1024 / 1024,
                    'disk_percent': disk.percent,
                    'disk_free_gb': disk.free / 1024 / 1024 / 1024,
                    'load_average': list(load_avg),
                    'network_bytes_sent': network.bytes_sent,
                    'network_bytes_recv': network.bytes_recv
                },
                'python_processes': {
                    'count': len(python_processes),
                    'total_cpu_percent': total_cpu_percent,
                    'total_memory_mb': total_memory_mb,
                    'processes': python_processes
                },
                'services': service_status,
                'database': db_connections
            }
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {str(e)}")
            return {
                'timestamp': timestamp.isoformat(),
                'error': str(e)
            }
    
    async def check_service_status(self) -> Dict[str, Any]:
        """Check status of all services"""
        services = [
            "ai-backend-optimized.service",
            "postgresql.service"
        ]
        
        status = {}
        for service in services:
            try:
                result = subprocess.run(
                    ["sudo", "systemctl", "is-active", service],
                    capture_output=True, text=True, timeout=10
                )
                status[service] = {
                    'active': result.returncode == 0,
                    'status': result.stdout.strip()
                }
            except Exception as e:
                status[service] = {
                    'active': False,
                    'error': str(e)
                }
        
        return status
    
    async def check_database_connections(self) -> Dict[str, Any]:
        """Check database connection status"""
        try:
            # Simple database connection test
            result = subprocess.run(
                ["sudo", "-u", "postgres", "psql", "-c", "SELECT count(*) FROM pg_stat_activity;"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                # Parse the count from output
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 3:
                    connection_count = lines[2].strip()
                    return {
                        'connected': True,
                        'active_connections': connection_count,
                        'status': 'healthy'
                    }
            
            return {
                'connected': False,
                'error': result.stderr
            }
            
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }
    
    async def log_performance_status(self, metrics: Dict[str, Any]):
        """Log current performance status"""
        system = metrics.get('system', {})
        python_procs = metrics.get('python_processes', {})
        services = metrics.get('services', {})
        
        logger.info(f"📊 Performance Status at {metrics['timestamp']}:")
        logger.info(f"  CPU: {system.get('cpu_percent', 'N/A')}%")
        logger.info(f"  Memory: {system.get('memory_percent', 'N/A')}%")
        logger.info(f"  Load: {system.get('load_average', 'N/A')}")
        logger.info(f"  Python Processes: {python_procs.get('count', 0)}")
        logger.info(f"  Python CPU: {python_procs.get('total_cpu_percent', 0):.1f}%")
        logger.info(f"  Python Memory: {python_procs.get('total_memory_mb', 0):.1f}MB")
        
        # Check service status
        backend_active = services.get('ai-backend-optimized.service', {}).get('active', False)
        logger.info(f"  Backend Service: {'✅ Active' if backend_active else '❌ Inactive'}")
    
    async def check_performance_issues(self, metrics: Dict[str, Any]):
        """Check for performance issues and alert"""
        system = metrics.get('system', {})
        python_procs = metrics.get('python_processes', {})
        
        issues = []
        
        # Check CPU usage
        cpu_percent = system.get('cpu_percent', 0)
        if cpu_percent > 80:
            issues.append(f"High CPU usage: {cpu_percent}%")
        
        # Check memory usage
        memory_percent = system.get('memory_percent', 0)
        if memory_percent > 85:
            issues.append(f"High memory usage: {memory_percent}%")
        
        # Check Python processes
        python_cpu = python_procs.get('total_cpu_percent', 0)
        if python_cpu > 50:
            issues.append(f"High Python CPU usage: {python_cpu:.1f}%")
        
        python_memory = python_procs.get('total_memory_mb', 0)
        if python_memory > 1000:  # 1GB
            issues.append(f"High Python memory usage: {python_memory:.1f}MB")
        
        # Check load average
        load_avg = system.get('load_average', [0, 0, 0])
        if load_avg[0] > 4:  # Assuming 4 CPU cores
            issues.append(f"High load average: {load_avg[0]:.2f}")
        
        if issues:
            logger.warning(f"⚠️ Performance issues detected: {', '.join(issues)}")
        else:
            logger.info("✅ Performance is within normal ranges")
    
    async def generate_performance_report(self):
        """Generate comprehensive performance report"""
        logger.info("📋 Generating performance report...")
        
        if not self.monitoring_data:
            logger.warning("No monitoring data available")
            return
        
        # Calculate averages
        cpu_values = [m.get('system', {}).get('cpu_percent', 0) for m in self.monitoring_data if 'system' in m]
        memory_values = [m.get('system', {}).get('memory_percent', 0) for m in self.monitoring_data if 'system' in m]
        python_cpu_values = [m.get('python_processes', {}).get('total_cpu_percent', 0) for m in self.monitoring_data if 'python_processes' in m]
        python_memory_values = [m.get('python_processes', {}).get('total_memory_mb', 0) for m in self.monitoring_data if 'python_processes' in m]
        
        # Calculate statistics
        report = {
            'monitoring_duration_minutes': len(self.monitoring_data) * 0.5,  # 30-second intervals
            'data_points': len(self.monitoring_data),
            'system_performance': {
                'cpu_percent': {
                    'average': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                    'max': max(cpu_values) if cpu_values else 0,
                    'min': min(cpu_values) if cpu_values else 0
                },
                'memory_percent': {
                    'average': sum(memory_values) / len(memory_values) if memory_values else 0,
                    'max': max(memory_values) if memory_values else 0,
                    'min': min(memory_values) if memory_values else 0
                }
            },
            'python_performance': {
                'cpu_percent': {
                    'average': sum(python_cpu_values) / len(python_cpu_values) if python_cpu_values else 0,
                    'max': max(python_cpu_values) if python_cpu_values else 0,
                    'min': min(python_cpu_values) if python_cpu_values else 0
                },
                'memory_mb': {
                    'average': sum(python_memory_values) / len(python_memory_values) if python_memory_values else 0,
                    'max': max(python_memory_values) if python_memory_values else 0,
                    'min': min(python_memory_values) if python_memory_values else 0
                }
            },
            'service_uptime': {
                'backend_active_percentage': self.calculate_service_uptime('ai-backend-optimized.service')
            }
        }
        
        # Log the report
        logger.info("📊 PERFORMANCE REPORT")
        logger.info("====================")
        logger.info(f"Monitoring Duration: {report['monitoring_duration_minutes']:.1f} minutes")
        logger.info(f"Data Points: {report['data_points']}")
        logger.info("")
        logger.info("System Performance:")
        logger.info(f"  CPU Usage - Avg: {report['system_performance']['cpu_percent']['average']:.1f}%, Max: {report['system_performance']['cpu_percent']['max']:.1f}%")
        logger.info(f"  Memory Usage - Avg: {report['system_performance']['memory_percent']['average']:.1f}%, Max: {report['system_performance']['memory_percent']['max']:.1f}%")
        logger.info("")
        logger.info("Python Performance:")
        logger.info(f"  CPU Usage - Avg: {report['python_performance']['cpu_percent']['average']:.1f}%, Max: {report['python_performance']['cpu_percent']['max']:.1f}%")
        logger.info(f"  Memory Usage - Avg: {report['python_performance']['memory_mb']['average']:.1f}MB, Max: {report['python_performance']['memory_mb']['max']:.1f}MB")
        logger.info("")
        logger.info(f"Backend Service Uptime: {report['service_uptime']['backend_active_percentage']:.1f}%")
        
        # Save report to file
        report_path = f"{self.logs_path}/performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Full report saved to: {report_path}")
        
        # Performance assessment
        await self.assess_performance_improvement(report)
    
    def calculate_service_uptime(self, service_name: str) -> float:
        """Calculate service uptime percentage"""
        active_count = 0
        total_count = 0
        
        for metrics in self.monitoring_data:
            if 'services' in metrics and service_name in metrics['services']:
                total_count += 1
                if metrics['services'][service_name].get('active', False):
                    active_count += 1
        
        return (active_count / total_count * 100) if total_count > 0 else 0
    
    async def assess_performance_improvement(self, report: Dict[str, Any]):
        """Assess if performance has improved"""
        logger.info("")
        logger.info("🎯 PERFORMANCE ASSESSMENT")
        logger.info("========================")
        
        # Check if performance is acceptable
        cpu_avg = report['system_performance']['cpu_percent']['average']
        memory_avg = report['system_performance']['memory_percent']['average']
        python_cpu_avg = report['python_performance']['cpu_percent']['average']
        backend_uptime = report['service_uptime']['backend_active_percentage']
        
        improvements = []
        issues = []
        
        if cpu_avg < 50:
            improvements.append(f"✅ CPU usage is good: {cpu_avg:.1f}%")
        else:
            issues.append(f"⚠️ CPU usage is high: {cpu_avg:.1f}%")
        
        if memory_avg < 80:
            improvements.append(f"✅ Memory usage is good: {memory_avg:.1f}%")
        else:
            issues.append(f"⚠️ Memory usage is high: {memory_avg:.1f}%")
        
        if python_cpu_avg < 30:
            improvements.append(f"✅ Python CPU usage is good: {python_cpu_avg:.1f}%")
        else:
            issues.append(f"⚠️ Python CPU usage is high: {python_cpu_avg:.1f}%")
        
        if backend_uptime > 95:
            improvements.append(f"✅ Backend uptime is excellent: {backend_uptime:.1f}%")
        elif backend_uptime > 90:
            improvements.append(f"✅ Backend uptime is good: {backend_uptime:.1f}%")
        else:
            issues.append(f"⚠️ Backend uptime is poor: {backend_uptime:.1f}%")
        
        # Log assessment
        if improvements:
            logger.info("✅ Performance Improvements:")
            for improvement in improvements:
                logger.info(f"  {improvement}")
        
        if issues:
            logger.warning("⚠️ Performance Issues:")
            for issue in issues:
                logger.warning(f"  {issue}")
        
        if not issues:
            logger.info("🎉 EXCELLENT! Performance is within acceptable ranges")
        elif len(improvements) > len(issues):
            logger.info("👍 GOOD! Performance has improved significantly")
        else:
            logger.warning("⚠️ ATTENTION! Performance issues still exist")

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor backend performance')
    parser.add_argument('--duration', type=int, default=60, help='Monitoring duration in minutes (default: 60)')
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor()
    await monitor.run_performance_monitoring(args.duration)

if __name__ == "__main__":
    asyncio.run(main()) 