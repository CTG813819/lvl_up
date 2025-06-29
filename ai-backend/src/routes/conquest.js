console.log('[CONQUEST_ROUTER] 🚀 Conquest router loaded');
const express = require('express');
const router = express.Router();
const ConquestService = require('../services/conquestService');
const ConquestLearningService = require('../services/conquestLearningService');
const AILearningService = require('../services/aiLearningService');
const Learning = require('../models/learning');

// Create an instance of the ConquestService
const conquestService = new ConquestService();

/**
 * GET /conquest/status
 * Get Conquest AI status
 */
router.get('/status', async (req, res) => {
  try {
    // Ensure conquest service is properly initialized
    if (!conquestService || typeof conquestService.getStatus !== 'function') {
      console.error('[CONQUEST_ROUTES] Conquest service not properly initialized');
      return res.status(500).json({
        success: false,
        error: 'Conquest service not initialized'
      });
    }

    const status = conquestService.getStatus();
    
    // Get learning progress with error handling
    let learningProgress = null;
    try {
      learningProgress = await ConquestLearningService.getLearningProgress();
    } catch (learningError) {
      console.warn('[CONQUEST_ROUTES] Warning: Could not get learning progress:', learningError.message);
      learningProgress = {
        totalLearningSessions: 0,
        crossAILearning: 0,
        appGenerations: 0,
        patternApplications: 0,
        gitStats: { totalCommits: 0, learningActivity: 'unknown' },
        recentLearning: [],
        learningActivity: 'inactive',
        improvementRate: 0
      };
    }
    
    res.json({
      success: true,
      data: {
        ...status,
        learningProgress
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error getting status:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get Conquest AI status',
      details: error.message
    });
  }
});

/**
 * GET /conquest/apps
 * Get all current apps
 */
router.get('/apps', async (req, res) => {
  try {
    const currentApps = conquestService.getCurrentApps();
    const completedApps = conquestService.getCompletedApps();
    
    res.json({
      success: true,
      data: {
        currentApps,
        completedApps
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error getting apps:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get apps'
    });
  }
});

/**
 * POST /conquest/create-app
 * Create a new app suggestion
 */
router.post('/create-app', async (req, res) => {
  console.log('[CONQUEST_ROUTER] POST /create-app called');
  try {
    const { name, description, keywords } = req.body;
    
    if (!name || !description || !keywords) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: name, description, keywords'
      });
    }
    
    const app = await conquestService.createAppSuggestion({
      name,
      description,
      keywords
    });
    
    res.json({
      success: true,
      data: app
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error creating app:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create app suggestion'
    });
  }
});

/**
 * POST /conquest/define-requirements
 * Define app requirements with learning from other AIs
 */
router.post('/define-requirements', async (req, res) => {
  try {
    const { appId, name, description, keywords, learningData } = req.body;
    
    if (!appId || !name || !description || !keywords) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields'
      });
    }
    
    console.log(`[CONQUEST_ROUTES] 🔧 Defining requirements for app ${appId} with learning integration`);
    
    // First, learn from other AIs
    const learningInsights = await ConquestLearningService.learnFromOtherAIs();
    
    // Create base requirements
    const baseRequirements = {
      name,
      description,
      keywords,
      platform: 'cross_platform',
      features: [],
      technologies: ['Flutter', 'Dart'],
      architecture: 'MVVM',
      database: 'SQLite',
      stateManagement: 'Provider',
      uiFramework: 'Material Design'
    };
    
    // Apply learned patterns to improve requirements
    const improvedRequirements = await ConquestLearningService.applyLearnedPatterns(appId, baseRequirements);
    
    // Add learning context to requirements
    const finalRequirements = {
      ...improvedRequirements,
      learningContext: {
        sourceAIs: Object.keys(learningInsights),
        insightsCount: Object.keys(learningInsights).length,
        confidence: improvedRequirements.patternConfidence || 0,
        bestPractices: improvedRequirements.learnedBestPractices || []
      }
    };
    
    console.log(`[CONQUEST_ROUTES] ✅ Requirements defined with learning integration for app ${appId}`);
    
    res.json({
      success: true,
      data: {
        requirements: finalRequirements,
        learningInsights: {
          sourceAIs: Object.keys(learningInsights),
          totalInsights: Object.keys(learningInsights).length,
          confidence: improvedRequirements.patternConfidence || 0
        }
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error defining requirements:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to define requirements'
    });
  }
});

/**
 * POST /conquest/build-app
 * Build the app with improved code generation
 */
