# Proposal Cleanup System Deployment Guide

## Overview
This guide will help you deploy the comprehensive proposal cleanup system to your EC2 backend server. The system provides robust cleanup of all pending proposals with multiple strategies and safety features.

## Files Created
1. `cleanup_all_pending_proposals.py` - Main cleanup script
2. `deploy_cleanup.sh` - Deployment wrapper script
3. `DEPLOYMENT_GUIDE.md` - This guide

## Quick Start

### 1. Deploy to EC2
```bash
# From your local machine, copy the files to EC2
scp -i "C:\projects\lvl_up\New.pem" cleanup_all_pending_proposals.py ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
scp -i "C:\projects\lvl_up\New.pem" deploy_cleanup.sh ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
scp -i "C:\projects\lvl_up\New.pem" DEPLOYMENT_GUIDE.md ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
```

### 2. SSH into EC2 and Setup
```bash
ssh -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com
cd /home/ubuntu/ai-backend-python
chmod +x deploy_cleanup.sh
```

### 3. Run Cleanup (Choose Strategy)

#### Conservative Cleanup (Recommended - Safe)
```bash
./deploy_cleanup.sh --conservative
```
- Removes only pending, test-failed, and expired proposals
- Keeps approved and rejected proposals
- Creates backup before deletion

#### Aggressive Cleanup (Use with Caution!)
```bash
./deploy_cleanup.sh --aggressive
```
- Removes ALL proposals regardless of status
- Will prompt for confirmation
- Creates backup before deletion

#### Selective Cleanup (Time-based)
```bash
./deploy_cleanup.sh --selective --hours 6
```
- Removes proposals older than specified hours
- Default is 24 hours if not specified

#### Backup Only (No Deletion)
```bash
./deploy_cleanup.sh --backup-only
```
- Creates backup without deleting anything
- Useful for safety checks

#### Verify Current State
```bash
./deploy_cleanup.sh --verify-only
```
- Shows current proposal statistics
- No changes made

## Cleanup Strategies Explained

### Conservative Strategy (Default)
- **Removes**: pending, test-failed, expired
- **Keeps**: approved, rejected, test-passed, testing
- **Use Case**: Safe cleanup for regular maintenance
- **Risk Level**: Low

### Aggressive Strategy
- **Removes**: ALL proposals
- **Keeps**: Nothing
- **Use Case**: Complete system reset
- **Risk Level**: High (requires confirmation)

### Selective Strategy
- **Removes**: Proposals older than N hours
- **Keeps**: Recent proposals regardless of status
- **Use Case**: Time-based cleanup
- **Risk Level**: Medium

## Safety Features

### Automatic Backup
- Creates timestamped JSON backup before any deletion
- Backup includes all proposal data and metadata
- Backup file: `proposal_backup_YYYYMMDD_HHMMSS.json`

### Verification
- Pre-flight checks for database connectivity
- Post-cleanup verification of results
- Detailed error reporting and logging

### Confirmation Prompts
- Aggressive strategy requires explicit confirmation
- Clear warnings about what will be deleted
- Option to cancel at any time

## Output Files

### Backup Files
- `proposal_backup_YYYYMMDD_HHMMSS.json` - Complete proposal backup
- Contains all proposal data in JSON format
- Can be used for restoration if needed

### Report Files
- `cleanup_report_YYYYMMDD_HHMMSS.json` - Detailed cleanup report
- Includes statistics, errors, warnings, and recommendations
- Useful for audit trails

## Monitoring and Logging

### Console Output
- Colored status messages
- Progress indicators
- Error and warning highlights
- Final summary with statistics

### Log Files
- Structured logging with timestamps
- Error tracking and reporting
- Performance metrics

## Emergency Procedures

### If Cleanup Fails
1. Check the error messages in console output
2. Review the cleanup report file
3. Verify database connectivity
4. Check file permissions
5. Ensure Python dependencies are installed

### If You Need to Restore
1. Locate the backup file: `proposal_backup_YYYYMMDD_HHMMSS.json`
2. Use the backup data to restore proposals manually
3. Contact system administrator if needed

## Integration with Existing System

### Database Compatibility
- Works with existing PostgreSQL/NeonDB setup
- Uses existing SQLAlchemy models
- Compatible with current proposal statuses

### API Endpoints
- The cleanup system is independent of the API
- Does not interfere with running backend services
- Can be run while backend is active (but recommended to stop first)

### Scheduled Cleanup
You can set up automated cleanup using cron:
```bash
# Add to crontab for daily conservative cleanup at 2 AM
0 2 * * * cd /home/ubuntu/ai-backend-python && ./deploy_cleanup.sh --conservative --no-backup
```

## Troubleshooting

### Common Issues

#### Permission Denied
```bash
chmod +x deploy_cleanup.sh
chmod +x cleanup_all_pending_proposals.py
```

#### Python Dependencies Missing
```bash
pip3 install structlog sqlalchemy asyncio
```

#### Database Connection Issues
- Check if backend service is running
- Verify database credentials
- Ensure network connectivity

#### Memory Issues
- For large databases, use selective cleanup
- Consider running during low-traffic periods
- Monitor system resources

### Getting Help
1. Check the cleanup report file for detailed error information
2. Review console output for specific error messages
3. Verify database connectivity manually
4. Check system logs for additional information

## Best Practices

### Before Running Cleanup
1. **Stop the backend service** (recommended)
2. **Create a manual backup** if needed
3. **Check current proposal statistics**
4. **Choose appropriate strategy**

### After Running Cleanup
1. **Verify cleanup results**
2. **Review the cleanup report**
3. **Restart backend service**
4. **Monitor system for any issues**

### Regular Maintenance
1. **Run conservative cleanup weekly**
2. **Monitor proposal accumulation**
3. **Review cleanup reports**
4. **Adjust strategies as needed**

## Command Reference

### Basic Commands
```bash
./deploy_cleanup.sh --help                    # Show help
./deploy_cleanup.sh --verify-only             # Check current state
./deploy_cleanup.sh --backup-only             # Create backup only
./deploy_cleanup.sh --conservative            # Safe cleanup
./deploy_cleanup.sh --aggressive              # Remove everything
./deploy_cleanup.sh --selective --hours 12    # Time-based cleanup
```

### Advanced Options
```bash
./deploy_cleanup.sh --conservative --no-backup    # Skip backup
./deploy_cleanup.sh --selective --hours 1         # Remove old proposals
./deploy_cleanup.sh --aggressive --no-backup      # Quick reset (dangerous!)
```

## Support

If you encounter issues:
1. Check this guide first
2. Review the cleanup report file
3. Check system logs
4. Verify database connectivity
5. Contact system administrator

---

**Remember**: Always start with `--verify-only` to understand your current state before running any cleanup operations! 