# Adding Port 8001 to AWS Security Group

## Current Status
✅ Enhanced Adversarial Testing Service is running on EC2 instance (port 8001)  
✅ Service is responding correctly locally  
❌ Port 8001 is not accessible externally (security group issue)

## Solution: Add Security Group Rule

### Option 1: AWS Console (Recommended)

1. **Go to AWS Console:**
   - Navigate to EC2 Dashboard
   - Click "Instances" in the left sidebar
   - Find your instance (IP: 34.202.215.209)

2. **Access Security Group:**
   - Click on your instance
   - In the "Security" tab, click on the security group name
   - Click "Edit inbound rules"

3. **Add New Rule:**
   ```
   Type: Custom TCP
   Protocol: TCP
   Port: 8001
   Source: 0.0.0.0/0 (or your specific IP for security)
   Description: Enhanced Adversarial Testing Service
   ```

4. **Save Rules:**
   - Click "Save rules"

### Option 2: AWS CLI (if you have AWS CLI configured)

```bash
# Get your instance ID
aws ec2 describe-instances --filters "Name=public-ip,Values=34.202.215.209" --query "Reservations[].Instances[].InstanceId" --output text

# Get security group ID
aws ec2 describe-instances --instance-ids <INSTANCE_ID> --query "Reservations[].Instances[].SecurityGroups[].GroupId" --output text

# Add rule for port 8001
aws ec2 authorize-security-group-ingress --group-id <SECURITY_GROUP_ID> --protocol tcp --port 8001 --cidr 0.0.0.0/0
```

## Test After Adding Rule

After adding the security group rule, test from your local machine:

```bash
# Test health endpoint
curl http://34.202.215.209:8001/health

# Test overview endpoint
curl http://34.202.215.209:8001/

# Test recent scenarios endpoint
curl http://34.202.215.209:8001/recent-scenarios
```

## Expected Results

You should get responses like:

```json
{
  "status": "healthy",
  "service": "Enhanced Adversarial Testing",
  "port": 8001,
  "timestamp": "2025-07-26T06:11:43.943053"
}
```

## Flutter App Integration

Once port 8001 is accessible, your Flutter app should work correctly with:

- **Enhanced Adversarial Testing:** `http://34.202.215.209:8001`
- **Main Backend:** `http://34.202.215.209:8000`

The Flutter app is already configured to use these URLs in `lib/screens/the_warp_screen.dart`. 