const express = require('express');
const router = express.Router();
const AILearningService = require('../services/aiLearningService');
const DeduplicationService = require('../services/deduplicationService');
const Proposal = require('../models/proposal');
const Experiment = require('../models/experiment');

// GET /api/analytics/ai-learning - Get comprehensive AI learning analytics
router.get('/ai-learning', async (req, res) => {
  try {
    const { aiType, days } = req.query;
    const aiTypes = aiType ? [aiType] : ['Imperium', 'Guardian', 'Sandbox'];
    
    const analytics = {
      learningStats: {},
      feedbackPatterns: {},
      performanceMetrics: {},
      duplicateStats: {},
      improvementTrends: {}
    };
    
    // Get learning statistics for each AI
    for (const type of aiTypes) {
      analytics.learningStats[type] = await AILearningService.getLearningStats(type);
      analytics.feedbackPatterns[type] = await AILearningService.analyzeFeedbackPatterns(type, parseInt(days) || 30);
    }
    
    // Get duplicate statistics
    analytics.duplicateStats = await DeduplicationService.getDuplicateStats();
    
    // Get performance metrics
    const cutoffDate = new Date(Date.now() - (parseInt(days) || 30) * 24 * 60 * 60 * 1000);
    
    const experiments = await Experiment.find({
      createdAt: { $gte: cutoffDate }
    }).select('aiName executionTime tokensUsed cost createdAt');
    
    analytics.performanceMetrics = {
      totalExperiments: experiments.length,
      totalCost: experiments.reduce((sum, exp) => sum + (exp.cost || 0), 0),
      avgExecutionTime: experiments.reduce((sum, exp) => sum + (exp.executionTime || 0), 0) / experiments.length,
      totalTokens: experiments.reduce((sum, exp) => sum + (exp.tokensUsed || 0), 0),
      byAI: {}
    };
    
    // Group by AI
    for (const type of aiTypes) {
      const aiExperiments = experiments.filter(exp => exp.aiName === type);
      analytics.performanceMetrics.byAI[type] = {
        count: aiExperiments.length,
        totalCost: aiExperiments.reduce((sum, exp) => sum + (exp.cost || 0), 0),
        avgExecutionTime: aiExperiments.length > 0 ? 
          aiExperiments.reduce((sum, exp) => sum + (exp.executionTime || 0), 0) / aiExperiments.length : 0,
        totalTokens: aiExperiments.reduce((sum, exp) => sum + (exp.tokensUsed || 0), 0)
      };
    }
    
    // Get improvement trends
    const proposals = await Proposal.find({
      createdAt: { $gte: cutoffDate }
    }).select('aiType improvementType userFeedback createdAt');
    
    analytics.improvementTrends = {
      byType: {},
      byAI: {},
      approvalRates: {}
    };
    
    // Group by improvement type
    const improvementTypes = ['performance', 'readability', 'security', 'bug-fix', 'refactor', 'feature'];
    improvementTypes.forEach(type => {
      const typeProposals = proposals.filter(p => p.improvementType === type);
      analytics.improvementTrends.byType[type] = {
        total: typeProposals.length,
        approved: typeProposals.filter(p => p.userFeedback === 'approved').length,
        rejected: typeProposals.filter(p => p.userFeedback === 'rejected').length,
        approvalRate: typeProposals.length > 0 ? 
          typeProposals.filter(p => p.userFeedback === 'approved').length / typeProposals.length : 0
      };
    });
    
    // Group by AI
    for (const type of aiTypes) {
      const aiProposals = proposals.filter(p => p.aiType === type);
      analytics.improvementTrends.byAI[type] = {
        total: aiProposals.length,
        approved: aiProposals.filter(p => p.userFeedback === 'approved').length,
        rejected: aiProposals.filter(p => p.userFeedback === 'rejected').length,
        approvalRate: aiProposals.length > 0 ? 
          aiProposals.filter(p => p.userFeedback === 'approved').length / aiProposals.length : 0
      };
    }
    
    // Overall approval rates
    analytics.improvementTrends.approvalRates = {
      overall: proposals.length > 0 ? 
        proposals.filter(p => p.userFeedback === 'approved').length / proposals.length : 0,
      byAI: {}
    };
    
    for (const type of aiTypes) {
      const aiProposals = proposals.filter(p => p.aiType === type);
      analytics.improvementTrends.approvalRates.byAI[type] = aiProposals.length > 0 ? 
        aiProposals.filter(p => p.userFeedback === 'approved').length / aiProposals.length : 0;
    }
    
    res.json(analytics);
  } catch (e) {
    console.error(`[ANALYTICS] Error getting AI learning analytics:`, e);
    res.status(500).json({ error: e.message });
  }
});

