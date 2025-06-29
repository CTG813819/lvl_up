const express = require('express');
const router = express.Router();
const { AIQuotaService, updateChaosWarpState } = require('../services/aiQuotaService');
const { logEvent } = require('../state');

// Global Chaos/Warp state
let chaosMode = false;
let warpMode = false;
let chaosStartTime = null;
let chaosEndTime = null;

// Operational hours configuration
const OPERATIONAL_START_HOUR = 5; // 5 AM
const OPERATIONAL_END_HOUR = 21; // 9 PM

// Helper function to check if within operational hours
function isWithinOperationalHours() {
  const now = new Date();
  return now.getHours() >= OPERATIONAL_START_HOUR && now.getHours() < OPERATIONAL_END_HOUR;
}

// Helper function to get AI operation status with hierarchy: Warp > Chaos > Operational Hours
function getAIOperationStatus() {
  // Warp mode completely stops all AI operations (highest priority)
  if (warpMode) {
    return {
      canOperate: false,
      reason: 'WARP_MODE_ACTIVE',
      message: 'All AI operations stopped by Warp mode',
      hierarchy: 'WARP > CHAOS > OPERATIONAL_HOURS',
      priority: 1
    };
  }
  
  // Chaos mode allows operations regardless of operational hours (overrides operational hours)
  if (chaosMode && chaosEndTime && new Date() < chaosEndTime) {
    return {
      canOperate: true,
      reason: 'CHAOS_MODE_ACTIVE',
      message: 'AI operations allowed by Chaos mode (overrides operational hours)',
      hierarchy: 'CHAOS > OPERATIONAL_HOURS',
      priority: 2
    };
  }
  
  // Normal operational hours check (lowest priority)
  const withinHours = isWithinOperationalHours();
  return {
    canOperate: withinHours,
    reason: withinHours ? 'OPERATIONAL_HOURS' : 'OUTSIDE_OPERATIONAL_HOURS',
    message: withinHours ? 'AI operations allowed during operational hours' : 'AI operations paused outside operational hours',
    hierarchy: 'OPERATIONAL_HOURS',
    priority: 3
  };
}

// Get current hierarchy status
function getCurrentHierarchyStatus() {
  if (warpMode) {
    return 'WARP (AI stopped)';
  } else if (chaosMode && chaosEndTime && new Date() < chaosEndTime) {
    return 'CHAOS (AI allowed - overrides operational hours)';
  } else if (isWithinOperationalHours()) {
    return 'OPERATIONAL HOURS (AI allowed)';
  } else {
    return 'OUTSIDE HOURS (AI stopped)';
  }
}

// Activate Chaos mode
router.post('/chaos/activate', async (req, res) => {
  try {
    if (warpMode) {
      return res.status(400).json({ 
        error: 'Cannot activate Chaos while Warp mode is active',
        hierarchy: 'WARP > CHAOS > OPERATIONAL_HOURS',
        currentStatus: getCurrentHierarchyStatus(),
        message: 'Warp mode has highest priority and must be deactivated first'
      });
    }

    // Calculate end time (until 9 PM next day)
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(OPERATIONAL_END_HOUR, 0, 0, 0); // 9 PM tomorrow

    chaosMode = true;
    warpMode = false; // Ensure Warp mode is off
    chaosStartTime = now;
    chaosEndTime = tomorrow;

    // Update the AIQuotaService state
    updateChaosWarpState(chaosMode, warpMode);

    const operationStatus = getAIOperationStatus();
    
    logEvent(`[CHAOS] Chaos mode activated at ${now.toISOString()}. Will run until ${tomorrow.toISOString()}`);
    logEvent(`[CHAOS] AI Operation Status: ${operationStatus.message}`);
    logEvent(`[CHAOS] Hierarchy: ${operationStatus.hierarchy}`);
    
    res.json({
      success: true,
      message: 'Chaos mode activated - AI operations now override operational hours',
      chaosStartTime: chaosStartTime.toISOString(),
      chaosEndTime: chaosEndTime.toISOString(),
      remainingTime: tomorrow.getTime() - now.getTime(),
      operationStatus: operationStatus,
      hierarchy: 'CHAOS > OPERATIONAL_HOURS',
      currentStatus: getCurrentHierarchyStatus()
    });
  } catch (error) {
    console.error('Error activating Chaos mode:', error);
    res.status(500).json({ error: 'Failed to activate Chaos mode' });
  }
});

