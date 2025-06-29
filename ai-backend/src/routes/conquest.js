const express = require('express');
const router = express.Router();
const conquestService = require('../services/conquestService');

/**
 * GET /conquest/status
 * Get Conquest AI status
 */
router.get('/status', async (req, res) => {
  try {
    const status = conquestService.getStatus();
    res.json({
      success: true,
      data: status
    });
  } catch (error) {
    console.error('[CONQUEST_ROUTES] Error getting status:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get Conquest AI status'
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
 * Define app requirements
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
    
    // This would typically call the Conquest service to define requirements
    // For now, we'll return a mock response
    const requirements = {
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
    
    res.json({
      success: true,
      data: {
        requirements
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
 * Build the app
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
    
    // This would typically call the Conquest service to build the app
    // For now, we'll return a mock response
    const appPath = `/conquest_apps/${appId}`;
    
    res.json({
      success: true,
      data: {
        appPath,
        buildStatus: 'completed'
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

module.exports = router; 