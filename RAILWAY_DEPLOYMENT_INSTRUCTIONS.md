# Railway Deployment Instructions

## Overview
This is a unified FastAPI backend designed for deployment on Railway. All configuration conflicts have been resolved and the deployment is now streamlined.

## Key Files for Railway Deployment

### 1. `main_unified.py` - The Main Application
- **This is the ONLY file Railway should use to start the application**
- Contains all endpoints including `/ping`, `/health`, and `/api/health`
- Properly configured to read Railway's `$PORT` environment variable
- All routers and services are consolidated here

### 2. `railway.toml` - Railway Configuration
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn main_unified:app --host 0.0.0.0 --port $PORT --log-level info"
healthcheckPath = "/ping"
healthcheckTimeout = 60
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

### 3. `nixpacks.toml` - Build Configuration
```toml
[phases.setup]
nixPkgs = ["python312", "gcc", "curl"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "uvicorn main_unified:app --host 0.0.0.0 --port $PORT --log-level info"
```

### 4. `Procfile` - Backup Startup Command
```
web: uvicorn main_unified:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
```

## Health Check Endpoints

The application provides multiple health check endpoints:

- **`/ping`** - Ultra-simple ping endpoint (used by Railway health checks)
- **`/health`** - Main health check with system information  
- **`/api/health`** - API-specific health check

## Environment Variables

Railway automatically provides:
- `PORT` - The port Railway assigns for your service
- `RAILWAY_ENVIRONMENT_NAME` - The environment name (production/staging)

## Testing Before Deployment

Run the readiness test:
```bash
python test_railway_ready.py
```

This will validate:
- All configuration files are correct
- Required endpoints exist
- Local startup works
- Dependencies are available

## Deployment Steps

1. **Commit all changes**:
   ```bash
   git add .
   git commit -m "Fix Railway deployment configuration"
   ```

2. **Push to Railway-connected repository**:
   ```bash
   git push origin main
   ```

3. **Railway will automatically**:
   - Detect the `railway.toml` configuration
   - Use Nixpacks to build the container
   - Start the application with the correct command
   - Run health checks on `/ping` endpoint

## Port Configuration

✅ **CORRECT**: Railway will set the `$PORT` environment variable dynamically
❌ **WRONG**: Hard-coding port 8000 (Railway uses random ports)

The application is configured to:
1. Read `$PORT` environment variable
2. Fall back to port 8000 for local development
3. Bind to `0.0.0.0` to accept external connections

## What Was Fixed

1. **Port Conflicts**: All configurations now use `$PORT` instead of hard-coded 8000
2. **Health Check Path**: Unified to use `/ping` endpoint across all configs
3. **Startup Command**: Standardized to `uvicorn main_unified:app`
4. **Conflicting Files**: Removed multiple startup scripts that could cause confusion
5. **Railway Detection**: Application properly detects Railway environment

## Troubleshooting

If deployment still fails:

1. **Check Railway logs** for specific error messages
2. **Verify environment variables** are being set correctly  
3. **Test locally** with `PORT=8000 python -m uvicorn main_unified:app --host 0.0.0.0 --port 8000`
4. **Ensure database connection** is configured for Railway's database

## Files Removed

The following conflicting files were removed to prevent confusion:
- `start.py`
- `start_unified_server.py` 
- `start_railway.py`
- `start_server.py`
- `start_app.py`
- `railway_start.py`

Only `main_unified.py` should be used for starting the application.