// Activate Warp mode
router.post('/warp/activate', async (req, res) => {
  try {
    warpMode = true;
    chaosMode = false; // Warp mode overrides Chaos mode
    chaosStartTime = null;
    chaosEndTime = null;

    // Update the AIQuotaService state
    updateChaosWarpState(chaosMode, warpMode);

    const operationStatus = getAIOperationStatus();
    
    logEvent(`[WARP] Warp mode activated at ${new Date().toISOString()}. All AI operations stopped.`);
    logEvent(`[WARP] AI Operation Status: ${operationStatus.message}`);
    logEvent(`[WARP] Hierarchy: ${operationStatus.hierarchy}`);
    
    res.json({
      success: true,
      message: 'Warp mode activated - all AI operations stopped, enforcing operational hours',
      warpMode: true,
      operationStatus: operationStatus,
      hierarchy: 'WARP > CHAOS > OPERATIONAL_HOURS',
      currentStatus: getCurrentHierarchyStatus()
    });
  } catch (error) {
    console.error('Error activating Warp mode:', error);
    res.status(500).json({ error: 'Failed to activate Warp mode' });
  }
});

// Deactivate Warp mode
router.post('/warp/deactivate', async (req, res) => {
  try {
    warpMode = false;
    
    // Update the AIQuotaService state
    updateChaosWarpState(chaosMode, warpMode);
    
    const operationStatus = getAIOperationStatus();
    
    logEvent(`[WARP] Warp mode deactivated at ${new Date().toISOString()}. AI operations can resume.`);
    logEvent(`[WARP] AI Operation Status: ${operationStatus.message}`);
    logEvent(`[WARP] Hierarchy: ${operationStatus.hierarchy}`);
    
    res.json({
      success: true,
      message: 'Warp mode deactivated - AI operations can resume based on Chaos mode or operational hours',
      warpMode: false,
      operationStatus: operationStatus,
      hierarchy: chaosMode ? 'CHAOS > OPERATIONAL_HOURS' : 'OPERATIONAL_HOURS',
      currentStatus: getCurrentHierarchyStatus()
    });
  } catch (error) {
    console.error('Error deactivating Warp mode:', error);
    res.status(500).json({ error: 'Failed to deactivate Warp mode' });
  }
});

// Get Chaos/Warp status
router.get('/chaos-warp/status', async (req, res) => {
  try {
    // Check if Chaos mode should be deactivated based on time
    if (chaosMode && chaosEndTime && new Date() >= chaosEndTime) {
      chaosMode = false;
      chaosStartTime = null;
      chaosEndTime = null;
      
      // Update the AIQuotaService state
      updateChaosWarpState(chaosMode, warpMode);
      
      logEvent(`[CHAOS] Chaos mode automatically deactivated at ${new Date().toISOString()}`);
    }

    const operationStatus = getAIOperationStatus();
    const now = new Date();

    res.json({
      chaosMode,
      warpMode,
      chaosStartTime: chaosStartTime?.toISOString(),
      chaosEndTime: chaosEndTime?.toISOString(),
      isChaosActive: chaosMode && chaosEndTime && new Date() < chaosEndTime,
      remainingTime: chaosEndTime ? chaosEndTime.getTime() - new Date().getTime() : null,
      operationStatus: operationStatus,
      operationalHours: {
        start: OPERATIONAL_START_HOUR,
        end: OPERATIONAL_END_HOUR,
        formatted: `${OPERATIONAL_START_HOUR.toString().padStart(2, '0')}:00 - ${OPERATIONAL_END_HOUR.toString().padStart(2, '0')}:00`,
        isWithin: isWithinOperationalHours()
      },
      currentTime: now.toISOString(),
      hierarchy: getCurrentHierarchyStatus(),
      systemStatus: {
        warpMode,
        chaosMode,
        isChaosActive: chaosMode && chaosEndTime && new Date() < chaosEndTime,
        isWithinOperationalHours: isWithinOperationalHours(),
        shouldOperateAI: operationStatus.canOperate,
        operationalHours: `${OPERATIONAL_START_HOUR.toString().padStart(2, '0')}:00 - ${OPERATIONAL_END_HOUR.toString().padStart(2, '0')}:00`,
        timeUntilOperational: AIQuotaService.getTimeUntilOperating(),
        chaosRemainingTime: chaosEndTime ? chaosEndTime.getTime() - new Date().getTime() : null
      }
    });
  } catch (error) {
    console.error('Error getting Chaos/Warp status:', error);
    res.status(500).json({ error: 'Failed to get status' });
  }
});

