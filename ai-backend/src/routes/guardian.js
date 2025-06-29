const express = require('express');
const router = express.Router();
const Proposal = require('../models/proposal');
const { OpenAI } = require('openai');
const { runGuardianExperiment } = require('../services/guardianService');
const { AIQuotaService } = require('../services/aiQuotaService');

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

// AI Cycle endpoint - triggered by autonomous orchestrator
router.post('/cycle', async (req, res) => {
  try {
    const { aiName, timestamp, cycleNumber, priority, platform } = req.body;
    console.log(`[GUARDIAN_ROUTE] 🚀 Cycle triggered for ${aiName} (cycle #${cycleNumber})`);
    
    // Check quota before proceeding
    const canSendProposals = await AIQuotaService.canSendProposals('Guardian');
    if (!canSendProposals) {
      console.log('[GUARDIAN_ROUTE] ❌ Quota reached, cannot send more proposals');
      return res.status(403).json({ 
        error: 'Quota reached', 
        message: 'Guardian has reached its proposal quota and is in learning mode' 
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
    console.log(`[GUARDIAN_ROUTE] Found ${dartFiles.length} Dart files to analyze`);
    
    if (dartFiles.length === 0) {
      console.log('[GUARDIAN_ROUTE] ⚠️ No Dart files found, using sample code');
      // Use sample code if no Dart files found
      const sampleCode = `
class Example {
  void method() {
    print('Hello World');
  }
}`;
      
      const sampleFilePath = 'lib/test_example.dart';
      const result = await runGuardianExperiment(sampleCode, sampleFilePath);
      
      if (result.proposal) {
        console.log('[GUARDIAN_ROUTE] ✅ Cycle completed with sample code');
        res.json({
          message: 'Guardian cycle completed successfully',
          proposalId: result.proposal._id,
          status: 'created',
          cycleNumber: cycleNumber
        });
      } else {
        console.log('[GUARDIAN_ROUTE] ⚠️ No proposal created from sample code');
        res.json({
          message: 'Guardian cycle completed but no proposal created',
          status: 'no-proposal',
          cycleNumber: cycleNumber
        });
      }
      return;
    }
    
    // Select a random Dart file to analyze
    const randomFile = dartFiles[Math.floor(Math.random() * dartFiles.length)];
    const relativePath = path.relative(LOCAL_PATH, randomFile);
    
    console.log(`[GUARDIAN_ROUTE] Analyzing file: ${relativePath}`);
    
    // Read the file content
    const code = fs.readFileSync(randomFile, 'utf8');
    
    // Run the experiment
    const result = await runGuardianExperiment(code, relativePath);
    
    if (result.proposal) {
      console.log('[GUARDIAN_ROUTE] ✅ Cycle completed successfully');
      res.json({
        message: 'Guardian cycle completed successfully',
        proposalId: result.proposal._id,
        status: 'created',
        filePath: relativePath,
        cycleNumber: cycleNumber
      });
    } else {
      console.log('[GUARDIAN_ROUTE] ⚠️ No proposal created');
      res.json({
        message: 'Guardian cycle completed but no proposal created',
        status: 'no-proposal',
        filePath: relativePath,
        cycleNumber: cycleNumber
      });
    }
    
  } catch (error) {
    console.error('[GUARDIAN_ROUTE] ❌ Error in cycle:', error);
    res.status(500).json({ error: error.message });
  }
});

// Status endpoint for Guardian AI
router.get('/status', async (req, res) => {
  try {
    // Get recent proposals from Guardian
    const recentProposals = await Proposal.find({ aiType: 'Guardian' })
      .sort({ createdAt: -1 })
      .limit(5);
    
    // Get quota status
    const quotaStatus = await AIQuotaService.getQuotaStatus('Guardian');
    
    res.json({
      success: true,
      data: {
        aiType: 'Guardian',
        status: 'active',
        isLearning: quotaStatus.isLearning || false,
        recentProposals: recentProposals.length,
        quotaStatus: quotaStatus,
        lastActivity: recentProposals[0]?.createdAt || null,
        timestamp: new Date()
      }
    });
  } catch (error) {
    console.error('[GUARDIAN_ROUTE] Error getting status:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get Guardian AI status'
    });
  }
});

module.exports = router;

console.log('[GUARDIAN_ROUTER] 🚀 Guardian router loaded');
console.log('[GUARDIAN_ROUTER] 📍 Available routes:', router.stack.map(r => r.route?.path).filter(Boolean));