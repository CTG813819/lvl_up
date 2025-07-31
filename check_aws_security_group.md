# AWS Security Group Configuration Guide

## Current Status
✅ Backend is running on EC2 instance (port 4000)  
✅ Backend is responding to local requests  
❌ Cannot access from your local machine  

## Problem
Your local machine cannot reach the EC2 instance on port 4000. This is a security group configuration issue.

## Solution Steps

### 1. Check Current Security Group Rules

1. **Go to AWS Console:**
   - Navigate to EC2 Dashboard
   - Click "Instances" in the left sidebar
   - Find your instance (should show IP: 34.202.215.209)

2. **Check Security Group:**
   - Click on your instance
   - In the "Security" tab, click on the security group name
   - Look at the "Inbound rules" tab

3. **Current Rules Should Include:**
   ```
   Type: SSH
   Protocol: TCP
   Port: 22
   Source: Your IP or 0.0.0.0/0
   ```

### 2. Add Port 4000 Rule

**Add this inbound rule:**
```
Type: Custom TCP
Protocol: TCP
Port: 4000
Source: 0.0.0.0/0 (or your specific IP for security)
Description: Backend API Access
```

### 3. Alternative: Use AWS CLI

If you have AWS CLI configured, run:
```bash
# Get your instance ID
aws ec2 describe-instances --filters "Name=public-ip,Values=34.202.215.209" --query "Reservations[].Instances[].InstanceId" --output text

# Get security group ID
aws ec2 describe-instances --instance-ids <INSTANCE_ID> --query "Reservations[].Instances[].SecurityGroups[].GroupId" --output text

# Add rule for port 4000
aws ec2 authorize-security-group-ingress --group-id <SECURITY_GROUP_ID> --protocol tcp --port 4000 --cidr 0.0.0.0/0
```

### 4. Test After Changes

After adding the security group rule, test from your local machine:
```bash
curl http://34.202.215.209:4000/health
```

## Expected Result
You should get a JSON response like:
```json
{
  "status": "ok",
  "timestamp": "2025-07-05T22:27:26.030639",
  "message": "AI Backend with scikit-learn is running",
  "version": "2.0.0"
}
```

## Security Note
For production, replace `0.0.0.0/0` with your specific IP address for better security.

## Next Steps
Once port 4000 is accessible, run the endpoint test script again:
```bash
python test_backend_endpoints.py
``` 