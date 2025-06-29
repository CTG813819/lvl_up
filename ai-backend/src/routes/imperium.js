const express = require('express');
const router = express.Router();
const Proposal = require('../models/proposal');
const { OpenAI } = require('openai');
const { runImperiumExperiment } = require('../services/imperiumService');
const { AIQuotaService } = require('../services/aiQuotaService');

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

// AI Cycle endpoint - triggered by autonomous orchestrator
router.post('/cycle', async (req, res) => {
  try {
    const { aiName, timestamp, cycleNumber, priority, platform } = req.body;
    console.log(`[IMPERIUM_ROUTE] 🚀 Cycle triggered for ${aiName} (cycle #${cycleNumber})`);
    
    // Check quota before proceeding
    const canSendProposals = await AIQuotaService.canSendProposals('Imperium');
    if (!canSendProposals) {
      console.log('[IMPERIUM_ROUTE] ❌ Quota reached, cannot send more proposals');
      return res.status(403).json({ 
        error: 'Quota reached', 
        message: 'Imperium has reached its proposal quota and is in learning mode' 
      });
    }
    
    // Get a random Dart file from the codebase to analyze
    const fs = require('fs');
    const path = require('path');
    const LOCAL_PATH = process.env.LOCAL_PATH || './temp-repo';
    
    // Find Dart files in the codebase
    function findDartFiles(dir) {
      let results = [];
      if (!fs.existsSync(dir)) return results;
      
      const list = fs.readdirSync(dir);
      for (const item of list) {
        const itemPath = path.join(dir, item);
        const stat = fs.statSync(itemPath);
        
        if (stat.isDirectory() && !item.startsWith('.') && item !== 'node_modules') {
          results = results.concat(findDartFiles(itemPath));
        } else if (item.endsWith('.dart')) {
          results.push(itemPath);
        }
      }
      return results;
    }
    
    const dartFiles = findDartFiles(LOCAL_PATH);
    console.log(`[IMPERIUM_ROUTE] Found ${dartFiles.length} Dart files to analyze`);
    
    if (dartFiles.length === 0) {
      console.log('[IMPERIUM_ROUTE] ⚠️ No Dart files found, using sample code');
      // Use sample code if no Dart files found
      const sampleCode = `
class Example {
  void method() {
    print('Hello World');
  }
}`;
      
      const sampleFilePath = 'lib/test_example.dart';
      const result = await runImperiumExperiment(sampleCode, sampleFilePath);
      
      if (result.proposal) {
        console.log('[IMPERIUM_ROUTE] ✅ Cycle completed with sample code');
        res.json({
          message: 'Imperium cycle completed successfully',
          proposalId: result.proposal._id,
          status: 'created',
          cycleNumber: cycleNumber
        });
      } else {
        console.log('[IMPERIUM_ROUTE] ⚠️ No proposal created from sample code');
        res.json({
          message: 'Imperium cycle completed but no proposal created',
          status: 'no-proposal',
          cycleNumber: cycleNumber
        });
      }
      return;
    }
    
    // Select a random Dart file to analyze
    const randomFile = dartFiles[Math.floor(Math.random() * dartFiles.length)];
    const relativePath = path.relative(LOCAL_PATH, randomFile);
    
    console.log(`[IMPERIUM_ROUTE] Analyzing file: ${relativePath}`);
    
    // Read the file content
    const code = fs.readFileSync(randomFile, 'utf8');
    
    // Run the experiment
    const result = await runImperiumExperiment(code, relativePath);
    
    if (result.proposal) {
      console.log('[IMPERIUM_ROUTE] ✅ Cycle completed successfully');
      res.json({
        message: 'Imperium cycle completed successfully',
        proposalId: result.proposal._id,
        status: 'created',
        filePath: relativePath,
        cycleNumber: cycleNumber
      });
    } else {
      console.log('[IMPERIUM_ROUTE] ⚠️ No proposal created');
      res.json({
        message: 'Imperium cycle completed but no proposal created',
        status: 'no-proposal',
        filePath: relativePath,
        cycleNumber: cycleNumber
      });
    }
    
  } catch (error) {
    console.error('[IMPERIUM_ROUTE] ❌ Error in cycle:', error);
    res.status(500).json({ error: error.message });
  }
});

// Status endpoint for Imperium AI
router.get('/status', async (req, res) => {
  try {
    // Get recent proposals from Imperium
    const recentProposals = await Proposal.find({ aiType: 'Imperium' })
      .sort({ createdAt: -1 })
      .limit(5);
    
    // Get quota status
    const quotaStatus = await AIQuotaService.getQuotaStatus('Imperium');
    
    res.json({
      success: true,
      data: {
        aiType: 'Imperium',
        status: 'active',
        isLearning: quotaStatus.isLearning || false,
        recentProposals: recentProposals.length,
        quotaStatus: quotaStatus,
        lastActivity: recentProposals[0]?.createdAt || null,
        timestamp: new Date()
      }
    });
  } catch (error) {
    console.error('[IMPERIUM_ROUTE] Error getting status:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get Imperium AI status'
    });
  }
});

module.exports = router;

console.log('[IMPERIUM_ROUTER] 🚀 Imperium router loaded');
console.log('[IMPERIUM_ROUTER] 📍 Available routes:', router.stack.map(r => r.route?.path).filter(Boolean));