// GET /api/analytics/duplicates - Get detailed duplicate analysis
router.get('/duplicates', async (req, res) => {
  try {
    const { aiType, days } = req.query;
    const cutoffDate = new Date(Date.now() - (parseInt(days) || 30) * 24 * 60 * 60 * 1000);
    
    const filter = { createdAt: { $gte: cutoffDate } };
    if (aiType) filter.aiType = aiType;
    
    const proposals = await Proposal.find(filter).select('aiType filePath codeHash semanticHash diffScore duplicateOf createdAt');
    
    const duplicateAnalysis = {
      totalProposals: proposals.length,
      duplicates: proposals.filter(p => p.duplicateOf).length,
      duplicateRate: proposals.length > 0 ? proposals.filter(p => p.duplicateOf).length / proposals.length : 0,
      byAI: {},
      byFileType: {},
      similarityDistribution: {
        exact: 0,
        high: 0,
        medium: 0,
        low: 0
      }
    };
    
    // Group by AI
    const aiTypes = aiType ? [aiType] : ['Imperium', 'Guardian', 'Sandbox'];
    for (const type of aiTypes) {
      const aiProposals = proposals.filter(p => p.aiType === type);
      duplicateAnalysis.byAI[type] = {
        total: aiProposals.length,
        duplicates: aiProposals.filter(p => p.duplicateOf).length,
        duplicateRate: aiProposals.length > 0 ? 
          aiProposals.filter(p => p.duplicateOf).length / aiProposals.length : 0
      };
    }
    
    // Group by file type
    const fileTypes = {};
    proposals.forEach(proposal => {
      const ext = proposal.filePath.split('.').pop();
      if (!fileTypes[ext]) fileTypes[ext] = { total: 0, duplicates: 0 };
      fileTypes[ext].total++;
      if (proposal.duplicateOf) fileTypes[ext].duplicates++;
    });
    
    Object.keys(fileTypes).forEach(ext => {
      fileTypes[ext].duplicateRate = fileTypes[ext].total > 0 ? 
        fileTypes[ext].duplicates / fileTypes[ext].total : 0;
    });
    duplicateAnalysis.byFileType = fileTypes;
    
    // Similarity distribution
    proposals.forEach(proposal => {
      if (proposal.diffScore === 1.0) {
        duplicateAnalysis.similarityDistribution.exact++;
      } else if (proposal.diffScore >= 0.8) {
        duplicateAnalysis.similarityDistribution.high++;
      } else if (proposal.diffScore >= 0.5) {
        duplicateAnalysis.similarityDistribution.medium++;
      } else if (proposal.diffScore > 0) {
        duplicateAnalysis.similarityDistribution.low++;
      }
    });
    
    res.json(duplicateAnalysis);
  } catch (e) {
    console.error(`[ANALYTICS] Error getting duplicate analytics:`, e);
    res.status(500).json({ error: e.message });
  }
});

// GET /api/analytics/performance - Get AI performance metrics
router.get('/performance', async (req, res) => {
  try {
    const { aiType, days } = req.query;
    const cutoffDate = new Date(Date.now() - (parseInt(days) || 30) * 24 * 60 * 60 * 1000);
    
    const filter = { createdAt: { $gte: cutoffDate } };
    if (aiType) filter.aiName = aiType;
    
    const experiments = await Experiment.find(filter).select('aiName executionTime tokensUsed cost createdAt experimentType');
    
    const performance = {
      totalExperiments: experiments.length,
      totalCost: experiments.reduce((sum, exp) => sum + (exp.cost || 0), 0),
      avgExecutionTime: experiments.length > 0 ? 
        experiments.reduce((sum, exp) => sum + (exp.executionTime || 0), 0) / experiments.length : 0,
      totalTokens: experiments.reduce((sum, exp) => sum + (exp.tokensUsed || 0), 0),
      byAI: {},
      byExperimentType: {},
      dailyStats: {}
    };
    
    // Group by AI
    const aiTypes = aiType ? [aiType] : ['Imperium', 'Guardian', 'Sandbox'];
    for (const type of aiTypes) {
      const aiExperiments = experiments.filter(exp => exp.aiName === type);
      performance.byAI[type] = {
        count: aiExperiments.length,
        totalCost: aiExperiments.reduce((sum, exp) => sum + (exp.cost || 0), 0),
        avgExecutionTime: aiExperiments.length > 0 ? 
          aiExperiments.reduce((sum, exp) => sum + (exp.executionTime || 0), 0) / aiExperiments.length : 0,
        totalTokens: aiExperiments.reduce((sum, exp) => sum + (exp.tokensUsed || 0), 0)
      };
    }
    
    // Group by experiment type
    const experimentTypes = {};
    experiments.forEach(exp => {
      if (!experimentTypes[exp.experimentType]) {
        experimentTypes[exp.experimentType] = { count: 0, totalCost: 0, avgExecutionTime: 0, totalTokens: 0 };
      }
      experimentTypes[exp.experimentType].count++;
      experimentTypes[exp.experimentType].totalCost += exp.cost || 0;
      experimentTypes[exp.experimentType].totalTokens += exp.tokensUsed || 0;
    });
    
    Object.keys(experimentTypes).forEach(type => {
      const typeExps = experiments.filter(exp => exp.experimentType === type);
      experimentTypes[type].avgExecutionTime = typeExps.length > 0 ? 
        typeExps.reduce((sum, exp) => sum + (exp.executionTime || 0), 0) / typeExps.length : 0;
    });
    performance.byExperimentType = experimentTypes;
    
    // Daily statistics
    const dailyStats = {};
    experiments.forEach(exp => {
      const date = exp.createdAt.toISOString().split('T')[0];
      if (!dailyStats[date]) {
        dailyStats[date] = { count: 0, cost: 0, tokens: 0 };
      }
      dailyStats[date].count++;
      dailyStats[date].cost += exp.cost || 0;
      dailyStats[date].tokens += exp.tokensUsed || 0;
    });
    performance.dailyStats = dailyStats;
    
    res.json(performance);
  } catch (e) {
    console.error(`[ANALYTICS] Error getting performance analytics:`, e);
    res.status(500).json({ error: e.message });
  }
});

module.exports = router; 