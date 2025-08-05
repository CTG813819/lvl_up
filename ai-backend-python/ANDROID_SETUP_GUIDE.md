# Android Setup Guide

## Overview
This guide helps you configure the Flutter app for Android compatibility and network connectivity.

## Android Network Issues

### **Common Problems:**
1. **localhost doesn't work** - Android devices can't access localhost
2. **Network security** - Android blocks cleartext HTTP by default
3. **Emulator vs Device** - Different network configurations needed
4. **Firewall issues** - Windows firewall blocking connections

## Quick Fixes

### 1. **Update Backend URL**

#### For Physical Android Device:
```dart
// lib/providers/proposal_provider.dart
static const String _backendUrl = 'http://192.168.1.118:4000'; // Your PC's IP
```

#### For Android Emulator:
```dart
// lib/providers/proposal_provider.dart
static const String _backendUrl = 'http://10.0.2.2:4000'; // Emulator localhost
```

### 2. **Find Your PC's IP Address**

#### Windows:
```cmd
ipconfig
```
Look for "IPv4 Address" under your active network adapter.

#### macOS/Linux:
```bash
ifconfig
# or
ip addr show
```

### 3. **Configure Android Network Security**

#### Update `android/app/src/main/AndroidManifest.xml`:
```xml
<application
    android:usesCleartextTraffic="true"
    ...>
```

#### Or create `android/app/src/main/res/xml/network_security_config.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">192.168.1.118</domain>
        <domain includeSubdomains="true">10.0.2.2</domain>
        <domain includeSubdomains="true">localhost</domain>
    </domain-config>
</network-security-config>
```

Then reference it in `AndroidManifest.xml`:
```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
```

### 4. **Windows Firewall Configuration**

#### Allow Node.js through firewall:
1. Open Windows Defender Firewall
2. Click "Allow an app or feature through Windows Defender Firewall"
3. Click "Change settings"
4. Click "Allow another app"
5. Browse to your Node.js installation (usually `C:\Program Files\nodejs\node.exe`)
6. Make sure both Private and Public are checked

#### Or use PowerShell:
```powershell
New-NetFirewallRule -DisplayName "Node.js Backend" -Direction Inbound -Protocol TCP -LocalPort 4000 -Action Allow
```

## Testing Connectivity

### 1. **Test from Android Device**
```bash
# Install curl on Android (if available) or use browser
curl http://192.168.1.118:4000/api/health
```

### 2. **Test from PC**
```bash
# Test if backend is accessible
curl http://localhost:4000/api/health
curl http://192.168.1.118:4000/api/health
```

### 3. **Use Network Config Service**
The app now includes automatic network detection:
```dart
// Automatically detects best backend URL
String backendUrl = NetworkConfig.backendUrl;

// Test all possible URLs
Map<String, bool> results = await NetworkConfig.testConnectivity();
```

## AWS Deployment (Recommended)

### **Why AWS is Better:**
- ✅ **No network configuration issues**
- ✅ **Works on any device, anywhere**
- ✅ **Better reliability and scalability**
- ✅ **Professional monitoring**

### **Quick AWS Setup:**
1. **Deploy backend to AWS EC2** (see `AWS_DEPLOYMENT_GUIDE.md`)
2. **Update Flutter app** with AWS IP:
   ```dart
   static const String _backendUrl = 'http://your-ec2-ip:4000';
   ```
3. **Test from any device**

## Troubleshooting

### **Connection Refused:**
- Check if backend is running: `npm start` in `ai-backend/`
- Check firewall settings
- Verify IP address is correct

### **Timeout Errors:**
- Increase timeout in Flutter app
- Check network stability
- Consider using AWS deployment

### **CORS Errors:**
- Backend already configured for CORS
- Check if backend URL is correct
- Verify backend is running

### **App Crashes:**
- Check Flutter logs: `flutter logs`
- Verify network permissions
- Test with different backend URLs

## Network Configuration Service

The app now includes automatic network detection:

```dart
import '../services/network_config.dart';

// Get best backend URL automatically
String url = await NetworkConfig.getBestBackendUrl();

// Test all URLs
Map<String, bool> results = await NetworkConfig.testConnectivity();
print('Working URLs: ${results.entries.where((e) => e.value).map((e) => e.key)}');
```

## Recommended Setup

### **For Development:**
1. Use local backend with correct IP address
2. Configure Android network security
3. Test on both emulator and physical device

### **For Production:**
1. Deploy to AWS EC2
2. Use AWS backend URL
3. No network configuration needed

## Testing Checklist

- [ ] Backend runs on `http://localhost:4000`
- [ ] Backend accessible on `http://your-ip:4000`
- [ ] Android app connects to backend
- [ ] Network security configured
- [ ] Firewall allows connections
- [ ] Test on both emulator and device 