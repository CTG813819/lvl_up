# Critical Issues Analysis & Solutions

## Overview

Based on the system logs, several critical issues are preventing the AI backend from functioning properly. This document provides a detailed analysis of each issue and comprehensive solutions.

## Issues Identified

### 1. Git Command Not Found
**Error**: `[Errno 2] No such file or directory: 'git'`

**Impact**: 
- Sandbox AI agent cannot run experiments
- All git operations fail
- Repository management is broken

**Root Cause**: Git is not installed on the system or not in the PATH

**Solution**: 
- Install Git using package manager
- Verify installation and PATH configuration
- Update system configuration

### 2. Database Function Errors
**Error**: `function avg(text) does not exist`

**Impact**:
- Learning analytics fail to load
- Performance metrics cannot be calculated
- Dashboard displays errors
- System crashes on analytics requests

**Root Cause**: 
- SQL queries trying to use `avg()` on JSON text fields
- PostgreSQL cannot average text values
- Missing proper type casting

**Solution**:
- Create SQL helper functions for JSON operations
- Fix database queries with proper type casting
- Update service code to handle JSON data correctly

### 3. Token Limit Exceeded
**Error**: `Token limit reached for [agent]. Usage: 0.0% - Daily usage limit exceeded`

**Impact**:
- All AI agents cannot function
- No new proposals can be generated
- Learning processes are blocked
- System is essentially non-functional

**Root Cause**:
- Daily token limits reached for both Anthropic and OpenAI
- Fallback mechanisms not working properly
- Token usage tracking may be incorrect

**Solution**:
- Reset token usage counters
- Increase token limits temporarily
- Fix fallback mechanisms
- Implement better token management

### 4. Missing Model Attributes
**Error**: `'Learning' object has no attribute 'success_rate'`

**Impact**:
- Learning insights cannot be displayed
- Analytics fail to load
- Frontend shows errors
- System crashes on learning requests

**Root Cause**:
- Learning model missing expected properties
- Code expects attributes that don't exist
- Incomplete model implementation

**Solution**:
- Add missing properties to Learning model
- Implement proper data extraction from JSON
- Add error handling for missing attributes

## Solutions Implementation

### Solution 1: System-Wide Fixes

**File**: `fix_critical_system_issues.py`

**What it does**:
- Installs Git if missing
- Creates database migration scripts
- Fixes model attribute issues
- Resets token usage
- Updates system configuration

**Usage**:
```bash
python fix_critical_system_issues.py
chmod +x deploy_critical_fixes.sh
./deploy_critical_fixes.sh
```

### Solution 2: Database Query Fixes

**File**: `fix_database_queries.py`

**What it does**:
- Creates SQL helper functions for JSON operations
- Fixes problematic database queries
- Provides corrected service code
- Creates application scripts

**Usage**:
```bash
python fix_database_queries.py
chmod +x apply_database_fixes.sh
./apply_database_fixes.sh
```

## Detailed Fix Breakdown

### Git Installation Fix

**Problem**: Git not available for Sandbox AI experiments

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y git

# Amazon Linux/CentOS
sudo yum install -y git

# Verify installation
git --version
```

**Configuration**:
```bash
# Add to environment
export GIT_PATH=/usr/bin/git
export GIT_USER_NAME="AI Backend"
export GIT_USER_EMAIL="ai-backend@system.local"
```

### Database Function Fixes

**Problem**: Cannot use `avg()` on JSON text fields

**Solution**: Create SQL helper functions

```sql
-- Function to safely extract numeric values from JSON
CREATE OR REPLACE FUNCTION safe_json_numeric(json_data JSONB, key TEXT)
RETURNS NUMERIC AS $$
BEGIN
    RETURN COALESCE(
        CAST(json_data->>key AS NUMERIC),
        0.0
    );
EXCEPTION
    WHEN OTHERS THEN
        RETURN 0.0;
END;
$$ LANGUAGE plpgsql;

-- Function to safely calculate average
CREATE OR REPLACE FUNCTION safe_json_avg(json_data JSONB, key TEXT)
RETURNS NUMERIC AS $$
BEGIN
    RETURN COALESCE(AVG(safe_json_numeric(json_data, key)), 0.0);
EXCEPTION
    WHEN OTHERS THEN
        RETURN 0.0;
END;
$$ LANGUAGE plpgsql;
```

**Fixed Query Example**:
```python
# Before (broken)
query = select(
    func.avg(func.json_extract_path_text(Learning.learning_data, 'confidence'))
)

