const express = require('express');
const router = express.Router();

router.post('/apk', (req, res) => {
  const { apkUrl } = req.body;
  req.app.get('io').emit('apk:available', {
    message: 'A new APK is available for download!',
    apkUrl,
  });
  res.json({ status: 'ok' });
});

module.exports = router; 