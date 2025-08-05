#!/usr/bin/env python3
# Enhanced Imperium Monitoring Service - Fixed Version

import asyncio
import json
import logging
import os
import psutil
import time
from datetime import datetime
from typing import Dict, List, Any
import aiohttp
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/imperium_monitoring.log'),
        logging.StreamHandler()
    ]
)

class ImperiumMonitoringService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitoring_data = {}
        self.last_scan = None
        self.scan_interval = 300  # 5 minutes
        
    async def start_monitoring(self):
        """Start the monitoring service"""
        self.logger.info("🚀 Starting Imperium Monitoring Service...")
        
        while True:
            try:
                await self.perform_system_scan()
                await self.analyze_system_health()
                await self.generate_improvements()
                await self.save_monitoring_report()
                
                self.logger.info(f"✅ System scan completed at {datetime.now()}")
                await asyncio.sleep(self.scan_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def perform_system_scan(self):
        """Perform comprehensive system scan"""
        self.logger.info("🔍 Performing system scan...")
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network metrics
        network = psutil.net_io_counters()
        
        # Process metrics
        processes = len(psutil.pids())
        
        self.monitoring_data = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available': memory.available,
                'disk_percent': disk.percent,
                'disk_free': disk.free,
                'processes': processes,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
            },
            'status': 'healthy' if cpu_percent < 80 and memory.percent < 85 else 'warning',
            'message': f"System running normally. CPU: {cpu_percent}%, Memory: {memory.percent}%"
        }
        
        self.last_scan = datetime.now()
    
    async def analyze_system_health(self):
        """Analyze system health and detect issues"""
        self.logger.info("🔬 Analyzing system health...")
        
        issues = []
        
        # Check CPU usage
        if self.monitoring_data['system']['cpu_percent'] > 80:
            issues.append({
                'type': 'high_cpu_usage',
                'severity': 'warning',
                'message': f"High CPU usage: {self.monitoring_data['system']['cpu_percent']}%",
                'timestamp': datetime.now().isoformat()
            })
        
        # Check memory usage
        if self.monitoring_data['system']['memory_percent'] > 85:
            issues.append({
                'type': 'high_memory_usage',
                'severity': 'warning',
                'message': f"High memory usage: {self.monitoring_data['system']['memory_percent']}%",
                'timestamp': datetime.now().isoformat()
            })
        
        # Check disk usage
        if self.monitoring_data['system']['disk_percent'] > 90:
            issues.append({
                'type': 'low_disk_space',
                'severity': 'error',
                'message': f"Low disk space: {self.monitoring_data['system']['disk_percent']}% used",
                'timestamp': datetime.now().isoformat()
            })
        
        self.monitoring_data['issues'] = issues
        
        if issues:
            self.monitoring_data['status'] = 'warning'
            self.monitoring_data['message'] = f"Found {len(issues)} issues"
    
    async def generate_improvements(self):
        """Generate improvement suggestions"""
        self.logger.info("💡 Generating improvement suggestions...")
        
        suggestions = []
        
        # CPU optimization suggestions
        if self.monitoring_data['system']['cpu_percent'] > 70:
            suggestions.append({
                'type': 'cpu_optimization',
                'priority': 'medium',
                'message': 'Consider optimizing CPU-intensive processes',
                'action': 'Review and optimize background tasks'
            })
        
        # Memory optimization suggestions
        if self.monitoring_data['system']['memory_percent'] > 80:
            suggestions.append({
                'type': 'memory_optimization',
                'priority': 'high',
                'message': 'Consider increasing memory or optimizing memory usage',
                'action': 'Monitor memory-intensive applications'
            })
        
        self.monitoring_data['suggestions'] = suggestions
    
    async def save_monitoring_report(self):
        """Save monitoring report to file"""
        try:
            report_path = '/tmp/imperium_monitoring_report.json'
            with open(report_path, 'w') as f:
                json.dump(self.monitoring_data, f, indent=2)
            self.logger.info(f"📊 Monitoring report saved to {report_path}")
        except Exception as e:
            self.logger.error(f"❌ Failed to save monitoring report: {e}")
    
    async def get_monitoring_data(self):
        """Get current monitoring data"""
        return self.monitoring_data
    
    async def get_health_status(self):
        """Get system health status"""
        return {
            'status': self.monitoring_data.get('status', 'unknown'),
            'message': self.monitoring_data.get('message', 'No status available'),
            'timestamp': self.monitoring_data.get('timestamp', datetime.now().isoformat()),
            'issues_count': len(self.monitoring_data.get('issues', [])),
            'suggestions_count': len(self.monitoring_data.get('suggestions', []))
        }

# Global instance
monitoring_service = ImperiumMonitoringService()

async def start_monitoring_service():
    """Start the monitoring service"""
    await monitoring_service.start_monitoring()

if __name__ == "__main__":
    asyncio.run(start_monitoring_service()) 