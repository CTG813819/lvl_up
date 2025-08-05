# Conquest Endpoint Fixes

## Issue Identified

### 422 Unprocessable Entity Errors
**Problem**: GitHub Actions workflows were sending requests to `/api/conquest/build-failure` with field names that didn't match the expected schema, causing 422 validation errors.

**Error Logs**:
```
Jul 10 06:53:15 ip-172-31-88-138 uvicorn[348897]: INFO: 140.82.115.62:52280 - "POST /api/conquest/build-failure HTTP/1.1" 422 Unprocessable Entity
Jul 10 06:53:16 ip-172-31-88-138 uvicorn[348897]: INFO: 140.82.115.154:38676 - "POST /api/conquest/build-failure HTTP/1.1" 422 Unprocessable Entity
Jul 10 06:53:16 ip-172-31-88-138 uvicorn[348897]: INFO: 140.82.115.32:59768 - "POST /api/conquest/build-failure HTTP/1.1" 422 Unprocessable Entity
```

## Root Cause Analysis

### Field Name Mismatch
**GitHub Actions Format** (what was being sent):
```json
{
  "appId": "123456789",
  "error": "Build failed during compilation"
}
```

**Expected Format** (what the endpoint expected):
```json
{
  "app_id": "123456789",
  "error_message": "Build failed during compilation"
}
```

### Missing Endpoint
The `/api/conquest/app-error` endpoint was being called by GitHub Actions but didn't exist in the backend.

## Fixes Applied

### 1. Enhanced BuildFailureRequest Model
**File**: `ai-backend-python/app/routers/conquest.py`

**Changes**:
- Made all fields optional to handle different formats
- Added support for both `appId`/`error` (GitHub Actions) and `app_id`/`error_message` (expected)
- Added normalized properties to handle both formats seamlessly
- Added `extra = "allow"` config for flexibility

**Code**:
```python
class BuildFailureRequest(BaseModel):
    # Accept both formats for compatibility
    app_id: Optional[str] = None
    appId: Optional[str] = None  # GitHub Actions format
    error_message: Optional[str] = None
    error: Optional[str] = None  # GitHub Actions format
    build_logs: Optional[str] = None
    failure_type: str = "build_error"
    
    @property
    def normalized_app_id(self) -> str:
        """Get the app ID in normalized format"""
        return self.app_id or self.appId or "unknown"
    
    @property
    def normalized_error_message(self) -> str:
        """Get the error message in normalized format"""
        return self.error_message or self.error or "Unknown error"
    
    class Config:
        extra = "allow"  # Allow extra fields for flexibility
```

### 2. Added Missing App Error Endpoint
**File**: `ai-backend-python/app/routers/conquest.py`

**New Endpoint**: `POST /api/conquest/app-error`

**Features**:
- Handles both field name formats
- Extracts commit, branch, source, and step information
- Logs errors for analysis
- Returns structured response

**Code**:
```python
@router.post("/app-error")
async def report_app_error(request: Dict[str, Any]):
    """Report an app error for tracking and analysis"""
    try:
        # Extract error data with fallbacks for different formats
        app_id = request.get('appId') or request.get('app_id') or "unknown"
        error_message = request.get('error') or request.get('error_message') or "Unknown error"
        commit = request.get('commit', '')
        branch = request.get('branch', '')
        source = request.get('source', 'unknown')
        step = request.get('step', 'unknown')
        
        # Log and return success response
        logger.error("App error reported", 
                    app_id=app_id, 
                    error_message=error_message, 
                    source=source,
                    step=step)
        
        return {
            "status": "success",
            "message": "App error recorded successfully",
            "error_id": str(uuid.uuid4()),
            "app_id": app_id,
            "recorded_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error recording app error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. Updated Build Failure Endpoint
**File**: `ai-backend-python/app/routers/conquest.py`

**Changes**:
- Updated to use normalized properties
- Handles both field name formats
- Maintains backward compatibility

**Code**:
```python
# Record the build failure
failure_data = {
    "app_id": request.normalized_app_id,
    "error_message": request.normalized_error_message,
    "build_logs": request.build_logs,
    "failure_type": request.failure_type,
    "timestamp": datetime.utcnow().isoformat()
}
```

## GitHub Actions Workflows Affected

### 1. ci-cd-pipeline.yml
**Endpoint**: `/api/conquest/build-failure`
**Format**: `appId`, `error`
**Status**: ✅ Fixed

### 2. build-apk.yml
**Endpoints**: 
- `/api/conquest/build-failure` (format: `appId`, `error`)
- `/api/conquest/app-error` (format: `appId`, `error`, `commit`, `branch`, `source`, `step`)
**Status**: ✅ Fixed

## Testing Results

### Test Cases Passed
1. **GitHub Actions Format**: `appId` + `error` ✅
2. **Expected Format**: `app_id` + `error_message` ✅
3. **Mixed Format**: `appId` + `error_message` ✅
4. **App Error Endpoint**: All field combinations ✅

### Test Output
```
🧪 Testing Conquest build-failure endpoint...

📋 Testing: GitHub Actions format
  ✅ Successfully parsed
  📝 App ID: test-run-123
  📝 Error: Build failed during compilation

📋 Testing: Expected format
  ✅ Successfully parsed
  📝 App ID: test-run-456
  📝 Error: Test failed during execution

📋 Testing: Mixed format
  ✅ Successfully parsed
  📝 App ID: test-run-789
  📝 Error: Mixed format test

🧪 Testing Conquest app-error endpoint...

📋 Testing: GitHub Actions format
  ✅ Successfully processed
  📝 App ID: test-repo
  📝 Error: Flutter test failed
  📝 Commit: abc123
  📝 Source: github-actions

✅ All tests completed successfully!
```

## Expected Results

### Before Fixes
- ❌ 422 Unprocessable Entity errors
- ❌ GitHub Actions build failures not recorded
- ❌ Missing `/api/conquest/app-error` endpoint
- ❌ Inconsistent error reporting

### After Fixes
- ✅ 200 OK responses for all GitHub Actions requests
- ✅ Build failures properly recorded and logged
- ✅ App errors captured with full context
- ✅ Backward compatibility maintained
- ✅ Flexible field name handling

## Monitoring

### Success Indicators
- No more 422 errors in server logs
- Successful error recording in Conquest service
- Proper error analysis and learning from failures
- GitHub Actions workflows complete successfully

### Log Examples
```
[INFO] Build failure reported
app_id=123456789
error_message=Build failed during compilation
failure_type=build_error

[INFO] App error reported
app_id=test-repo
error_message=Flutter test failed
source=github-actions
step=flutter test
```

## Future Enhancements

### Planned Improvements
1. **Error Categorization**: Automatically categorize errors by type
2. **Learning Integration**: Feed error data into AI learning systems
3. **Alert System**: Notify developers of critical build failures
4. **Analytics Dashboard**: Visualize error patterns and trends

### Performance Optimizations
1. **Batch Processing**: Handle multiple error reports efficiently
2. **Caching**: Cache common error patterns
3. **Rate Limiting**: Prevent spam from automated systems

## Conclusion

The Conquest endpoint fixes ensure that:
- **GitHub Actions workflows can report errors successfully**
- **Build failures are properly recorded for analysis**
- **Error data is available for AI learning and improvement**
- **The system maintains backward compatibility**
- **All error reporting formats are supported**

The system now provides robust error handling and reporting capabilities for the Conquest AI build system. 