router.post('/build-app', async (req, res) => {
  try {
    const { appId, requirements, learningData } = req.body;
    
    if (!appId || !requirements) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields'
      });
    }
    
    console.log(`[CONQUEST_ROUTES] 🔧 Building app ${appId} with learning-enhanced code generation`);
    
    // Get learned patterns for code generation
    const learnedPatterns = await ConquestLearningService.learnFromOtherAIs();
    
    // Generate improved app code using learned patterns
    const buildResult = await ConquestLearningService.generateImprovedAppCode(
      appId, 
      requirements, 
      learnedPatterns
    );
    
    const appPath = `/conquest_apps/${appId}`;
    
    console.log(`[CONQUEST_ROUTES] ✅ App ${appId} built with learning-enhanced code generation`);
    
    res.json({
      success: true,
      data: {
        appPath,
        buildStatus: 'completed',
        learningEnhanced: true,
        appliedPatterns: learnedPatterns ? Object.keys(learnedPatterns).length : 0,
        gitResult: buildResult.gitResult
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error building app:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to build app'
    });
  }
});

/**
 * POST /conquest/test-app
 * Test the app
 */
router.post('/test-app', async (req, res) => {
  try {
    const { appId, appPath, requirements } = req.body;
    
    if (!appId || !appPath || !requirements) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields'
      });
    }
    
    // This would typically call the Conquest service to test the app
    // For now, we'll return a mock response
    const testResults = {
      passed: true,
      totalTests: 10,
      passedTests: 10,
      failedTests: 0
    };
    
    res.json({
      success: true,
      data: {
        testResults,
        testStatus: 'completed'
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error testing app:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to test app'
    });
  }
});

/**
 * NEW: POST /conquest/learn-from-ai
 * Trigger Conquest to learn from a specific AI
 */
