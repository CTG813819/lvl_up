const express = require('express');
const router = express.Router();
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const upload = multer({ dest: 'uploads/' });
const { suggestImprovement } = require('../services/aiServices');
const Proposal = require('../models/proposal');

router.post('/analyze', async (req, res) => {
  const { filePath, code } = req.body;
  const aiSuggestion = await suggestImprovement(code);
  const proposal = new Proposal({
    filePath,
    oldCode: code,
    newCode: aiSuggestion,
    aiReasoning: 'AI suggested improvement',
  });
  await proposal.save();
  res.json(proposal);
});

// New endpoint: Upload multiple Dart files
router.post('/upload', upload.array('files'), async (req, res) => {
  if (!req.files || req.files.length === 0) {
    return res.status(400).json({ error: 'No files uploaded.' });
  }
  const proposals = [];
  for (const file of req.files) {
    const code = fs.readFileSync(file.path, 'utf8');
    // Stub: Use file.originalname as filePath, and code as oldCode
    // TODO: Replace with real AI suggestion
    const aiSuggestion = code + '\n// AI suggestion: Refactor this code.';
    const proposal = new Proposal({
      filePath: file.originalname,
      oldCode: code,
      newCode: aiSuggestion,
      aiReasoning: 'Stub AI suggestion',
    });
    await proposal.save();
    proposals.push(proposal);
    // Clean up uploaded file
    fs.unlinkSync(file.path);
  }
  res.json({ status: 'Files received and proposals created.', proposals });
});

module.exports = router;