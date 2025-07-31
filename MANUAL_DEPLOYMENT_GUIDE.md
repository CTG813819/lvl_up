# Manual Deployment Guide for Imperium Master Orchestrator

## Your EC2 Configuration
- **EC2 Host**: `ec2-34-202-215-209.compute-1.amazonaws.com`
- **User**: `ubuntu`
- **SSH Key**: `C:\projects\lvl_up\New.pem`
- **Project Directory**: `/home/ubuntu/`
- **Backend Directory**: `/home/ubuntu/ai-backend-python/`

## Option 1: Automated Deployment (Recommended)

### Step 1: Run the Automated Script
```bash
python deploy_to_ec2.py
```

This script will:
- ✅ Upload all necessary files
- ✅ Create required directories
- ✅ Set up the systemd service
- ✅ Start the Imperium service
- ✅ Test the deployment

## Option 2: Manual Deployment

### Step 1: Upload the Enhanced Files

```bash
# Upload the enhanced SQL models
scp -i "C:\projects\lvl_up\New.pem" "C:\projects\lvl_up\ai-backend-python\app\models\sql_models.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/app/models/

# Upload the enhanced Imperium learning controller
scp -i "C:\projects\lvl_up\New.pem" "C:\projects\lvl_up\ai-backend-python\app\services\imperium_learning_controller.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/app/services/

# Upload the enhanced router
scp -i "C:\projects\lvl_up\New.pem" "C:\projects\lvl_up\ai-backend-python\app\routers\imperium_learning.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/app/routers/

# Upload the database migration script
scp -i "C:\projects\lvl_up\New.pem" "C:\projects\lvl_up\ai-backend-python\create_imperium_tables.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
```

### Step 2: SSH into EC2 and Set Up Directories

```bash
ssh -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com
```

Once connected, run:
```bash
# Navigate to project directory
cd /home/ubuntu

# Create necessary directories if they don't exist
mkdir -p ai-backend-python/app/models
mkdir -p ai-backend-python/app/services
mkdir -p ai-backend-python/app/routers
mkdir -p ai-backend-python/app/core

# Check if main.py exists, if not create it
if [ ! -f ai-backend-python/app/main.py ]; then
    cat > ai-backend-python/app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

# Create FastAPI app
app = FastAPI(title="Imperium Master Orchestrator", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
try:
    from app.routers import imperium_learning
    app.include_router(imperium_learning.router)
    print("✅ Imperium learning router loaded")
except Exception as e:
    print(f"⚠️ Could not load imperium_learning router: {e}")

@app.get("/")
async def root():
    return {"message": "Imperium Master Orchestrator is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Imperium Master Orchestrator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
fi
```

### Step 3: Run Database Migration

```bash
# Navigate to backend directory
cd /home/ubuntu/ai-backend-python

# Run the database migration
python create_imperium_tables.py
```

### Step 4: Create Systemd Service

```bash
# Create the systemd service file
sudo tee /etc/systemd/system/imperium_master.service > /dev/null << EOF
[Unit]
Description=Imperium Master Orchestrator
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable imperium_master
sudo systemctl start imperium_master
```

### Step 5: Verify Deployment

```bash
# Check service status
sudo systemctl status imperium_master

# View logs
sudo journalctl -u imperium_master -f

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/api/imperium/status
```

## Testing the Deployment

### Test from Your Local Machine

```bash
# Test basic endpoints
curl http://ec2-34-202-215-209.compute-1.amazonaws.com:8000/
curl http://ec2-34-202-215-209.compute-1.amazonaws.com:8000/health
curl http://ec2-34-202-215-209.compute-1.amazonaws.com:8000/api/imperium/status

# Test persistence endpoints
curl http://ec2-34-202-215-209.compute-1.amazonaws.com:8000/api/imperium/persistence/agent-metrics
curl http://ec2-34-202-215-209.compute-1.amazonaws.com:8000/api/imperium/persistence/learning-cycles

# Test agent registration
curl -X POST http://ec2-34-202-215-209.compute-1.amazonaws.com:8000/api/imperium/agents/register \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "test_agent", "agent_type": "TestAI", "priority": "high"}'
```

### Run the Test Suite

```bash
# Upload the test script
scp -i "C:\projects\lvl_up\New.pem" "C:\projects\lvl_up\test_imperium_master.py" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/

# SSH into EC2 and run tests
ssh -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com
cd /home/ubuntu
python test_imperium_master.py
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status imperium_master

# View detailed logs
sudo journalctl -u imperium_master -f

# Check if port 8000 is available
sudo netstat -tlnp | grep :8000

# Check if uvicorn is installed
which uvicorn
```

### Database Connection Issues

```bash
# Check if database is accessible
python -c "from app.core.database import init_database; import asyncio; asyncio.run(init_database())"

# Check environment variables
echo $DATABASE_URL
```

### File Permission Issues

```bash
# Fix file permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/ai-backend-python/
sudo chmod -R 755 /home/ubuntu/ai-backend-python/
```

### Port Already in Use

```bash
# Check what's using port 8000
sudo lsof -i :8000

# Kill the process if needed
sudo kill -9 <PID>
```

## Useful Commands

### Service Management
```bash
# Start service
sudo systemctl start imperium_master

# Stop service
sudo systemctl stop imperium_master

# Restart service
sudo systemctl restart imperium_master

# Enable auto-start
sudo systemctl enable imperium_master

# Disable auto-start
sudo systemctl disable imperium_master
```

### Logs
```bash
# View real-time logs
sudo journalctl -u imperium_master -f

# View recent logs
sudo journalctl -u imperium_master -n 50

# View logs since boot
sudo journalctl -u imperium_master -b
```

### API Testing
```bash
# Test all endpoints
curl http://ec2-34-202-215-209.compute-1.amazonaws.com:8000/api/imperium/status
curl http://ec2-34-202-215-209.compute-1.amazonaws.com:8000/api/imperium/agents
curl http://ec2-34-202-215-209.compute-1.amazonaws.com:8000/api/imperium/persistence/agent-metrics
```

## Success Indicators

✅ **Service is running**: `sudo systemctl status imperium_master` shows "active (running)"

✅ **API responds**: `curl http://localhost:8000/` returns JSON response

✅ **Database tables created**: `python create_imperium_tables.py` runs without errors

✅ **All endpoints accessible**: Test suite passes all tests

✅ **Logs show no errors**: `sudo journalctl -u imperium_master` shows clean startup

## Next Steps

1. **Test the API**: Use the test script to verify all functionality
2. **Monitor Performance**: Check logs and system resources
3. **Configure Database**: Set up proper database connection if needed
4. **Set Up Monitoring**: Configure alerts and monitoring
5. **Scale if Needed**: Add load balancing and scaling as required

## Support

If you encounter issues:
1. Check the logs: `sudo journalctl -u imperium_master -f`
2. Verify file permissions and ownership
3. Check database connectivity
4. Ensure all dependencies are installed
5. Review the troubleshooting section above 