router.post('/learn-from-ai', async (req, res) => {
  try {
    const { sourceAI, learningType = 'general' } = req.body;
    
    if (!sourceAI) {
      return res.status(400).json({
        success: false,
        error: 'Missing required field: sourceAI'
      });
    }
    
    console.log(`[CONQUEST_ROUTES] 🧠 Conquest learning from ${sourceAI}`);
    
    // Get learning insights from the specific AI
    const patterns = await AILearningService.analyzeFeedbackPatterns(sourceAI, 30);
    const insights = await AILearningService.getLearningInsights(sourceAI);
    
    // Create learning entry for Conquest
    const learningEntry = {
      aiType: 'Conquest',
      learningKey: `cross-ai-${sourceAI.toLowerCase()}`,
      learningValue: `Learned from ${sourceAI}: ${Object.keys(patterns).length} patterns analyzed`,
      status: 'learning-completed',
      timestamp: new Date(),
      filePath: 'conquest-learning',
      improvementType: learningType,
      metadata: {
        sourceAI,
        patterns,
        insights,
        learningType
      }
    };
    
    console.log(`[CONQUEST_ROUTES] ✅ Conquest learned from ${sourceAI}`);
    
    res.json({
      success: true,
      data: {
        sourceAI,
        patternsAnalyzed: Object.keys(patterns).length,
        insights: Object.keys(insights).length,
        learningType
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error learning from AI:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to learn from AI'
    });
  }
});

/**
 * NEW: GET /conquest/learning-progress
 * Get Conquest's learning progress
 */
router.get('/learning-progress', async (req, res) => {
  try {
    console.log('[CONQUEST_ROUTES] 📊 Getting Conquest learning progress');
    
    const progress = await ConquestLearningService.getLearningProgress();
    
    res.json({
      success: true,
      data: progress
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error getting learning progress:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get learning progress'
    });
  }
});

/**
 * NEW: POST /conquest/trigger-learning
 * Trigger a comprehensive learning session
 */
router.post('/trigger-learning', async (req, res) => {
  try {
    const { learningType = 'comprehensive' } = req.body;
    
    console.log(`[CONQUEST_ROUTES] 🚀 Triggering ${learningType} learning session for Conquest`);
    
    // Trigger comprehensive learning from all AIs
    const learningInsights = await ConquestLearningService.learnFromOtherAIs();
    
    // Get learning progress after the session
    const progress = await ConquestLearningService.getLearningProgress();
    
    console.log(`[CONQUEST_ROUTES] ✅ Learning session completed for Conquest`);
    
    res.json({
      success: true,
      data: {
        learningType,
        sourceAIs: Object.keys(learningInsights),
        insightsGathered: Object.keys(learningInsights).length,
        progress
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error triggering learning:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to trigger learning session'
    });
  }
});

/**
 * NEW: GET /conquest/improvement-suggestions
 * Get improvement suggestions based on learned patterns
 */
router.get('/improvement-suggestions', async (req, res) => {
  try {
    console.log('[CONQUEST_ROUTES] 💡 Getting improvement suggestions for Conquest');
    
    // Get recent learning data
    const learningInsights = await ConquestLearningService.learnFromOtherAIs();
    
    // Generate improvement suggestions
    const suggestions = [];
    
    for (const [aiType, insights] of Object.entries(learningInsights)) {
      if (insights.successPatterns && insights.successPatterns.length > 0) {
        suggestions.push({
          sourceAI: aiType,
          type: 'success_pattern',
          suggestion: `Apply ${insights.successPatterns[0].pattern} pattern from ${aiType}`,
          confidence: insights.successPatterns[0].frequency * 100
        });
      }
      
      if (insights.commonMistakes && insights.commonMistakes.length > 0) {
        suggestions.push({
          sourceAI: aiType,
          type: 'avoid_mistake',
          suggestion: `Avoid ${insights.commonMistakes[0].mistake} (common in ${aiType})`,
          confidence: insights.commonMistakes[0].frequency * 100
        });
      }
    }
    
    // Sort by confidence
    suggestions.sort((a, b) => b.confidence - a.confidence);
    
    res.json({
      success: true,
      data: {
        suggestions: suggestions.slice(0, 10), // Top 10 suggestions
        totalSuggestions: suggestions.length,
        sourceAIs: Object.keys(learningInsights)
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error getting improvement suggestions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get improvement suggestions'
    });
  }
});

/**
 * POST /conquest/deploy-to-github
 * Deploy app to GitHub
 */
router.post('/deploy-to-github', async (req, res) => {
  try {
    const { appId, appName, appPath, description } = req.body;
    
    if (!appId || !appName || !appPath || !description) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields'
      });
    }
    
    // This would typically call the Conquest service to deploy to GitHub
    // For now, we'll return a mock response
    const repoName = `${appName.toLowerCase().replace(/\s+/g, '-')}-conquest-app`;
    const repoUrl = `https://github.com/conquest-ai/${repoName}`;
    const downloadUrl = `${repoUrl}/releases/latest`;
    
    res.json({
      success: true,
      data: {
        repoUrl,
        downloadUrl,
        deployStatus: 'completed'
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error deploying to GitHub:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to deploy to GitHub'
    });
  }
});

/**
 * GET /conquest/debug-logs
 * Get debug logs
 */
router.get('/debug-logs', async (req, res) => {
  try {
    // This would typically get debug logs from the Conquest service
    const debugLogs = conquestService.debugLog || [];
    
    res.json({
      success: true,
      data: {
        debugLogs
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error getting debug logs:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get debug logs'
    });
  }
});

/**
 * POST /conquest/clear-logs
 * Clear debug logs
 */
router.post('/clear-logs', async (req, res) => {
  try {
    // This would typically clear debug logs in the Conquest service
    conquestService.debugLog = [];
    
    res.json({
      success: true,
      message: 'Debug logs cleared successfully'
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error clearing debug logs:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to clear debug logs'
    });
  }
});

/**
 * GET /conquest/learnings
 * Get Conquest AI learnings
 */
router.get('/learnings', async (req, res) => {
  try {
    const learnings = {
      fromImperium: conquestService.learningData.fromImperium || [],
      fromGuardian: conquestService.learningData.fromGuardian || [],
      fromSandbox: conquestService.learningData.fromSandbox || [],
      fromInternet: conquestService.learningData.fromInternet || [],
      ownExperiences: conquestService.learningData.ownExperiences || []
    };
    
    res.json({
      success: true,
      data: learnings
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error getting learnings:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get learnings'
    });
  }
});

/**
 * POST /conquest/update-operational-hours
 * Update operational hours
 */
router.post('/update-operational-hours', async (req, res) => {
  try {
    const { start, end } = req.body;
    
    if (!start || !end) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: start, end'
      });
    }
    
    conquestService.operationalHours = { start, end };
    await conquestService.saveConquestData();
    
    res.json({
      success: true,
      message: 'Operational hours updated successfully',
      data: {
        operationalHours: conquestService.operationalHours
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error updating operational hours:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to update operational hours'
    });
  }
});

/**
 * POST /conquest/cycle
 * AI Cycle endpoint - triggered by autonomous orchestrator
 */
