// Buffer for test events
let testEventsBuffer = [];
let lastBackendNotification = 0;
const FOUR_HOURS = 4 * 60 * 60 * 1000;
const TEST_NOTIFICATION_INTERVAL = 30 * 60 * 1000; // 30 minutes
let connectionErrorBuffer = [];

// Grouped test notification sender
setInterval(async () => {
  if (testEventsBuffer.length > 0) {
    await sendNotification({
      title: 'Test Summary',
      body: `${testEventsBuffer.length} tests run in the last 30 minutes.`,
      type: 'test',
      // userId: ... (add userId if needed)
    });
    testEventsBuffer = [];
  }
}, TEST_NOTIFICATION_INTERVAL);

// Call this when a test runs
async function notifyTestEvent(testName) {
  testEventsBuffer.push({ timestamp: Date.now(), testName });
}

// --- Operational Hours Check ---
function checkOperatingWindow() {
  // Replace with your actual logic for operational hours
  // Example: 5:00 AM to 9:00 PM
  const now = new Date();
  const start = new Date(now);
  start.setHours(5, 0, 0, 0);
  const end = new Date(now);
  end.setHours(21, 0, 0, 0);
  return now >= start && now < end;
}

const notificationBuffers = {};
const notificationTimers = {};
const NOTIFICATION_INTERVAL = 30 * 60 * 1000; // 30 minutes

function bufferNotification(type, notification) {
  if (!checkOperatingWindow()) return; // Only buffer/send during operational hours
  if (!notificationBuffers[type]) notificationBuffers[type] = [];
  notificationBuffers[type].push(notification);

  // Start or reset the timer for this type
  if (notificationTimers[type]) clearTimeout(notificationTimers[type]);
  notificationTimers[type] = setTimeout(() => {
    flushNotificationBuffer(type);
  }, NOTIFICATION_INTERVAL);
}

async function flushNotificationBuffer(type) {
  if (!checkOperatingWindow()) return; // Only send during operational hours
  const buffer = notificationBuffers[type] || [];
  if (buffer.length === 0) return;

  // Compose a summary notification
  let title = '';
  let body = '';
  switch (type) {
    case 'proposal':
      title = 'AI Proposals Summary';
      body = `${buffer.length} new proposals in the last 30 minutes.`;
      break;
    case 'approval':
      title = 'Proposal Approvals Summary';
      body = `${buffer.length} proposals approved/rejected in the last 30 minutes.`;
      break;
    case 'build':
      title = 'Build/Deploy Summary';
      body = `${buffer.length} build/deploy events in the last 30 minutes.`;
      break;
    case 'error':
      title = 'System Errors Summary';
      body = `${buffer.length} errors occurred in the last 30 minutes.`;
      break;
    case 'learning':
      title = 'Learning Cycle Summary';
      body = `${buffer.length} learning cycles completed in the last 30 minutes.`;
      break;
    case 'quota':
      title = 'Quota/Limit Summary';
      body = `${buffer.length} quota/limit events in the last 30 minutes.`;
      break;
    case 'test':
      title = 'Test Summary';
      body = `${buffer.length} tests run in the last 30 minutes.`;
      break;
    default:
      title = `${type.charAt(0).toUpperCase() + type.slice(1)} Summary`;
      body = `${buffer.length} events in the last 30 minutes.`;
  }

  await sendNotification({
    title,
    body,
    type,
    // Optionally, aggregate data for more detail
    // userId: ...,
  });

  notificationBuffers[type] = [];
}

// Call this when a connection is successfully established
async function notifyBackendConnected(userId) {
  if (!checkOperatingWindow()) return;
  const now = Date.now();
  if (now - lastBackendNotification < FOUR_HOURS) return;
  lastBackendNotification = now;
  let errorSummary = '';
  if (connectionErrorBuffer.length > 0) {
    errorSummary = `\n${connectionErrorBuffer.length} connection errors/timeouts occurred in the last 4 hours.`;
  }
  await sendNotification({
    title: 'Connected to AI Backend',
    body: 'The app is connected to the backend.' + errorSummary,
    type: 'system',
    userId,
  });
  connectionErrorBuffer = [];
}

// Call this when a connection error/timeout occurs
function bufferConnectionError(errorType) {
  if (!checkOperatingWindow()) return;
  connectionErrorBuffer.push({ timestamp: Date.now(), errorType });
}

module.exports = {
  sendNotification,
  bufferNotification,
  flushNotificationBuffer,
  notifyBackendConnected,
  bufferConnectionError,
}; 