// Get operational hours status
router.get('/chaos-warp/operational-hours', async (req, res) => {
  try {
    const now = new Date();
    const operationStatus = getAIOperationStatus();
    
    res.json({
      operationalHours: {
        start: OPERATIONAL_START_HOUR,
        end: OPERATIONAL_END_HOUR,
        formatted: `${OPERATIONAL_START_HOUR.toString().padStart(2, '0')}:00 - ${OPERATIONAL_END_HOUR.toString().padStart(2, '0')}:00`
      },
      currentTime: now.toISOString(),
      isWithinOperationalHours: isWithinOperationalHours(),
      operationStatus: operationStatus,
      chaosMode: chaosMode,
      warpMode: warpMode,
      hierarchy: getCurrentHierarchyStatus()
    });
  } catch (error) {
    console.error('Error getting operational hours status:', error);
    res.status(500).json({ error: 'Failed to get operational hours status' });
  }
});

// Get detailed system status
router.get('/chaos-warp/system-status', async (req, res) => {
  try {
    const now = new Date();
    const operationStatus = getAIOperationStatus();
    
    res.json({
      systemStatus: {
        warpMode,
        chaosMode,
        isChaosActive: chaosMode && chaosEndTime && new Date() < chaosEndTime,
        isWithinOperationalHours: isWithinOperationalHours(),
        shouldOperateAI: operationStatus.canOperate,
        operationalHours: `${OPERATIONAL_START_HOUR.toString().padStart(2, '0')}:00 - ${OPERATIONAL_END_HOUR.toString().padStart(2, '0')}:00`,
        timeUntilOperational: AIQuotaService.getTimeUntilOperating(),
        chaosRemainingTime: chaosEndTime ? chaosEndTime.getTime() - new Date().getTime() : null,
        hierarchy: getCurrentHierarchyStatus()
      },
      operationStatus: operationStatus,
      currentTime: now.toISOString(),
      chaosStartTime: chaosStartTime?.toISOString(),
      chaosEndTime: chaosEndTime?.toISOString()
    });
  } catch (error) {
    console.error('Error getting system status:', error);
    res.status(500).json({ error: 'Failed to get system status' });
  }
});

// AI Quota Service status endpoint
router.get('/ai-quota/status', async (req, res) => {
  try {
    const now = new Date();
    const operationStatus = getAIOperationStatus();
    
    res.json({
      operationStatus: operationStatus,
      currentTime: now.toISOString(),
      chaosMode: chaosMode,
      warpMode: warpMode,
      isChaosActive: chaosMode && chaosEndTime && new Date() < chaosEndTime,
      isWithinOperationalHours: isWithinOperationalHours(),
      operationalHours: {
        start: OPERATIONAL_START_HOUR,
        end: OPERATIONAL_END_HOUR,
        formatted: `${OPERATIONAL_START_HOUR.toString().padStart(2, '0')}:00 - ${OPERATIONAL_END_HOUR.toString().padStart(2, '0')}:00`
      }
    });
  } catch (error) {
    console.error('Error getting AI quota status:', error);
    res.status(500).json({ error: 'Failed to get AI quota status' });
  }
});

