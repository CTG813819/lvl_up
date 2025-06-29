const express = require('express');
const router = express.Router();
const Learning = require('../models/learning');
const Proposal = require('../models/proposal');
const Experiment = require('../models/experiment');
const { AIQuotaService } = require('../services/aiQuotaService');
const AILearningService = require('../services/aiLearningService');
const AISelfImprovementService = require('../services/aiSelfImprovementService');
const gitService = require('../services/gitService');
const fs = require('fs').promises;
const path = require('path');

// Get learning data for all AIs
router.get('/data', async (req, res) => {
  try {
    console.log('[LEARNING_ROUTES] 📊 Fetching learning data for all AIs...');
    
    const aiTypes = ['Imperium', 'Sandbox', 'Guardian'];
    const learningData = {};
    
    for (const aiType of aiTypes) {
      // Get recent proposals for this AI (limit to 10 to reduce memory)
      const proposals = await Proposal.find({ aiType })
        .sort({ createdAt: -1 })
        .limit(10)
        .select('userFeedbackReason status filePath improvementType createdAt')
        .lean(); // Use lean() for better memory efficiency
      
      // Get recent learning entries for this AI (limit to 10)
      const learningEntries = await Learning.find({ aiType })
        .sort({ timestamp: -1 })
        .limit(10)
        .select('learningValue learningKey status timestamp filePath improvementType')
        .lean();
      
      // Get recent experiments for this AI (limit to 10)
      const experiments = await Experiment.find({ 
        aiName: aiType === 'Imperium' ? 'The Imperium' : aiType === 'Sandbox' ? 'AI Sandbox' : 'AI Guardian' 
      })
        .sort({ createdAt: -1 })
        .limit(10)
        .select('experimentType result.suggestion result.reasoning createdAt executionTime')
        .lean();
      
      // Extract lessons from learning entries (limit to 5)
      const lessons = learningEntries
        .filter(entry => entry.learningValue && entry.learningValue.length > 0)
        .slice(0, 5)
        .map(entry => ({
          lesson: entry.learningValue,
          source: entry.learningKey,
          timestamp: entry.timestamp,
          status: entry.status
        }));
      
      // Extract user feedback from proposals (limit to 5)
      const userFeedback = proposals
        .filter(proposal => proposal.userFeedbackReason)
        .slice(0, 5)
        .map(proposal => ({
          feedback: proposal.userFeedbackReason,
          status: proposal.status,
          timestamp: proposal.createdAt,
          filePath: proposal.filePath
        }));
      
      // Extract backend test results from experiments (limit to 5)
      const backendTestResults = experiments
        .filter(exp => exp.result && exp.result.suggestion !== undefined)
        .slice(0, 5)
        .map(exp => ({
          testType: exp.experimentType,
          result: exp.result.suggestion ? 'pass' : 'fail',
          details: exp.result.reasoning || 'No reasoning provided',
          timestamp: exp.createdAt,
          executionTime: exp.executionTime
        }));
      
      learningData[aiType] = {
        lessons: lessons,
        userFeedback: userFeedback,
        backendTestResults: backendTestResults,
        debugLog: [], // Will be populated from debug log
        learningScore: Math.floor(Math.random() * 100), // Placeholder
        totalProposals: proposals.length,
        totalLearningEntries: learningEntries.length,
        totalExperiments: experiments.length
      };
    }
    
    console.log('[LEARNING_ROUTES] ✅ Learning data fetched successfully');
    
    // Emit real-time update
    const io = req.app.get('io');
    if (io) {
      io.emit('learning:data-updated', learningData);
    }
    
    res.json(learningData);
  } catch (error) {
    console.error('[LEARNING_ROUTES] ❌ Error fetching learning data:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get learning metrics for all AIs
router.get('/metrics', async (req, res) => {
  try {
    console.log('[LEARNING_ROUTES] 📈 Fetching learning metrics for all AIs...');
    
    const aiTypes = ['Imperium', 'Sandbox', 'Guardian'];
    const learningMetrics = {};
    
    for (const aiType of aiTypes) {
      // Get counts instead of full documents to save memory
      const totalProposals = await Proposal.countDocuments({ aiType });
      const approvedProposals = await Proposal.countDocuments({ aiType, status: 'approved' });
      const rejectedProposals = await Proposal.countDocuments({ aiType, status: 'rejected' });
      
      const totalLearningEntries = await Learning.countDocuments({ aiType });
      const appliedLearningEntries = await Learning.countDocuments({ aiType, status: 'approved' });
      
      const totalExperiments = await Experiment.countDocuments({ 
        aiName: aiType === 'Imperium' ? 'The Imperium' : aiType === 'Sandbox' ? 'AI Sandbox' : 'AI Guardian' 
      });
      const successfulExperiments = await Experiment.countDocuments({ 
        aiName: aiType === 'Imperium' ? 'The Imperium' : aiType === 'Sandbox' ? 'AI Sandbox' : 'AI Guardian',
        'result.suggestion': true
      });
      
      // Calculate metrics
      const successRate = totalProposals > 0 ? Math.round((approvedProposals / totalProposals) * 100) : 0;
      const appliedLearning = totalLearningEntries > 0 ? Math.round((appliedLearningEntries / totalLearningEntries) * 100) : 0;
      const backendTestSuccessRate = totalExperiments > 0 ? Math.round((successfulExperiments / totalExperiments) * 100) : 0;
      const learningScore = Math.round((successRate + appliedLearning + backendTestSuccessRate) / 3);
      
      learningMetrics[aiType] = {
        learningScore: learningScore,
        successRate: successRate,
        appliedLearning: appliedLearning,
        backendTestSuccessRate: backendTestSuccessRate,
        totalProposals: totalProposals,
        backendTests: totalExperiments,
        totalLearningEntries: totalLearningEntries,
        approvedProposals: approvedProposals,
        rejectedProposals: rejectedProposals
      };
    }
    
    console.log('[LEARNING_ROUTES] ✅ Learning metrics fetched successfully');
    
    // Emit real-time update
    const io = req.app.get('io');
    if (io) {
      io.emit('learning:metrics-updated', learningMetrics);
    }
    
    res.json(learningMetrics);
  } catch (error) {
    console.error('[LEARNING_ROUTES] ❌ Error fetching learning metrics:', error);
    res.status(500).json({ error: error.message });
  }
});

// NEW: Cross-AI Learning Endpoint
router.post('/cross-ai-learning', async (req, res) => {
  try {
    const { sourceAI, targetAI, learningType, data } = req.body;
    
    console.log(`[LEARNING_ROUTES] 🔄 Cross-AI learning: ${sourceAI} → ${targetAI} (${learningType})`);
    
    if (!sourceAI || !targetAI || !learningType) {
      return res.status(400).json({ error: 'Missing required fields: sourceAI, targetAI, learningType' });
    }
    
    // Validate AI types
    const validAIs = ['Imperium', 'Sandbox', 'Guardian'];
    if (!validAIs.includes(sourceAI) || !validAIs.includes(targetAI)) {
      return res.status(400).json({ error: 'Invalid AI type' });
    }
    
    // Create learning entry for cross-AI learning
    const learningEntry = new Learning({
      aiType: targetAI,
      learningKey: `cross-ai-${learningType}`,
      learningValue: `Learned from ${sourceAI}: ${data.insight || 'Cross-AI knowledge transfer'}`,
      status: 'learning-completed',
      timestamp: new Date(),
      filePath: data.filePath || 'cross-ai-learning',
      improvementType: learningType,
      metadata: {
        sourceAI,
        learningType,
        originalData: data
      }
    });
    
    await learningEntry.save();
    
    // Trigger learning context update for target AI
    await AILearningService.generateLearningContext(targetAI);
    
    console.log(`[LEARNING_ROUTES] ✅ Cross-AI learning completed: ${sourceAI} → ${targetAI}`);
    
    // Emit real-time update
    const io = req.app.get('io');
    if (io) {
      io.emit('learning:cross-ai-completed', {
        sourceAI,
        targetAI,
        learningType,
        timestamp: new Date()
      });
    }
    
    res.json({
      success: true,
      message: `Cross-AI learning completed: ${sourceAI} → ${targetAI}`,
      learningEntry
    });
  } catch (error) {
    console.error('[LEARNING_ROUTES] ❌ Error in cross-AI learning:', error);
    res.status(500).json({ error: error.message });
  }
});

// NEW: Source Code Improvement Endpoint
router.post('/improve-source-code', async (req, res) => {
  try {
    const { aiType, filePath, improvementType, newCode, reasoning } = req.body;
    
    console.log(`[LEARNING_ROUTES] 🔧 Source code improvement for ${aiType}: ${filePath}`);
    
    if (!aiType || !filePath || !improvementType || !newCode) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    
    // Validate AI type
    const validAIs = ['Imperium', 'Sandbox', 'Guardian'];
    if (!validAIs.includes(aiType)) {
      return res.status(400).json({ error: 'Invalid AI type' });
    }
    
    // Create learning entry for source code improvement
    const learningEntry = new Learning({
      aiType,
      learningKey: 'source-code-improvement',
      learningValue: `Improved ${filePath}: ${reasoning || improvementType}`,
      status: 'learning-completed',
      timestamp: new Date(),
      filePath,
      improvementType,
      metadata: {
        newCode,
        reasoning,
        originalFile: filePath
      }
    });
    
    await learningEntry.save();
    
    // Apply the code improvement to the actual file
    try {
      const fullPath = path.join(process.env.GIT_REPO_PATH || '.', filePath);
      await fs.writeFile(fullPath, newCode, 'utf8');
      
      // Commit and push to Git
      await gitService.applyProposalAndPush(filePath, newCode, `ai-${aiType.toLowerCase()}-improvements`);
      
      console.log(`[LEARNING_ROUTES] ✅ Source code improvement applied and pushed to Git: ${filePath}`);
      
      // Emit real-time update
      const io = req.app.get('io');
      if (io) {
        io.emit('learning:source-code-improved', {
          aiType,
          filePath,
          improvementType,
          timestamp: new Date()
        });
      }
      
      res.json({
        success: true,
        message: `Source code improvement applied and pushed to Git`,
        filePath,
        gitBranch: `ai-${aiType.toLowerCase()}-improvements`
      });
    } catch (gitError) {
      console.error('[LEARNING_ROUTES] ❌ Git operation failed:', gitError);
      res.status(500).json({ 
        error: 'Source code improvement saved but Git operation failed',
        details: gitError.message 
      });
    }
  } catch (error) {
    console.error('[LEARNING_ROUTES] ❌ Error in source code improvement:', error);
    res.status(500).json({ error: error.message });
  }
});

// NEW: Get AI Learning Insights
router.get('/insights/:aiType', async (req, res) => {
  try {
    const { aiType } = req.params;
    
    console.log(`[LEARNING_ROUTES] 🧠 Getting learning insights for ${aiType}`);
    
    if (!['Imperium', 'Sandbox', 'Guardian'].includes(aiType)) {
      return res.status(400).json({ error: 'Invalid AI type' });
    }
    
    // Get learning insights from the service
    const insights = await AILearningService.getLearningInsights(aiType);
    
    // Get recent improvements
    const recentImprovements = await Learning.find({ 
      aiType, 
      status: 'learning-completed',
      learningKey: { $in: ['source-code-improvement', 'cross-ai-learning'] }
    })
    .sort({ timestamp: -1 })
    .limit(10)
    .lean();
    
    // Get learning patterns
    const patterns = await AILearningService.analyzeFeedbackPatterns(aiType, 30);
    
    const learningInsights = {
      aiType,
      insights,
      recentImprovements,
      patterns,
      learningContext: await AILearningService.generateLearningContext(aiType),
      timestamp: new Date()
    };
    
    console.log(`[LEARNING_ROUTES] ✅ Learning insights fetched for ${aiType}`);
    res.json(learningInsights);
  } catch (error) {
    console.error('[LEARNING_ROUTES] ❌ Error getting learning insights:', error);
    res.status(500).json({ error: error.message });
  }
});

// NEW: Trigger AI Self-Improvement
router.post('/trigger-improvement/:aiType', async (req, res) => {
  try {
    const { aiType } = req.params;
    const { improvementType, targetFile } = req.body;
    
    console.log(`[LEARNING_ROUTES] 🚀 Triggering self-improvement for ${aiType}`);
    
    if (!['Imperium', 'Sandbox', 'Guardian'].includes(aiType)) {
      return res.status(400).json({ error: 'Invalid AI type' });
    }
    
    // Trigger self-improvement using the service
    const result = await AISelfImprovementService.triggerSelfImprovement(aiType, improvementType, targetFile);
    
    console.log(`[LEARNING_ROUTES] ✅ Self-improvement triggered for ${aiType}`);
    
    // Emit real-time update
    const io = req.app.get('io');
    if (io) {
      io.emit('learning:self-improvement-triggered', {
        aiType,
        improvementType,
        result,
        timestamp: new Date()
      });
    }
    
    res.json({
      success: true,
      message: `Self-improvement triggered for ${aiType}`,
      result
    });
  } catch (error) {
    console.error('[LEARNING_ROUTES] ❌ Error triggering self-improvement:', error);
    res.status(500).json({ error: error.message });
  }
});

// NEW: Get Self-Improvement History
router.get('/self-improvement-history/:aiType', async (req, res) => {
  try {
    const { aiType } = req.params;
    const { days = 30 } = req.query;
    
    console.log(`[LEARNING_ROUTES] 📊 Getting self-improvement history for ${aiType}`);
    
    if (!['Imperium', 'Sandbox', 'Guardian'].includes(aiType)) {
      return res.status(400).json({ error: 'Invalid AI type' });
    }
    
    const history = await AISelfImprovementService.getImprovementHistory(aiType, parseInt(days));
    
    res.json({
      success: true,
      data: history
    });
  } catch (error) {
    console.error('[LEARNING_ROUTES] ❌ Error getting self-improvement history:', error);
    res.status(500).json({ error: error.message });
  }
});

// NEW: Get Self-Improvement Suggestions
router.get('/self-improvement-suggestions/:aiType', async (req, res) => {
  try {
    const { aiType } = req.params;
    
    console.log(`[LEARNING_ROUTES] 💡 Getting self-improvement suggestions for ${aiType}`);
    
    if (!['Imperium', 'Sandbox', 'Guardian'].includes(aiType)) {
      return res.status(400).json({ error: 'Invalid AI type' });
    }
    
    const suggestions = await AISelfImprovementService.getImprovementSuggestions(aiType);
    
    res.json({
      success: true,
      data: suggestions
    });
  } catch (error) {
    console.error('[LEARNING_ROUTES] ❌ Error getting self-improvement suggestions:', error);
    res.status(500).json({ error: error.message });
  }
});

// NEW: Get Learning Progress for Conquest AI
router.get('/conquest-progress', async (req, res) => {
  try {
    console.log('[LEARNING_ROUTES] 📊 Getting Conquest AI learning progress...');
    
    // Get learning data from all AIs that Conquest can learn from
    const sourceAIs = ['Imperium', 'Sandbox', 'Guardian'];
    const conquestLearningData = {};
    
    for (const sourceAI of sourceAIs) {
      // Get successful patterns from each AI
      const patterns = await AILearningService.analyzeFeedbackPatterns(sourceAI, 30);
      
      // Get recent successful proposals
      const successfulProposals = await Proposal.find({
        aiType: sourceAI,
        status: 'approved'
      })
      .sort({ createdAt: -1 })
      .limit(5)
      .select('filePath improvementType userFeedbackReason aiReasoning')
      .lean();
      
      conquestLearningData[sourceAI] = {
        successPatterns: patterns.successPatterns,
        commonMistakes: patterns.commonMistakes,
        successfulProposals,
        learningScore: await AILearningService.getLearningStats(sourceAI)
      };
    }
    
    // Get Conquest's own learning progress
    const conquestLearningEntries = await Learning.find({
      aiType: 'Conquest',
      learningKey: { $regex: /cross-ai|source-code-improvement/ }
    })
    .sort({ timestamp: -1 })
    .limit(20)
    .lean();
    
    const conquestProgress = {
      sourceAILearning: conquestLearningData,
      conquestLearning: conquestLearningEntries,
      totalLearningSessions: conquestLearningEntries.length,
      recentImprovements: conquestLearningEntries.filter(entry => 
        entry.learningKey === 'source-code-improvement'
      ).length,
      crossAILearning: conquestLearningEntries.filter(entry => 
        entry.learningKey.includes('cross-ai')
      ).length
    };
    
    console.log('[LEARNING_ROUTES] ✅ Conquest learning progress fetched');
    res.json(conquestProgress);
  } catch (error) {
    console.error('[LEARNING_ROUTES] ❌ Error getting Conquest progress:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get learning effectiveness data
router.get('/effectiveness', async (req, res) => {
  try {
    console.log('[LEARNING_ROUTES] 📊 Fetching learning effectiveness data...');
    
    const aiTypes = ['Imperium', 'Sandbox', 'Guardian'];
    const overall = {
      completionRate: 0,
      averageImprovement: 0,
      totalLearningSessions: 0
    };
    
    const byAI = {};
    
    for (const aiType of aiTypes) {
      const allLearningEntries = await Learning.find({ aiType });
      const completedLearning = allLearningEntries.filter(l => l.status === 'learning-completed');
      const improvementEntries = allLearningEntries.filter(l => l.status === 'approved');
      
      const completionRate = allLearningEntries.length > 0 ? Math.round((completedLearning.length / allLearningEntries.length) * 100) : 0;
      const averageImprovement = improvementEntries.length > 0 ? Math.round((improvementEntries.length / allLearningEntries.length) * 100) : 0;
      const learningSessions = allLearningEntries.length;
      
      byAI[aiType] = {
        completionRate: completionRate,
        averageDuration: Math.floor(Math.random() * 24) + 1, // Placeholder
        successImprovement: averageImprovement,
        learningSessions: learningSessions
      };
      
      overall.totalLearningSessions += learningSessions;
    }
    
    // Calculate overall metrics
    const totalEntries = Object.values(byAI).reduce((sum, ai) => sum + ai.learningSessions, 0);
    overall.completionRate = totalEntries > 0 ? Math.round(Object.values(byAI).reduce((sum, ai) => sum + ai.completionRate, 0) / aiTypes.length) : 0;
    overall.averageImprovement = totalEntries > 0 ? Math.round(Object.values(byAI).reduce((sum, ai) => sum + ai.successImprovement, 0) / aiTypes.length) : 0;
    
    const effectiveness = {
      overall: overall,
      byAI: byAI
    };
    
    console.log('[LEARNING_ROUTES] ✅ Learning effectiveness data fetched successfully');
    res.json({ effectiveness });
  } catch (error) {
    console.error('[LEARNING_ROUTES] ❌ Error fetching learning effectiveness:', error);
    res.status(500).json({ error: error.message });
  }
});

// Test endpoint to verify data structure
router.get('/test', async (req, res) => {
  try {
    console.log('[LEARNING_ROUTES] 🧪 Test endpoint called');
    
    const sampleData = {
      'Imperium': {
        lessons: [
          { lesson: 'Test lesson 1', source: 'test', timestamp: new Date(), filePath: 'test.dart', improvementType: 'test' },
          { lesson: 'Test lesson 2', source: 'test', timestamp: new Date(), filePath: 'test.dart', improvementType: 'test' }
        ],
        userFeedback: [
          { feedback: 'Test feedback 1', status: 'approved', timestamp: new Date(), filePath: 'test.dart' },
          { feedback: 'Test feedback 2', status: 'rejected', timestamp: new Date(), filePath: 'test.dart' }
        ],
        backendTestResults: [
          { testType: 'compilation', result: 'pass', details: 'Test passed', timestamp: new Date(), executionTime: 1000 },
          { testType: 'dependency', result: 'fail', details: 'Test failed', timestamp: new Date(), executionTime: 500 }
        ],
        debugLog: [],
        learningScore: 75,
        totalProposals: 2,
        totalLearningEntries: 2,
        totalExperiments: 2
      },
      'Sandbox': {
        lessons: [
          { lesson: 'Sandbox test lesson', source: 'test', timestamp: new Date(), filePath: 'test.dart', improvementType: 'test' }
        ],
        userFeedback: [
          { feedback: 'Sandbox test feedback', status: 'pending', timestamp: new Date(), filePath: 'test.dart' }
        ],
        backendTestResults: [
          { testType: 'syntax', result: 'pass', details: 'Syntax test passed', timestamp: new Date(), executionTime: 800 }
        ],
        debugLog: [],
        learningScore: 60,
        totalProposals: 1,
        totalLearningEntries: 1,
        totalExperiments: 1
      },
      'Guardian': {
        lessons: [
          { lesson: 'Guardian test lesson', source: 'test', timestamp: new Date(), filePath: 'test.dart', improvementType: 'test' }
        ],
        userFeedback: [
          { feedback: 'Guardian test feedback', status: 'approved', timestamp: new Date(), filePath: 'test.dart' }
        ],
        backendTestResults: [
          { testType: 'security', result: 'pass', details: 'Security test passed', timestamp: new Date(), executionTime: 1200 }
        ],
        debugLog: [],
        learningScore: 85,
        totalProposals: 1,
        totalLearningEntries: 1,
        totalExperiments: 1
      }
    };
    
    console.log('[LEARNING_ROUTES] ✅ Test data generated');
    res.json(sampleData);
  } catch (error) {
    console.error('[LEARNING_ROUTES] ❌ Error in test endpoint:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get quota status for all AIs
router.get('/quota', async (req, res) => {
  try {
    console.log('[LEARNING_ROUTES] 📊 Fetching quota status for all AIs...');
    
    const quotaStatus = await AIQuotaService.getAllQuotaStatus();
    
    console.log('[LEARNING_ROUTES] ✅ Quota status fetched successfully');
    
    // Emit real-time update
    const io = req.app.get('io');
    if (io) {
      io.emit('learning:quota-updated', quotaStatus);
    }
    
    res.json(quotaStatus);
  } catch (error) {
    console.error('[LEARNING_ROUTES] ❌ Error fetching quota status:', error);
    res.status(500).json({ error: error.message });
  }
});

// Get quota status for a specific AI
router.get('/quota/:aiType', async (req, res) => {
  try {
    const { aiType } = req.params;
    
    if (!['Imperium', 'Sandbox', 'Guardian'].includes(aiType)) {
      return res.status(400).json({ error: 'Invalid AI type' });
    }
    
    console.log(`[LEARNING_ROUTES] 📊 Fetching quota status for ${aiType}...`);
    
    const quotaStatus = await AIQuotaService.getQuotaStatus(aiType);
    
    console.log(`[LEARNING_ROUTES] ✅ Quota status fetched for ${aiType}`);
    res.json(quotaStatus);
  } catch (error) {
    console.error(`[LEARNING_ROUTES] ❌ Error fetching quota status for ${req.params.aiType}:`, error);
    res.status(500).json({ error: error.message });
  }
});

// Reset quota for a specific AI (for testing/debugging)
router.post('/quota/:aiType/reset', async (req, res) => {
  try {
    const { aiType } = req.params;
    
    if (!['Imperium', 'Sandbox', 'Guardian'].includes(aiType)) {
      return res.status(400).json({ error: 'Invalid AI type' });
    }
    
    console.log(`[LEARNING_ROUTES] 🔄 Resetting quota for ${aiType}...`);
    
    await AIQuotaService.resetQuota(aiType);
    
    console.log(`[LEARNING_ROUTES] ✅ Quota reset for ${aiType}`);
    
    res.json({ 
      message: `Quota reset for ${aiType}`,
      aiType
    });
  } catch (error) {
    console.error(`[LEARNING_ROUTES] ❌ Error resetting quota for ${req.params.aiType}:`, error);
    res.status(500).json({ error: error.message });
  }
});

// Test endpoint to verify basic functionality
router.get('/test/:aiType', async (req, res) => {
  try {
    const { aiType } = req.params;
    
    console.log(`[LEARNING_ROUTE] 🧪 Testing basic functionality for ${aiType}`);
    
    // Test basic operations
    const testResult = {
      aiType,
      timestamp: new Date().toISOString(),
      status: 'working',
      message: 'Basic learning route functionality is working'
    };
    
    res.json(testResult);
  } catch (error) {
    console.error('[LEARNING_ROUTE] Error in test endpoint:', error);
    res.status(500).json({ error: 'Test endpoint failed' });
  }
});

// Trigger AI self-improvement
router.post('/trigger-self-improvement/:aiType', async (req, res) => {
  try {
    const { aiType } = req.params;
    const { improvementTypes } = req.body;
    
    console.log(`[LEARNING_ROUTE] 🧠 Triggering self-improvement for ${aiType}`);
    
    // Generate improvement suggestions using static method
    const suggestions = await AISelfImprovementService.generateSelfImprovementSuggestions(aiType);
    
    // Apply improvements if specified
    let appliedImprovements = null;
    if (improvementTypes && improvementTypes.length > 0) {
      const selectedImprovements = suggestions.suggestions.filter(s => 
        improvementTypes.includes(s.type)
      );
      // Create instance for instance methods
      const selfImprovementService = new AISelfImprovementService();
      appliedImprovements = await selfImprovementService.applyFlutterImprovements(aiType, selectedImprovements);
    }
    
    // Emit learning event
    const io = req.app.get('io');
    if (io) {
      io.emit('ai:self-improvement-triggered', {
        aiType,
        suggestions: suggestions.suggestions.length,
        appliedImprovements: appliedImprovements ? appliedImprovements.appliedChanges : 0,
        timestamp: new Date().toISOString()
      });
    }
    
    res.json({
      aiType,
      suggestions,
      appliedImprovements,
      message: 'Self-improvement triggered successfully'
    });
  } catch (error) {
    console.error('[LEARNING_ROUTE] Error triggering self-improvement:', error);
    res.status(500).json({ error: 'Failed to trigger self-improvement' });
  }
});

// Trigger cross-AI learning
router.post('/trigger-cross-ai-learning', async (req, res) => {
  try {
    const { sourceAI, targetAI, learningFocus } = req.body;
    
    console.log(`[LEARNING_ROUTE] 🔄 Triggering cross-AI learning from ${sourceAI} to ${targetAI}`);
    
    // Get successful patterns from source AI
    const sourcePatterns = await AILearningService.getSuccessfulPatterns(sourceAI);
    
    // Apply patterns to target AI
    const learningResult = await AILearningService.learnFromAI(targetAI, sourceAI, {
      patterns: sourcePatterns,
      learningFocus: learningFocus || 'general_improvements'
    });
    
    // Emit cross-learning event
    const io = req.app.get('io');
    if (io) {
      io.emit('ai:cross-learning-triggered', {
        sourceAI,
        targetAI,
        patternsLearned: sourcePatterns.length,
        learningResult,
        timestamp: new Date().toISOString()
      });
    }
    
    res.json({
      sourceAI,
      targetAI,
      patternsLearned: sourcePatterns.length,
      learningResult,
      message: 'Cross-AI learning completed successfully'
    });
  } catch (error) {
    console.error('[LEARNING_ROUTE] Error triggering cross-AI learning:', error);
    res.status(500).json({ error: 'Failed to trigger cross-AI learning' });
  }
});

// Get Flutter-specific learning insights
router.get('/flutter-insights/:aiType', async (req, res) => {
  try {
    const { aiType } = req.params;
    
    console.log(`[LEARNING_ROUTE] 📊 Getting Flutter insights for ${aiType}`);
    
    // Get Flutter-specific learning data
    const flutterLearning = await Learning.find({
      aiType,
      $or: [
        { learningKey: { $regex: /flutter/i } },
        { learningValue: { $regex: /flutter/i } },
        { filePath: { $regex: /\.dart$/ } }
      ]
    }).sort({ timestamp: -1 }).limit(50);
    
    // Get recent Flutter proposals
    const recentProposals = await Proposal.find({
      aiType,
      filePath: { $regex: /\.dart$/ },
      createdAt: { $gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) }
    }).sort({ createdAt: -1 }).limit(20);
    
    // Count Flutter-specific mistakes from recent proposals
    const flutterMistakes = recentProposals.filter(proposal => {
      const feedback = (proposal.userFeedbackReason || '').toLowerCase();
      const testOutput = (proposal.testOutput || '').toLowerCase();
      const combined = feedback + ' ' + testOutput;
      
      return combined.includes('flutter sdk') || 
             combined.includes('dart pub') || 
             combined.includes('image decoder') || 
             combined.includes('version solving') ||
             combined.includes('flutter_test');
    });
    
    const insights = {
      aiType,
      flutterLearningCount: flutterLearning.length,
      flutterMistakes: flutterMistakes.length,
      recentFlutterProposals: recentProposals.length,
      topFlutterMistakes: flutterMistakes.slice(0, 5).map(mistake => ({
        filePath: mistake.filePath,
        feedback: mistake.userFeedbackReason,
        testOutput: mistake.testOutput,
        timestamp: mistake.createdAt
      })),
      recentFlutterLearning: flutterLearning.slice(0, 10).map(learning => ({
        key: learning.learningKey,
        value: learning.learningValue,
        timestamp: learning.timestamp
      })),
      successRate: recentProposals.length > 0 ? 
        recentProposals.filter(p => p.status === 'approved').length / recentProposals.length : 0,
      timestamp: new Date().toISOString()
    };
    
    res.json(insights);
  } catch (error) {
    console.error('[LEARNING_ROUTE] Error getting Flutter insights:', error);
    res.status(500).json({ error: 'Failed to get Flutter insights' });
  }
});

// Force AI to learn from specific failures
router.post('/learn-from-failures/:aiType', async (req, res) => {
  try {
    const { aiType } = req.params;
    const { failureTypes, forceLearning } = req.body;
    
    console.log(`[LEARNING_ROUTE] 📚 Forcing ${aiType} to learn from failures`);
    
    // Get recent failures
    const recentFailures = await Proposal.find({
      aiType,
      status: { $in: ['rejected', 'test-failed'] },
      createdAt: { $gte: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000) } // Last 3 days
    }).sort({ createdAt: -1 });
    
    // Filter by failure types if specified
    const filteredFailures = failureTypes ? 
      recentFailures.filter(failure => {
        const feedback = (failure.userFeedbackReason || '').toLowerCase();
        const testOutput = (failure.testOutput || '').toLowerCase();
        const combined = feedback + ' ' + testOutput;
        
        return failureTypes.some(type => {
          switch (type) {
            case 'flutter_sdk':
              return combined.includes('flutter sdk') || combined.includes('flutter_test');
            case 'dependency':
              return combined.includes('dart pub') || combined.includes('version solving');
            case 'image_decoder':
              return combined.includes('image decoder') || combined.includes('unimplemented');
            case 'test':
              return combined.includes('test') && (combined.includes('failed') || combined.includes('error'));
            default:
              return true;
          }
        });
      }) : recentFailures;
    
    // Create learning entries for each failure
    const learningEntries = filteredFailures.map(failure => ({
      aiType,
      learningKey: `failure_learning_${Date.now()}`,
      learningValue: `Learn from failure: ${failure.userFeedbackReason || failure.testOutput}`,
      filePath: failure.filePath,
      status: 'learning',
      failureType: categorizeFailure(failure),
      timestamp: new Date().toISOString()
    }));
    
    // Save learning entries
    const savedEntries = await Learning.insertMany(learningEntries);
    
    // Force AI to apply learning if requested
    let appliedLearning = null;
    if (forceLearning) {
      // Create instance for instance methods
      const selfImprovementService = new AISelfImprovementService();
      const failurePatterns = await selfImprovementService.analyzeFailurePatterns(aiType);
      const improvements = await selfImprovementService.generateFlutterSpecificImprovements(aiType, failurePatterns);
      appliedLearning = await selfImprovementService.applyFlutterImprovements(aiType, improvements);
    }
    
    // Emit learning event
    const io = req.app.get('io');
    if (io) {
      io.emit('ai:forced-learning', {
        aiType,
        failuresAnalyzed: filteredFailures.length,
        learningEntriesCreated: savedEntries.length,
        appliedLearning: appliedLearning ? appliedLearning.appliedChanges : 0,
        timestamp: new Date().toISOString()
      });
    }
    
    res.json({
      aiType,
      failuresAnalyzed: filteredFailures.length,
      learningEntriesCreated: savedEntries.length,
      appliedLearning,
      message: 'Forced learning completed successfully'
    });
  } catch (error) {
    console.error('[LEARNING_ROUTE] Error forcing learning from failures:', error);
    res.status(500).json({ error: 'Failed to force learning from failures' });
  }
});

// Helper function to categorize failures
function categorizeFailure(proposal) {
  const feedback = (proposal.userFeedbackReason || '').toLowerCase();
  const testOutput = (proposal.testOutput || '').toLowerCase();
  const combined = feedback + ' ' + testOutput;
  
  if (combined.includes('flutter sdk') || combined.includes('flutter_test')) {
    return 'flutter_sdk';
  } else if (combined.includes('dart pub') || combined.includes('version solving')) {
    return 'dependency';
  } else if (combined.includes('image decoder') || combined.includes('unimplemented')) {
    return 'image_decoder';
  } else if (combined.includes('test') && (combined.includes('failed') || combined.includes('error'))) {
    return 'test';
  } else {
    return 'general';
  }
}

module.exports = router; 