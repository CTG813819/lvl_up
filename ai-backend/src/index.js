// ai-backend/src/index.js

require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const http = require('http');
const { Server } = require('socket.io');
const Proposal = require('./models/proposal');
const fs = require('fs');
const path = require('path');
const { runImperiumExperiment } = require('./services/imperiumService');
const { runSandboxExperiment } = require('./services/sandboxService');
const { runGuardianExperiment } = require('./services/guardianService');
const simpleGit = require('simple-git');
const REPO = process.env.GITHUB_REPO;
const LOCAL_PATH = '/tmp/lvlup-repo';
const { aiStatus, logEvent, getAIStatus, getDebugLog } = require('./state');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

// Make io globally available for learning service
global.io = io;

app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    message: 'AI Backend is running'
  });
});

// Debug endpoint to show proposal statistics
app.get('/debug', async (req, res) => {
  try {
    const proposals = await Proposal.find({}).sort({ createdAt: -1 });
    const stats = {
      total: proposals.length,
      pending: proposals.filter(p => p.status === 'pending').length,
      approved: proposals.filter(p => p.status === 'approved').length,
      rejected: proposals.filter(p => p.status === 'rejected').length,
      applied: proposals.filter(p => p.status === 'applied').length,
      testPassed: proposals.filter(p => p.status === 'test-passed').length,
      testFailed: proposals.filter(p => p.status === 'test-failed').length,
    };
    
    res.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      stats,
      recentProposals: proposals.slice(0, 5).map(p => ({
        id: p._id,
        aiType: p.aiType,
        filePath: p.filePath,
        status: p.status,
        createdAt: p.createdAt,
      }))
    });
  } catch (error) {
    res.status(500).json({ 
      status: 'error', 
      message: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Debug log endpoint
app.get('/api/debug-log', (req, res) => {
  try {
    const debugLog = getDebugLog();
    res.json(debugLog);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// AI status endpoint
app.get('/api/ai-status', (req, res) => {
  try {
    const status = getAIStatus();
    res.json(status);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    message: 'AI Learning Backend is running'
  });
});

// Import your route files
const proposalsRouter = require('./routes/proposals');
const codeRouter = require('./routes/code');
const experiementsRouter = require('./routes/experiements');
const guardianRouter = require('./routes/guardian');
const imperiumRouter = require('./routes/imperium');
const sandboxRouter = require('./routes/sandbox');
const analyticsRouter = require('./routes/analytics');
const notifyRouter = require('./routes/notify')(io);
const learningRouter = require('./routes/learning');
const chaosWarpRouter = require('./routes/chaos-warp');
const approvalRouter = require('./routes/approval');

// Make io available to routes
app.set('io', io);

// Mount them under /api
app.use('/api/proposals', proposalsRouter);
app.use('/api/code', codeRouter);
app.use('/api/experiements', experiementsRouter);
app.use('/api/guardian', guardianRouter);
app.use('/api/imperium', imperiumRouter);
app.use('/api/sandbox', sandboxRouter);
app.use('/api/analytics', analyticsRouter);
app.use('/api/notify', notifyRouter);
app.use('/api/learning', learningRouter);
app.use('/api/approval', approvalRouter);
app.use('/api', chaosWarpRouter);

// MongoDB connection with detailed logging
const redactedUri = process.env.MONGODB_URI
  ? process.env.MONGODB_URI.replace(/(mongodb\+srv:\/\/.*:)(.*)(@.*)/, '$1***$3')
  : 'NO_URI_SET';
console.log('Connecting to MongoDB Atlas with URI:', redactedUri);

mongoose.connect(process.env.MONGODB_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => {
    console.log('MongoDB connected successfully!');
    const PORT = process.env.PORT || 4000;
    server.listen(PORT, '0.0.0.0', () => console.log(`Server running on port ${PORT}`));

    // Force immediate GitHub pull and scan after server start
    (async () => {
      console.log('[AI-AUTO] Immediate GitHub pull and scan after server start...');
      io.emit('backend:startup', { message: 'AI Backend is starting up and pulling latest code...' });
      await ensureRepoUpToDate();
      io.emit('backend:code-pulled', { message: 'Latest code pulled from GitHub successfully' });
      const files = getAllDartFiles(path.join(LOCAL_PATH, 'lib'));
      console.log(`[AI-AUTO] Found ${files.length} Dart files in repo.`);
      io.emit('backend:scan-complete', { fileCount: files.length, message: `Found ${files.length} Dart files to analyze` });

      // Limit to 5 files per run
      const filesToProcess = files.slice(0, 5);

      // Run Imperium on limited files
      for (const filePath of filesToProcess) {
        const code = fs.readFileSync(filePath, 'utf8');
        io.emit('ai:experiment-start', { ai: 'Imperium', filePath, message: 'Imperium is analyzing code...' });
        await runImperiumExperiment(code, filePath);
        io.emit('ai:experiment-complete', { ai: 'Imperium', filePath, message: 'Imperium analysis complete' });
      }
      // Run Sandbox on limited files
      for (const filePath of filesToProcess) {
        const code = fs.readFileSync(filePath, 'utf8');
        io.emit('ai:experiment-start', { ai: 'Sandbox', filePath, message: 'Sandbox is running experiments...' });
        await runSandboxExperiment(code, filePath);
        io.emit('ai:experiment-complete', { ai: 'Sandbox', filePath, message: 'Sandbox experiments complete' });
      }
      // Run Guardian on limited mission files
      const missionFiles = files.filter(f => f.includes('mission'));
      const missionFilesToProcess = missionFiles.slice(0, 5);
      for (const filePath of missionFilesToProcess) {
        const code = fs.readFileSync(filePath, 'utf8');
        io.emit('ai:experiment-start', { ai: 'Guardian', filePath, message: 'Guardian is performing health checks...' });
        await runGuardianExperiment(code, filePath);
        io.emit('ai:experiment-complete', { ai: 'Guardian', filePath, message: 'Guardian health checks complete' });
      }
      console.log('[AI-AUTO] Immediate AI experiments complete.');
    })();

    // Background job: Apply and push approved proposals every minute
    setInterval(async () => {
      try {
        console.log('[AI-AUTO] Checking for approved proposals to apply...');
        const allProposals = await Proposal.find({});
        console.log(`[AI-AUTO] Total proposals in database: ${allProposals.length}`);
        
        // Log all proposals and their statuses
        for (const proposal of allProposals) {
          console.log(`[AI-AUTO] Proposal ${proposal._id}: ${proposal.aiType} - ${proposal.filePath} - Status: ${proposal.status}`);
        }
        
        const approvedProposals = await Proposal.find({ status: 'approved' });
        console.log(`[AI-AUTO] Found ${approvedProposals.length} approved proposals`);
        
        if (approvedProposals.length === 0 && allProposals.length > 0) {
          console.log('[AI-AUTO] ⚠️ No approved proposals found, but proposals exist. Checking for pending proposals...');
          const pendingProposals = await Proposal.find({ status: 'pending' });
          console.log(`[AI-AUTO] Found ${pendingProposals.length} pending proposals that need user approval`);
        }
        
        for (const proposal of approvedProposals) {
          try {
            console.log(`[AI-AUTO] Processing proposal ${proposal._id} for file: ${proposal.filePath}`);
            
            // --- Run Dart tests before applying ---
            const { runDartTests } = require('./services/testRunner');
            
            // Clean the file path - remove LOCAL_PATH prefix if it exists
            let cleanFilePath = proposal.filePath;
            if (cleanFilePath.includes(LOCAL_PATH)) {
              cleanFilePath = cleanFilePath.replace(LOCAL_PATH, '').replace(/^[\\\/]/, '');
            }
            
            // Fix file path - proposal.filePath should be relative to repo root
            let absPath;
            if (cleanFilePath.startsWith('/')) {
              // If it's an absolute path, use it directly
              absPath = cleanFilePath;
            } else if (cleanFilePath.startsWith('lib/')) {
              // If it's a lib path, join with LOCAL_PATH
              absPath = path.join(LOCAL_PATH, cleanFilePath);
            } else {
              // Default case: assume it's relative to repo root
              absPath = path.join(LOCAL_PATH, cleanFilePath);
            }
            
            console.log(`[AI-AUTO] Original filePath: ${proposal.filePath}`);
            console.log(`[AI-AUTO] Cleaned filePath: ${cleanFilePath}`);
            console.log(`[AI-AUTO] Absolute path: ${absPath}`);
            
            // Ensure the directory exists
            const dir = path.dirname(absPath);
            if (!fs.existsSync(dir)) {
              fs.mkdirSync(dir, { recursive: true });
            }
            
            // Write the proposed code to the file (but not committed yet)
            console.log(`[AI-AUTO] Writing proposed code to ${absPath}`);
            fs.writeFileSync(absPath, proposal.codeAfter, 'utf8');
            
            // Run tests in the repo
            console.log(`[AI-AUTO] Running tests for proposal ${proposal._id}`);
            io.emit('proposal:test-started', { proposalId: proposal._id, filePath: proposal.filePath });
            
            const testResult = await runDartTests(LOCAL_PATH);
            console.log(`[AI-AUTO] Test result for proposal ${proposal._id}: ${testResult.success ? 'PASSED' : 'FAILED'}`);
            console.log(`[AI-AUTO] Test output: ${testResult.output.substring(0, 200)}...`);
            
            proposal.testStatus = testResult.success ? 'passed' : 'failed';
            proposal.testOutput = testResult.output;
            await proposal.save();
            
            io.emit('proposal:test-finished', {
              proposalId: proposal._id,
              filePath: proposal.filePath,
              testStatus: proposal.testStatus,
              testOutput: proposal.testOutput,
            });
            
            if (!testResult.success) {
              proposal.status = 'test-failed';
              await proposal.save();
              
              // Update AI learning with test failure feedback
              try {
                const AILearningService = require('./services/aiLearningService');
                await AILearningService.updateLearning(
                  proposal._id.toString(), 
                  'rejected', 
                  `Test failed: ${testResult.output.substring(0, 200)}...`
                );
                console.log(`[AI-AUTO] 📚 Updated AI learning for failed test: ${proposal.aiType}`);
              } catch (learningError) {
                console.error(`[AI-AUTO] ❌ Error updating AI learning for test failure:`, learningError);
              }
              
              io.emit('proposal:test-failed', {
                proposalId: proposal._id,
                filePath: proposal.filePath,
                testOutput: proposal.testOutput,
              });
              console.log(`[AI-AUTO] ❌ Proposal ${proposal._id} failed tests and will not be applied`);
              continue; // Skip applying this proposal
            }
            
            proposal.status = 'test-passed';
            await proposal.save();
            
            // Update AI learning with test success feedback
            try {
              const AILearningService = require('./services/aiLearningService');
              await AILearningService.updateLearning(
                proposal._id.toString(), 
                'approved', 
                'Tests passed successfully'
              );
              console.log(`[AI-AUTO] 📚 Updated AI learning for passed test: ${proposal.aiType}`);
            } catch (learningError) {
              console.error(`[AI-AUTO] ❌ Error updating AI learning for test success:`, learningError);
            }
            
            console.log(`[AI-AUTO] ✅ Proposal ${proposal._id} passed tests, proceeding to apply`);
            
            // --- Apply and push to GitHub if tests pass ---
            console.log(`[AI-AUTO] Applying proposal ${proposal._id} to GitHub...`);
            
            // Dynamic import to avoid ES module issues
            const { applyProposalAndPR } = await import('./services/githubService.js');
            const prUrl = await applyProposalAndPR({
              filePath: proposal.filePath,
              codeAfter: proposal.codeAfter,
              proposalId: proposal._id.toString(),
            });
            
            proposal.status = 'applied';
            proposal.result = prUrl;
            await proposal.save();
            
            io.emit('proposal:applied', {
              proposalId: proposal._id,
              filePath: proposal.filePath,
              prUrl,
              aiType: proposal.aiType,
            });
            
            console.log(`[AI-AUTO] ✅ Successfully applied and pushed proposal ${proposal._id} (${proposal.filePath}) to GitHub`);
            console.log(`[AI-AUTO] PR URL: ${prUrl}`);
            
          } catch (err) {
            console.error(`[AI-AUTO] ❌ Failed to apply proposal ${proposal._id}:`, err);
            console.error(`[AI-AUTO] Error details:`, err.message);
            console.error(`[AI-AUTO] Stack trace:`, err.stack);
          }
        }
      } catch (e) {
        console.error('[AI-AUTO] ❌ Error in proposal automation:', e);
        console.error('[AI-AUTO] Stack trace:', e.stack);
      }
    }, 60 * 1000); // every minute

    async function ensureRepoUpToDate() {
      if (!REPO) {
        console.error('[AI-AUTO] ERROR: GITHUB_REPO environment variable is not set. Cannot pull or clone repo.');
        return;
      }
      if (!fs.existsSync(LOCAL_PATH)) {
        console.log(`[AI-AUTO] Cloning repo https://github.com/${REPO}.git to ${LOCAL_PATH}`);
        await simpleGit().clone(`https://github.com/${REPO}.git`, LOCAL_PATH);
      } else {
        console.log(`[AI-AUTO] Pulling latest changes in ${LOCAL_PATH}`);
        await simpleGit(LOCAL_PATH).pull();
      }
    }

    function getAllDartFiles(dirPath) {
      let results = [];
      if (!fs.existsSync(dirPath)) return results;
      const list = fs.readdirSync(dirPath);
      list.forEach(function(file) {
        const filePath = path.join(dirPath, file);
        const stat = fs.statSync(filePath);
        if (stat && stat.isDirectory()) {
          results = results.concat(getAllDartFiles(filePath));
        } else if (filePath.endsWith('.dart')) {
          results.push(filePath);
        }
      });
      return results;
    }

    // Imperium: Self-improvement and cross-AI suggestions
    setInterval(async () => {
      try {
        console.log('[AI-AUTO] Imperium: Pulling latest code from GitHub...');
        io.emit('ai:periodic-start', { ai: 'Imperium', message: 'Imperium starting periodic analysis...' });
        await ensureRepoUpToDate();
        io.emit('ai:pull', { ai: 'Imperium', message: 'Imperium is pulling latest code from GitHub.' });
        const files = getAllDartFiles(path.join(LOCAL_PATH, 'lib'));
        const filesToProcess = files.slice(0, 5);
        for (const filePath of filesToProcess) {
          const code = fs.readFileSync(filePath, 'utf8');
          await runImperiumExperiment(code, filePath);
        }
        io.emit('ai:periodic-complete', { ai: 'Imperium', message: 'Imperium periodic analysis complete' });
        console.log('[AI-AUTO] Imperium scanned and proposed improvements.');
      } catch (e) {
        console.error('[AI-AUTO] Imperium error:', e);
        io.emit('ai:periodic-error', { ai: 'Imperium', message: 'Imperium encountered an error: ' + e.message });
      }
    }, 10 * 60 * 1000); // every 10 minutes

    // Sandbox: Experiments and learning from user uploads
    setInterval(async () => {
      try {
        console.log('[AI-AUTO] Sandbox: Pulling latest code from GitHub...');
        io.emit('ai:periodic-start', { ai: 'Sandbox', message: 'Sandbox starting periodic experiments...' });
        await ensureRepoUpToDate();
        io.emit('ai:pull', { ai: 'Sandbox', message: 'Sandbox is pulling latest code from GitHub.' });
        const files = getAllDartFiles(path.join(LOCAL_PATH, 'lib'));
        const filesToProcess = files.slice(0, 5);
        for (const filePath of filesToProcess) {
          const code = fs.readFileSync(filePath, 'utf8');
          await runSandboxExperiment(code, filePath);
        }
        // Learn from user uploads (if any in uploads/)
        const uploadDir = path.join(__dirname, '../uploads');
        if (fs.existsSync(uploadDir)) {
          const uploadFiles = fs.readdirSync(uploadDir);
          for (const file of uploadFiles) {
            const filePath = path.join(uploadDir, file);
            if (filePath.endsWith('.dart')) {
              const code = fs.readFileSync(filePath, 'utf8');
              await runSandboxExperiment(code, filePath);
            }
          }
        }
        io.emit('ai:periodic-complete', { ai: 'Sandbox', message: 'Sandbox periodic experiments complete' });
        console.log('[AI-AUTO] Sandbox ran experiments and learned from user uploads.');
      } catch (e) {
        console.error('[AI-AUTO] Sandbox error:', e);
        io.emit('ai:periodic-error', { ai: 'Sandbox', message: 'Sandbox encountered an error: ' + e.message });
      }
    }, 15 * 60 * 1000); // every 15 minutes

    // Guardian: Mission-focused proposals
    setInterval(async () => {
      try {
        console.log('[AI-AUTO] Guardian: Pulling latest code from GitHub...');
        io.emit('ai:periodic-start', { ai: 'Guardian', message: 'Guardian starting periodic health checks...' });
        await ensureRepoUpToDate();
        io.emit('ai:pull', { ai: 'Guardian', message: 'Guardian is pulling latest code from GitHub.' });
        const missionFiles = getAllDartFiles(path.join(LOCAL_PATH, 'lib')).filter(f => f.includes('mission'));
        const missionFilesToProcess = missionFiles.slice(0, 5);
        for (const filePath of missionFilesToProcess) {
          const code = fs.readFileSync(filePath, 'utf8');
          await runGuardianExperiment(code, filePath);
        }
        console.log('[AI-AUTO] Guardian scanned mission files and proposed improvements.');
      } catch (e) {
        console.error('[AI-AUTO] Guardian error:', e);
      }
    }, 20 * 60 * 1000); // every 20 minutes

    // Run learning checks every 5 minutes (increased from 2 minutes)
    setInterval(async () => {
      try {
        const AILearningService = require('./services/aiLearningService');
        await AILearningService.runLearningChecks();
        
        // Force garbage collection if available
        if (global.gc) {
          global.gc();
        }
      } catch (error) {
        console.error('[INDEX] Error running learning checks:', error);
      }
    }, 5 * 60 * 1000); // 5 minutes

    // Memory cleanup every 10 minutes
    setInterval(() => {
      try {
        // Force garbage collection if available
        if (global.gc) {
          global.gc();
          console.log('[INDEX] Memory cleanup completed');
        }
      } catch (error) {
        console.error('[INDEX] Error during memory cleanup:', error);
      }
    }, 10 * 60 * 1000); // 10 minutes

    // Memory monitoring endpoint
    app.get('/api/memory', (req, res) => {
      const memUsage = process.memoryUsage();
      const memInfo = {
        rss: Math.round(memUsage.rss / 1024 / 1024), // MB
        heapTotal: Math.round(memUsage.heapTotal / 1024 / 1024), // MB
        heapUsed: Math.round(memUsage.heapUsed / 1024 / 1024), // MB
        external: Math.round(memUsage.external / 1024 / 1024), // MB
        timestamp: new Date().toISOString()
      };
      
      console.log(`[MEMORY] Usage: ${memInfo.heapUsed}MB/${memInfo.heapTotal}MB (${Math.round(memInfo.heapUsed/memInfo.heapTotal*100)}%)`);
      
      res.json(memInfo);
    });
  })
  .catch(e => {
    console.error('MongoDB connection error:', e.message);
    if (e.message.includes('Authentication failed')) {
      console.error('Possible cause: Wrong username or password.');
    } else if (e.message.includes('ENOTFOUND') || e.message.includes('failed to connect')) {
      console.error('Possible cause: Network error, IP not whitelisted, or cluster URL typo.');
    }
    process.exit(1);
  });

// Example health endpoint
app.get('/', (req, res) => res.send('Backend is running!'));

// Debug endpoint to show AI learning state
app.get('/debug/learning', async (req, res) => {
  try {
    const AILearningService = require('./services/aiLearningService');
    const Learning = require('./models/learning');
    
    const allLearning = await Learning.find().sort({ timestamp: -1 }).limit(20);
    const imperiumInsights = await AILearningService.getLearningInsights('Imperium');
    const sandboxInsights = await AILearningService.getLearningInsights('Sandbox');
    const guardianInsights = await AILearningService.getLearningInsights('Guardian');
    
    res.json({
      recentLearning: allLearning,
      imperiumInsights: imperiumInsights.length,
      sandboxInsights: sandboxInsights.length,
      guardianInsights: guardianInsights.length,
      imperiumLessons: imperiumInsights.map(i => i.lesson),
      sandboxLessons: sandboxInsights.map(i => i.lesson),
      guardianLessons: guardianInsights.map(i => i.lesson)
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Learning analytics endpoint
app.get('/api/learning-analytics', async (req, res) => {
  try {
    const LearningAnalyticsService = require('./services/learningAnalyticsService');
    const metrics = await LearningAnalyticsService.calculateLearningMetrics();
    
    console.log('[API] 📊 Learning analytics requested, returning metrics:', metrics);
    
    res.json({
      metrics,
      timestamp: new Date().toISOString(),
      summary: {
        totalProposals: Object.values(metrics).reduce((sum, m) => sum + m.totalProposals, 0),
        totalLearning: Object.values(metrics).reduce((sum, m) => sum + m.learningEntries, 0),
        averageLearningScore: Math.round(
          Object.values(metrics).reduce((sum, m) => sum + m.learningScore, 0) / Object.keys(metrics).length
        )
      }
    });
  } catch (error) {
    console.error('[API] ❌ Error getting learning analytics:', error);
    res.status(500).json({ error: error.message });
  }
});

// Detailed learning analysis for specific AI
app.get('/api/learning-analytics/:aiType', async (req, res) => {
  try {
    const { aiType } = req.params;
    const LearningAnalyticsService = require('./services/learningAnalyticsService');
    const analysis = await LearningAnalyticsService.getDetailedLearningAnalysis(aiType);
    
    console.log(`[API] 📊 Detailed analysis requested for ${aiType}:`, analysis);
    
    res.json({
      aiType,
      analysis,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error(`[API] ❌ Error getting detailed analysis for ${req.params.aiType}:`, error);
    res.status(500).json({ error: error.message });
  }
});

// Learning verification endpoint
app.get('/api/learning-verification', async (req, res) => {
  try {
    const LearningVerificationService = require('./services/learningVerificationService');
    const verificationResults = await LearningVerificationService.verifyAllAILearning();
    const recommendations = LearningVerificationService.generateLearningRecommendations(verificationResults);
    
    console.log('[API] 🔍 Learning verification requested, returning results:', verificationResults);
    
    res.json({
      verification: verificationResults,
      recommendations,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('[API] ❌ Error in learning verification:', error);
    res.status(500).json({ error: error.message });
  }
});

// Individual AI learning verification
app.get('/api/learning-verification/:aiType', async (req, res) => {
  try {
    const { aiType } = req.params;
    const LearningVerificationService = require('./services/learningVerificationService');
    const result = await LearningVerificationService.verifyAILearning(aiType);
    
    console.log(`[API] 🔍 Learning verification requested for ${aiType}:`, result);
    
    res.json({
      aiType,
      result,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error(`[API] ❌ Error in learning verification for ${req.params.aiType}:`, error);
    res.status(500).json({ error: error.message });
  }
});

// Endpoint to set AI learning state (admin/testing)
app.post('/api/ai/:aiType/learning', (req, res) => {
  const { aiType } = req.params;
  const { isLearning } = req.body;
  const AILearningService = require('./services/aiLearningService');
  if (!['Imperium', 'Sandbox', 'Guardian'].includes(aiType)) {
    return res.status(400).json({ error: 'Invalid AI type' });
  }
  AILearningService.setLearningState(aiType, !!isLearning);
  res.json({ aiType, isLearning: !!isLearning });
});

// Learning effectiveness endpoint
app.get('/api/learning-effectiveness', async (req, res) => {
  try {
    const LearningAnalyticsService = require('./services/learningAnalyticsService');
    const effectiveness = await LearningAnalyticsService.getLearningEffectiveness();
    
    console.log('[API] 📊 Learning effectiveness requested, returning metrics:', effectiveness);
    
    res.json({
      effectiveness,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('[API] ❌ Error getting learning effectiveness:', error);
    res.status(500).json({ error: error.message });
  }
});

// Learning session details endpoint
app.get('/api/learning-sessions/:aiType', async (req, res) => {
  try {
    const { aiType } = req.params;
    const LearningAnalyticsService = require('./services/learningAnalyticsService');
    const analysis = await LearningAnalyticsService.getDetailedLearningAnalysis(aiType);
    
    console.log(`[API] 📊 Learning sessions requested for ${aiType}:`, analysis);
    
    res.json({
      aiType,
      analysis,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error(`[API] ❌ Error getting learning sessions for ${req.params.aiType}:`, error);
    res.status(500).json({ error: error.message });
  }
});

// Manual learning trigger endpoint (for testing)
app.post('/api/ai/:aiType/trigger-learning', async (req, res) => {
  try {
    const { aiType } = req.params;
    const AILearningService = require('./services/aiLearningService');
    
    if (!['Imperium', 'Sandbox', 'Guardian'].includes(aiType)) {
      return res.status(400).json({ error: 'Invalid AI type' });
    }
    
    await AILearningService.checkForLearningTrigger(aiType);
    
    const { aiStatus } = require('./state');
    const isLearning = aiStatus[aiType]?.isLearning || false;
    
    res.json({ 
      aiType, 
      isLearning,
      message: isLearning ? 'Learning triggered successfully' : 'No learning trigger conditions met'
    });
  } catch (error) {
    console.error(`[API] ❌ Error triggering learning for ${req.params.aiType}:`, error);
    res.status(500).json({ error: error.message });
  }
});

// Manual learning completion check endpoint (for testing)
app.post('/api/ai/:aiType/check-completion', async (req, res) => {
  try {
    const { aiType } = req.params;
    const AILearningService = require('./services/aiLearningService');
    
    if (!['Imperium', 'Sandbox', 'Guardian'].includes(aiType)) {
      return res.status(400).json({ error: 'Invalid AI type' });
    }
    
    await AILearningService.checkLearningCompletion(aiType);
    
    const { aiStatus } = require('./state');
    const isLearning = aiStatus[aiType]?.isLearning || false;
    
    res.json({ 
      aiType, 
      isLearning,
      message: isLearning ? 'Still in learning state' : 'Learning completed or not in learning state'
    });
  } catch (error) {
    console.error(`[API] ❌ Error checking learning completion for ${req.params.aiType}:`, error);
    res.status(500).json({ error: error.message });
  }
});

// Manual trigger endpoints for AIs
app.post('/api/ai/:aiType/trigger', async (req, res) => {
  try {
    const { aiType } = req.params;
    console.log(`[MANUAL_TRIGGER] 🚀 Manually triggering ${aiType}...`);
    
    // Get a sample file to test with
    const files = getAllDartFiles(path.join(LOCAL_PATH, 'lib'));
    if (files.length === 0) {
      return res.status(404).json({ error: 'No Dart files found to analyze' });
    }
    
    const testFile = files[0];
    const code = fs.readFileSync(testFile, 'utf8');
    
    let result;
    switch (aiType.toLowerCase()) {
      case 'imperium':
        result = await runImperiumExperiment(code, testFile);
        break;
      case 'sandbox':
        result = await runSandboxExperiment(code, testFile);
        break;
      case 'guardian':
        result = await runGuardianExperiment(code, testFile);
        break;
      default:
        return res.status(400).json({ error: `Unknown AI type: ${aiType}` });
    }
    
    console.log(`[MANUAL_TRIGGER] ✅ ${aiType} triggered successfully`);
    res.json({ 
      message: `${aiType} triggered successfully`,
      filePath: testFile,
      result: result
    });
  } catch (error) {
    console.error(`[MANUAL_TRIGGER] ❌ Error triggering ${req.params.aiType}:`, error);
    res.status(500).json({ error: error.message });
  }
});

// TODO: Add your routes here (e.g., proposals, experiments, etc.)