const express = require('express');
const router = express.Router();
const Proposal = require('../models/proposal');
const AILearningService = require('../services/aiLearningService');
const DeduplicationService = require('../services/deduplicationService');
const { AIQuotaService } = require('../services/aiQuotaService');
const Learning = require('../models/learning');
const gitService = require('../services/gitService');
const apkBuildService = require('../services/apkBuildService');
const { io } = require('../index');

// Create a new proposal (AI submits)
router.post('/', async (req, res) => {
  try {
    const proposal = new Proposal(req.body);
    await proposal.save();
    
    // Fix Socket.IO access
    const io = req.app.get('io');
    if (io) {
      io.emit('proposal:created', proposal);
    }
    
    res.json(proposal);
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

// Get all proposals (optionally filter by status)
router.get('/', async (req, res) => {
  try {
    const { status } = req.query;
    const filter = status ? { status } : {};
    const proposals = await Proposal.find(filter).sort({ createdAt: -1 });
    
    // Remove duplicate proposals based on filePath and similar code changes
    const uniqueProposals = [];
    const seenProposals = new Set();
    
    for (const proposal of proposals) {
      const key = `${proposal.filePath}-${proposal.aiType}-${proposal.status}`;
      
      // Check if this is a duplicate or improvement
      const existingProposal = uniqueProposals.find(p => 
        p.filePath === proposal.filePath && 
        p.aiType === proposal.aiType &&
        p.status === proposal.status
      );
      
      if (existingProposal) {
        // If it's a duplicate, keep the newer one if it's an improvement
        if (proposal.createdAt > existingProposal.createdAt) {
          const index = uniqueProposals.indexOf(existingProposal);
          uniqueProposals[index] = proposal;
        }
      } else {
        uniqueProposals.push(proposal);
      }
    }
    
    res.json(uniqueProposals);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Approve/reject a proposal
router.post('/:id/decision', async (req, res) => {
  const { decision } = req.body; // 'approved' or 'rejected'
  if (!['approved', 'rejected'].includes(decision)) {
    return res.status(400).json({ error: 'Invalid decision' });
  }
  let proposal = await Proposal.findById(req.params.id);
  if (!proposal) return res.status(404).json({ error: 'Proposal not found' });

  if (decision === 'approved') {
    // Apply code change to GitHub and create PR
    try {
      // Dynamic import to avoid ES module issues
      const { applyProposalAndPR } = await import('../services/githubService.js');
      const prUrl = await applyProposalAndPR({
        filePath: proposal.filePath,
        codeAfter: proposal.codeAfter,
        proposalId: proposal._id,
      });
      proposal.prUrl = prUrl;
      proposal.status = 'pr_opened';
      await proposal.save();
      
      // Fix Socket.IO access
      const io = req.app.get('io');
      if (io) {
        io.emit('pr_opened', { proposalId: proposal._id, prUrl });
      }
    } catch (e) {
      return res.status(500).json({ error: 'Failed to create PR: ' + e.message });
    }
  } else {
    proposal.status = 'rejected';
    await proposal.save();
  }
  
  // Fix Socket.IO access
  const io = req.app.get('io');
  if (io) {
    io.emit('proposal:update', proposal);
  }
  
  res.json(proposal);
});

// Approve a proposal with enhanced learning
router.post('/:id/approve', async (req, res) => {
  try {
    console.log(`[PROPOSALS] Approving proposal: ${req.params.id}`);
    
    const proposal = await Proposal.findById(req.params.id);
    if (!proposal) return res.status(404).json({ error: 'Proposal not found' });
    
    // Block if AI is in learning state
    const { aiStatus, logEvent } = require('../state');
    if (aiStatus[proposal.aiType] && aiStatus[proposal.aiType].isLearning) {
      logEvent(`[PROPOSALS] Blocked approval: ${proposal.aiType} is in learning state.`);
      return res.status(403).json({ error: `${proposal.aiType} is currently learning. Approval is temporarily disabled.` });
    }
    
    console.log(`[PROPOSALS] Found proposal: ${proposal.aiType} - ${proposal.filePath}`);
    
    // Get feedback reason from request body (safely handle undefined req.body)
    const feedbackReason = (req.body && req.body.feedbackReason) ? req.body.feedbackReason : 'Approved by user';
    
    console.log(`[PROPOSALS] Using feedback reason: ${feedbackReason}`);
    
    // Update proposal with feedback
    proposal.status = 'approved';
    proposal.userFeedback = 'approved';
    proposal.userFeedbackReason = feedbackReason;
    await proposal.save();
    
    // Update AI learning with positive feedback
    await AILearningService.updateLearning(req.params.id, 'approved', feedbackReason);
    
    // Increment processed proposals count for quota tracking
    await AIQuotaService.incrementProcessedProposals(proposal.aiType);
    
    // Check if AI should enter learning state after this action
    await AILearningService.checkForLearningTrigger(proposal.aiType);
    
    console.log(`[PROPOSALS] Proposal approved and learning updated`);
    
    // Fix Socket.IO access
    const io = req.app.get('io');
    console.log(`[PROPOSALS] Socket.IO instance: ${io ? 'found' : 'not found'}`);
    
    if (io) {
      io.emit('proposal:approved', proposal);
      io.emit('learning:proposal-updated', { 
        aiType: proposal.aiType, 
        action: 'approved', 
        proposalId: proposal._id 
      });
      console.log(`[PROPOSALS] Socket.IO event emitted: proposal:approved`);
    } else {
      console.log(`[PROPOSALS] WARNING: Socket.IO instance not available`);
    }
    
    res.json(proposal);
  } catch (e) {
    console.error(`[PROPOSALS] Error approving proposal:`, e);
    res.status(500).json({ error: e.message });
  }
});

// Reject a proposal with enhanced learning
router.post('/:id/reject', async (req, res) => {
  try {
    console.log(`[PROPOSALS] Rejecting proposal: ${req.params.id}`);
    
    const proposal = await Proposal.findById(req.params.id);
    if (!proposal) return res.status(404).json({ error: 'Proposal not found' });
    
    // Block if AI is in learning state
    const { aiStatus, logEvent } = require('../state');
    if (aiStatus[proposal.aiType] && aiStatus[proposal.aiType].isLearning) {
      logEvent(`[PROPOSALS] Blocked rejection: ${proposal.aiType} is in learning state.`);
      return res.status(403).json({ error: `${proposal.aiType} is currently learning. Rejection is temporarily disabled.` });
    }
    
    // Get feedback reason from request body (safely handle undefined req.body)
    const feedbackReason = (req.body && req.body.feedbackReason) ? req.body.feedbackReason : 'Rejected by user';
    
    console.log(`[PROPOSALS] Using feedback reason: ${feedbackReason}`);
    
    proposal.status = 'rejected';
    proposal.userFeedback = 'rejected';
    proposal.userFeedbackReason = feedbackReason;
    await proposal.save();
    
    // Update AI learning with negative feedback
    await AILearningService.updateLearning(req.params.id, 'rejected', feedbackReason);
    
    // Increment processed proposals count for quota tracking
    await AIQuotaService.incrementProcessedProposals(proposal.aiType);
    
    // Check if AI should enter learning state after this action
    await AILearningService.checkForLearningTrigger(proposal.aiType);
    
    console.log(`[PROPOSALS] Proposal rejected and learning updated`);
    
    // Fix Socket.IO access
    const io = req.app.get('io');
    if (io) {
      io.emit('proposal:rejected', proposal);
      io.emit('learning:proposal-updated', { 
        aiType: proposal.aiType, 
        action: 'rejected', 
        proposalId: proposal._id 
      });
    }
    
    res.json(proposal);
  } catch (e) {
    console.error(`[PROPOSALS] Error rejecting proposal:`, e);
    res.status(500).json({ error: e.message });
  }
});

// Reset learning state for an AI
router.post('/reset-learning/:aiType', async (req, res) => {
  try {
    const { aiType } = req.params;
    
    if (!['Imperium', 'Sandbox', 'Guardian'].includes(aiType)) {
      return res.status(400).json({ error: 'Invalid AI type' });
    }
    
    console.log(`[PROPOSALS] 🔄 Resetting learning state for ${aiType}...`);
    
    // Reset learning state
    const AILearningService = require('../services/aiLearningService');
    AILearningService.setLearningState(aiType, false);
    
    // Store a reset event
    await Learning.create({
      aiType,
      status: 'learning-reset',
      feedbackReason: 'Manual learning state reset',
      learningKey: 'manual_reset',
      learningValue: 'Learning state manually reset by user',
      filePath: 'system',
      improvementType: 'system'
    });
    
    console.log(`[PROPOSALS] ✅ Learning state reset for ${aiType}`);
    
    res.json({ 
      message: `Learning state reset for ${aiType}`,
      aiType,
      isLearning: false
    });
  } catch (error) {
    console.error(`[PROPOSALS] ❌ Error resetting learning state:`, error);
    res.status(500).json({ error: error.message });
  }
});

// Get current AI status
router.get('/ai-status', async (req, res) => {
  try {
    const { getAIStatus } = require('../state');
    const status = getAIStatus();
    res.json(status);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// GET /api/proposals/debug - Show all proposals with their status
router.get('/debug', async (req, res) => {
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
      stats,
      proposals: proposals.map(p => ({
        id: p._id,
        aiType: p.aiType,
        filePath: p.filePath,
        status: p.status,
        testStatus: p.testStatus,
        createdAt: p.createdAt,
        hasTestOutput: !!p.testOutput,
      }))
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// GET /api/proposals/learning-stats - Get AI learning statistics
router.get('/learning-stats', async (req, res) => {
  try {
    const { aiType } = req.query;
    const aiTypes = aiType ? [aiType] : ['Imperium', 'Guardian', 'Sandbox'];
    
    const stats = {};
    for (const type of aiTypes) {
      stats[type] = await AILearningService.getLearningStats(type);
    }
    
    // Get duplicate statistics
    const duplicateStats = await DeduplicationService.getDuplicateStats();
    
    res.json({
      learningStats: stats,
      duplicateStats
    });
  } catch (e) {
    console.error(`[PROPOSALS] Error getting learning stats:`, e);
    res.status(500).json({ error: e.message });
  }
});

// GET /api/proposals/feedback-patterns - Get feedback patterns for AI learning
router.get('/feedback-patterns', async (req, res) => {
  try {
    const { aiType, days } = req.query;
    const aiTypes = aiType ? [aiType] : ['Imperium', 'Guardian', 'Sandbox'];
    
    const patterns = {};
    for (const type of aiTypes) {
      patterns[type] = await AILearningService.analyzeFeedbackPatterns(type, parseInt(days) || 30);
    }
    
    res.json(patterns);
  } catch (e) {
    console.error(`[PROPOSALS] Error getting feedback patterns:`, e);
    res.status(500).json({ error: e.message });
  }
});

// Get operating hours status
router.get('/operating-hours', async (req, res) => {
  try {
    const status = AIQuotaService.getOperatingStatus();
    res.json(status);
  } catch (error) {
    console.error('Error getting operating hours status:', error);
    res.status(500).json({ error: 'Failed to get operating hours status' });
  }
});

// Get all quota status
router.get('/quotas', async (req, res) => {
  try {
    const status = await AIQuotaService.getAllQuotaStatus();
    res.json(status);
  } catch (error) {
    console.error('Error getting quota status:', error);
    res.status(500).json({ error: 'Failed to get quota status' });
  }
});

// POST /api/proposals/trigger-learning - Manually trigger AI learning cycle
router.post('/trigger-learning', async (req, res) => {
  try {
    const { aiType, proposalId, result } = req.body;
    
    if (!aiType || !proposalId || !result) {
      return res.status(400).json({ error: 'Missing required fields: aiType, proposalId, result' });
    }
    
    if (!['Imperium', 'Sandbox', 'Guardian'].includes(aiType)) {
      return res.status(400).json({ error: 'Invalid AI type' });
    }
    
    if (!['passed', 'failed', 'approved', 'rejected'].includes(result)) {
      return res.status(400).json({ error: 'Invalid result type' });
    }
    
    console.log(`[PROPOSALS] 🎯 Manually triggering learning cycle for ${aiType} - Result: ${result}`);
    
    // Get the proposal
    const proposal = await Proposal.findById(proposalId);
    if (!proposal) {
      return res.status(404).json({ error: 'Proposal not found' });
    }
    
    // Import the orchestrator
    const AILearningOrchestrator = require('../services/aiLearningOrchestrator');
    
    // Trigger the learning cycle
    const learningResult = await AILearningOrchestrator.triggerLearningCycle(aiType, proposal, result);
    
    console.log(`[PROPOSALS] ✅ Learning cycle triggered successfully for ${aiType}`);
    
    res.json({
      success: true,
      message: `Learning cycle triggered for ${aiType}`,
      learningResult
    });
    
  } catch (error) {
    console.error(`[PROPOSALS] ❌ Error triggering learning cycle:`, error);
    res.status(500).json({ error: error.message });
  }
});

// GET /api/proposals/learning-cycle-stats - Get AI learning cycle statistics
router.get('/learning-cycle-stats', async (req, res) => {
  try {
    const { aiType, days } = req.query;
    const aiTypes = aiType ? [aiType] : ['Imperium', 'Guardian', 'Sandbox'];
    
    const AILearningOrchestrator = require('../services/aiLearningOrchestrator');
    const stats = {};
    
    for (const type of aiTypes) {
      stats[type] = await AILearningOrchestrator.getLearningCycleStats(type, parseInt(days) || 30);
    }
    
    res.json({
      learningCycleStats: stats,
      summary: {
        totalAIs: aiTypes.length,
        daysAnalyzed: parseInt(days) || 30
      }
    });
    
  } catch (error) {
    console.error(`[PROPOSALS] Error getting learning cycle stats:`, error);
    res.status(500).json({ error: error.message });
  }
});

// GET /api/proposals/github-status - Get GitHub repository status for AI learning
router.get('/github-status', async (req, res) => {
  try {
    const { getRepositoryStatus } = require('../services/githubService');
    const status = await getRepositoryStatus();
    
    res.json(status);
    
  } catch (error) {
    console.error(`[PROPOSALS] Error getting GitHub status:`, error);
    res.status(500).json({ error: error.message });
  }
});

// POST /api/proposals/merge-learning-pr - Merge AI learning pull request
router.post('/merge-learning-pr', async (req, res) => {
  try {
    const { prUrl } = req.body;
    
    if (!prUrl) {
      return res.status(400).json({ error: 'Missing PR URL' });
    }
    
    console.log(`[PROPOSALS] 🔄 Merging AI learning PR: ${prUrl}`);
    
    const { mergeAILearningPR } = require('../services/githubService');
    const success = await mergeAILearningPR(prUrl);
    
    if (success) {
      console.log(`[PROPOSALS] ✅ Successfully merged AI learning PR: ${prUrl}`);
      res.json({
        success: true,
        message: 'AI learning PR merged successfully',
        prUrl
      });
    } else {
      res.status(400).json({
        success: false,
        message: 'Failed to merge AI learning PR',
        prUrl
      });
    }
    
  } catch (error) {
    console.error(`[PROPOSALS] ❌ Error merging AI learning PR:`, error);
    res.status(500).json({ error: error.message });
  }
});

// GET /api/proposals/internet-learning-status - Get internet learning system status
router.get('/internet-learning-status', async (req, res) => {
  try {
    const { aiType } = req.query;
    const aiTypes = aiType ? [aiType] : ['Imperium', 'Guardian', 'Sandbox'];
    
    const status = {};
    
    for (const type of aiTypes) {
      // Get recent internet learning entries
      const recentLearning = await Learning.find({
        aiType: type,
        learningKey: { $regex: /^internet_/ },
        timestamp: { $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) } // Last 24 hours
      }).sort({ timestamp: -1 }).limit(10);
      
      // Get learning cycle stats
      const AILearningOrchestrator = require('../services/aiLearningOrchestrator');
      const cycleStats = await AILearningOrchestrator.getLearningCycleStats(type, 1); // Last day
      
      status[type] = {
        recentInternetLearning: recentLearning.length,
        learningCycles: cycleStats.totalCycles || 0,
        successRate: cycleStats.successRate || 0,
        averageInsights: cycleStats.averageInsightsPerCycle || 0,
        lastLearning: recentLearning[0]?.timestamp || null
      };
    }
    
    res.json({
      internetLearningStatus: status,
      summary: {
        totalAIs: aiTypes.length,
        timeRange: 'Last 24 hours'
      }
    });
    
  } catch (error) {
    console.error(`[PROPOSALS] Error getting internet learning status:`, error);
    res.status(500).json({ error: error.message });
  }
});

// Update proposal status
router.put('/:id/status', async (req, res) => {
  try {
    const { id } = req.params;
    const { status, userFeedbackReason } = req.body;
    
    const proposal = await Proposal.findByIdAndUpdate(
      id,
      { 
        status,
        userFeedbackReason,
        userFeedbackTime: new Date()
      },
      { new: true }
    );
    
    if (!proposal) {
      return res.status(404).json({ error: 'Proposal not found' });
    }
    
    // Emit status update event
    io.emit('proposal:status-updated', {
      proposalId: id,
      status,
      userFeedbackReason,
      timestamp: new Date()
    });
    
    // If proposal is approved or test-passed, trigger APK build
    if (status === 'approved' || status === 'test-passed') {
      console.log(`[PROPOSALS_ROUTE] 🏗️ Triggering APK build for approved proposal: ${id}`);
      
      // Trigger APK build asynchronously
      apkBuildService.buildAPKAfterProposal(id)
        .then(buildResult => {
          console.log(`[PROPOSALS_ROUTE] ✅ APK build completed for proposal ${id}:`, buildResult.success);
          
          // Emit APK build event
          io.emit('proposal:apk-built', {
            proposalId: id,
            success: buildResult.success,
            apkPath: buildResult.apkPath,
            apkSize: buildResult.apkSize,
            buildTime: buildResult.buildTime
          });
        })
        .catch(error => {
          console.error(`[PROPOSALS_ROUTE] ❌ APK build failed for proposal ${id}:`, error.message);
          
          // Emit APK build failure event
          io.emit('proposal:apk-build-failed', {
            proposalId: id,
            error: error.message
          });
        });
    }
    
    // Update AI learning data
    await AILearningService.updateLearningData(proposal.aiType, {
      proposalId: id,
      status,
      userFeedbackReason,
      filePath: proposal.filePath,
      improvementType: proposal.improvementType
    });
    
    res.json(proposal);
  } catch (error) {
    console.error('[PROPOSALS_ROUTE] Error updating proposal status:', error);
    res.status(500).json({ error: 'Failed to update proposal status' });
  }
});

// Get APK build status for a proposal
router.get('/:id/apk-status', async (req, res) => {
  try {
    const { id } = req.params;
    
    const proposal = await Proposal.findById(id);
    if (!proposal) {
      return res.status(404).json({ error: 'Proposal not found' });
    }
    
    const apkStatus = await apkBuildService.getCurrentAPKStatus();
    
    res.json({
      proposalId: id,
      proposalStatus: proposal.status,
      apkBuildInfo: proposal.apkBuildInfo || null,
      currentAPKStatus: apkStatus
    });
  } catch (error) {
    console.error('[PROPOSALS_ROUTE] Error getting APK status:', error);
    res.status(500).json({ error: 'Failed to get APK status' });
  }
});

// Trigger APK build manually
router.post('/:id/build-apk', async (req, res) => {
  try {
    const { id } = req.params;
    
    const proposal = await Proposal.findById(id);
    if (!proposal) {
      return res.status(404).json({ error: 'Proposal not found' });
    }
    
    console.log(`[PROPOSALS_ROUTE] 🏗️ Manually triggering APK build for proposal: ${id}`);
    
    // Trigger APK build
    const buildResult = await apkBuildService.buildAPKAfterProposal(id);
    
    res.json({
      proposalId: id,
      buildResult,
      message: buildResult.success ? 'APK build started successfully' : 'APK build failed'
    });
  } catch (error) {
    console.error('[PROPOSALS_ROUTE] Error triggering APK build:', error);
    res.status(500).json({ error: 'Failed to trigger APK build' });
  }
});

// Get APK build history
router.get('/apk-build-history', async (req, res) => {
  try {
    const { days = 7 } = req.query;
    
    const buildHistory = await apkBuildService.getAPKBuildHistory(parseInt(days));
    
    res.json(buildHistory);
  } catch (error) {
    console.error('[PROPOSALS_ROUTE] Error getting APK build history:', error);
    res.status(500).json({ error: 'Failed to get APK build history' });
  }
});

// Clean old APK builds
router.post('/clean-apk-builds', async (req, res) => {
  try {
    await apkBuildService.cleanOldAPKBuilds();
    
    res.json({ message: 'Old APK builds cleaned successfully' });
  } catch (error) {
    console.error('[PROPOSALS_ROUTE] Error cleaning APK builds:', error);
    res.status(500).json({ error: 'Failed to clean APK builds' });
  }
});

module.exports = router;