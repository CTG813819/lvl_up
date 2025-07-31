# Railway Deployment Guide

This guide explains how to deploy the AI Backend to Railway with Neon database.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Neon Database**: Create a Neon PostgreSQL database at [neon.tech](https://neon.tech)
3. **GitHub Repository**: Your code should be in a GitHub repository

## Deployment Steps

### 1. Connect to Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select this repository

### 2. Configure Environment Variables

In your Railway project dashboard, add these environment variables:

#### Database Configuration
```
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require
DATABASE_NAME=your_database_name
```

#### Server Configuration
```
PORT=8000
HOST=0.0.0.0
DEBUG=false
```

#### AI Services (Optional)
```
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
```

#### GitHub Integration (Optional)
```
GITHUB_TOKEN=your_github_token
GITHUB_REPO=your_repo_name
GITHUB_USERNAME=your_username
GITHUB_EMAIL=your_email
```

#### AWS (Optional - for file storage)
```
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
```

#### Twilio (Optional - for notifications)
```
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number
ADMIN_PHONE_NUMBER=your_admin_number
```

### 3. Neon Database Setup

1. Create a Neon database at [neon.tech](https://neon.tech)
2. Get your connection string from the Neon dashboard
3. Set the `DATABASE_URL` environment variable in Railway
4. The database will be automatically initialized on first deployment

### 4. Deploy

1. Railway will automatically detect the Python project
2. It will use the `railway.json` configuration
3. The app will start using `python start.py`
4. Health checks will be performed at `/health`

## Configuration Files

### railway.json
- Configures the build and deployment settings
- Specifies health check endpoint and timeout
- Sets restart policy for reliability

### Procfile
- Alternative deployment method
- Specifies the web process command

### runtime.txt
- Specifies Python version (3.11.7)
- Ensures consistent runtime environment

### start.py
- Entry point for the application
- Reads PORT from environment (Railway sets this)
- Starts uvicorn server on 0.0.0.0:PORT

## Health Checks

The application provides multiple health check endpoints:

- `/health` - Simple health check (used by Railway)
- `/api/health` - Detailed health check
- `/api/database/health` - Database connection health
- `/api/status` - System status

## Monitoring

Railway provides:
- Automatic health checks
- Log streaming
- Performance metrics
- Automatic restarts on failure

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify `DATABASE_URL` is correct
   - Ensure Neon database is active
   - Check SSL mode in connection string

2. **Port Issues**
   - Railway automatically sets PORT environment variable
   - Application reads PORT from environment
   - Default fallback is port 8000

3. **Dependencies**
   - All dependencies are in `requirements.txt`
   - Railway uses Nixpacks builder
   - Python 3.11.7 is specified in `runtime.txt`

4. **Health Check Failures**
   - Verify `/health` endpoint is accessible
   - Check application logs in Railway dashboard
   - Ensure all required environment variables are set

### Logs

View logs in Railway dashboard:
1. Go to your project
2. Click on the service
3. Go to "Deployments" tab
4. Click on latest deployment
5. View logs for debugging

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | Neon PostgreSQL connection string |
| PORT | No | Port (set by Railway) |
| HOST | No | Host (default: 0.0.0.0) |
| DEBUG | No | Debug mode (default: false) |
| OPENAI_API_KEY | No | OpenAI API key |
| ANTHROPIC_API_KEY | No | Anthropic API key |
| GITHUB_TOKEN | No | GitHub personal access token |

## Database Migrations

The application automatically:
1. Initializes the database on startup
2. Creates all required tables
3. Sets up indexes for performance
4. Handles connection pooling

## Security

- CORS is configured for production
- Security headers are automatically added
- Environment variables are encrypted
- SSL is enforced for database connections

## Scaling

Railway supports:
- Automatic scaling based on traffic
- Multiple replicas
- Load balancing
- Zero-downtime deployments

## Cost Optimization

- Use Railway's free tier for development
- Monitor usage in Railway dashboard
- Set up alerts for usage limits
- Consider Neon's free tier for database 