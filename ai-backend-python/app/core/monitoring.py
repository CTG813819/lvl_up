"""
Comprehensive monitoring and alerting system for backend health
"""

import asyncio
import time
import psutil
import structlog
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
import os

logger = structlog.get_logger()


class SystemMonitor:
    """Monitor system resources and performance"""
    
    def __init__(self):
        self.metrics_history = defaultdict(lambda: deque(maxlen=100))
        self.alerts = []
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time_ms': 5000.0,
            'error_rate': 0.1,
            'connection_pool_usage': 0.8,
            'open_fds_percent': 80.0  # Alert if open FDs > 80% of limit
        }
        self.monitoring_active = False
        self.fd_limit = self._get_fd_limit()
        self.max_observed_fds = 0
        self.adaptive_fd_threshold = int(self.fd_limit * 0.8)
    
    async def start_monitoring(self):
        """Start system monitoring"""
        self.monitoring_active = True
        asyncio.create_task(self._monitor_loop())
        logger.info("System monitoring started")
    
    async def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring_active = False
        logger.info("System monitoring stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                await self._collect_metrics()
                await self._check_alerts()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error("Error in monitoring loop", error=str(e))
                await asyncio.sleep(60)
    
    async def _collect_metrics(self):
        """Collect system metrics, including open file descriptors"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics_history['cpu_percent'].append(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics_history['memory_percent'].append(memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.metrics_history['disk_percent'].append(disk.percent)
            
            # Network I/O
            network = psutil.net_io_counters()
            self.metrics_history['network_bytes_sent'].append(network.bytes_sent)
            self.metrics_history['network_bytes_recv'].append(network.bytes_recv)
            
            # Open file descriptors
            open_fds = self._get_open_fds()
            self.metrics_history['open_fds'].append(open_fds)
            if open_fds > self.max_observed_fds:
                self.max_observed_fds = open_fds
            # Adaptive threshold: if max observed is much lower than limit, relax; if close, tighten
            if self.max_observed_fds > self.adaptive_fd_threshold:
                self.adaptive_fd_threshold = int(self.max_observed_fds * 1.05)
            
            logger.debug("System metrics collected", 
                        cpu=cpu_percent, 
                        memory=memory.percent, 
                        disk=disk.percent,
                        open_fds=open_fds,
                        fd_limit=self.fd_limit)
            
        except Exception as e:
            logger.error("Error collecting system metrics", error=str(e))
    
    async def _check_alerts(self):
        """Check for alert conditions, including open file descriptors"""
        alerts = []
        
        # Check CPU usage
        if self.metrics_history['cpu_percent']:
            avg_cpu = sum(self.metrics_history['cpu_percent']) / len(self.metrics_history['cpu_percent'])
            if avg_cpu > self.thresholds['cpu_percent']:
                alerts.append(f"High CPU usage: {avg_cpu:.1f}%")
        
        # Check memory usage
        if self.metrics_history['memory_percent']:
            avg_memory = sum(self.metrics_history['memory_percent']) / len(self.metrics_history['memory_percent'])
            if avg_memory > self.thresholds['memory_percent']:
                alerts.append(f"High memory usage: {avg_memory:.1f}%")
        
        # Check disk usage
        if self.metrics_history['disk_percent']:
            avg_disk = sum(self.metrics_history['disk_percent']) / len(self.metrics_history['disk_percent'])
            if avg_disk > self.thresholds['disk_percent']:
                alerts.append(f"High disk usage: {avg_disk:.1f}%")
        
        # Check open file descriptors
        if self.metrics_history['open_fds']:
            current_fds = self.metrics_history['open_fds'][-1]
            percent_fds = (current_fds / self.fd_limit) * 100 if self.fd_limit else 0
            if percent_fds > self.thresholds['open_fds_percent']:
                alerts.append(f"High open file descriptors: {current_fds} ({percent_fds:.1f}% of limit {self.fd_limit})")
        
        # Process alerts
        for alert in alerts:
            await self._process_alert(alert)
    
    async def _process_alert(self, alert: str):
        """Process and log alerts"""
        logger.warning(f"System alert: {alert}")
        self.alerts.append({
            'timestamp': datetime.now().isoformat(),
            'message': alert,
            'severity': 'warning'
        })
    
    def get_metrics(self) -> Dict:
        """Get current system metrics, including open file descriptors"""
        metrics = {}
        for key, values in self.metrics_history.items():
            if values:
                metrics[key] = {
                    'current': values[-1],
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }
        # Add FD stats
        metrics['open_fds_limit'] = self.fd_limit
        metrics['max_observed_fds'] = self.max_observed_fds
        metrics['adaptive_fd_threshold'] = self.adaptive_fd_threshold
        return metrics
    
    def get_alerts(self) -> List[Dict]:
        """Get recent alerts"""
        return self.alerts[-10:]  # Last 10 alerts

    def _get_fd_limit(self):
        """Get the system's file descriptor limit (ulimit -n)"""
        try:
            import resource
            return resource.getrlimit(resource.RLIMIT_NOFILE)[0]
        except Exception:
            return 1024  # Fallback default
    def _get_open_fds(self):
        """Get the number of open file descriptors for this process"""
        try:
            proc = psutil.Process()
            if hasattr(proc, 'num_fds'):
                return proc.num_fds()
            # Fallback: count /proc/self/fd (Linux only)
            fd_dir = f"/proc/{proc.pid}/fd"
            return len(os.listdir(fd_dir))
        except Exception:
            return -1


class DatabaseMonitor:
    """Monitor database performance and health"""
    
    def __init__(self, db_session_func: Callable):
        self.db_session_func = db_session_func
        self.query_times = deque(maxlen=100)
        self.error_counts = defaultdict(int)
        self.connection_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'failed_connections': 0
        }
    
    async def monitor_query_performance(self, query_name: str, query_func: Callable):
        """Monitor database query performance"""
        start_time = time.time()
        try:
            result = await query_func()
            query_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            self.query_times.append(query_time)
            
            if query_time > 1000:  # Log slow queries
                logger.warning(f"Slow query detected: {query_name}", 
                             query_time=query_time, query_name=query_name)
            
            return result
        except Exception as e:
            self.error_counts[query_name] += 1
            logger.error(f"Database query failed: {query_name}", 
                        error=str(e), query_name=query_name)
            raise
    
    def get_performance_stats(self) -> Dict:
        """Get database performance statistics"""
        if not self.query_times:
            return {}
        
        return {
            'query_times': {
                'average_ms': sum(self.query_times) / len(self.query_times),
                'min_ms': min(self.query_times),
                'max_ms': max(self.query_times),
                'total_queries': len(self.query_times)
            },
            'error_counts': dict(self.error_counts),
            'connection_stats': self.connection_stats
        }


