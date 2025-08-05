#!/usr/bin/env python3
# Enhanced Imperium Monitoring Service

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
from app.core.database import get_session

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
        
        # Process monitoring
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Network monitoring
        network = psutil.net_io_counters()
        
        self.monitoring_data = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3)
            },
            "processes": processes[:20],  # Top 20 processes
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv
            }
        }
        
        self.last_scan = datetime.now()
    
    async def analyze_system_health(self):
        """Analyze system health and detect issues"""
        issues = []
        
        # CPU analysis
        if self.monitoring_data["system"]["cpu_percent"] > 80:
            issues.append({
                "type": "high_cpu_usage",
                "severity": "warning",
                "description": f"CPU usage is {self.monitoring_data['system']['cpu_percent']}%",
                "recommendation": "Consider optimizing processes or scaling resources"
            })
        
        # Memory analysis
        if self.monitoring_data["system"]["memory_percent"] > 85:
            issues.append({
                "type": "high_memory_usage",
                "severity": "critical",
                "description": f"Memory usage is {self.monitoring_data['system']['memory_percent']}%",
                "recommendation": "Immediate action required - consider restarting services or adding memory"
            })
        
        # Disk analysis
        if self.monitoring_data["system"]["disk_percent"] > 90:
            issues.append({
                "type": "low_disk_space",
                "severity": "critical",
                "description": f"Disk usage is {self.monitoring_data['system']['disk_percent']}%",
                "recommendation": "Clean up disk space immediately"
            })
        
        self.monitoring_data["issues"] = issues
    
    async def generate_improvements(self):
        """Generate AI improvements based on system analysis"""
        improvements = []
        
        # Performance improvements
        if self.monitoring_data["system"]["cpu_percent"] > 70:
            improvements.append({
                "type": "performance_optimization",
                "description": "System experiencing high CPU load",
                "impact_score": 8,
                "recommendation": "Implement caching and optimize database queries"
            })
        
        # Security improvements
        improvements.append({
            "type": "security_enhancement",
            "description": "Regular security scan recommended",
            "impact_score": 9,
            "recommendation": "Run security audit and update dependencies"
        })
        
        # Monitoring improvements
        improvements.append({
            "type": "monitoring_enhancement",
            "description": "Enhanced logging and alerting",
            "impact_score": 7,
            "recommendation": "Implement structured logging and alerting system"
        })
        
        self.monitoring_data["improvements"] = improvements
    
    async def save_monitoring_report(self):
        """Save monitoring report to file and database"""
        try:
            # Save to file
            with open("imperium_monitoring_report.json", "w") as f:
                json.dump(self.monitoring_data, f, indent=2, default=str)
            
            # Save to database
            session = get_session()
            async with session as s:
                # Save improvements
                for improvement in self.monitoring_data.get("improvements", []):
                    await s.execute(sa.text("""
                        INSERT INTO ai_improvements 
                        (ai_type, improvement_type, description, impact_score, status, timestamp)
                        VALUES (:ai_type, :improvement_type, :description, :impact_score, :status, :timestamp)
                    """), {
                        "ai_type": "imperium",
                        "improvement_type": improvement["type"],
                        "description": improvement["description"],
                        "impact_score": improvement["impact_score"],
                        "status": "pending",
                        "timestamp": datetime.now()
                    })
                
                # Save issues
                for issue in self.monitoring_data.get("issues", []):
                    await s.execute(sa.text("""
                        INSERT INTO system_issues 
                        (issue_type, severity, description, affected_components, resolution_status, timestamp)
                        VALUES (:issue_type, :severity, :description, :affected_components, :resolution_status, :timestamp)
                    """), {
                        "issue_type": issue["type"],
                        "severity": issue["severity"],
                        "description": issue["description"],
                        "affected_components": "system",
                        "resolution_status": "open",
                        "timestamp": datetime.now()
                    })
                
                await s.commit()
            
            self.logger.info("✅ Monitoring report saved successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving monitoring report: {str(e)}")

async def main():
    """Main function to start the monitoring service"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    service = ImperiumMonitoringService()
    await service.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
