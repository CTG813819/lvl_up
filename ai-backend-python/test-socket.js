const io = require('socket.io-client');

console.log('Testing Socket.IO connection...');

const socket = io('http://localhost:4000', {
  transports: ['websocket', 'polling'],
  timeout: 10000,
  forceNew: true,
});

socket.on('connect', () => {
  console.log('✅ Socket.IO connected successfully!');
  console.log('Socket ID:', socket.id);
  process.exit(0);
});

socket.on('connect_error', (error) => {
  console.log('❌ Socket.IO connection error:', error.message);
  process.exit(1);
});

socket.on('disconnect', () => {
  console.log('⚠️ Socket.IO disconnected');
});

// Timeout after 10 seconds
setTimeout(() => {
  console.log('⏰ Socket.IO connection timeout');
  process.exit(1);
}, 10000); 