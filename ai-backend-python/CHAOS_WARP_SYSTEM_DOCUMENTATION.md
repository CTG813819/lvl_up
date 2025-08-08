# Chaos/Warp System Documentation

## Overview

The Chaos/Warp system is a comprehensive AI operation management system that implements a clear hierarchy for controlling when AI operations are allowed to run. The system integrates with GitHub workflows for automated proposal testing, validation, and deployment.

## System Hierarchy

The system follows a strict hierarchy: **WARP > CHAOS > OPERATIONAL_HOURS**

### 1. WARP Mode (Highest Priority)
- **Purpose**: Completely stops all AI operations
- **Override**: Cannot be overridden by Chaos mode
- **Use Case**: Emergency situations, maintenance, or when AI operations need to be completely halted
- **Activation**: Manual activation via API or UI
- **Deactivation**: Manual deactivation required

### 2. CHAOS Mode (Medium Priority)
- **Purpose**: Allows AI operations regardless of operational hours
- **Override**: Overrides operational hours but is overridden by Warp mode
- **Use Case**: Urgent AI tasks, development work, or when operations are needed outside normal hours
- **Activation**: Manual activation via API or UI
- **Duration**: Automatically deactivates at 9 PM the next day
- **Override**: Cannot be activated while Warp mode is active

### 3. Operational Hours (Lowest Priority)
- **Purpose**: Normal AI operation schedule
- **Hours**: 5:00 AM to 9:00 PM (05:00 - 21:00)
- **Use Case**: Regular AI operations during business hours
- **Override**: Overridden by both Chaos and Warp modes

## API Endpoints

### Chaos/Warp Management

#### Get System Status
```http
GET /api/chaos-warp/status
```

**Response:**
```json
{
  "chaosMode": false,
  "warpMode": false,
  "chaosStartTime": null,
  "chaosEndTime": null,
  "isChaosActive": false,
  "remainingTime": null,
  "operationStatus": {
    "canOperate": true,
    "reason": "OPERATIONAL_HOURS",
    "message": "AI operations allowed during operational hours",
    "hierarchy": "OPERATIONAL_HOURS",
    "priority": 3
  },
  "operationalHours": {
    "start": 5,
    "end": 21,
    "formatted": "05:00 - 21:00",
    "isWithin": true
  },
  "currentTime": "2024-01-15T14:30:00.000Z",
  "hierarchy": "OPERATIONAL HOURS (AI allowed)"
}
```

#### Activate Chaos Mode
```http
POST /api/chaos/activate
```

**Response:**
```json
{
  "success": true,
  "message": "Chaos mode activated - AI operations now override operational hours",
  "chaosStartTime": "2024-01-15T14:30:00.000Z",
  "chaosEndTime": "2024-01-16T21:00:00.000Z",
  "remainingTime": 114000000,
  "operationStatus": {
    "canOperate": true,
    "reason": "CHAOS_MODE_ACTIVE",
    "message": "AI operations allowed by Chaos mode (overrides operational hours)",
    "hierarchy": "CHAOS > OPERATIONAL_HOURS",
    "priority": 2
  },
  "hierarchy": "CHAOS > OPERATIONAL_HOURS",
  "currentStatus": "CHAOS (AI allowed - overrides operational hours)"
}
```

#### Activate Warp Mode
```http
POST /api/warp/activate
```

**Response:**
```json
{
  "success": true,
  "message": "Warp mode activated - all AI operations stopped, enforcing operational hours",
  "warpMode": true,
  "operationStatus": {
    "canOperate": false,
    "reason": "WARP_MODE_ACTIVE",
    "message": "All AI operations stopped by Warp mode",
    "hierarchy": "WARP > CHAOS > OPERATIONAL_HOURS",
    "priority": 1
  },
  "hierarchy": "WARP > CHAOS > OPERATIONAL_HOURS",
  "currentStatus": "WARP (AI stopped)"
}
```

#### Deactivate Warp Mode
```http
POST /api/warp/deactivate
```

#### Get Operational Hours
```http
GET /api/operational-hours
```

#### Get System Status (Detailed)
```http
GET /api/system-status
```

## Flutter Integration

### ChaosWarpProvider

The Flutter app uses a `ChaosWarpProvider` to manage Chaos/Warp state:

