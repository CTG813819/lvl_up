const express = require('express');
const router = express.Router();
const Proposal = require('../models/proposal');
const { OpenAI } = require('openai');

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// Mock AI analysis function (replace with real AI logic)
async function analyzeCodeGuardian(code, filePath) {
  const prompt = `You are Guardian AI. Analyze the following Dart code for safety, best practices, and bug fixes. Suggest improvements and return the improved code.\n\nCode:\n${code}`;
  const response = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    messages: [
      { role: 'system', content: 'You are Guardian AI.' },
      { role: 'user', content: prompt }
    ],
    max_tokens: 500,
    temperature: 0.2,
  });
  const suggestion = response.choices[0].message.content.trim();
  return {
    summary: 'AI-generated suggestion',
    codeAfter: suggestion,
    suggestion: 'See AI suggestion above.'
  };
}

router.post('/experiment', async (req, res) => {
  const { code, filePath } = req.body;
  if (!code || !filePath) return res.status(400).json({ error: 'Missing code or filePath' });

  const aiResult = await analyzeCodeGuardian(code, filePath);

  const proposal = new Proposal({
    aiType: 'Guardian',
    filePath,
    codeBefore: code,
    codeAfter: aiResult.codeAfter,
    status: 'pending',
    summary: aiResult.summary,
    suggestion: aiResult.suggestion,
    timestamp: new Date()
  });
  await proposal.save();

  res.json({
    message: 'Guardian experiment complete',
    summary: aiResult.summary,
    suggestion: aiResult.suggestion,
    proposalId: proposal._id
  });
});

module.exports = router;