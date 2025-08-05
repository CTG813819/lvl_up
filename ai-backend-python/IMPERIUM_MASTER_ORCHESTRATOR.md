# Imperium Master Orchestrator

## Overview

The Imperium Master Orchestrator is the central nervous system of the AI learning ecosystem. It coordinates, monitors, and orchestrates the learning activities of all AI agents while maintaining comprehensive persistence and analytics capabilities.

## Key Features

### 🎯 Master Orchestration
- **Centralized Learning Control**: Coordinates learning cycles across all AI agents
- **Agent Registration & Management**: Handles agent lifecycle and status tracking
- **Priority-Based Scheduling**: Manages learning priorities and resource allocation
- **Real-Time Monitoring**: Tracks agent performance and learning progress

### 🗄️ Database Persistence
- **Agent Metrics Storage**: Persistent storage of agent learning metrics
- **Learning Cycle Tracking**: Complete history of learning cycles and outcomes
- **Structured Event Logging**: Comprehensive logging of all learning events
- **Internet Learning Results**: Storage of internet-based learning outcomes

### 📊 Analytics & Insights
- **Learning Analytics**: Comprehensive analytics with filtering capabilities
- **Performance Metrics**: Success rates, failure rates, and learning patterns
- **Impact Analysis**: Measurement of learning impact and effectiveness
- **Trend Analysis**: Historical data analysis for improvement insights

### 🌐 Internet-Based Learning
- **Multi-Source Learning**: Integration with StackOverflow, GitHub, ArXiv, Medium
- **Trusted Source Management**: Curated list of reliable learning sources
- **Relevance Scoring**: Intelligent scoring of learning content relevance
- **Learning Value Calculation**: Assessment of learning value per agent type

## Architecture

### Core Components

```
ImperiumLearningController
├── Agent Management
│   ├── Registration & Lifecycle
│   ├── Status Tracking
│   └── Priority Management
├── Learning Orchestration
│   ├── Cycle Management
│   ├── Scheduler
│   └── Resource Allocation
├── Persistence Layer
│   ├── Agent Metrics
│   ├── Learning Cycles
│   ├── Event Logs
│   └── Internet Results
└── Analytics Engine
    ├── Performance Metrics
    ├── Impact Analysis
    └── Trend Detection
```

### Database Schema

