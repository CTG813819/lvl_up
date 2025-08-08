# Dynamic Mock Mode System Guide

## Overview

The app now uses a **dynamic mock mode system** that automatically switches between real and mock mode based on backend connectivity and operational hours. This solves the issue where the app was hardcoded to always use mock mode.

## ✅ **New Features Added**

### 1. **Operational Hours Awareness**
- **Automatic Detection**: The system knows when it's outside operational hours (5 AM - 9 PM)
- **Smart Fallback**: When outside hours, the app stays in mock mode even if backend is available
- **Automatic Recovery**: When operational hours resume, the app automatically tries to reconnect

### 2. **Manual Retry Button**
- **Retry Connection**: Tap the refresh icon in the app bar to manually retry backend connection
- **Smart Retry Logic**: Only attempts connection during operational hours
- **Visual Feedback**: Shows success/failure status with colored notifications

### 3. **Enhanced Mock Mode Indicators**
- **App Bar Indicator**: Compact "Mock" badge appears when in mock mode
- **Banner Warning**: Prominent orange banner shows when mock mode is active
- **Status Chips**: Shows which systems (Proposals/AI Learning) are in mock mode
- **Tap for Details**: Tap the mock indicator to see detailed status

### 4. **Fixed System Status Text Overlap**
- **Improved Layout**: Fixed text overlap in system status indicators
- **Better Spacing**: Added proper constraints and spacing
- **Responsive Design**: Text adapts to available space

## 🔧 **How It Works**

### **Start in Real Mode**
- Both `ProposalProvider` and `AILearningProvider` start in **real mode** (`_useMockMode = false`)
- The app attempts to connect to the backend immediately

### **Automatic Fallback to Mock Mode**
- If the backend is unavailable, the app tracks consecutive failures
- After **3 consecutive failures**, it automatically switches to mock mode
- **Operational Hours Check**: If outside 5 AM - 9 PM, stays in mock mode regardless
- Users get a notification: "🎭 Backend Unavailable - Switched to mock mode"

### **Automatic Recovery to Real Mode**
- The app continuously checks backend connectivity
- When backend becomes available **AND** within operational hours, switches back to real mode
- Users get a notification: "✅ Backend Connected - Switched to real mode"

### **Manual Control**
- **Retry Button**: Tap refresh icon to manually retry connection
- **Force Real Mode**: For testing, can force switch to real mode
- **Force Mock Mode**: For testing, can force switch to mock mode

## 🎯 **Visual Indicators**

### **App Bar Indicators**
```
[🔧] [🏰] [🤖] [⚠️ Mock]  ← Mock mode indicator
```

### **Mock Mode Banner**
```
🎭 Mock Mode Active
Using local AI proposals - Backend unavailable or outside operational hours
[Retry] [Proposals: Mock] [AI Learning: Mock]
```

### **Status Colors**
- **Green**: Real mode, connected to backend
- **Orange**: Mock mode, using local data
- **Red**: Error state

## 🧪 **Testing the System**

### **Test Backend Connection**
1. Tap the debug button (bug icon) in proposal approval screen
2. View connection status and test results
3. Check mode, backend availability, and failure count

### **Test Manual Retry**
1. Tap the refresh icon in the app bar
2. Watch for success/failure notification
3. Check if mode switches appropriately

### **Test Operational Hours**
1. Outside 5 AM - 9 PM: App stays in mock mode
2. Within 5 AM - 9 PM: App can switch to real mode if backend available
3. Chaos mode: Overrides operational hours (allows AI operations)

### **Force Mode Testing**
```dart
// Force real mode for testing
proposalProvider.forceRealMode();

// Force mock mode for testing  
proposalProvider.forceMockMode();
```

## 🔍 **Debugging**

### **Check Current Status**
```dart
final status = proposalProvider.getConnectionStatus();
print('Mode: ${status['mode']}');
print('Backend Available: ${status['backendAvailable']}');
print('Failures: ${status['consecutiveFailures']}');
```

