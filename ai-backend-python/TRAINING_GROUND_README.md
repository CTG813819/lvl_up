# Training Ground System

## Overview

The Training Ground System is a modern, AI-powered training facility that provides dynamic scenario generation and sandbox deployment capabilities. It runs on port 8002 and integrates seamlessly with the main backend system.

## Features

### 🎯 Automatic Difficulty Selection
- **Performance-Based Scenarios**: Automatically determines optimal difficulty based on sandbox success/failure patterns
- **Adaptive Learning**: Adjusts challenge levels based on recent performance metrics
- **Smart Progression**: Ensures continuous improvement through data-driven difficulty adjustment

### 🔬 Scenario Generation
- **Dynamic Content**: Generates unique scenarios based on current sandbox level
- **Real-Time Analysis**: Uses ML models to create relevant and challenging scenarios
- **Performance Tracking**: Monitors success rates and learning progress

### 🚀 Sandbox Deployment
- **Live Attack Simulation**: Deploys sandbox AI against generated scenarios
- **Real-Time Progress Tracking**: Monitors deployment status and results
- **Result Analysis**: Provides detailed feedback and learning insights

### ⚔️ Weapon System
- **Code Arsenal**: Save successful attack patterns as reusable weapons
- **Weapon Management**: Organize and categorize saved attack strategies
- **Deployment History**: Track weapon usage and effectiveness

## Architecture

### Backend Components

#### Training Ground Server (`training_ground_server.py`)
- **Port**: 8002
- **Framework**: FastAPI
- **Features**: 
  - Automatic difficulty selection
  - Performance-based scenario generation
  - Real-time deployment tracking
  - Weapon management system

#### Training Ground Router (`app/routers/training_ground.py`)
- **Endpoints**:
  - `POST /custody/training-ground/scenario` - Generate scenarios
  - `POST /custody/training-ground/deploy` - Deploy sandbox attacks
  - `POST /custody/weapons/save` - Save weapons
  - `GET /custody/weapons/list` - List weapons
  - `POST /custody/weapons/use` - Use weapons
  - `GET /custody/training-ground/status` - System status

#### Enhanced Sandbox AI Service (`app/services/sandbox_ai_service.py`)
- **ML Integration**: Comprehensive scikit-learn integration
- **Pattern Recognition**: Advanced pattern analysis capabilities
- **Autonomous Learning**: Self-improving attack strategies
- **SCKIPIT Integration**: Enhanced with SCKIPIT models

### Frontend Components

#### Modern Training Ground Screen (`lib/screens/training_ground_screen.dart`)
- **Matrix-Style UI**: Cyberpunk aesthetic with animated elements
- **Real-Time Updates**: Live status and progress indicators
- **Weapon Arsenal**: Visual weapon management interface
- **Performance Dashboard**: Statistics and metrics display

## Installation & Deployment

### Prerequisites
- Python 3.8+
- FastAPI
- PostgreSQL database
- Flutter (for frontend)

### Backend Setup

1. **Clone and Setup**:
```bash
cd ai-backend-python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Database Setup**:
```bash
# Ensure database is running and configured
python -m alembic upgrade head
```

3. **Start Training Ground Server**:
```bash
# Manual start
python training_ground_server.py

# Or use the startup script
./start_training_ground.sh
```

### EC2 Deployment

Use the provided deployment script:

```bash
# Windows
deploy_training_ground.bat

# Linux/Mac
./deploy_training_ground.sh
```

The deployment script will:
- Deploy all necessary files to EC2
- Set up systemd service for auto-start
- Configure firewall rules for port 8002
- Start the training ground server

### Frontend Integration

The Flutter app automatically connects to the training ground server on port 8002. Ensure the backend is running before using the training ground features.

## API Reference

### Generate Scenario
```http
POST /custody/training-ground/scenario
Content-Type: application/json

{
  "sandbox_level": 1,
  "auto_difficulty": true
}
```

**Response**:
```json
{
  "status": "success",
  "scenario": {
    "description": "Scenario description",
    "difficulty": "auto",
    "objectives": ["objective1", "objective2"]
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Deploy Sandbox Attack
```http
POST /custody/training-ground/deploy
Content-Type: application/json

{
  "scenario": {
    "description": "Scenario description",
    "difficulty": "auto"
  },
  "user_id": "user_123"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "result": "Attack result",
    "score": 85,
    "xp_awarded": 100,
    "learning_awarded": 50
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Save Weapon
```http
POST /custody/weapons/save
Content-Type: application/json

{
  "name": "SQL Injection Attack",
  "code": "attack_code_here",
  "description": "Effective SQL injection pattern",
  "user_id": "user_123"
}
```

## Configuration

### Environment Variables
```bash
# Training Ground Server
TRAINING_GROUND_PORT=8002
TRAINING_GROUND_HOST=0.0.0.0
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://username:password@localhost/dbname

# ML Models
ML_MODEL_PATH=./models/
```

### Systemd Service
The deployment creates a systemd service for auto-start:

```ini
[Unit]
Description=Training Ground Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python training_ground_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Monitoring & Maintenance

### Health Checks
```bash
# Check server health
curl http://localhost:8002/health

# Check service status
sudo systemctl status training-ground

# View logs
sudo journalctl -u training-ground -f
```

### Performance Monitoring
- **Success Rate Tracking**: Monitor scenario success rates
- **Difficulty Adjustment**: Review automatic difficulty selection
- **Weapon Effectiveness**: Track weapon usage and success rates
- **Learning Progress**: Monitor sandbox AI improvement

### Troubleshooting

#### Common Issues

1. **Server Won't Start**:
   - Check port availability: `netstat -tulpn | grep 8002`
   - Verify dependencies: `pip list | grep fastapi`
   - Check logs: `sudo journalctl -u training-ground -n 50`

2. **Database Connection Issues**:
   - Verify DATABASE_URL in environment
   - Check database service status
   - Test connection manually

3. **ML Model Loading Errors**:
   - Ensure model files exist in ML_MODEL_PATH
   - Check file permissions
   - Verify scikit-learn installation

#### Performance Optimization
- **Model Caching**: ML models are cached for faster loading
- **Connection Pooling**: Database connections are pooled
- **Async Processing**: All operations are asynchronous
- **Memory Management**: Automatic cleanup of unused resources

## Security Considerations

### Network Security
- **Firewall Rules**: Only port 8002 should be exposed
- **Authentication**: Implement proper authentication for production
- **Rate Limiting**: Consider implementing rate limiting for API endpoints

### Data Security
- **Weapon Storage**: Weapons are stored securely with user isolation
- **Scenario Isolation**: Each scenario is isolated and secure
- **Logging**: Comprehensive logging for audit trails

## Future Enhancements

### Planned Features
- **Multi-Player Mode**: Collaborative training scenarios
- **Advanced Analytics**: Detailed performance analytics
- **Custom Scenarios**: User-defined scenario creation
- **Integration APIs**: Third-party tool integration

### ML Improvements
- **Enhanced Models**: More sophisticated ML models
- **Real-Time Learning**: Continuous model improvement
- **Cross-AI Learning**: Knowledge sharing between AI systems

## Support

For issues and questions:
1. Check the logs: `sudo journalctl -u training-ground -f`
2. Review this documentation
3. Check the main backend logs for related issues
4. Contact the development team

## License

This system is part of the LVL_UP project and follows the same licensing terms. 