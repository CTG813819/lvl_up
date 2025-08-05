const express = require('express');
const router = express.Router();
const Proposal = require('../models/proposal');

// Returns feedback stats grouped by AI type and user feedback
router.get('/feedback-stats', async (req, res) => {
  const stats = await Proposal.aggregate([
    { $group: { _id: { aiType: '$aiType', userFeedback: '$userFeedback' }, count: { $sum: 1 } } }
  ]);
  res.json(stats);
});

module.exports = router; 