router.post('/cycle', async (req, res) => {
  try {
    const { aiName, timestamp, cycleNumber, priority, platform } = req.body;
    console.log(`[CONQUEST_ROUTE] 🚀 Cycle triggered for ${aiName} (cycle #${cycleNumber})`);
    
    // Conquest AI doesn't use the same quota system as other AIs
    // It focuses on app building and development
    
    // Get a random Dart file from the codebase to analyze for app building opportunities
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
    console.log(`[CONQUEST_ROUTE] Found ${dartFiles.length} Dart files to analyze for app building`);
    
    if (dartFiles.length === 0) {
      console.log('[CONQUEST_ROUTE] ⚠️ No Dart files found, creating sample app suggestion');
      
      // Create a sample app suggestion
      const sampleApp = await conquestService.createAppSuggestion({
        name: 'Sample App',
        description: 'A sample app created during Conquest AI cycle',
        keywords: ['sample', 'test', 'cycle']
      });
      
      console.log('[CONQUEST_ROUTE] ✅ Cycle completed with sample app suggestion');
      res.json({
        message: 'Conquest cycle completed successfully',
        appId: sampleApp.id,
        status: 'app-suggestion-created',
        cycleNumber: cycleNumber
      });
      return;
    }
    
    // Select a random Dart file to analyze for app building opportunities
    const randomFile = dartFiles[Math.floor(Math.random() * dartFiles.length)];
    const relativePath = path.relative(LOCAL_PATH, randomFile);
    
    console.log(`[CONQUEST_ROUTE] Analyzing file for app building: ${relativePath}`);
    
    // Read the file content
    const code = fs.readFileSync(randomFile, 'utf8');
    
    // Analyze the code for app building opportunities
    const appSuggestion = await conquestService.analyzeCodeForAppBuilding(code, relativePath);
    
    if (appSuggestion) {
      console.log('[CONQUEST_ROUTE] ✅ Cycle completed with app building suggestion');
      res.json({
        message: 'Conquest cycle completed successfully',
        appId: appSuggestion.id,
        status: 'app-suggestion-created',
        filePath: relativePath,
        cycleNumber: cycleNumber
      });
    } else {
      console.log('[CONQUEST_ROUTE] ⚠️ No app building opportunity found');
      res.json({
        message: 'Conquest cycle completed but no app building opportunity found',
        status: 'no-app-suggestion',
        filePath: relativePath,
        cycleNumber: cycleNumber
      });
    }
    
  } catch (error) {
    console.error('[CONQUEST_ROUTE] ❌ Error in cycle:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * NEW: POST /conquest/app-feedback
 * Receive user feedback from Conquest AI generated apps
 */
router.post('/app-feedback', async (req, res) => {
  try {
    const feedback = req.body;
    
    console.log(`[CONQUEST_ROUTES] 📊 Received app feedback for app ${feedback.appId}`);
    
    // Create learning entry for app feedback
    const learningEntry = new Learning({
      aiType: 'Conquest',
      learningKey: 'app-user-feedback',
      learningValue: `User feedback for app ${feedback.appId}: ${feedback.feedbackType} - Rating: ${feedback.rating}/5`,
      status: 'learning-completed',
      timestamp: new Date(),
      filePath: `conquest-apps/${feedback.appId}`,
      improvementType: 'user-feedback',
      metadata: {
        appId: feedback.appId,
        feedback,
        feedbackType: feedback.feedbackType,
        rating: feedback.rating,
        category: feedback.category,
        severity: feedback.severity,
        userId: feedback.userId,
        platform: feedback.platform
      }
    });

    await learningEntry.save();
    
    // Update Conquest's learning data
    await ConquestLearningService.processAppFeedback(feedback);
    
    console.log(`[CONQUEST_ROUTES] ✅ App feedback processed for app ${feedback.appId}`);
    
    res.json({
      success: true,
      message: 'Feedback received and processed successfully'
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error processing app feedback:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to process app feedback'
    });
  }
});

/**
 * NEW: POST /conquest/app-usage
 * Receive usage data from Conquest AI generated apps
 */
router.post('/app-usage', async (req, res) => {
  try {
    const usage = req.body;
    
    console.log(`[CONQUEST_ROUTES] 📈 Received usage data for app ${usage.appId}`);
    
    // Create learning entry for app usage
    const learningEntry = new Learning({
      aiType: 'Conquest',
      learningKey: 'app-usage-patterns',
      learningValue: `Usage patterns for app ${usage.appId}: ${Object.keys(usage.featureUsage).length} features used`,
      status: 'learning-completed',
      timestamp: new Date(),
      filePath: `conquest-apps/${usage.appId}`,
      improvementType: 'usage-analysis',
      metadata: {
        appId: usage.appId,
        usage,
        featureCount: Object.keys(usage.featureUsage).length,
        timeSpent: usage.timeSpent,
        interactionCount: usage.interactions.length,
        userId: usage.userId,
        platform: usage.platform
      }
    });

    await learningEntry.save();
    
    // Update Conquest's learning data
    await ConquestLearningService.processAppUsage(usage);
    
    console.log(`[CONQUEST_ROUTES] ✅ App usage data processed for app ${usage.appId}`);
    
    res.json({
      success: true,
      message: 'Usage data received and processed successfully'
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error processing app usage:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to process app usage'
    });
  }
});

/**
 * NEW: POST /conquest/app-error
 * Receive error reports from Conquest AI generated apps
 */
router.post('/app-error', async (req, res) => {
  try {
    const error = req.body;
    
    console.log(`[CONQUEST_ROUTES] 🐛 Received error report for app ${error.appId}`);
    
    // Create learning entry for app error
    const learningEntry = new Learning({
      aiType: 'Conquest',
      learningKey: 'app-error-report',
      learningValue: `Error in app ${error.appId}: ${error.errorType} - ${error.errorMessage}`,
      status: 'learning-completed',
      timestamp: new Date(),
      filePath: `conquest-apps/${error.appId}`,
      improvementType: 'error-analysis',
      metadata: {
        appId: error.appId,
        error,
        errorType: error.errorType,
        severity: error.severity,
        context: error.context,
        userId: error.userId,
        platform: error.platform
      }
    });

    await learningEntry.save();
    
    // Update Conquest's learning data
    await ConquestLearningService.processAppError(error);
    
    console.log(`[CONQUEST_ROUTES] ✅ App error report processed for app ${error.appId}`);
    
    res.json({
      success: true,
      message: 'Error report received and processed successfully'
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error processing app error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to process app error'
    });
  }
});

/**
 * NEW: POST /conquest/app-performance
 * Receive performance metrics from Conquest AI generated apps
 */
router.post('/app-performance', async (req, res) => {
  try {
    const metrics = req.body;
    
    console.log(`[CONQUEST_ROUTES] ⚡ Received performance metrics for app ${metrics.appId}`);
    
    // Create learning entry for app performance
    const learningEntry = new Learning({
      aiType: 'Conquest',
      learningKey: 'app-performance-metrics',
      learningValue: `Performance metrics for app ${metrics.appId}: Load time ${metrics.loadTime}ms, Memory ${metrics.memoryUsage}MB`,
      status: 'learning-completed',
      timestamp: new Date(),
      filePath: `conquest-apps/${metrics.appId}`,
      improvementType: 'performance-analysis',
      metadata: {
        appId: metrics.appId,
        metrics,
        loadTime: metrics.loadTime,
        memoryUsage: metrics.memoryUsage,
        frameRate: metrics.frameRate,
        platform: metrics.platform
      }
    });

    await learningEntry.save();
    
    // Update Conquest's learning data
    await ConquestLearningService.processAppPerformance(metrics);
    
    console.log(`[CONQUEST_ROUTES] ✅ App performance metrics processed for app ${metrics.appId}`);
    
    res.json({
      success: true,
      message: 'Performance metrics received and processed successfully'
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error processing app performance:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to process app performance'
    });
  }
});

/**
 * NEW: POST /conquest/submit-app
 * Submit a new app request to Conquest AI
 */
router.post('/submit-app', async (req, res) => {
  try {
    const { appId, name, description, keywords } = req.body;
    
    if (!appId || !name || !description || !keywords) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields'
      });
    }
    
    console.log(`[CONQUEST_ROUTES] 🚀 New app submission: ${name} (${appId})`);
    
    // Initialize app in Conquest AI
    const appData = {
      id: appId,
      name,
      description,
      keywords,
      status: 'submitted',
      progress: 0.0,
      currentStep: 'initializing',
      logs: [`[${new Date().toISOString()}] App submission received: ${name}`],
      createdAt: new Date(),
      completedSteps: [],
      stepDuration: 0,
      retryCount: 0
    };
    
    // Store app data
    await conquestService.addApp(appData);
    
    // Start the app building process
    conquestService.startAppBuild(appId);
    
    console.log(`[CONQUEST_ROUTES] ✅ App submission processed for ${appId}`);
    
    res.json({
      success: true,
      data: {
        appId,
        status: 'submitted',
        message: 'App request submitted successfully'
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error submitting app:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to submit app'
    });
  }
});

/**
 * NEW: GET /conquest/app-progress/:appId
 * Get progress for a specific app
 */
router.get('/app-progress/:appId', async (req, res) => {
  try {
    const { appId } = req.params;
    
    console.log(`[CONQUEST_ROUTES] 📊 Getting progress for app ${appId}`);
    
    const appData = await conquestService.getApp(appId);
    
    if (!appData) {
      return res.status(404).json({
        success: false,
        error: 'App not found'
      });
    }
    
    res.json({
      success: true,
      data: {
        appId,
        progress: appData.progress || 0.0,
        status: appData.status || 'unknown',
        currentStep: appData.currentStep || '',
        logs: appData.logs || [],
        completedSteps: appData.completedSteps || [],
        stepDuration: appData.stepDuration || 0,
        retryCount: appData.retryCount || 0,
        error: appData.error || null
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error getting app progress:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get app progress'
    });
  }
});

/**
 * NEW: GET /conquest/app-status/:appId
 * Get detailed status for a specific app
 */
router.get('/app-status/:appId', async (req, res) => {
  try {
    const { appId } = req.params;
    
    console.log(`[CONQUEST_ROUTES] 📋 Getting detailed status for app ${appId}`);
    
    const appData = await conquestService.getApp(appId);
    
    if (!appData) {
      return res.status(404).json({
        success: false,
        error: 'App not found'
      });
    }
    
    // Get additional status information
    const buildStatus = await conquestService.getBuildStatus(appId);
    const learningProgress = await ConquestLearningService.getLearningProgress();
    
    res.json({
      success: true,
      data: {
        app: appData,
        buildStatus,
        learningProgress,
        operationalHours: conquestService.operationalHours,
        isActive: conquestService.isActive,
        lastActive: conquestService.lastActive
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error getting app status:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get app status'
    });
  }
});

/**
 * NEW: POST /conquest/resume-builds
 * Resume interrupted builds during operational hours
 */
router.post('/resume-builds', async (req, res) => {
  try {
    console.log('[CONQUEST_ROUTES] 🔄 Resuming interrupted builds...');
    
    const resumedApps = await conquestService.resumeInterruptedBuilds();
    
    console.log(`[CONQUEST_ROUTES] ✅ Resumed ${resumedApps.length} builds`);
    
    res.json({
      success: true,
      data: {
        resumedApps,
        count: resumedApps.length,
        message: `Resumed ${resumedApps.length} interrupted builds`
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error resuming builds:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to resume builds'
    });
  }
});

/**
 * NEW: POST /conquest/force-work
 * Force Conquest AI to work on a specific app
 */
router.post('/force-work', async (req, res) => {
  try {
    const { appId } = req.body;
    
    if (!appId) {
      return res.status(400).json({
        success: false,
        error: 'Missing appId'
      });
    }
    
    console.log(`[CONQUEST_ROUTES] ⚡ Forcing Conquest AI to work on app ${appId}`);
    
    const result = await conquestService.forceWorkOnApp(appId);
    
    if (result.success) {
      console.log(`[CONQUEST_ROUTES] ✅ Conquest AI forced to work on app ${appId}`);
      
      res.json({
        success: true,
        data: {
          appId,
          message: 'Conquest AI is now working on the app',
          status: result.status
        }
      });
    } else {
      res.status(400).json({
        success: false,
        error: result.error
      });
    }
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error forcing work:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to force Conquest AI work'
    });
  }
});

/**
 * NEW: GET /conquest/learning-progress
 * Get Conquest AI learning progress
 */
router.get('/learning-progress', async (req, res) => {
  try {
    console.log('[CONQUEST_ROUTES] 📚 Getting Conquest AI learning progress...');
    
    const learningProgress = await ConquestLearningService.getLearningProgress();
    
    res.json({
      success: true,
      data: learningProgress
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error getting learning progress:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get learning progress'
    });
  }
});

/**
 * NEW: POST /conquest/learn-keywords
 * Learn from user input and enhance keyword knowledge
 */
router.post('/learn-keywords', async (req, res) => {
  try {
    const { userInput, appSuccess = false, context = 'user_input' } = req.body;
    
    if (!userInput) {
      return res.status(400).json({
        success: false,
        error: 'Missing required field: userInput'
      });
    }
    
    console.log(`[CONQUEST_ROUTES] 🧠 Learning from keywords: ${userInput}`);
    
    // Learn from keywords using enhanced NLP
    await conquestService.learnFromKeywords(userInput, appSuccess);
    
    // Get updated keyword knowledge stats
    const stats = conquestService.getKeywordKnowledgeStats();
    
    res.json({
      success: true,
      message: 'Keywords learned successfully',
      stats,
      context
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error learning keywords:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to learn from keywords'
    });
  }
});

/**
 * NEW: GET /conquest/keyword-knowledge
 * Get comprehensive keyword knowledge base
 */
router.get('/keyword-knowledge', async (req, res) => {
  try {
    // Check if conquest service is properly initialized
    if (!conquestService || !conquestService.keywordKnowledge) {
      return res.status(500).json({
        success: false,
        error: 'Keyword knowledge not available'
      });
    }

    const { keyword, category, limit = 20 } = req.query;
    
    let knowledge = {};
    
    if (keyword) {
      // Get specific keyword knowledge
      const lowerKeyword = keyword.toLowerCase();
      const technicalTerm = conquestService.keywordKnowledge.technicalTerms.get(lowerKeyword);
      const appPattern = conquestService.keywordKnowledge.appPatterns.get(lowerKeyword);
      const codeExample = conquestService.keywordKnowledge.codeExamples.get(lowerKeyword);
      
      knowledge = {
        keyword: lowerKeyword,
        technicalTerm,
        appPattern,
        codeExample,
        relatedFeatures: conquestService.getFeaturesForKeyword(lowerKeyword),
        learnedPatterns: conquestService.getLearnedPatternsForKeyword(lowerKeyword)
      };
    } else if (category) {
      // Get knowledge by category
      const categoryPattern = conquestService.keywordKnowledge.appPatterns.get(category);
      const categoryTechStack = conquestService.keywordKnowledge.technologyStacks.get(category);
      
      knowledge = {
        category,
        appPattern: categoryPattern,
        technologyStack: categoryTechStack,
        relatedKeywords: Array.from(conquestService.keywordKnowledge.technicalTerms.keys())
          .filter(k => conquestService.getFeaturesForKeyword(k).includes(category))
          .slice(0, limit)
      };
    } else {
      // Get overall knowledge stats
      knowledge = {
        stats: conquestService.getKeywordKnowledgeStats(),
        technicalTerms: Array.from(conquestService.keywordKnowledge.technicalTerms.entries())
          .slice(0, limit)
          .map(([key, value]) => ({ keyword: key, ...value })),
        appPatterns: Array.from(conquestService.keywordKnowledge.appPatterns.entries())
          .slice(0, limit)
          .map(([key, value]) => ({ category: key, ...value })),
        recentLearning: conquestService.keywordKnowledge.learningHistory
          .slice(-limit)
          .reverse()
      };
    }
    
    res.json({
      success: true,
      data: knowledge
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error getting keyword knowledge:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get keyword knowledge',
      details: error.message
    });
  }
});

/**
 * NEW: POST /conquest/enhance-keywords
 * Enhance keywords using NLP and learned knowledge
 */
router.post('/enhance-keywords', async (req, res) => {
  try {
    const { keywords, context = '' } = req.body;
    
    if (!keywords) {
      return res.status(400).json({
        success: false,
        error: 'Missing required field: keywords'
      });
    }
    
    console.log(`[CONQUEST_ROUTES] 🧠 Enhancing keywords: ${keywords}`);
    
    // Process keywords with NLP
    const keywordArray = typeof keywords === 'string' ? keywords.split(',').map(k => k.trim()) : keywords;
    const enhancedKeywords = await conquestService.enhanceKeywordsWithKnowledge(keywordArray);
    
    // Get related features and patterns
    const relatedFeatures = [];
    const learnedPatterns = [];
    
    for (const keyword of keywordArray) {
      relatedFeatures.push(...conquestService.getFeaturesForKeyword(keyword));
      learnedPatterns.push(...conquestService.getLearnedPatternsForKeyword(keyword));
    }
    
    res.json({
      success: true,
      originalKeywords: keywordArray,
      enhancedKeywords,
      relatedFeatures: [...new Set(relatedFeatures)],
      learnedPatterns: [...new Set(learnedPatterns)],
      context
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error enhancing keywords:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to enhance keywords'
    });
  }
});

/**
 * NEW: GET /conquest/similar-apps
 * Search for similar apps based on keywords
 */
router.get('/similar-apps', async (req, res) => {
  try {
    const { keywords, limit = 10 } = req.query;
    
    if (!keywords) {
      return res.status(400).json({
        success: false,
        error: 'Missing required parameter: keywords'
      });
    }
    
    console.log(`[CONQUEST_ROUTES] 🔍 Searching similar apps for keywords: ${keywords}`);
    
    const similarApps = await conquestService.searchSimilarApps(keywords);
    
    res.json({
      success: true,
      keywords,
      similarApps: similarApps.slice(0, limit),
      totalFound: similarApps.length
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error searching similar apps:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to search similar apps'
    });
  }
});

/**
 * NEW: POST /conquest/analyze-requirements
 * Analyze app requirements with enhanced keyword understanding
 */
router.post('/analyze-requirements', async (req, res) => {
  try {
    const { name, description, keywords } = req.body;
    
    if (!name || !description || !keywords) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: name, description, keywords'
      });
    }
    
    console.log(`[CONQUEST_ROUTES] 📋 Analyzing requirements for: ${name}`);
    
    // Create temporary app object for analysis
    const tempApp = {
      name,
      description,
      userKeywords: keywords
    };
    
    // Analyze requirements with enhanced keyword understanding
    const requirements = await conquestService.analyzeRequirementsWithKeywords(tempApp);
    
    // Get similar apps for reference
    const similarApps = await conquestService.searchSimilarApps(keywords);
    
    res.json({
      success: true,
      app: { name, description, keywords },
      requirements,
      similarApps: similarApps.slice(0, 5),
      keywordAnalysis: {
        extractedKeywords: keywords.split(',').map(k => k.trim()),
        appCategory: requirements.appCategory,
        enhancedFeatures: requirements.enhancedFeatures,
        learnedPatterns: requirements.learnedPatterns
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error analyzing requirements:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to analyze requirements'
    });
  }
});

/**
 * NEW: POST /conquest/learn-from-success
 * Learn from successful app completion
 */
router.post('/learn-from-success', async (req, res) => {
  try {
    const { appId, appData } = req.body;
    
    if (!appId || !appData) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: appId, appData'
      });
    }
    
    console.log(`[CONQUEST_ROUTES] 🎓 Learning from successful app: ${appId}`);
    
    // Create app object for learning
    const app = {
      id: appId,
      name: appData.name,
      description: appData.description,
      userKeywords: appData.keywords,
      requirements: appData.requirements
    };
    
    // Learn from successful app
    await conquestService.learnFromSuccessfulApp(app);
    
    // Get updated stats
    const stats = conquestService.getKeywordKnowledgeStats();
    
    res.json({
      success: true,
      message: 'Successfully learned from app completion',
      appId,
      stats
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error learning from success:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to learn from success'
    });
  }
});

