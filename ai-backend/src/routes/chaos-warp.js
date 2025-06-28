const express = require('express');
const router = express.Router();
const { AIQuotaService, updateChaosWarpState } = require('../services/aiQuotaService');
const { logEvent } = require('../state');

// Global Chaos/Warp state
let chaosMode = false;
let warpMode = false;
let chaosStartTime = null;
let chaosEndTime = null;

// Activate Chaos mode
router.post('/chaos/activate', async (req, res) => {
  try {
    if (warpMode) {
      return res.status(400).json({ 
        error: 'Cannot activate Chaos while Warp mode is active' 
      });
    }

    // Calculate end time (until 9 PM next day)
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(21, 0, 0, 0); // 9 PM tomorrow

    chaosMode = true;
    warpMode = false;
    chaosStartTime = now;
    chaosEndTime = tomorrow;

    // Update the AIQuotaService state
    updateChaosWarpState(chaosMode, warpMode);

    logEvent(`[CHAOS] Chaos mode activated at ${now.toISOString()}. Will run until ${tomorrow.toISOString()}`);
    
    res.json({
      success: true,
      message: 'Chaos mode activated',
      chaosStartTime: chaosStartTime.toISOString(),
      chaosEndTime: chaosEndTime.toISOString(),
      remainingTime: tomorrow.getTime() - now.getTime()
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
    chaosMode = false; // Override Chaos mode
    chaosStartTime = null;
    chaosEndTime = null;

    // Update the AIQuotaService state
    updateChaosWarpState(chaosMode, warpMode);

    logEvent(`[WARP] Warp mode activated at ${new Date().toISOString()}. All AI operations stopped.`);
    
    res.json({
      success: true,
      message: 'Warp mode activated - all AI operations stopped',
      warpMode: true
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
    
    logEvent(`[WARP] Warp mode deactivated at ${new Date().toISOString()}. AI operations can resume.`);
    
    res.json({
      success: true,
      message: 'Warp mode deactivated',
      warpMode: false
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

    res.json({
      chaosMode,
      warpMode,
      chaosStartTime: chaosStartTime?.toISOString(),
      chaosEndTime: chaosEndTime?.toISOString(),
      isChaosActive: chaosMode && chaosEndTime && new Date() < chaosEndTime,
      remainingTime: chaosEndTime ? chaosEndTime.getTime() - new Date().getTime() : null
    });
  } catch (error) {
    console.error('Error getting Chaos/Warp status:', error);
    res.status(500).json({ error: 'Failed to get status' });
  }
});

module.exports = router; 