### **Test Backend Connectivity**
```dart
await proposalProvider.testBackendConnection();
```

### **Monitor Logs**
Look for these log messages:
- `[PROPOSAL_PROVIDER] ✅ Backend is healthy and responding`
- `[PROPOSAL_PROVIDER] ❌ Backend failure #1: Connection timeout`
- `[PROPOSAL_PROVIDER] 🔄 Too many failures - switching to mock mode`
- `[PROPOSAL_PROVIDER] ⏰ Outside operational hours - staying in mock mode`

## 🚀 **Usage Examples**

### **Normal Operation**
1. App starts in real mode
2. Connects to backend successfully
3. Shows green indicators
4. Uses real AI proposals and learning data

### **Backend Unavailable**
1. App detects backend failure
2. After 3 failures, switches to mock mode
3. Shows orange mock mode banner
4. Uses local mock data
5. Continues to retry in background

### **Outside Operational Hours**
1. App detects it's outside 5 AM - 9 PM
2. Stays in mock mode regardless of backend status
3. Shows "Outside Hours" message
4. Waits for operational hours to resume

### **Manual Retry**
1. User taps retry button
2. App checks operational hours
3. If within hours, attempts backend connection
4. Shows success/failure notification
5. Updates mode accordingly

## 🔧 **Configuration**

### **Operational Hours**
- **Start**: 5:00 AM
- **End**: 9:00 PM (21:00)
- **Format**: 24-hour

### **Failure Threshold**
- **Max Failures**: 3 consecutive failures before switching to mock mode
- **Retry Interval**: Automatic retry every 30 seconds
- **Timeout**: 5 seconds per connection attempt

### **Backend URLs**
- **Health Check**: `http://31.54.106.71:4000/health`
- **Proposals**: `http://31.54.106.71:4000/api/proposals`
- **AI Learning**: `http://31.54.106.71:4000/api/learning/status`

## 🎯 **Benefits**

1. **Automatic Recovery**: No manual intervention needed
2. **Operational Hours Awareness**: Respects business hours
3. **Visual Feedback**: Clear indicators of current mode
4. **Manual Control**: Users can force retry when needed
5. **Robust Fallback**: Always works, even when backend is down
6. **Testing Support**: Easy to test both modes

## 🐛 **Troubleshooting**

### **App Stuck in Mock Mode**
1. Check if within operational hours (5 AM - 9 PM)
2. Verify backend is running and accessible
3. Try manual retry button
4. Check debug logs for specific error messages

### **App Not Switching to Real Mode**
1. Ensure backend health endpoint responds with 200
2. Check network connectivity
3. Verify operational hours
4. Look for Chaos/Warp mode overrides

### **Text Overlap Issues**
1. Fixed in system status indicators
2. Added proper constraints and spacing
3. Responsive text sizing

## 📱 **User Interface**

### **Mock Mode Banner**
- **Location**: Top of proposal approval screen
- **Color**: Orange background with warning icon
- **Content**: Mode status, description, retry button
- **Behavior**: Only shows when in mock mode

### **App Bar Indicator**
- **Location**: Right side of app bar
- **Appearance**: Compact "Mock" badge with warning icon
- **Behavior**: Tap to see detailed status dialog

### **Retry Button**
- **Location**: App bar (refresh icon)
- **Appearance**: Green checkmark when connected, orange refresh when in mock
- **Behavior**: Attempts connection and shows result

This system ensures the app is always functional while providing clear feedback about its current state and allowing users to take control when needed.

## Key Features

### Connection State Tracking
- **Consecutive Failures**: Tracks failed connection attempts
- **Backend Availability**: Real-time status of backend connectivity
- **Mode Switching**: Automatic transitions between real and mock modes