```dart
class ChaosWarpProvider with ChangeNotifier {
  bool _chaosMode = false;
  bool _warpMode = false;
  DateTime? _chaosStartTime;
  DateTime? _chaosEndTime;
  
  // Main AI operation decision logic
  bool get shouldOperateAI {
    if (_warpMode) return false; // Warp mode stops all AI
    if (_chaosMode && isChaosActive) return true; // Chaos overrides hours
    return isWithinOperationalHours; // Normal operational hours
  }
  
  // Get current hierarchy status
  String get currentHierarchyStatus {
    if (_warpMode) return 'WARP (AI stopped)';
    if (_chaosMode && isChaosActive) return 'CHAOS (AI allowed - overrides operational hours)';
    if (isWithinOperationalHours) return 'OPERATIONAL HOURS (AI allowed)';
    return 'OUTSIDE HOURS (AI stopped)';
  }
}
```

### Usage in UI

```dart
Consumer<ChaosWarpProvider>(
  builder: (context, chaosWarp, _) {
    return Column(
      children: [
        if (chaosWarp.warpMode)
          Text('WARP MODE ACTIVE: All AI operations stopped'),
        if (chaosWarp.chaosMode)
          Text('CHAOS MODE: AI operations override operational hours'),
        if (!chaosWarp.shouldOperateAI)
          Text('AI operations paused outside operational hours'),
      ],
    );
  },
)
```

## GitHub Workflow Integration

### CI/CD Pipeline

The system includes a comprehensive GitHub Actions workflow (`.github/workflows/ci-cd-pipeline.yml`) that:

1. **Proposal Testing**: Validates AI-generated proposals
2. **Chaos/Warp Testing**: Tests Chaos/Warp functionality
3. **Backend Testing**: Runs backend tests and builds
4. **Flutter Testing**: Runs Flutter tests and builds
5. **Security Scanning**: Performs security audits
6. **Integration Testing**: Tests proposal integration
7. **App Functionality Validation**: Validates app functionality
8. **Deployment**: Deploys to staging and production
9. **Post-Deployment Validation**: Validates deployment

### Workflow Triggers

```yaml
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      aiType:
        description: 'AI Type (Imperium, Guardian, Sandbox, etc.)'
        required: true
        default: 'Imperium'
      proposalId:
        description: 'Proposal ID (for tracking)'
        required: false
      approved:
        description: 'User approval (true/false)'
        required: false
        default: 'false'
      testChaosWarp:
        description: 'Test Chaos/Warp functionality'
        required: false
        default: 'false'
```

### Testing Scripts

#### 1. Chaos/Warp Testing (`test-chaos-warp.js`)
- Tests Chaos/Warp hierarchy enforcement
- Validates operational hours functionality
- Tests mode activation/deactivation
- Comprehensive error handling tests

#### 2. Proposal Validation (`validate-proposal.js`)
- Validates AI-generated proposals
- Checks code compatibility
- Tests proposal structure
- Validates AI type permissions

#### 3. Integration Testing (`test-proposal-integration.js`)
- Tests proposal integration with existing system
- Validates Chaos/Warp integration
- Tests GitHub integration
- Tests database connectivity

#### 4. App Functionality Validation (`validate-app-functionality.js`)
- Tests app functionality with new proposals
- Validates performance impact
- Tests error handling
- Validates user experience

#### 5. Deployment Validation (`validate-deployment.js`)
- Validates deployment after proposal integration
- Tests production health
- Validates performance in production
- Tests security in production

#### 6. Production Testing (`test-chaos-warp-production.js`)
- Tests Chaos/Warp functionality in production
- Validates production performance
- Tests production reliability
- Validates production security

## Testing and Validation

### Running Tests

#### Manual Testing
```bash
# Test Chaos/Warp functionality
node ai-backend/scripts/test-chaos-warp.js --testMode=comprehensive

# Validate a proposal
node ai-backend/scripts/validate-proposal.js --aiType=Imperium --proposalId=test-123 --approved=true

# Test proposal integration
node ai-backend/scripts/test-proposal-integration.js --aiType=Imperium --proposalId=test-123

# Validate app functionality
node ai-backend/scripts/validate-app-functionality.js --proposalId=test-123 --aiType=Imperium

# Validate deployment
node ai-backend/scripts/validate-deployment.js --proposalId=test-123 --aiType=Imperium --environment=production

# Test production Chaos/Warp
node ai-backend/scripts/test-chaos-warp-production.js
```

