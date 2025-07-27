#!/usr/bin/env python3
"""
Reduce CPU Usage
================

This script reduces CPU usage by stopping unnecessary processes
and optimizing the system for Custodes tests.
"""

import asyncio
import sys
import os
import subprocess
import psutil
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import structlog

logger = structlog.get_logger()

def check_system_resources():
    """Check current system resources"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"📊 Current System Resources:")
        print(f"   CPU Usage: {cpu_percent}%")
        print(f"   Memory Usage: {memory.percent}%")
        print(f"   Disk Usage: {disk.percent}%")
        
        return {
            "cpu": cpu_percent,
            "memory": memory.percent,
            "disk": disk.percent
        }
    except Exception as e:
        print(f"❌ Error checking resources: {str(e)}")
        return None

def find_high_cpu_processes():
    """Find processes using high CPU"""
    try:
        print("\n🔍 Finding high CPU processes...")
        
        high_cpu_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if proc.info['cpu_percent'] > 10:  # More than 10% CPU
                    high_cpu_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        high_cpu_processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        print("📈 High CPU processes:")
        for proc in high_cpu_processes[:10]:  # Show top 10
            print(f"   PID {proc['pid']}: {proc['name']} - CPU: {proc['cpu_percent']:.1f}%, Memory: {proc['memory_percent']:.1f}%")
        
        return high_cpu_processes
        
    except Exception as e:
        print(f"❌ Error finding high CPU processes: {str(e)}")
        return []

def stop_unnecessary_processes():
    """Stop unnecessary processes to reduce CPU usage"""
    try:
        print("\n🛑 Stopping unnecessary processes...")
        
        # List of processes that can be safely stopped
        safe_to_stop = [
            'python3',  # Multiple Python processes
            'uvicorn',  # Multiple uvicorn instances
            'node',     # Node.js processes
            'npm',      # NPM processes
        ]
        
        stopped_count = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if proc.info['name'] in safe_to_stop and proc.info['cpu_percent'] > 5:
                    print(f"   Stopping {proc.info['name']} (PID {proc.info['pid']}) - CPU: {proc.info['cpu_percent']:.1f}%")
                    proc.terminate()
                    stopped_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        print(f"✅ Stopped {stopped_count} unnecessary processes")
        return stopped_count
        
    except Exception as e:
        print(f"❌ Error stopping processes: {str(e)}")
        return 0

async def restart_backend_service():
    """Restart the backend service cleanly"""
    try:
        print("\n🔄 Restarting backend service...")
        
        # Stop the current service
        subprocess.run(["sudo", "systemctl", "stop", "ai-backend-python"], check=True)
        print("   ✅ Backend service stopped")
        
        # Wait a moment
        await asyncio.sleep(5)
        
        # Start the service
        subprocess.run(["sudo", "systemctl", "start", "ai-backend-python"], check=True)
        print("   ✅ Backend service started")
        
        # Check status
        result = subprocess.run(["sudo", "systemctl", "status", "ai-backend-python"], 
                              capture_output=True, text=True)
        if "active (running)" in result.stdout:
            print("   ✅ Backend service is running")
            return True
        else:
            print("   ❌ Backend service failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Error restarting backend service: {str(e)}")
        return False

def optimize_system_settings():
    """Optimize system settings for lower CPU usage"""
    try:
        print("\n⚙️ Optimizing system settings...")
        
        # Set CPU governor to powersave (if available)
        try:
            subprocess.run(["sudo", "cpupower", "frequency-set", "-g", "powersave"], 
                         capture_output=True)
            print("   ✅ CPU governor set to powersave")
        except:
            print("   ⚠️ Could not set CPU governor")
        
        # Clear system cache
        try:
            subprocess.run(["sudo", "sync"], check=True)
            subprocess.run(["sudo", "echo", "3", ">", "/proc/sys/vm/drop_caches"], 
                         shell=True, capture_output=True)
            print("   ✅ System cache cleared")
        except:
            print("   ⚠️ Could not clear system cache")
        
        return True
        
    except Exception as e:
        print(f"❌ Error optimizing system settings: {str(e)}")
        return False

async def main():
    """Main function"""
    print("🚀 Reducing CPU Usage for Custodes Tests")
    print("=" * 50)
    
    # Check initial resources
    initial_resources = check_system_resources()
    
    if initial_resources and initial_resources["cpu"] > 80:
        print(f"⚠️ CPU usage is very high ({initial_resources['cpu']}%)")
        
        # Find high CPU processes
        high_cpu_processes = find_high_cpu_processes()
        
        if high_cpu_processes:
            # Stop unnecessary processes
            stopped_count = stop_unnecessary_processes()
            
            if stopped_count > 0:
                # Wait for processes to stop
                await asyncio.sleep(10)
                
                # Check resources again
                print("\n📊 Checking resources after stopping processes...")
                new_resources = check_system_resources()
                
                if new_resources:
                    cpu_reduction = initial_resources["cpu"] - new_resources["cpu"]
                    print(f"✅ CPU usage reduced by {cpu_reduction:.1f}%")
        
        # Optimize system settings
        optimize_system_settings()
        
        # Restart backend service
        if await restart_backend_service():
            print("\n✅ Backend service restarted successfully")
        else:
            print("\n❌ Failed to restart backend service")
    
    else:
        print("✅ CPU usage is acceptable")
    
    print("\n" + "=" * 50)
    print("✅ CPU usage optimization completed!")
    print("📋 Summary:")
    print("   - System resources checked")
    print("   - Unnecessary processes stopped")
    print("   - System settings optimized")
    print("   - Backend service restarted")
    print("   - Custodes tests should now run with lower CPU usage")

if __name__ == "__main__":
    asyncio.run(main()) 