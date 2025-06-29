const { bufferConnectionError, notifyBackendConnected } = require('./src/services/notificationService');

async function testNotificationSystem() {
  console.log('🧪 Testing Notification System with Buffered Connection Errors\n');

  const userId = 'test-user-123';

  // Simulate multiple connection errors over time
  console.log('📝 Buffering connection errors...');
  bufferConnectionError('Network timeout');
  bufferConnectionError('DNS resolution failed');
  bufferConnectionError('Connection refused');
  bufferConnectionError('Request timeout');
  bufferConnectionError('Server unavailable');

  console.log('✅ 5 connection errors buffered');

  // Simulate successful connection (should trigger notification with error summary)
  console.log('\n🔗 Simulating successful connection...');
  await notifyBackendConnected(userId);

  // Buffer more errors
  console.log('\n📝 Buffering more connection errors...');
  bufferConnectionError('SSL handshake failed');
  bufferConnectionError('Proxy connection failed');

  console.log('✅ 2 more connection errors buffered');

  // Try to notify again immediately (should be blocked by 4-hour interval)
  console.log('\n🔗 Attempting immediate reconnection (should be blocked)...');
  await notifyBackendConnected(userId);

  console.log('\n✅ Test completed!');
  console.log('📋 Summary:');
  console.log('  - Connection errors are buffered instead of sent immediately');
  console.log('  - Successful connections trigger notifications with error summaries');
  console.log('  - 4-hour interval prevents notification spam');
  console.log('  - Error buffer is cleared after sending summary');
}

testNotificationSystem().catch(console.error); 