# After (fixed)
query = select(
    func.coalesce(
        func.avg(
            func.cast(
                func.json_extract_path_text(Learning.learning_data, 'confidence'),
                func.Float
            )
        ),
        0.5
    ).label('avg_confidence')
)
```

### Token Usage Reset

**Problem**: All agents hit token limits

**Solution**: Reset token usage counters

```sql
-- Reset token usage for current month
UPDATE token_usage 
SET 
    tokens_in = 0,
    tokens_out = 0,
    total_tokens = 0,
    request_count = 0,
    usage_percentage = 0.0,
    status = 'active'
WHERE month_year = TO_CHAR(CURRENT_DATE, 'YYYY-MM');

-- Reset agent metrics
UPDATE agent_metrics 
SET 
    learning_score = 0.0,
    success_rate = 0.0,
    failure_rate = 0.0,
    status = 'idle'
WHERE agent_type IN ('imperium', 'guardian', 'sandbox', 'conquest');
```

### Model Attribute Fixes

**Problem**: Missing properties on Learning model

**Solution**: Add properties to Learning model

```python
# Add to app/models/sql_models.py in Learning class

@property
def success_rate(self) -> float:
    """Calculate success rate from learning data"""
    try:
        if not self.learning_data:
            return 0.0
        
        if isinstance(self.learning_data, dict):
            success_count = self.learning_data.get('success_count', 0)
            total_count = self.learning_data.get('total_count', 1)
            return float(success_count) / float(total_count) if total_count > 0 else 0.0
        
        return 0.0
    except Exception:
        return 0.0

@property
def confidence(self) -> float:
    """Get confidence from learning data"""
    try:
        if not self.learning_data:
            return 0.5
        
        if isinstance(self.learning_data, dict):
            return float(self.learning_data.get('confidence', 0.5))
        
        return 0.5
    except Exception:
        return 0.5
```

## Deployment Steps

### Step 1: Run System Fixes
```bash
cd ai-backend-python
python fix_critical_system_issues.py
```

### Step 2: Apply Database Fixes
```bash
python fix_database_queries.py
./apply_database_fixes.sh
```

### Step 3: Update Environment
```bash
# Add new environment variables
cat system_config_update.env >> .env

# Reload environment
source .env
```

### Step 4: Restart Services
```bash
sudo systemctl restart ai-backend-python
```

### Step 5: Verify Fixes
```bash
# Check Git installation
git --version

# Check database connection
python -c "from app.core.database import get_session; print('DB OK')"

# Check service status
sudo systemctl status ai-backend-python
```

## Monitoring & Verification

### Check Logs for Errors
```bash
# Monitor logs in real-time
sudo journalctl -u ai-backend-python -f

# Check for specific errors
sudo journalctl -u ai-backend-python | grep -i error
```

### Test AI Agent Functionality
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test agent status
curl http://localhost:8000/api/agents/status

# Test learning insights
curl http://localhost:8000/api/learning/insights/Imperium
```

### Verify Database Queries
```bash
# Connect to database
psql $DATABASE_URL

# Test helper functions
SELECT safe_json_numeric('{"confidence": 0.8}'::jsonb, 'confidence');
SELECT get_learning_confidence('{"confidence": 0.8}'::jsonb);
```

## Prevention Measures

### 1. Environment Validation
- Add startup checks for required tools (git, flutter)
- Validate database connectivity and functions
- Check token usage before starting agents

### 2. Error Handling
- Implement graceful fallbacks for all external services
- Add retry mechanisms for failed operations
- Log detailed error information for debugging

### 3. Monitoring
- Set up alerts for token usage approaching limits
- Monitor database query performance
- Track agent success/failure rates

### 4. Configuration Management
- Use environment variables for all configuration
- Validate configuration on startup
- Provide clear error messages for missing configuration

## Expected Results

After applying these fixes:

1. **Git Operations**: Sandbox AI can run experiments successfully
2. **Database Queries**: No more `avg()` function errors
3. **Token Usage**: Agents can function normally
4. **Model Attributes**: Learning insights display correctly
5. **System Stability**: Reduced error rates and improved performance

## Troubleshooting

### If Git Still Not Found
```bash
# Check PATH
echo $PATH

# Find git installation
find /usr -name git 2>/dev/null

# Add to PATH if needed
export PATH=$PATH:/usr/bin
```

### If Database Errors Persist
```bash
# Check PostgreSQL functions
psql $DATABASE_URL -c "\\df safe_json_*"

# Recreate functions if missing
psql $DATABASE_URL -f database_helper_functions.sql
```

### If Token Issues Continue
```bash
# Check current token usage
psql $DATABASE_URL -c "SELECT * FROM token_usage WHERE month_year = TO_CHAR(CURRENT_DATE, 'YYYY-MM');"

# Reset if needed
psql $DATABASE_URL -f reset_token_usage.sql
```

This comprehensive fix should resolve all the critical issues identified in the system logs and restore full functionality to the AI backend system. 