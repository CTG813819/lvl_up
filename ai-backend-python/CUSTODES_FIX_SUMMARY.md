# Custodes and Timeout Fix Summary

## Issues Identified

1. **Permission Denied**: The original script tried to create systemd services in `/etc/systemd/system/` which requires root permissions
2. **Package Installation Failures**: Attempted to install packages in an externally managed Python environment
3. **Timeout Issues**: Guardian and Conquest AI tests were timing out after 60 seconds (too short for complex AI operations)
4. **Service Creation Failures**: Could not create systemd services due to permission restrictions

## Fixes Implemented

### 1. Virtual Environment Support
- Added automatic virtual environment creation (`venv/`)
- Install packages in virtual environment instead of system Python
- Handles externally managed environment restrictions

### 2. User-Level Systemd Services
- Create services in `~/.config/systemd/user/` instead of `/etc/systemd/system/`
- No root permissions required
- Use `systemctl --user` commands instead of `systemctl`

### 3. Extended Timeouts
- **Guardian AI**: Increased from 60s to 180s (3 minutes)
- **Conquest AI**: Increased from 60s to 180s (3 minutes)
- **Imperium AI**: Increased from 45s to 90s
- **Sandbox AI**: Increased from 45s to 90s

### 4. Improved Error Handling
- Better retry logic with longer delays between attempts
- Graceful handling of permission errors
- Comprehensive logging and status reporting

## Files Created

1. **`fix_custodes_and_timeouts_fixed.py`** - Main fixed script
2. **`deploy_custodes_fix.sh`** - Deployment script
3. **`custodes_scheduler.py`** - Generated scheduler script
4. **`~/.config/systemd/user/custodes-scheduler.service`** - User-level systemd service

## Usage Instructions

### Deploy the Fix
```bash
# Make deployment script executable
chmod +x deploy_custodes_fix.sh

# Run the fix
./deploy_custodes_fix.sh
```

### Enable the Scheduler Service
```bash
# Enable the user-level service
systemctl --user enable custodes-scheduler.service

# Start the service
systemctl --user start custodes-scheduler.service

# Check service status
systemctl --user status custodes-scheduler.service

# View logs
journalctl --user -u custodes-scheduler.service -f
```

### Manual Scheduler Execution
```bash
# Run scheduler manually (for testing)
python3 custodes_scheduler.py
```

## SCP Command to Copy Files

To copy the fixed files to your EC2 instance:

```bash
# Copy the fixed script and deployment script
scp -i "C:\projects\lvl_up\New.pem" fix_custodes_and_timeouts_fixed.py deploy_custodes_fix.sh ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/

# Or copy the entire directory (if you want all files)
scp -i "C:\projects\lvl_up\New.pem" -r ai-backend-python/ ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/
```

## Expected Results

After running the fix:

1. ✅ Virtual environment created for package installation
2. ✅ Dependencies installed without permission errors
3. ✅ Custodes testing schedule configured
4. ✅ Scheduler script created with proper permissions
5. ✅ User-level systemd service created
6. ✅ AI tests run with extended timeouts
7. ✅ Guardian and Conquest AI tests should complete successfully

## Monitoring

- Check scheduler logs: `journalctl --user -u custodes-scheduler.service -f`
- Monitor AI test results in the backend logs
- Verify Custodes is testing AIs after their learning cycles

## Troubleshooting

If issues persist:

1. **Permission errors**: Ensure you're running as the ubuntu user
2. **Backend not responding**: Check if backend is running on port 8000
3. **Service not starting**: Check user systemd service status
4. **Timeout still occurring**: Further increase timeouts in the script

## Key Improvements

- **No root access required**: All operations work with user permissions
- **Better timeout handling**: Extended timeouts for complex AI operations
- **Virtual environment isolation**: Prevents system Python conflicts
- **User-level services**: Proper systemd integration without sudo
- **Comprehensive logging**: Better visibility into what's happening 