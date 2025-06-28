# AWS Connection Troubleshooting

## 🔍 SSH Connection Timeout Issues

### **Problem:**
```
ssh: connect to host 13.60.99.108 port 22: Connection timed out
```

### **Possible Causes:**

1. **EC2 Instance Not Running**
2. **Security Group Not Configured**
3. **Instance in Wrong State**
4. **Network/Firewall Issues**

## 🚀 Step-by-Step Fix

### **Step 1: Check EC2 Instance Status**

1. **Go to AWS Console**: https://console.aws.amazon.com
2. **Navigate to EC2 Dashboard**
3. **Check Instance State**:
   - Should be "Running" (green)
   - If "Stopped" → Start it
   - If "Terminated" → Create new instance

### **Step 2: Verify Security Group**

1. **Click on your EC2 instance**
2. **Click "Security" tab**
3. **Click on Security Group name**
4. **Check "Inbound rules"** - Should have:

```
Type        Protocol    Port Range    Source
SSH         TCP         22            Your IP / 0.0.0.0/0
HTTP        TCP         80            0.0.0.0/0
HTTPS       TCP         443           0.0.0.0/0
Custom TCP  TCP         4000          0.0.0.0/0
```

### **Step 3: Add Missing Security Group Rules**

If SSH (port 22) is missing:

1. **Click "Edit inbound rules"**
2. **Click "Add rule"**
3. **Configure:**
   - Type: SSH
   - Protocol: TCP
   - Port range: 22
   - Source: 0.0.0.0/0 (or your IP for security)
4. **Click "Save rules"**

### **Step 4: Check Your IP Address**

```powershell
# Get your public IP
curl ifconfig.me
# or
Invoke-WebRequest -Uri "http://ifconfig.me" -UseBasicParsing
```

### **Step 5: Test Connection Again**

```bash
# Test with verbose output
ssh -v -i LvlUp.pem ubuntu@13.60.99.108

# Or test with timeout
ssh -o ConnectTimeout=10 -i LvlUp.pem ubuntu@13.60.99.108
```

## 🔧 Alternative Solutions

### **Option A: Create New EC2 Instance**

If the current instance has issues:

1. **Terminate current instance**
2. **Launch new instance**:
   - Instance Type: `t3.medium`
   - AMI: Ubuntu Server 22.04 LTS
   - Security Group: Create new with all required ports
   - Key Pair: Use existing `LvlUp` key pair

### **Option B: Use AWS Systems Manager (SSM)**

If SSH doesn't work, use AWS SSM:

1. **Attach IAM role** to EC2 instance with SSM permissions
2. **Connect via AWS Console**:
   - Go to EC2 → Instances
   - Select your instance
   - Click "Connect" → "Session Manager"

### **Option C: Check Instance Console**

1. **Go to EC2 Dashboard**
2. **Select your instance**
3. **Click "Actions" → "Monitor and troubleshoot" → "Get system log"**
4. **Check for boot errors**

## 🛠️ Quick Fix Commands

### **Check Instance Status (AWS CLI):**
```bash
aws ec2 describe-instances --instance-ids i-1234567890abcdef0 --query 'Reservations[0].Instances[0].State.Name'
```

### **Start Instance (if stopped):**
```bash
aws ec2 start-instances --instance-ids i-1234567890abcdef0
```

### **Get Instance Public IP:**
```bash
aws ec2 describe-instances --instance-ids i-1234567890abcdef0 --query 'Reservations[0].Instances[0].PublicIpAddress'
```

## 🔍 Common Issues & Solutions

### **Issue: Instance Not Running**
- **Solution**: Start the instance in AWS Console

### **Issue: Wrong Security Group**
- **Solution**: Add SSH rule (port 22) to security group

### **Issue: Wrong Key Pair**
- **Solution**: Verify you're using the correct .pem file

### **Issue: Instance in Different Region**
- **Solution**: Check AWS region in console

### **Issue: Network/Firewall Blocking**
- **Solution**: Try from different network or use AWS Systems Manager

## 📞 Next Steps

1. **Check EC2 instance status** in AWS Console
2. **Verify security group** has SSH rule
3. **Try connection again**
4. **If still failing**, create new instance with proper configuration

## 🎯 Success Indicators

- ✅ Instance shows "Running" status
- ✅ Security group has SSH (port 22) rule
- ✅ SSH connection establishes
- ✅ Can run commands on EC2

Let me know what you find in the AWS Console and I'll help you fix the specific issue! 