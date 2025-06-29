const express = require('express');
const router = express.Router();

module.exports = (io) => {
  // GET /api/notify/test - Test endpoint for integration tests
  router.get('/test', (req, res) => {
    res.json({ 
      success: true, 
      message: 'Notification system is working',
      timestamp: new Date().toISOString(),
      endpoints: ['/test', '/status', '/apk-built']
    });
  });

  // GET /api/notify/status - Status endpoint for integration tests
  router.get('/status', (req, res) => {
    res.json({ 
      status: 'active',
      message: 'Notification system is active',
      timestamp: new Date().toISOString(),
      connectedClients: io.engine.clientsCount || 0
    });
  });

  // POST /api/notify/apk-built
  router.post('/apk-built', (req, res) => {
    const { apkUrl } = req.body;
    if (!apkUrl) {
      return res.status(400).json({ error: 'apkUrl is required' });
    }
    io.emit('apk:built', { apkUrl });
    res.json({ success: true });
  });

  // POST /api/notify/proposal-update - For proposal status updates
  router.post('/proposal-update', (req, res) => {
    const { proposalId, status, message } = req.body;
    if (!proposalId || !status) {
      return res.status(400).json({ error: 'proposalId and status are required' });
    }
    io.emit('proposal:update', { proposalId, status, message, timestamp: new Date().toISOString() });
    res.json({ success: true, message: 'Proposal update notification sent' });
  });

  // POST /api/notify/chaos-warp - For Chaos/Warp mode changes
  router.post('/chaos-warp', (req, res) => {
    const { mode, status, message } = req.body;
    if (!mode || !status) {
      return res.status(400).json({ error: 'mode and status are required' });
    }
    io.emit('chaos-warp:update', { mode, status, message, timestamp: new Date().toISOString() });
    res.json({ success: true, message: 'Chaos/Warp notification sent' });
  });

  return router;
}; 