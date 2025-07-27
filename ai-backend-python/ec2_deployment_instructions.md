# EC2 Database and Backend Fixes Deployment Instructions

## Step 1: Copy Files to EC2 Instance

Use the following SCP command to copy the fix files to your EC2 instance:

```bash
# Copy the deployment script and Python fix script
scp -i "C:\projects\lvl_up\New.pem" deploy_ec2_fixes.sh fix_ec2_database_issues.py ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/

# Or copy the entire directory (if you want to copy everything)
scp -i "C:\projects\lvl_up\New.pem" -r . ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
```

## Step 2: SSH into EC2 and Run Fixes

After copying the files, SSH into your EC2 instance:

```bash
ssh -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com
```

## Step 3: Navigate to Directory and Run Fixes

Once connected to EC2:

```bash
# Navigate to the project directory
cd /home/ubuntu/ai-backend-python

# Make the deployment script executable
chmod +x deploy_ec2_fixes.sh

# Run the deployment script
./deploy_ec2_fixes.sh
```

## Step 4: Alternative - Run Python Script

If you prefer to run the Python script instead:

```bash
# Activate virtual environment (if you have one)
source venv/bin/activate

# Run the Python fix script
python fix_ec2_database_issues.py
```

## Step 5: Test the Fixes

After running the fixes, test that everything is working:

```bash
# Run the test script
python test_fixes.py

# Check if the database function was created
psql -d your_database_name -c "SELECT json_extract_path_text('{\"test\": \"value\"}'::jsonb, 'test');"
```

## Step 6: Restart Application

Finally, restart your application to apply all fixes:

```bash
# If using systemd
sudo systemctl restart your-app-service

# Or if running manually
pkill -f "python.*main.py"
python app/main.py
```

## Troubleshooting

### If SCP fails:
- Check that your .pem file has the correct permissions
- Verify the EC2 instance is running and accessible
- Make sure the security group allows SSH access

### If migration fails:
- The script will create a `create_json_function.sql` file
- Run this SQL manually in your database:
  ```bash
  psql -d your_database_name -f create_json_function.sql
  ```

### If services still have issues:
- Check the logs for specific error messages
- Verify that all dependencies are installed
- Ensure the database connection is working

## Files Created/Modified

The deployment will fix the following files:
- `app/migrations/versions/fix_json_extract_function.py` - Fixed migration file
- `app/services/ai_growth_service.py` - Fixed Learning model usage
- `app/services/guardian_ai_service.py` - Fixed Learning model usage
- `app/services/internet_fetchers.py` - Added rate limiting
- `app/services/terra_extension_service.py` - Added real AI code generation
- `app/services/sckipit_service.py` - Fixed TODOs
- `app/services/conquest_ai_service.py` - Fixed TODOs
- `app/routers/proposals.py` - Added error logging

## Summary of Fixes

1. **Database/Backend Fixes:**
   - Fixed `json_extract_path_text` error by adding proper migration
   - Fixed Learning model usage to work with current schema
   - Added proper error handling and logging to proposal endpoints

2. **Service/Logic Fixes:**
   - Enabled and rate-limited internet fetchers (StackOverflow, Arxiv, Medium, GitHub)
   - Replaced placeholder/stub code with real implementations
   - Made plugin system live and functional
   - Updated Terra Extension Service to use real AI code generation
   - Fixed all TODOs in Sckipit and Conquest AI services

3. **Proposal Status Transitions:**
   - Ensured proposal endpoints return correct status and fields
   - Fixed proposal status transitions (pending → test-passed/approved)
   - Added proper error logging for debugging

## Verification

After deployment, verify that:
- Database migration completed successfully
- All services start without errors
- Proposal endpoints return correct data
- Internet fetchers work with rate limiting
- AI services are functional and not stubbed 