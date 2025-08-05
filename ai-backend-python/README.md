# LVL AI Backend

A comprehensive AI-powered backend system for the LVL (Level Up) application, designed for deployment on Railway with Neon database.

## Features

- **AI Agent Management**: Complete AI agent lifecycle management with learning and adaptation
- **Adversarial Testing**: Advanced testing system with dynamic difficulty scaling
- **Database Integration**: PostgreSQL integration with Neon database
- **Real-time Analytics**: Comprehensive metrics and analytics tracking
- **Token Management**: Intelligent token usage and fallback systems
- **Learning Systems**: Adaptive learning with XP and leveling mechanics

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database (Neon recommended)
- Railway account

### Environment Variables

Create a `.env` file with the following variables:

```env
DATABASE_URL=your_neon_database_url
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
JWT_SECRET_KEY=your_jwt_secret
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start the server
python start.py
```

### Railway Deployment

The application is configured for Railway deployment with:

- **Start Command**: `python start.py`
- **Health Check**: `/health` endpoint
- **Port**: Automatically configured via `PORT` environment variable
- **Database**: Neon PostgreSQL integration
- **Configuration**: See `RAILWAY_DEPLOYMENT.md` for detailed setup

#### Quick Railway Setup

1. **Prepare for deployment**:
   ```bash
   python deploy_to_railway.py
   ```

2. **Deploy to Railway**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and deploy
   railway login
   railway up
   ```

3. **Set environment variables** in Railway dashboard:
   - `DATABASE_URL`: Your Neon PostgreSQL connection string
   - `DEBUG`: false (for production)
   - Optional: AI service API keys

## API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `GET /docs` - API documentation (Swagger UI)

### AI Agent Endpoints
- `POST /agents/create` - Create new AI agent
- `GET /agents/{agent_id}` - Get agent details
- `PUT /agents/{agent_id}/update` - Update agent
- `DELETE /agents/{agent_id}` - Delete agent

### Testing Endpoints
- `POST /testing/adversarial` - Run adversarial tests
- `GET /testing/results` - Get test results
- `POST /testing/custody` - Run custody tests

### Analytics Endpoints
- `GET /analytics/metrics` - Get system metrics
- `GET /analytics/learning` - Get learning analytics
- `POST /analytics/track` - Track custom events

## Architecture

### Core Components

1. **AI Services** (`app/services/`)
   - Agent management and coordination
   - Learning systems and adaptation
   - Token management and fallback

2. **Routers** (`app/routers/`)
   - REST API endpoints
   - Request/response handling
   - Authentication and authorization

3. **Models** (`app/models/`)
   - Database models and schemas
   - Pydantic validation models
   - Data transfer objects

4. **Core** (`app/core/`)
   - Configuration management
   - Database connections
   - Security and authentication

### Database Schema

The system uses PostgreSQL with the following key tables:

- `agent_metrics` - AI agent performance metrics
- `learning_logs` - Learning and adaptation data
- `custody_tests` - Test results and analytics
- `proposals` - AI-generated proposals and suggestions

## Deployment

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Configure environment variables in Railway dashboard
3. Deploy automatically on push to main branch

### Environment Configuration

Required environment variables for Railway:

```env
DATABASE_URL=postgresql://user:password@host:port/database
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
JWT_SECRET_KEY=your-secret-key
RAILWAY_ENVIRONMENT=production
```

## Monitoring and Health Checks

The application includes comprehensive monitoring:

- **Health Check**: `/health` endpoint for Railway
- **Metrics**: Real-time performance metrics
- **Logging**: Structured logging with structlog
- **Error Tracking**: Comprehensive error handling and reporting

## Development

### Adding New Features

1. Create new router in `app/routers/`
2. Add corresponding service in `app/services/`
3. Update database models if needed
4. Add tests in `test/` directory
5. Update documentation

### Testing

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest test/test_agents.py

# Run with coverage
python -m pytest --cov=app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is part of the LVL (Level Up) system.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the documentation in `/docs`
- Review the deployment logs in Railway dashboard 