// Alias: /chaos-warp/ai-quota-hierarchy returns the same as /chaos-warp/status
router.get('/chaos-warp/ai-quota-hierarchy', async (req, res) => {
  try {
    // Reuse the logic from /chaos-warp/status
    // Check if Chaos mode should be deactivated based on time
    if (chaosMode && chaosEndTime && new Date() >= chaosEndTime) {
      chaosMode = false;
      chaosStartTime = null;
      chaosEndTime = null;
      updateChaosWarpState(chaosMode, warpMode);
      logEvent(`[CHAOS] Chaos mode automatically deactivated at ${new Date().toISOString()}`);
    }
    const operationStatus = getAIOperationStatus();
    const now = new Date();
    res.json({
      chaosMode,
      warpMode,
      chaosStartTime: chaosStartTime?.toISOString(),
      chaosEndTime: chaosEndTime?.toISOString(),
      isChaosActive: chaosMode && chaosEndTime && new Date() < chaosEndTime,
      remainingTime: chaosEndTime ? chaosEndTime.getTime() - new Date().getTime() : null,
      operationStatus: operationStatus,
      operationalHours: {
        start: OPERATIONAL_START_HOUR,
        end: OPERATIONAL_END_HOUR,
        formatted: `${OPERATIONAL_START_HOUR.toString().padStart(2, '0')}:00 - ${OPERATIONAL_END_HOUR.toString().padStart(2, '0')}:00`,
        isWithin: isWithinOperationalHours()
      },
      currentTime: now.toISOString(),
      hierarchy: getCurrentHierarchyStatus(),
      systemStatus: {
        warpMode,
        chaosMode,
        isChaosActive: chaosMode && chaosEndTime && new Date() < chaosEndTime,
        isWithinOperationalHours: isWithinOperationalHours(),
        shouldOperateAI: operationStatus.canOperate,
        operationalHours: `${OPERATIONAL_START_HOUR.toString().padStart(2, '0')}:00 - ${OPERATIONAL_END_HOUR.toString().padStart(2, '0')}:00`,
        timeUntilOperational: AIQuotaService.getTimeUntilOperating(),
        chaosRemainingTime: chaosEndTime ? chaosEndTime.getTime() - new Date().getTime() : null
      }
    });
  } catch (error) {
    console.error('Error getting AI quota hierarchy:', error);
    res.status(500).json({ error: 'Failed to get AI quota hierarchy' });
  }
});

// Alias: /chaos-warp/complete-system-status returns the same as /system-status
router.get('/chaos-warp/complete-system-status', async (req, res) => {
  try {
    const now = new Date();
    const operationStatus = getAIOperationStatus();
    res.json({
      systemStatus: {
        warpMode,
        chaosMode,
        isChaosActive: chaosMode && chaosEndTime && new Date() < chaosEndTime,
        isWithinOperationalHours: isWithinOperationalHours(),
        shouldOperateAI: operationStatus.canOperate,
        operationalHours: `${OPERATIONAL_START_HOUR.toString().padStart(2, '0')}:00 - ${OPERATIONAL_END_HOUR.toString().padStart(2, '0')}:00`,
        timeUntilOperational: AIQuotaService.getTimeUntilOperating(),
        chaosRemainingTime: chaosEndTime ? chaosEndTime.getTime() - new Date().getTime() : null,
        hierarchy: getCurrentHierarchyStatus()
      },
      operationStatus: operationStatus,
      currentTime: now.toISOString(),
      chaosStartTime: chaosStartTime?.toISOString(),
      chaosEndTime: chaosEndTime?.toISOString()
    });
  } catch (error) {
    console.error('Error getting complete system status:', error);
    res.status(500).json({ error: 'Failed to get complete system status' });
  }
});

module.exports = router; 