#### Agent Metrics Table
```sql
CREATE TABLE agent_metrics (
    id UUID PRIMARY KEY,
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    learning_score FLOAT DEFAULT 0.0,
    success_rate FLOAT DEFAULT 0.0,
    failure_rate FLOAT DEFAULT 0.0,
    total_learning_cycles INTEGER DEFAULT 0,
    last_learning_cycle TIMESTAMP,
    last_success TIMESTAMP,
    last_failure TIMESTAMP,
    learning_patterns JSON DEFAULT '[]',
    improvement_suggestions JSON DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'idle',
    is_active BOOLEAN DEFAULT TRUE,
    priority VARCHAR(20) DEFAULT 'medium',
    capabilities JSON,
    config JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Learning Cycles Table
```sql
CREATE TABLE learning_cycles (
    id UUID PRIMARY KEY,
    cycle_id VARCHAR(100) UNIQUE NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    participating_agents JSON DEFAULT '[]',
    total_learning_value FLOAT DEFAULT 0.0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    insights_generated JSON DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'learning',
    metadata JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Learning Logs Table
```sql
CREATE TABLE learning_logs (
    id UUID PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    agent_id VARCHAR(100),
    agent_type VARCHAR(50),
    topic VARCHAR(200),
    results_count INTEGER DEFAULT 0,
    results_sample JSON,
    insights JSON,
    error_message TEXT,
    processing_time FLOAT,
    impact_score FLOAT DEFAULT 0.0,
    event_data JSON,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Internet Learning Results Table
```sql
CREATE TABLE internet_learning_results (
    id UUID PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    topic VARCHAR(200) NOT NULL,
    source VARCHAR(100) NOT NULL,
    title VARCHAR(500),
    url VARCHAR(1000),
    summary TEXT,
    content TEXT,
    relevance_score FLOAT DEFAULT 0.0,
    learning_value FLOAT DEFAULT 0.0,
    insights_extracted JSON,
    applied_to_agent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API Endpoints

### Core Orchestration Endpoints

#### Agent Management
- `GET /api/imperium/agents` - Get all registered agents
- `GET /api/imperium/agents/{agent_id}` - Get specific agent metrics
- `POST /api/imperium/agents/register` - Register new agent
- `DELETE /api/imperium/agents/{agent_id}` - Unregister agent
- `POST /api/imperium/agents/{agent_id}/pause` - Pause agent learning
- `POST /api/imperium/agents/{agent_id}/resume` - Resume agent learning

#### Learning Cycles
- `GET /api/imperium/cycles` - Get learning cycles
- `POST /api/imperium/cycles/trigger` - Trigger new learning cycle

#### System Status
- `GET /api/imperium/status` - Get overall system status
- `GET /api/imperium/dashboard` - Get learning dashboard

### Persistence Endpoints

#### Agent Metrics Persistence
- `GET /api/imperium/persistence/agent-metrics` - Get persisted agent metrics
- `POST /api/imperium/persistence/agent-metrics` - Persist agent metrics

#### Learning Cycles Persistence
- `GET /api/imperium/persistence/learning-cycles` - Get persisted learning cycles

#### Analytics
- `GET /api/imperium/persistence/learning-analytics` - Get comprehensive analytics

#### Event Logging
- `POST /api/imperium/persistence/log-learning-event` - Log learning event
- `POST /api/imperium/persistence/internet-learning-result` - Persist internet learning result

### Internet Learning Endpoints

#### Learning Management
- `POST /api/imperium/internet-learning/trigger` - Trigger internet learning
- `POST /api/imperium/internet-learning/agent/{agent_id}` - Agent-specific learning
- `GET /api/imperium/internet-learning/log` - Get learning log
- `GET /api/imperium/internet-learning/impact` - Get learning impact

#### Configuration
- `GET /api/imperium/internet-learning/interval` - Get learning interval
- `POST /api/imperium/internet-learning/interval` - Set learning interval
- `GET /api/imperium/internet-learning/topics` - Get learning topics
- `POST /api/imperium/internet-learning/topics` - Set learning topics

#### Trusted Sources
- `GET /api/imperium/trusted-sources` - List trusted sources
- `POST /api/imperium/trusted-sources` - Add trusted source
- `DELETE /api/imperium/trusted-sources` - Remove trusted source

## Usage Examples

### Registering an Agent
```bash
curl -X POST http://localhost:8000/api/imperium/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my_ai_agent",
    "agent_type": "CustomAI",
    "priority": "high"
  }'
```

### Triggering a Learning Cycle
```bash
curl -X POST http://localhost:8000/api/imperium/cycles/trigger
```

### Persisting Agent Metrics
```bash
curl -X POST http://localhost:8000/api/imperium/persistence/agent-metrics \
  -H "Content-Type: application/json" \
  -d '"imperium"'
```

### Logging a Learning Event
```bash
curl -X POST http://localhost:8000/api/imperium/persistence/log-learning-event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "internet_learning",
    "agent_id": "imperium",
    "agent_type": "Imperium",
    "topic": "AI orchestration",
    "results_count": 5,
    "impact_score": 0.8
  }'
```

### Getting Learning Analytics
```bash
curl "http://localhost:8000/api/imperium/persistence/learning-analytics?agent_id=imperium&event_types=internet_learning,agent_registration"
```

## Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Learning Configuration
LEARNING_CYCLE_INTERVAL=300  # 5 minutes
MAX_CONCURRENT_LEARNING=3
LEARNING_TIMEOUT=600  # 10 minutes

# Internet Learning
INTERNET_LEARNING_INTERVAL=1800  # 30 minutes
MAX_INTERNET_RESULTS=5

# Logging
LOG_LEVEL=INFO
```

### Agent Topics Configuration
```python
# Default agent learning topics
_agent_topics = {
    "imperium": [
        "meta-learning AI",
        "autonomous agent orchestration", 
        "AI self-improvement",
        "AI governance"
    ],
    "guardian": [
        "AI security best practices",
        "AI code quality",
        "vulnerability detection",
        "secure coding"
    ],
    "sandbox": [
        "AI experimentation",
        "novel ML techniques",
        "rapid prototyping AI",
        "AI innovation"
    ],
    "conquest": [
        "app development AI",
        "AI-driven app design",
        "mobile AI frameworks",
        "AI UX optimization"
    ]
}
```

## Deployment

### Prerequisites
- Python 3.8+
- PostgreSQL database
- EC2 instance (for production deployment)

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run database migration
python create_imperium_tables.py

# Start the service
uvicorn app.main:app --reload
```

### Production Deployment
```bash
# Run deployment script
python deploy_imperium_master.py

# Or manual deployment
# 1. Upload files to EC2
# 2. Run database migration
# 3. Update systemd service
# 4. Restart service
```

### Systemd Service
```ini
[Unit]
Description=Imperium Master Orchestrator
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory=/home/ubuntu/lvl_up/ai-backend-python
Environment=PATH=/home/ubuntu/lvl_up/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/lvl_up/ai-backend-python/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Monitoring & Maintenance

### Service Management
```bash
# Check service status
sudo systemctl status imperium_master

# View logs
sudo journalctl -u imperium_master -f

# Restart service
sudo systemctl restart imperium_master

# Enable auto-start
sudo systemctl enable imperium_master
```

### Database Maintenance
```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE tablename LIKE '%imperium%';

-- Clean old logs (older than 30 days)
DELETE FROM learning_logs 
WHERE created_at < NOW() - INTERVAL '30 days';

-- Analyze performance
ANALYZE agent_metrics;
ANALYZE learning_cycles;
ANALYZE learning_logs;
ANALYZE internet_learning_results;
```

### Performance Optimization
- Monitor database query performance
- Implement connection pooling
- Use appropriate indexes
- Regular database maintenance
- Monitor memory usage

## Troubleshooting

### Common Issues

#### Service Won't Start
1. Check logs: `sudo journalctl -u imperium_master -f`
2. Verify database connection
3. Check file permissions
4. Validate configuration

#### Database Connection Issues
1. Verify DATABASE_URL environment variable
2. Check database server status
3. Validate network connectivity
4. Check SSL configuration

#### API Endpoints Not Responding
1. Verify service is running
2. Check port configuration
3. Validate firewall settings
4. Test with curl

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with debug output
uvicorn app.main:app --reload --log-level debug
```

## Future Enhancements

### Planned Features
- **Machine Learning Integration**: ML-based learning optimization
- **Advanced Analytics**: Predictive analytics and trend forecasting
- **Plugin System**: Extensible plugin architecture
- **Real-Time Notifications**: WebSocket-based real-time updates
- **Multi-Tenant Support**: Support for multiple organizations
- **Advanced Security**: Enhanced security and access control

### Performance Improvements
- **Caching Layer**: Redis-based caching
- **Async Processing**: Background task processing
- **Load Balancing**: Horizontal scaling support
- **Database Sharding**: Multi-database support

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Standards
- Follow PEP 8 style guidelines
- Add type hints
- Include docstrings
- Write unit tests
- Update documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide
- Contact the development team 