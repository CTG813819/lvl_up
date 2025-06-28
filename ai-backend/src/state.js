// Global state management for AI learning system
// This file avoids circular dependencies between index.js and service files

// Global AI status tracking
const aiStatus = {
  Imperium: { isLearning: false },
  Sandbox: { isLearning: false },
  Guardian: { isLearning: false }
};

// Debug log for system events
const debugLog = [];

/**
 * Log an event to the debug log
 */
function logEvent(message) {
  debugLog.push({ timestamp: new Date().toISOString(), message });
  if (debugLog.length > 200) debugLog.shift();
  console.log('[DEBUG_LOG]', message);
}

/**
 * Set learning state for an AI
 */
function setLearningState(aiType, isLearning) {
  if (aiStatus[aiType]) {
    aiStatus[aiType].isLearning = isLearning;
    logEvent(`[STATE] ${aiType} learning state changed: isLearning=${isLearning}`);
  }
}

/**
 * Get current AI status
 */
function getAIStatus() {
  return aiStatus;
}

/**
 * Get debug log
 */
function getDebugLog() {
  return debugLog.slice(-100).reverse();
}

module.exports = {
  aiStatus,
  debugLog,
  logEvent,
  setLearningState,
  getAIStatus,
  getDebugLog
}; 