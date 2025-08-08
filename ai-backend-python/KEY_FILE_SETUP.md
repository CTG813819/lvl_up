# AWS Key File Setup

## 📁 Where to Put LvlUp.pem

### **Recommended Location:**
```
C:\projects\lvl_up\LvlUp.pem
```

### **File Structure:**
```
lvl_up/
├── LvlUp.pem                    ← Place your key file here
├── deploy-to-aws-simple.bat     ← Deployment script
├── deploy-commands.sh           ← EC2 commands
├── setup-ec2.sh                 ← EC2 setup
├── ai-backend/                  ← Backend code
├── lib/                         ← Flutter app
└── ...
```

## 🔐 Key File Security

### **Set Proper Permissions (Windows):**
1. Right-click on `LvlUp.pem`
2. Select "Properties"
3. Click "Security" tab
4. Click "Advanced"
5. Click "Disable inheritance"
6. Remove all users except your account
7. Set permissions to "Read" only for your account

### **Set Proper Permissions (PowerShell):**
```powershell
# Navigate to project directory
cd C:\projects\lvl_up

# Set restrictive permissions
icacls LvlUp.pem /inheritance:r
icacls LvlUp.pem /grant:r "%USERNAME%:R"
```

## 🚀 Quick Setup Steps

### **1. Download Key File**
- Download `LvlUp.pem` from AWS Console
- Save it to: `C:\projects\lvl_up\LvlUp.pem`

### **2. Set Permissions**
```powershell
# Run in PowerShell as Administrator
cd C:\projects\lvl_up
icacls LvlUp.pem /inheritance:r
icacls LvlUp.pem /grant:r "%USERNAME%:R"
```

### **3. Test Connection**
```bash
# Test SSH connection (replace with your EC2 IP)
ssh -i LvlUp.pem ubuntu@your-ec2-ip
```

### **4. Run Deployment**
```bash
# Update EC2 IP in deploy-to-aws-simple.bat
# Then run:
deploy-to-aws-simple.bat
```

## 🔍 Troubleshooting

### **"Permission denied" Error:**
```bash
# Set correct permissions
chmod 400 LvlUp.pem  # On Linux/Mac
icacls LvlUp.pem /inheritance:r /grant:r "%USERNAME%:R"  # On Windows
```

### **"Key file not found" Error:**
- Ensure `LvlUp.pem` is in the project root directory
- Check file name spelling (case-sensitive)
- Verify file extension is `.pem`

### **"Bad permissions" Error:**
- Key file permissions are too open
- Set restrictive permissions as shown above
- Only your user should have read access

## 📋 Verification Checklist

- [ ] `LvlUp.pem` is in project root directory
- [ ] File permissions are set correctly
- [ ] SSH connection works: `ssh -i LvlUp.pem ubuntu@your-ec2-ip`
- [ ] Deployment script can find the key file
- [ ] Key file is not shared or committed to git

## 🔒 Security Best Practices

1. **Never commit key files to git**
   - Add `*.pem` to `.gitignore`
   - Keep keys secure and private

2. **Use IAM roles instead of access keys**
   - For production, use AWS IAM roles
   - Access keys are for development only

3. **Rotate keys regularly**
   - Generate new key pairs periodically
   - Delete old unused keys

4. **Limit key usage**
   - Use different keys for different purposes
   - Restrict key permissions in AWS

## 📞 Support

If you have issues with the key file:
1. Check file location and permissions
2. Verify EC2 IP address is correct
3. Test SSH connection manually
4. Check AWS Console for key pair status 