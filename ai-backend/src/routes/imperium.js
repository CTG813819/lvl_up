const express = require('express');
const router = express.Router();
const Proposal = require('../models/proposal');
const { OpenAI } = require('openai');
const { runImperiumExperiment } = require('../services/imperiumService');
const AIQuotaService = require('../services/aiQuotaService');

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// Mock AI analysis function (replace with real AI logic)
async function analyzeCodeImperium(code, filePath) {
  const prompt = `Analyze and improve the following Dart code. Suggest improvements and return the improved code.\n\nCode:\n${code}`;
  const response = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    messages: [
      { role: 'system', content: 'You are Imperium AI.' },
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

  const aiResult = await analyzeCodeImperium(code, filePath);

  const proposal = new Proposal({
    aiType: 'Imperium',
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
    message: 'Imperium experiment complete',
    summary: aiResult.summary,
    suggestion: aiResult.suggestion,
    proposalId: proposal._id
  });
});

// Trigger Imperium to run an experiment (for testing quota system)
router.post('/trigger', async (req, res) => {
  try {
    console.log('[IMPERIUM_ROUTE] 🚀 Manual trigger requested');
    
    // Check quota before proceeding
    const canSendProposals = await AIQuotaService.canSendProposals('Imperium');
    if (!canSendProposals) {
      console.log('[IMPERIUM_ROUTE] ❌ Quota reached, cannot send more proposals');
      return res.status(403).json({ 
        error: 'Quota reached', 
        message: 'Imperium has reached its proposal quota and is in learning mode' 
      });
    }
    
    // Sample code to test with
    const sampleCode = `
class Example {
  void method() {
    print('Hello World');
  }
}`;
    
    const sampleFilePath = 'lib/test_example.dart';
    
    console.log('[IMPERIUM_ROUTE] Running experiment with sample code...');
    const result = await runImperiumExperiment(sampleCode, sampleFilePath);
    
    if (result.proposal) {
      console.log('[IMPERIUM_ROUTE] ✅ Experiment completed successfully');
      res.json({
        message: 'Imperium experiment triggered successfully',
        proposalId: result.proposal._id,
        status: 'created'
      });
    } else {
      console.log('[IMPERIUM_ROUTE] ⚠️ No proposal created (likely duplicate or invalid)');
      res.json({
        message: 'Imperium experiment completed but no proposal created',
        status: 'no-proposal'
      });
    }
  } catch (error) {
    console.error('[IMPERIUM_ROUTE] ❌ Error triggering experiment:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;