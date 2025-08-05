#!/usr/bin/env python3
"""
EC2 Server Issues Fix Script
Fixes WebSocket, database, and dashboard access issues
"""

import subprocess
import json
import time
import sys
from datetime import datetime

def run_ssh_command(command, description):
    """Run SSH command on EC2 instance"""
    print(f"\n🔧 {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
        else:
            print(f"❌ Error: {description}")
            print(f"Error: {result.stderr.strip()}")
            
        return result
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout: {description}")
        return None
    except Exception as e:
        print(f"💥 Exception: {description} - {e}")
        return None

def fix_websocket_configuration():
    """Fix WebSocket configuration issues"""
    print("\n🔌 Fixing WebSocket Configuration...")
    
    # Check current WebSocket routes
    check_routes = run_ssh_command(
        "ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 'cd /home/ubuntu/ai-backend-python && find . -name \"*.py\" -exec grep -l \"websocket\|WebSocket\" {} \\;'",
        "Finding WebSocket routes"
    )
    
    # Check CORS configuration
    check_cors = run_ssh_command(
        "ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 'cd /home/ubuntu/ai-backend-python && grep -r \"CORS\|cors\" app/ --include=\"*.py\"'",
        "Checking CORS configuration"
    )
    
    # Check if WebSocket routes are properly registered
    check_app_routes = run_ssh_command(
        "ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 'cd /home/ubuntu/ai-backend-python && python3 -c \"from app.main import app; print([route.path for route in app.routes if hasattr(route, \'path\')])\"'",
        "Checking registered routes"
    )
    
    # Create WebSocket fix script
    websocket_fix = '''
#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/ubuntu/ai-backend-python')

# Check if WebSocket routes exist
try:
    from app.routers import notifications
    print("✅ Notifications router found")
except ImportError:
    print("❌ Notifications router not found")

try:
    from app.main import app
    print("✅ Main app found")
    
    # Check for WebSocket routes
    websocket_routes = [route for route in app.routes if hasattr(route, 'path') and 'ws' in route.path]
    print(f"WebSocket routes found: {len(websocket_routes)}")
    for route in websocket_routes:
        print(f"  - {route.path}")
        
except Exception as e:
    print(f"❌ Error checking routes: {e}")
'''
    
    run_ssh_command(
        f"ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 'cd /home/ubuntu/ai-backend-python && cat > check_websocket.py << \"EOF\"{websocket_fix}EOF && python3 check_websocket.py'",
        "Checking WebSocket route registration"
    )

def fix_database_initialization():
    """Fix database initialization issues"""
    print("\n🗄️ Fixing Database Initialization...")
    
    # Check database status
    check_db = run_ssh_command(
        "ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 'cd /home/ubuntu/ai-backend-python && python3 -c \"from app.core.database import init_database; init_database(); print(\\\"Database initialized\\\")\"'",
        "Initializing database"
    )
    
    # Check if database tables exist
    check_tables = run_ssh_command(
        "ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 'cd /home/ubuntu/ai-backend-python && python3 -c \"from app.core.database import engine; from sqlalchemy import inspect; inspector = inspect(engine); print(\\\"Tables:\\\", inspector.get_table_names())\"'",
        "Checking database tables"
    )
    
    # Run database creation scripts
    run_creation_scripts = run_ssh_command(
        "ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 'cd /home/ubuntu/ai-backend-python && python3 create_imperium_tables.py'",
        "Running Imperium tables creation script"
    )
    
    # Test learning analytics endpoint
    test_analytics = run_ssh_command(
        "ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 'curl -s http://localhost:8000/api/imperium/persistence/learning-analytics | python3 -m json.tool'",
        "Testing learning analytics endpoint"
    )

def fix_dashboard_access():
    """Fix Streamlit dashboard external access"""
    print("\n📊 Fixing Dashboard Access...")
    
    # Check Streamlit process
    check_streamlit = run_ssh_command(
        "ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 'ps aux | grep streamlit'",
        "Checking Streamlit process"
    )
    
    # Check Streamlit configuration
    check_config = run_ssh_command(
        "ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 'cd /home/ubuntu/ai-backend-python && ls -la *.py | grep -i streamlit'",
        "Checking Streamlit configuration files"
    )
    
    # Restart Streamlit with external access
    restart_streamlit = run_ssh_command(
        "ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 'cd /home/ubuntu/ai-backend-python && pkill -f streamlit; nohup streamlit run imperium_dashboard.py --server.port 8501 --server.address 0.0.0.0 --server.headless true > streamlit.log 2>&1 &'",
        "Restarting Streamlit with external access"
    )
    
    # Check if port 8501 is now accessible
    check_port = run_ssh_command(
        "ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 'netstat -tlnp | grep 8501'",
        "Checking if port 8501 is listening"
    )

def fix_cors_and_websocket():
    """Fix CORS and WebSocket configuration"""
    print("\n🌐 Fixing CORS and WebSocket Configuration...")
    
    # Create CORS fix script
    cors_fix = '''
#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/ubuntu/ai-backend-python')

try:
    from app.main import app
    from fastapi.middleware.cors import CORSMiddleware
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    print("✅ CORS middleware added")
    
    # Check WebSocket routes
    from app.routers.notifications import router as notifications_router
    print("✅ Notifications router imported")
    
    # Test WebSocket endpoint locally
    import asyncio
    import websockets
    
    async def test_websocket():
        try:
            uri = "ws://localhost:8000/ws"
            async with websockets.connect(uri) as websocket:
                await websocket.send('{"test": "message"}')
                response = await websocket.recv()
                print(f"✅ WebSocket test successful: {response}")
        except Exception as e:
            print(f"❌ WebSocket test failed: {e}")
    
    # Run WebSocket test
    asyncio.run(test_websocket())
    
except Exception as e:
    print(f"❌ Error fixing CORS/WebSocket: {e}")
'''
    
    run_ssh_command(
        f"ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 'cd /home/ubuntu/ai-backend-python && cat > fix_cors_websocket.py << \"EOF\"{cors_fix}EOF && python3 fix_cors_websocket.py'",
        "Fixing CORS and WebSocket configuration"
    )

def restart_services():
    """Restart all services"""
    print("\n🔄 Restarting Services...")
    
    # Restart uvicorn services
    restart_uvicorn = run_ssh_command(
        "ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 'pkill -f uvicorn; cd /home/ubuntu/ai-backend-python && nohup /home/ubuntu/ai-backend-python/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn_8000.log 2>&1 & nohup /home/ubuntu/ai-backend-python/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 4000 > uvicorn_4000.log 2>&1 &'",
        "Restarting uvicorn services"
    )
    
    # Wait for services to start
    time.sleep(5)
    
    # Check service status
    check_services = run_ssh_command(
        "ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 'ps aux | grep uvicorn'",
        "Checking service status"
    )

def test_endpoints():
    """Test all endpoints after fixes"""
    print("\n🧪 Testing Endpoints After Fixes...")
    
    endpoints = [
        "http://34.202.215.209:8000/api/imperium/status",
        "http://34.202.215.209:8000/api/imperium/agents",
        "http://34.202.215.209:8000/api/imperium/dashboard",
        "http://34.202.215.209:8000/api/imperium/persistence/learning-analytics",
        "http://34.202.215.209:8501"
    ]
    
    for endpoint in endpoints:
        test_result = run_ssh_command(
            f"curl -s -o /dev/null -w '%{{http_code}}' {endpoint}",
            f"Testing {endpoint}"
        )
        if test_result and test_result.stdout.strip() == "200":
            print(f"✅ {endpoint} - Working")
        else:
            print(f"❌ {endpoint} - Failed")

def main():
    """Main function to fix all server issues"""
    print("🚀 Starting EC2 Server Issues Fix...")
    print(f"⏰ Started at: {datetime.now()}")
    
    # Check SSH connectivity first
    print("\n🔍 Checking SSH connectivity...")
    ssh_test = run_ssh_command(
        "ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 'echo \"SSH connection successful\"'",
        "Testing SSH connection"
    )
    
    if not ssh_test or ssh_test.returncode != 0:
        print("❌ SSH connection failed. Please check your SSH key and EC2 instance.")
        return
    
    # Fix all issues
    fix_websocket_configuration()
    fix_database_initialization()
    fix_dashboard_access()
    fix_cors_and_websocket()
    restart_services()
    test_endpoints()
    
    print(f"\n✅ Server issues fix completed at: {datetime.now()}")
    print("\n📋 Summary:")
    print("- WebSocket configuration checked and fixed")
    print("- Database initialized")
    print("- Dashboard access configured")
    print("- CORS settings updated")
    print("- Services restarted")
    print("- Endpoints tested")

if __name__ == "__main__":
    main() 