#### Automated Testing via GitHub Actions
```bash
# Trigger workflow manually
gh workflow run ci-cd-pipeline.yml \
  --field aiType=Imperium \
  --field proposalId=test-123 \
  --field approved=true \
  --field testChaosWarp=true
```

### Test Results

All tests generate detailed reports saved to `ai-backend/test-results/`:

- `proposal-validation-{id}.json`
- `chaos-warp-test-results.json`
- `proposal-integration-{id}.json`
- `app-functionality-{id}.json`
- `deployment-validation-{id}.json`
- `chaos-warp-production-{timestamp}.json`

## Configuration

### Operational Hours
```javascript
// Backend configuration
const OPERATIONAL_START_HOUR = 5; // 5 AM
const OPERATIONAL_END_HOUR = 21; // 9 PM

// Flutter configuration
static const int _operationalStartHour = 5; // 5 AM
static const int _operationalEndHour = 21; // 9 PM
```

### Environment Variables
```bash
# Backend
MONGODB_URI=mongodb://localhost:27017/ai-system
GITHUB_TOKEN=your-github-token
GITHUB_REPO=owner/repo
GITHUB_USER=username
GITHUB_EMAIL=email@example.com

# Testing
BACKEND_URL=http://localhost:3000
PRODUCTION_MODE=false
```

## Monitoring and Logging

### Log Events
The system logs all Chaos/Warp events:

```javascript
logEvent(`[CHAOS] Chaos mode activated at ${now.toISOString()}`);
logEvent(`[WARP] Warp mode activated at ${new Date().toISOString()}`);
logEvent(`[QUOTA] AI operations blocked by Warp mode`);
```

### Status Monitoring
- Real-time status updates via API
- Automatic Chaos mode deactivation
- Operational hours tracking
- Performance monitoring

## Best Practices

### 1. Hierarchy Enforcement
- Always check Warp mode first (highest priority)
- Chaos mode should override operational hours
- Operational hours are the default fallback

### 2. Error Handling
- Graceful degradation when services are unavailable
- Proper error messages for users
- Fallback to safe defaults

### 3. Performance
- Cache Chaos/Warp status to reduce API calls
- Implement polling for status updates
- Monitor response times in production

### 4. Security
- Validate all inputs
- Implement proper authentication
- Log security-relevant events

### 5. Testing
- Test all hierarchy combinations
- Validate edge cases (time boundaries)
- Test error conditions
- Monitor performance impact

## Troubleshooting

### Common Issues

#### 1. Chaos Mode Not Activating
- Check if Warp mode is active (prevents Chaos activation)
- Verify API endpoint is accessible
- Check backend logs for errors

#### 2. Operational Hours Not Working
- Verify timezone settings
- Check operational hours configuration
- Validate time comparison logic

#### 3. GitHub Workflow Failures
- Check GitHub token permissions
- Verify repository access
- Review workflow logs for specific errors

#### 4. Performance Issues
- Monitor API response times
- Check database connectivity
- Review caching implementation

### Debug Commands

```bash
# Check current status
curl http://localhost:3000/api/chaos-warp/status

# Test Chaos activation
curl -X POST http://localhost:3000/api/chaos/activate

# Test Warp activation
curl -X POST http://localhost:3000/api/warp/activate

# Check operational hours
curl http://localhost:3000/api/operational-hours
```

## Future Enhancements

### Planned Features
1. **Scheduled Chaos Mode**: Pre-schedule Chaos mode activation
2. **Conditional Warp Mode**: Automatic Warp mode based on conditions
3. **Advanced Monitoring**: Real-time dashboard for system status
4. **Mobile Notifications**: Push notifications for mode changes
5. **Analytics**: Track AI operation patterns and usage

### Integration Opportunities
1. **Slack Integration**: Notify teams of mode changes
2. **Calendar Integration**: Sync with team calendars
3. **Jira Integration**: Link to development tickets
4. **Monitoring Tools**: Integration with Prometheus, Grafana
5. **Alert Systems**: Integration with PagerDuty, OpsGenie

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review test results and logs
3. Consult the API documentation
4. Contact the development team

---

**Last Updated**: January 2024
**Version**: 1.0.0
**Status**: Production Ready 