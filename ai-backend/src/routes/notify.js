const express = require('express');
const router = express.Router();

module.exports = (io) => {
  // POST /api/notify/apk-built
  router.post('/apk-built', (req, res) => {
    const { apkUrl } = req.body;
    if (!apkUrl) {
      return res.status(400).json({ error: 'apkUrl is required' });
    }
    io.emit('apk:built', { apkUrl });
    res.json({ success: true });
  });
  return router;
}; 