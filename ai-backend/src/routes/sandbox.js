const express = require('express');
const router = express.Router();
const Proposal = require('../models/proposal');
const { OpenAI } = require('openai');
const { runSandboxExperiment } = require('../services/sandboxService');
const AIQuotaService = require('../services/aiQuotaService');

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// Mock AI analysis function (replace with real AI logic)
async function analyzeCodeSandbox(code, filePath) {
  const prompt = `You are Sandbox AI. Analyze the following Dart code for experimental improvements, refactoring, and optimizations. Suggest improvements and return the improved code.\n\nCode:\n${code}`;
  const response = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    messages: [
      { role: 'system', content: 'You are Sandbox AI.' },
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

  const aiResult = await analyzeCodeSandbox(code, filePath);

  const proposal = new Proposal({
    aiType: 'Sandbox',
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
    message: 'Sandbox experiment complete',
    summary: aiResult.summary,
    suggestion: aiResult.suggestion,
    proposalId: proposal._id
  });
});

// AI Cycle endpoint - triggered by autonomous orchestrator
router.post('/cycle', async (req, res) => {
  try {
    const { aiName, timestamp, cycleNumber, priority, platform } = req.body;
    console.log(`[SANDBOX_ROUTE] 🚀 Cycle triggered for ${aiName} (cycle #${cycleNumber})`);
    
    // Check quota before proceeding
    const canSendProposals = await AIQuotaService.canSendProposals('Sandbox');
    if (!canSendProposals) {
      console.log('[SANDBOX_ROUTE] ❌ Quota reached, cannot send more proposals');
      return res.status(403).json({ 
        error: 'Quota reached', 
        message: 'Sandbox has reached its proposal quota and is in learning mode' 
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
    console.log(`[SANDBOX_ROUTE] Found ${dartFiles.length} Dart files to analyze`);
    
    if (dartFiles.length === 0) {
      console.log('[SANDBOX_ROUTE] ⚠️ No Dart files found, using sample code');
      // Use sample code if no Dart files found
      const sampleCode = `
class Example {
  void method() {
    print('Hello World');
  }
}`;
      
      const sampleFilePath = 'lib/test_example.dart';
      const result = await runSandboxExperiment(sampleCode, sampleFilePath);
      
      if (result.proposal) {
        console.log('[SANDBOX_ROUTE] ✅ Cycle completed with sample code');
        res.json({
          message: 'Sandbox cycle completed successfully',
          proposalId: result.proposal._id,
          status: 'created',
          cycleNumber: cycleNumber
        });
      } else {
        console.log('[SANDBOX_ROUTE] ⚠️ No proposal created from sample code');
        res.json({
          message: 'Sandbox cycle completed but no proposal created',
          status: 'no-proposal',
          cycleNumber: cycleNumber
        });
      }
      return;
    }
    
    // Select a random Dart file to analyze
    const randomFile = dartFiles[Math.floor(Math.random() * dartFiles.length)];
    const relativePath = path.relative(LOCAL_PATH, randomFile);
    
    console.log(`[SANDBOX_ROUTE] Analyzing file: ${relativePath}`);
    
    // Read the file content
    const code = fs.readFileSync(randomFile, 'utf8');
    
    // Run the experiment
    const result = await runSandboxExperiment(code, relativePath);
    
    if (result.proposal) {
      console.log('[SANDBOX_ROUTE] ✅ Cycle completed successfully');
      res.json({
        message: 'Sandbox cycle completed successfully',
        proposalId: result.proposal._id,
        status: 'created',
        filePath: relativePath,
        cycleNumber: cycleNumber
      });
    } else {
      console.log('[SANDBOX_ROUTE] ⚠️ No proposal created');
      res.json({
        message: 'Sandbox cycle completed but no proposal created',
        status: 'no-proposal',
        filePath: relativePath,
        cycleNumber: cycleNumber
      });
    }
    
  } catch (error) {
    console.error('[SANDBOX_ROUTE] ❌ Error in cycle:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;