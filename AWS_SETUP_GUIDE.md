# AWS Deployment Setup Guide

## 🚀 Quick Setup Steps

### Step 1: Add SSH Key to AWS Server

SSH into your AWS server and add the public key:

```bash
# SSH into your AWS server
ssh ubuntu@44.204.184.21

# Add the public key to authorized_keys
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAi8i3ntErKum7z9q/JwrkzRY6IDsJOL4DsPbWit5tqj canice@DESKTOP-P13549Q' >> ~/.ssh/authorized_keys

# Set proper permissions
chmod 600 ~/.ssh/authorized_keys

# Test the connection (optional)
exit
```

### Step 2: Add GitHub Secrets

Go to your GitHub repository: https://github.com/CTG813819/Lvl_UP

1. Navigate to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add these 3 secrets:

#### Secret 1: AWS_SSH_PRIVATE_KEY
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAIvIt57RKyrpu8/avycK5M0WOiA7CTi+A7D21orebaowAAAKDgDeSa4A3k
mgAAAAtzc2gtZWQyNTUxOQAAACAIvIt57RKyrpu8/avycK5M0WOiA7CTi+A7D21orebaow
AAAEByZ3u/7aTPn6agNgOPZX5JMhMLQXMDwDZbep5P5mkVfwi8i3ntErKum7z9q/JwrkzR
Y6IDsJOL4DsPbWit5tqjAAAAFmNhbmljZUBERVNLVE9QLVAxMzU0OVEBAgMEBQYH
-----END OPENSSH PRIVATE KEY-----
```

#### Secret 2: AWS_HOST
```
44.204.184.21
```

#### Secret 3: AWS_USER
```
ubuntu
```

### Step 3: Test SSH Connection

Run this command to test if the SSH connection works:

```powershell
.\test-aws-connection.ps1
```

### Step 4: Trigger Deployment

Once the secrets are added, any push to the `master` branch will automatically deploy to AWS.

## 🔧 What the Deployment Does

The GitHub Actions workflow will:

1. **SSH into your AWS server** using the provided credentials
2. **Navigate to the backend directory**: `/home/ubuntu/ai-backend`
3. **Pull the latest code** from GitHub
4. **Install dependencies** with `npm install`
5. **Restart the backend** with `pm2 restart all`

## 📋 Included Updates

The deployment includes all the latest fixes:

- ✅ **Conquest AI routes** (`/api/conquest/define-requirements`, `/api/conquest/build-app`, etc.)
- ✅ **Quota reset functionality** (`/api/proposals/reset-quota/:aiType`)
- ✅ **Fixed AI quota management** with `resetQuota` method
- ✅ **All AI cycle endpoints** for autonomous orchestrator
- ✅ **Updated learning and proposal systems**

## 🎯 After Deployment

Once deployed, your Flutter app will be able to:

- Connect to the AWS backend at `http://44.204.184.21:4000`
- Use all Conquest AI features without 404 errors
- Reset AI quotas when needed
- Have all AIs working properly with updated routes

## 🚨 Troubleshooting

### If SSH connection fails:
1. Make sure the public key is correctly added to `~/.ssh/authorized_keys` on AWS
2. Check that AWS security group allows SSH (port 22)
3. Verify the AWS server is running

### If deployment fails:
1. Check GitHub Actions logs for specific errors
2. Ensure all 3 secrets are correctly added
3. Verify the backend directory path on AWS is correct

### If Conquest AI still has 404 errors:
1. Wait for the deployment to complete
2. Check that the AWS server has the latest code
3. Restart the backend manually if needed: `pm2 restart all`

## 📞 Support

If you encounter any issues, check:
1. GitHub Actions logs in your repository
2. AWS server logs: `pm2 logs`
3. Test individual endpoints on AWS: `curl http://44.204.184.21:4000/health` 