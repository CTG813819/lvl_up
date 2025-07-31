# Guardian AI Enhancements Deployment Guide

## Overview

This guide covers the deployment of the new Guardian AI health check and suggestion management system, which provides comprehensive health checks for missions, entries, and masteries with user-driven approval workflows.

## 🚀 Backend Deployment

### Prerequisites

- Access to EC2 instance: `ec2-34-202-215-209.compute-1.amazonaws.com`
- SSH access with key-based authentication
- Python 3.8+ on EC2 instance
- PostgreSQL database access

### New Features Added

1. **GuardianSuggestion Model** - Database table for tracking health check issues
2. **GuardianAIService** - Comprehensive health check and suggestion management
3. **Enhanced Guardian Router** - New API endpoints for health checks and suggestions
4. **Database Migration** - Script to create the new table

### Deployment Steps

#### Option 1: Automated Deployment (Windows)

```bash
# Run the automated deployment script
deploy_guardian_enhancements.bat
```

#### Option 2: Manual Deployment

1. **Create Database Migration**
   ```bash
   cd ai-backend-python
   python3 create_guardian_suggestions_table.py
   ```

2. **Upload Files to EC2**
   ```bash
   scp -r app/ ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
   scp create_guardian_suggestions_table.py ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
   ```

3. **Run Migration on EC2**
   ```bash
   ssh ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com
   cd /home/ubuntu/ai-backend-python
   python3 create_guardian_suggestions_table.py
   ```

4. **Restart Backend Service**
   ```bash
   sudo systemctl restart ai-backend-python
   sudo systemctl status ai-backend-python
   ```

### New API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/guardian/health-check` | POST | Run comprehensive health checks |
| `/api/guardian/suggestions` | GET | Get Guardian suggestions with filtering |
| `/api/guardian/suggestions/{id}/approve` | POST | Approve a suggestion |
| `/api/guardian/suggestions/{id}/reject` | POST | Reject a suggestion |
| `/api/guardian/suggestions/statistics` | GET | Get suggestion statistics |
| `/api/guardian/health-status` | GET | Get current health status |

### Testing Backend Deployment

```bash
# Test health check endpoint
curl -X POST http://ec2-34-202-215-209.compute-1.amazonaws.com:4000/api/guardian/health-check

# Test suggestions endpoint
curl http://ec2-34-202-215-209.compute-1.amazonaws.com:4000/api/guardian/suggestions

# Test health status endpoint
curl http://ec2-34-202-215-209.compute-1.amazonaws.com:4000/api/guardian/health-status
```

## 📱 Frontend Deployment

### New Components Added

1. **GuardianSuggestionsWidget** - Main widget for displaying and managing suggestions
2. **Enhanced GuardianService** - Updated with new API calls
3. **Terra Screen Integration** - Added suggestions widget to Terra screen

### Frontend Files Modified

- `lib/guardian_service.dart` - Added new API methods
- `lib/terra_screen.dart` - Integrated GuardianSuggestionsWidget
- `lib/widgets/guardian_suggestions_widget.dart` - New widget (created)

### Deployment Options

#### Option 1: Flutter Web Deployment

```bash
# Build for web
flutter build web

# Deploy to your web server or hosting platform
# Copy build/web/ contents to your web server
```

#### Option 2: Flutter Mobile Deployment

```bash
# Build for Android
flutter build apk --release

# Build for iOS
flutter build ios --release

# Deploy to app stores or distribute APK/IPA
```

#### Option 3: Flutter Desktop Deployment

```bash
# Build for Windows
flutter build windows

# Build for macOS
flutter build macos

# Build for Linux
flutter build linux

# Distribute the executable or package
```

## 🔧 Health Check Features

### What Gets Checked

1. **Proposal System Health**
   - Missing required fields
   - Status inconsistencies
   - Duplicate proposals

2. **Learning System Health**
   - Confidence vs success rate inconsistencies
   - Frequent errors without solutions

3. **Mission/Entry/Mastery Health** (Placeholder)
   - ID validation
   - Name consistency
   - Progress tracking
   - Logical consistency

### Suggestion Types

- **Critical** - Immediate attention required
- **High** - Important issues to address
- **Medium** - Moderate priority issues
- **Low** - Minor issues or improvements

### User Workflow

1. **Health Check** - Guardian AI runs comprehensive checks
2. **Issue Detection** - Problems are logged as suggestions
3. **User Review** - Users see suggestions in Terra screen
4. **Approval/Rejection** - Users can approve or reject fixes
5. **Fix Application** - Approved fixes are automatically applied
6. **Feedback** - Users can provide feedback on suggestions

## 📊 Monitoring and Analytics

### Suggestion Statistics

- Total suggestions by status
- Suggestions by severity level
- Approval/rejection rates
- Recent activity tracking

### Health Status Dashboard

- Overall system health
- Pending suggestions count
- Severity breakdown
- Recommendations

## 🛠️ Troubleshooting

### Common Issues

1. **Database Migration Fails**
   - Check PostgreSQL connection
   - Verify database permissions
   - Check migration script syntax

2. **Backend Service Won't Start**
   - Check logs: `sudo journalctl -u ai-backend-python`
   - Verify Python dependencies
   - Check file permissions

3. **API Endpoints Not Responding**
   - Verify service is running
   - Check firewall settings
   - Test with curl commands

4. **Frontend Widget Not Loading**
   - Check network connectivity
   - Verify API endpoint URLs
   - Check browser console for errors

### Log Locations

- Backend logs: `sudo journalctl -u ai-backend-python`
- Application logs: `/home/ubuntu/ai-backend-python/logs/`
- Database logs: PostgreSQL logs (system dependent)

## 🔄 Rollback Procedure

If deployment fails, you can rollback:

```bash
# SSH to EC2
ssh ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com

# Stop service
sudo systemctl stop ai-backend-python

# Restore backup (replace with actual backup name)
sudo cp -r /home/ubuntu/ai-backend-python.backup.YYYYMMDD_HHMMSS /home/ubuntu/ai-backend-python

# Restart service
sudo systemctl start ai-backend-python
```

## 📈 Future Enhancements

1. **Mission/Entry/Mastery Models** - Add actual health checks when models are implemented
2. **Automated Scheduling** - Run health checks on a schedule
3. **Email Notifications** - Alert users to critical issues
4. **Advanced Analytics** - More detailed reporting and trends
5. **Bulk Operations** - Approve/reject multiple suggestions at once

## 🎯 Success Metrics

- **System Health** - Reduced number of critical issues
- **User Engagement** - Active use of suggestion approval workflow
- **Issue Resolution** - Faster detection and resolution of problems
- **Data Quality** - Improved consistency and integrity

## 📞 Support

For deployment issues or questions:

1. Check the troubleshooting section above
2. Review backend logs for error details
3. Test individual components in isolation
4. Verify network connectivity and permissions

---

**Deployment Status**: ✅ Ready for deployment  
**Last Updated**: January 2025  
**Version**: 1.0.0 