class APIMonitor:
    """Monitor API endpoints and performance"""
    
    def __init__(self):
        self.endpoint_stats = defaultdict(lambda: {
            'requests': 0,
            'errors': 0,
            'response_times': deque(maxlen=50),
            'last_request': None
        })
        self.rate_limits = {
            'growth_analytics': {'limit': 30, 'window': 60},
            'oath_papers': {'limit': 20, 'window': 60},
            'proposals': {'limit': 50, 'window': 60}
        }
    
    def record_request(self, endpoint: str, response_time: float, success: bool):
        """Record API request statistics"""
        stats = self.endpoint_stats[endpoint]
        stats['requests'] += 1
        stats['response_times'].append(response_time)
        stats['last_request'] = datetime.now().isoformat()
        
        if not success:
            stats['errors'] += 1
        
        # Log high error rates
        error_rate = stats['errors'] / stats['requests'] if stats['requests'] > 0 else 0
        if error_rate > 0.1 and stats['requests'] > 10:
            logger.warning(f"High error rate for endpoint: {endpoint}", 
                         error_rate=error_rate, total_requests=stats['requests'])
    
    def get_endpoint_stats(self) -> Dict:
        """Get API endpoint statistics"""
        stats = {}
        for endpoint, data in self.endpoint_stats.items():
            if data['response_times']:
                stats[endpoint] = {
                    'total_requests': data['requests'],
                    'total_errors': data['errors'],
                    'error_rate': data['errors'] / data['requests'] if data['requests'] > 0 else 0,
                    'avg_response_time': sum(data['response_times']) / len(data['response_times']),
                    'last_request': data['last_request']
                }
        return stats


class HealthChecker:
    """Comprehensive health checking system"""
    
    def __init__(self):
        self.health_checks = {}
        self.health_status = {
            'database': 'unknown',
            'api': 'unknown',
            'system': 'unknown',
            'last_check': None
        }
    
    def register_health_check(self, name: str, check_func: Callable):
        """Register a health check function"""
        self.health_checks[name] = check_func
    
    async def run_health_checks(self):
        """Run all registered health checks"""
        results = {}
        
        for name, check_func in self.health_checks.items():
            try:
                result = await check_func()
                results[name] = {'status': 'healthy', 'details': result}
                self.health_status[name] = 'healthy'
            except Exception as e:
                results[name] = {'status': 'unhealthy', 'error': str(e)}
                self.health_status[name] = 'unhealthy'
                logger.error(f"Health check failed: {name}", error=str(e))
        
        self.health_status['last_check'] = datetime.now().isoformat()
        return results
    
    def get_health_status(self) -> Dict:
        """Get current health status"""
        return self.health_status


# Global monitoring instances
system_monitor = SystemMonitor()
api_monitor = APIMonitor()
health_checker = HealthChecker()


async def start_monitoring():
    """Start all monitoring systems"""
    await system_monitor.start_monitoring()
    logger.info("All monitoring systems started")


async def stop_monitoring():
    """Stop all monitoring systems"""
    await system_monitor.stop_monitoring()
    logger.info("All monitoring systems stopped")


def get_comprehensive_stats() -> Dict:
    """Get comprehensive system statistics"""
    return {
        'system': system_monitor.get_metrics(),
        'api': api_monitor.get_endpoint_stats(),
        'health': health_checker.get_health_status(),
        'alerts': system_monitor.get_alerts()
    } 