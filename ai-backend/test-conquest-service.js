// Test Conquest Service directly
const conquestService = require('./src/services/conquestService');

async function testConquestService() {
  console.log('🧪 Testing Conquest AI Service directly...\n');

  try {
    // Test 1: Get status
    console.log('1. Testing getStatus()');
    const status = conquestService.getStatus();
    console.log('✅ Status:', status);
    console.log('');

    // Test 2: Get current apps
    console.log('2. Testing getCurrentApps()');
    const currentApps = conquestService.getCurrentApps();
    console.log('✅ Current Apps:', currentApps);
    console.log('');

    // Test 3: Get completed apps
    console.log('3. Testing getCompletedApps()');
    const completedApps = conquestService.getCompletedApps();
    console.log('✅ Completed Apps:', completedApps);
    console.log('');

    // Test 4: Create app suggestion
    console.log('4. Testing createAppSuggestion()');
    const appData = {
      name: 'Test Conquest App',
      description: 'A test app created by Conquest AI',
      keywords: 'test, conquest, ai, flutter'
    };
    const newApp = await conquestService.createAppSuggestion(appData);
    console.log('✅ New App Created:', newApp);
    console.log('');

    // Test 5: Check status after creating app
    console.log('5. Testing getStatus() after creating app');
    const statusAfter = conquestService.getStatus();
    console.log('✅ Status After:', statusAfter);
    console.log('');

    // Test 6: Get current apps after creating app
    console.log('6. Testing getCurrentApps() after creating app');
    const currentAppsAfter = conquestService.getCurrentApps();
    console.log('✅ Current Apps After:', currentAppsAfter);
    console.log('');

    // Test 7: Test app ID generation
    console.log('7. Testing generateAppId()');
    const appId1 = conquestService.generateAppId();
    const appId2 = conquestService.generateAppId();
    console.log('✅ App ID 1:', appId1);
    console.log('✅ App ID 2:', appId2);
    console.log('✅ IDs are different:', appId1 !== appId2);
    console.log('');

    // Test 8: Test debug logging
    console.log('8. Testing addDebugLog()');
    conquestService.addDebugLog('Test debug message');
    conquestService.addDebugLog('Another test message');
    console.log('✅ Debug logs added');
    console.log('');

    // Test 9: Check operational hours
    console.log('9. Testing checkOperationalHours()');
    const shouldOperate = await conquestService.checkOperationalHours();
    console.log('✅ Should operate:', shouldOperate);
    console.log('✅ Operational hours:', conquestService.operationalHours);
    console.log('');

    console.log('🎉 All Conquest AI service tests completed successfully!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error('Stack trace:', error.stack);
  }
}

// Run the tests
testConquestService(); 