### Visual Indicators
- **App Bar Badge**: Shows current mode (Real/Mock) with color coding
- **Debug Button**: Enhanced to show connection status and test backend
- **Status Notifications**: Real-time notifications for mode changes

### Error Handling
- **Graceful Degradation**: App continues to function in mock mode
- **Retry Logic**: Automatic retry attempts with exponential backoff
- **Error Buffering**: Connection errors are buffered to prevent spam

## Testing the System

### 1. **Test Real Mode (Backend Available)**
```bash
# Start your backend server
cd ai-backend
npm start

# Run the Flutter app
flutter run
```

**Expected Behavior:**
- App starts in "Real" mode (green badge)
- Proposals come from backend
- Debug button shows "Mode: Real | Backend: Available"

### 2. **Test Fallback to Mock Mode (Backend Unavailable)**
```bash
# Stop your backend server
# Or disconnect from network
```

**Expected Behavior:**
- After 3 failed attempts, app switches to "Mock" mode (orange badge)
- Proposals come from local mock data
- Debug button shows "Mode: Mock | Backend: Unavailable"
- Notification: "🎭 Backend Unavailable - Switched to mock mode"

### 3. **Test Recovery to Real Mode**
```bash
# Restart your backend server
cd ai-backend
npm start
```

**Expected Behavior:**
- App detects backend is available
- Switches back to "Real" mode (green badge)
- Proposals come from backend again
- Notification: "✅ Backend Connected - Switched to real mode"

## Debug Tools

### Debug Button (🐛)
Located in the AI Proposals screen, shows:
- Current mode (Real/Mock)
- Backend availability status
- Consecutive failure count
- Backend URL
- Proposal counts

### Connection Status API
```dart
final status = provider.getConnectionStatus();
// Returns: {
//   'mode': 'Real' | 'Mock',
//   'backendAvailable': true | false,
//   'consecutiveFailures': 0-3,
//   'backendUrl': 'http://...'
// }
```

## Configuration

### Backend URLs
The app tries these URLs in order:
1. `http://44.204.184.21:4000` (AWS production)
2. `http://10.0.2.2:4000` (Android emulator)
3. `http://192.168.1.118:4000` (Local network)

### Timeout Settings
- **Health Check**: 5 seconds
- **API Requests**: 10-15 seconds
- **Socket.IO**: 30 seconds

### Failure Threshold
- **Max Failures**: 3 consecutive failures before switching to mock mode
- **Retry Delay**: Exponential backoff (2s, 4s, 8s)

## Troubleshooting

### App Stuck in Mock Mode
1. Check if backend is running: `curl http://localhost:4000/health`
2. Check network connectivity
3. Verify backend URL in `NetworkConfig`
4. Use debug button to test connection

### App Not Switching to Real Mode
1. Ensure backend is responding to health checks
2. Check firewall/network settings
3. Verify backend URL is correct
4. Check backend logs for errors

### Frequent Mode Switching
1. Check backend stability
2. Increase timeout values if needed
3. Check network stability
4. Monitor backend performance

## Files Modified

### Core Providers
- `lib/providers/proposal_provider.dart` - Dynamic mock mode for proposals
- `lib/providers/ai_learning_provider.dart` - Dynamic mock mode for AI learning

### UI Components
- `lib/screens/proposal_approval_screen.dart` - Mode indicator in app bar
- Debug button enhanced with connection status

### Tests
- `test/ai_guardian_test.dart` - Added tests for dynamic mock mode

## Benefits

1. **Better User Experience**: App works regardless of backend status
2. **Automatic Recovery**: No manual intervention needed
3. **Clear Status**: Users always know what mode they're in
4. **Robust Error Handling**: Graceful degradation with retry logic
5. **Real-time Feedback**: Notifications for mode changes

## Next Steps

1. **Test the system** with your backend
2. **Monitor logs** for connection issues
3. **Adjust timeouts** if needed for your environment
4. **Add more visual indicators** if desired
5. **Consider adding manual mode override** for testing 