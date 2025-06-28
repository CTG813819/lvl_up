const express = require('express');
const router = express.Router();
const Learning = require('../models/learning');
const Proposal = require('../models/proposal');
const Experiment = require('../models/experiment');
const { AIQuotaService } = require('../services/aiQuotaService');

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

module.exports = router; 