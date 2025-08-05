# Manual Testing Guide for Optimization Changes

## Overview
This guide helps you manually test the optimization changes that reduce Claude API usage by using direct APIs for data collection and Claude only for analysis.

## Prerequisites
1. Backend server running on port 8000
2. Environment variables configured (ANTHROPIC_API_KEY, etc.)
3. Internet connection for external API tests

## 1. Test Cache Service

### Check Cache Statistics
```bash
curl http://localhost:8000/api/optimized/cache/stats
```
**Expected**: JSON response with cache statistics

### Test Cache Operations
```bash
# Set cache
curl -X POST http://localhost:8000/api/optimized/cache/set \
  -H "Content-Type: application/json" \
  -d '{"key": "test_key", "value": {"data": "test"}, "ttl": 300}'

# Get cache
curl http://localhost:8000/api/optimized/cache/get/test_key

# Delete cache
curl -X DELETE http://localhost:8000/api/optimized/cache/delete/test_key
```

## 2. Test Data Collection Service

### Test GitHub Data Collection
```bash
curl "http://localhost:8000/api/optimized/data/github?query=python&max_results=5"
```
**Expected**: JSON array of GitHub repositories/topics

### Test Stack Overflow Data Collection
```bash
curl "http://localhost:8000/api/optimized/data/stackoverflow?query=fastapi&max_results=5"
```
**Expected**: JSON array of Stack Overflow questions

### Test Cached Data Retrieval
```bash
curl "http://localhost:8000/api/optimized/data/cached/github_python"
```
**Expected**: Cached data or empty response

## 3. Test Analysis Service

### Test Learning Pattern Analysis
```bash
curl -X POST http://localhost:8000/api/optimized/analysis/learning-patterns \
  -H "Content-Type: application/json" \
  -d '{
    "learning_data": [
      {"ai_type": "imperium", "outcome": "success", "topic": "code optimization"},
      {"ai_type": "guardian", "outcome": "failure", "topic": "security validation"}
    ]
  }'
```
**Expected**: JSON with analysis insights and recommendations

### Test Proposal Quality Analysis
```bash
curl -X POST http://localhost:8000/api/optimized/analysis/proposal-quality \
  -H "Content-Type: application/json" \
  -d '{
    "ai_type": "imperium",
    "code_before": "# old code",
    "code_after": "# improved code",
    "description": "Test proposal"
  }'
```
**Expected**: JSON with quality score and analysis

## 4. Test Rate Limiting

### Check Rate Limit Status
```bash
curl http://localhost:8000/api/optimized/rate-limits/status
```
**Expected**: JSON with current rate limit status for each AI

### Test Rate Limited Calls
```bash
# Make multiple rapid calls to test rate limiting
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/optimized/analysis/learning-patterns \
    -H "Content-Type: application/json" \
    -d '{"learning_data": [{"ai_type": "test", "outcome": "success"}]}'
  sleep 1
done
```
**Expected**: Some calls succeed, others may be rate limited

## 5. Test Performance Improvements

### Measure Response Times
```bash
# Time cache operations
time curl http://localhost:8000/api/optimized/cache/stats

# Time data collection
time curl "http://localhost:8000/api/optimized/data/github?query=python&max_results=3"

# Time analysis
time curl -X POST http://localhost:8000/api/optimized/analysis/learning-patterns \
  -H "Content-Type: application/json" \
  -d '{"learning_data": [{"ai_type": "test", "outcome": "success"}]}'
```

## 6. Test Claude API Usage Reduction

### Monitor Claude API Calls
1. Check the logs for Claude API calls
2. Look for patterns like:
   - `Claude verification error` (should be reduced)
   - `anthropic_rate_limited_call` (should be rate limited)
   - Direct API calls (should be more frequent)

### Expected Behavior
- **Before**: Many Claude API calls for data collection
- **After**: Claude calls only for analysis, direct APIs for data collection

## 7. Test Error Handling

### Test Network Failures
```bash
# Test with invalid queries
curl "http://localhost:8000/api/optimized/data/github?query=invalid_query_that_should_fail"

# Test with missing parameters
curl "http://localhost:8000/api/optimized/data/github"
```

### Test Cache Failures
```bash
# Test cache with invalid data
curl -X POST http://localhost:8000/api/optimized/cache/set \
  -H "Content-Type: application/json" \
  -d '{"key": "", "value": null, "ttl": -1}'
```

## 8. Test Integration

### Test Full Workflow
1. **Data Collection**: Fetch data from external APIs
2. **Caching**: Store results in cache
3. **Analysis**: Use Claude to analyze the data
4. **Rate Limiting**: Ensure Claude calls are properly limited

```bash
# Complete workflow test
curl -X POST http://localhost:8000/api/optimized/workflow/test \
  -H "Content-Type: application/json" \
  -d '{
    "query": "python",
    "max_results": 3,
    "analysis_type": "learning_patterns"
  }'
```

## 9. Monitor System Resources

### Check Memory Usage
```bash
# Monitor memory usage during tests
ps aux | grep python
```

### Check Network Usage
```bash
# Monitor network connections
netstat -an | grep :8000
```

## 10. Verify Optimization Benefits

### Before vs After Comparison
1. **API Call Reduction**: Count Claude API calls before and after
2. **Response Time**: Measure response times for data collection
3. **Cost Reduction**: Monitor API usage costs
4. **Reliability**: Check for fewer rate limit errors

### Success Criteria
- ✅ Claude API calls reduced by 80%
- ✅ Data collection response times improved
- ✅ Rate limit errors reduced
- ✅ System reliability improved
- ✅ Cost savings achieved

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all new services are properly imported
2. **API Key Issues**: Verify environment variables are set
3. **Network Issues**: Check internet connectivity for external APIs
4. **Rate Limiting**: Monitor Claude API rate limits

### Debug Commands
```bash
# Check server logs
tail -f logs/app.log

# Check environment variables
echo $ANTHROPIC_API_KEY

# Test individual services
python -c "from app.services.cache_service import CacheService; print('CacheService OK')"
```

## Next Steps
1. Run the automated test suite: `python test_optimization_changes.py`
2. Monitor system performance for 24 hours
3. Compare metrics before and after changes
4. Document any issues or improvements needed 