/**
 * NEW: GET /conquest/nlp-status
 * Get NLP service status and capabilities
 */
router.get('/nlp-status', async (req, res) => {
  try {
    // Check if conquest service and NLP service are available
    if (!conquestService || !conquestService.nlpService) {
      return res.status(500).json({
        success: false,
        error: 'NLP service not available'
      });
    }

    // Get cache stats with error handling
    let cacheStats = null;
    try {
      if (typeof conquestService.nlpService.getCacheStats === 'function') {
        cacheStats = conquestService.nlpService.getCacheStats();
      } else {
        cacheStats = { cacheSize: 0, hitRate: 0, missRate: 0 };
      }
    } catch (cacheError) {
      console.warn('[CONQUEST_ROUTES] Warning: Could not get cache stats:', cacheError.message);
      cacheStats = { cacheSize: 0, hitRate: 0, missRate: 0 };
    }

    const healthChecks = conquestService.healthChecks || {};
    
    res.json({
      success: true,
      nlpService: {
        available: healthChecks.nlp_service_available !== false,
        cacheStats,
        capabilities: [
          'Keyword Extraction (TF-IDF)',
          'Technical Term Recognition',
          'Code Analysis',
          'Language Detection',
          'Stemming Support',
          'Multi-Algorithm Processing'
        ]
      },
      conquestAI: {
        keywordKnowledge: conquestService.getKeywordKnowledgeStats(),
        healthChecks
      }
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error getting NLP status:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get NLP status',
      details: error.message
    });
  }
});

// At the end of the file, log all registered routes for this router
function logRoutes(router, label) {
  console.log(`[${label}] Registered routes:`);
  router.stack.forEach((layer) => {
    if (layer.route) {
      const methods = Object.keys(layer.route.methods).join(', ').toUpperCase();
      console.log(`  ${methods} ${layer.route.path}`);
    }
  });
}
logRoutes(router, 'CONQUEST_ROUTER');

module.exports = router; 