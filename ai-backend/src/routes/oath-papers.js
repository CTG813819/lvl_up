const express = require('express');
const router = express.Router();
const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');
const natural = require('natural');
const axios = require('axios');
const OathPapersService = require('../services/oathPapersService');

// Initialize the enhanced oath papers service
const oathPapersService = new OathPapersService();

// Middleware to add request timing
router.use((req, res, next) => {
  req.startTime = Date.now();
  next();
});

// Enhanced oath paper processing with AI learning capabilities
router.post('/enhanced-learning', async (req, res) => {
  try {
    console.log('[OATH_PAPERS] 🧠 Enhanced learning request received');
    
    const {
      subject,
      tags,
      description,
      code,
      targetAI,
      aiWeights,
      learningInstructions,
    } = req.body;

    console.log('[OATH_PAPERS] Subject:', subject);
    console.log('[OATH_PAPERS] Target AI:', targetAI);
    console.log('[OATH_PAPERS] Tags:', tags);

    // Use the enhanced service for processing
    const result = await oathPapersService.processOathPaper({
      subject,
      tags,
      description,
      code,
      targetAI,
      aiWeights,
      learningInstructions,
    });

    if (result.success) {
      console.log('[OATH_PAPERS] ✅ Enhanced learning completed successfully');
      
      // Add processing time to response
      result.processingTime = Date.now() - req.startTime;
      
      res.json(result);
    } else {
      console.log('[OATH_PAPERS] ❌ Enhanced learning failed');
      res.status(500).json(result);
    }

  } catch (error) {
    console.error('[OATH_PAPERS] ❌ Error in enhanced learning:', error);
    
    res.status(500).json({
      success: false,
      error: error.message,
      retryable: oathPapersService.isRetryableError(error),
      retryAfter: oathPapersService.getRetryDelay(error),
      timestamp: new Date().toISOString(),
      processingTime: Date.now() - req.startTime,
    });
  }
});

// Queue management endpoints
router.get('/queue/status', async (req, res) => {
  try {
    const pendingQueue = oathPapersService.getPendingQueue();
    const failedQueue = oathPapersService.getFailedQueue();
    
    res.json({
      success: true,
      pending: pendingQueue.length,
      failed: failedQueue.length,
      pendingQueue: pendingQueue.slice(0, 10), // Show first 10
      failedQueue: failedQueue.slice(0, 10), // Show first 10
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

router.post('/queue/retry/:paperId', async (req, res) => {
  try {
    const { paperId } = req.params;
    const result = await oathPapersService.retryFailedPaper(paperId);
    res.json(result);
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

router.delete('/queue/failed', async (req, res) => {
  try {
    await oathPapersService.clearFailedQueue();
    res.json({
      success: true,
      message: 'Failed queue cleared',
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// Enhanced keyword extraction with advanced NLP
async function extractKeywordsEnhanced(description, code, tags) {
  const keywords = new Set();

  // Add user-provided tags
  if (tags && Array.isArray(tags)) {
    tags.forEach(tag => keywords.add(tag.toLowerCase()));
  }

  // Enhanced text processing with NLP
  if (description) {
    const descriptionKeywords = await extractKeywordsFromTextEnhanced(description);
    descriptionKeywords.forEach(keyword => keywords.add(keyword));
  }

  // Enhanced code analysis
  if (code) {
    const codeKeywords = await extractKeywordsFromCodeEnhanced(code);
    codeKeywords.forEach(keyword => keywords.add(keyword));
  }

  return Array.from(keywords);
}

// Enhanced text keyword extraction using NLP
async function extractKeywordsFromTextEnhanced(text) {
  const tokenizer = new natural.WordTokenizer();
  const words = tokenizer.tokenize(text.toLowerCase())
    .filter(word => word.length > 3)
    .filter(word => !commonWords.has(word));

  // Use TF-IDF for better keyword extraction
  const wordCount = {};
  words.forEach(word => {
    wordCount[word] = (wordCount[word] || 0) + 1;
  });

  // Calculate TF-IDF scores (simplified)
  const totalWords = words.length;
  const sortedWords = Object.entries(wordCount)
    .map(([word, count]) => ({
      word,
      score: (count / totalWords) * Math.log(totalWords / count)
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 15)
    .map(item => item.word);

  return sortedWords;
}

// Enhanced code keyword extraction
async function extractKeywordsFromCodeEnhanced(code) {
  const keywords = new Set();

  // Enhanced pattern matching for various programming languages
  const patterns = {
    function: /(?:def|function|func|fn)\s+(\w+)/gi,
    class: /(?:class|struct|interface)\s+(\w+)/gi,
    import: /(?:import|from|require)\s+[\w\.]+/gi,
    variable: /(?:const|let|var|final)\s+(\w+)/gi,
    method: /(\w+)\s*\([^)]*\)\s*{/gi,
    api: /(?:api|endpoint|route|controller)/gi,
    database: /(?:database|db|table|collection|model)/gi,
  };

  for (const [type, pattern] of Object.entries(patterns)) {
    const matches = code.match(pattern) || [];
    matches.forEach(match => {
      const cleanMatch = match.replace(/[^\w]/g, ' ').trim();
      if (cleanMatch.length > 2) {
        keywords.add(cleanMatch.toLowerCase());
      }
    });
  }

  return Array.from(keywords);
}

// Enhanced internet search with multiple sources
async function searchInternetEnhanced(keywords, tags) {
  const searchResults = [];
  const searchTerms = [...keywords, ...tags].slice(0, 5);

  // Search from multiple sources
  const searchSources = [
    searchGoogleCustom,
    searchStackOverflow,
    searchGitHub,
    searchDocumentation,
  ];

  for (const term of searchTerms) {
    for (const searchSource of searchSources) {
      try {
        const results = await searchSource(term);
        searchResults.push(...results);
        
        // Rate limiting to avoid overwhelming APIs
        await new Promise(resolve => setTimeout(resolve, 200));
      } catch (error) {
        console.warn(`[OATH_PAPERS] ⚠️ Search failed for term "${term}" from ${searchSource.name}:`, error.message);
      }
    }
  }

  // Remove duplicates and sort by relevance
  const uniqueResults = removeDuplicateResults(searchResults);
  return uniqueResults.sort((a, b) => b.relevance - a.relevance).slice(0, 20);
}

// Google Custom Search API
async function searchGoogleCustom(term) {
  const apiKey = process.env.GOOGLE_SEARCH_API_KEY;
  const searchEngineId = process.env.GOOGLE_SEARCH_ENGINE_ID;
  
  if (!apiKey || !searchEngineId) {
    return []; // Fallback to mock results
  }

  try {
    const response = await axios.get('https://www.googleapis.com/customsearch/v1', {
      params: {
        key: apiKey,
        cx: searchEngineId,
        q: term,
        num: 5,
      },
    });

    return response.data.items?.map(item => ({
      title: item.title,
      url: item.link,
      snippet: item.snippet,
      relevance: 0.9,
      source: 'Google',
    })) || [];
  } catch (error) {
    console.warn('[OATH_PAPERS] Google search failed:', error.message);
    return [];
  }
}

// Stack Overflow API search
async function searchStackOverflow(term) {
  try {
    const response = await axios.get('https://api.stackexchange.com/2.3/search', {
      params: {
        order: 'desc',
        sort: 'relevance',
        tagged: term,
        site: 'stackoverflow',
        pagesize: 5,
      },
    });

    return response.data.items?.map(item => ({
      title: item.title,
      url: item.link,
      snippet: item.title,
      relevance: 0.8,
      source: 'Stack Overflow',
    })) || [];
  } catch (error) {
    console.warn('[OATH_PAPERS] Stack Overflow search failed:', error.message);
    return [];
  }
}

// GitHub API search
async function searchGitHub(term) {
  const githubToken = process.env.GITHUB_TOKEN;
  
  if (!githubToken) {
    return [];
  }

  try {
    const response = await axios.get('https://api.github.com/search/repositories', {
      headers: {
        'Authorization': `token ${githubToken}`,
      },
      params: {
        q: term,
        sort: 'stars',
        order: 'desc',
        per_page: 5,
      },
    });

    return response.data.items?.map(item => ({
      title: item.full_name,
      url: item.html_url,
      snippet: item.description || 'GitHub repository',
      relevance: 0.7,
      source: 'GitHub',
    })) || [];
  } catch (error) {
    console.warn('[OATH_PAPERS] GitHub search failed:', error.message);
    return [];
  }
}

// Documentation search (placeholder for various docs)
async function searchDocumentation(term) {
  // This would integrate with various documentation APIs
  // For now, return mock results
  await new Promise(resolve => setTimeout(resolve, 100));
  
  return [
    {
      title: `${term} Documentation`,
      url: `https://docs.example.com/${term}`,
      snippet: `Official documentation for ${term}`,
      relevance: 0.6,
      source: 'Documentation',
    }
  ];
}

// Remove duplicate search results
function removeDuplicateResults(results) {
  const seen = new Set();
  return results.filter(result => {
    const key = `${result.source}-${result.url}`;
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

// Enhanced learning with retry logic
async function learnFromCombinedDataWithRetry(data, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const learningEntry = {
        type: 'oath_paper_learning',
        subject: data.subject,
        keywords: data.keywords,
        searchResults: data.searchResults,
        targetAI: data.targetAI,
        aiWeights: data.aiWeights,
        timestamp: new Date().toISOString(),
        learningData: {
          description: data.description,
          code: data.code,
          tags: data.tags,
          extractedKeywords: data.keywords,
          internetSources: data.searchResults.length,
          processingAttempt: attempt,
        },
      };

      // Save to learning data file with backup
      await saveLearningDataWithBackup(learningEntry);
      
      console.log('[OATH_PAPERS] 📚 Learning data updated successfully');
      return learningEntry;
    } catch (error) {
      console.warn(`[OATH_PAPERS] ⚠️ Learning attempt ${attempt} failed:`, error.message);
      
      if (attempt === maxRetries) {
        throw error;
      }
      
      // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
    }
  }
}

// Save learning data with backup
async function saveLearningDataWithBackup(learningEntry) {
  const learningDataPath = path.join(__dirname, '../data/learning_data.json');
  const backupPath = path.join(__dirname, '../data/learning_data_backup.json');
  
  let learningData = [];
  
  try {
    const existingData = await fs.readFile(learningDataPath, 'utf8');
    learningData = JSON.parse(existingData);
    
    // Create backup
    await fs.writeFile(backupPath, existingData);
  } catch (error) {
    // File doesn't exist or is invalid, start with empty array
    console.warn('[OATH_PAPERS] ⚠️ Could not read existing learning data:', error.message);
  }

  learningData.push(learningEntry);
  
  // Write with atomic operation
  const tempPath = `${learningDataPath}.tmp`;
  await fs.writeFile(tempPath, JSON.stringify(learningData, null, 2));
  await fs.rename(tempPath, learningDataPath);
}

// Enhanced AI capabilities update
async function updateAICapabilitiesEnhanced(targetAI, keywords, searchResults) {
  const capabilitiesPath = path.join(__dirname, '../data/ai_capabilities.json');
  const backupPath = path.join(__dirname, '../data/ai_capabilities_backup.json');
  
  let capabilities = {};
  
  try {
    const existingData = await fs.readFile(capabilitiesPath, 'utf8');
    capabilities = JSON.parse(existingData);
    
    // Create backup
    await fs.writeFile(backupPath, existingData);
  } catch (error) {
    console.warn('[OATH_PAPERS] ⚠️ Could not read existing capabilities:', error.message);
  }

  const aiTypes = targetAI ? [targetAI] : ['Imperium', 'Sandbox', 'Guardian'];

  aiTypes.forEach(aiType => {
    capabilities[aiType] = capabilities[aiType] || {};
    capabilities[aiType].capabilities = capabilities[aiType].capabilities || [];
    capabilities[aiType].recentLearning = capabilities[aiType].recentLearning || [];
    capabilities[aiType].learningStats = capabilities[aiType].learningStats || {
      totalPapers: 0,
      totalKeywords: 0,
      lastUpdated: null,
    };

    // Add new capabilities with relevance scoring
    keywords.slice(0, 10).forEach(keyword => {
      if (!capabilities[aiType].capabilities.includes(keyword)) {
        capabilities[aiType].capabilities.push(keyword);
      }
    });

    // Add recent learning entry with enhanced data
    capabilities[aiType].recentLearning.unshift({
      type: 'oath_paper',
      keywords: keywords.slice(0, 5),
      sources: searchResults.length,
      timestamp: new Date().toISOString(),
      relevance: calculateRelevanceScore(keywords, searchResults),
    });

    // Update learning stats
    capabilities[aiType].learningStats.totalPapers++;
    capabilities[aiType].learningStats.totalKeywords += keywords.length;
    capabilities[aiType].learningStats.lastUpdated = new Date().toISOString();

    // Keep only recent entries
    if (capabilities[aiType].recentLearning.length > 20) {
      capabilities[aiType].recentLearning = capabilities[aiType].recentLearning.slice(0, 20);
    }
  });

  // Write with atomic operation
  const tempPath = `${capabilitiesPath}.tmp`;
  await fs.writeFile(tempPath, JSON.stringify(capabilities, null, 2));
  await fs.rename(tempPath, capabilitiesPath);
  
  console.log('[OATH_PAPERS] 🧠 AI capabilities updated for:', aiTypes);
}

// Calculate relevance score for learning entries
function calculateRelevanceScore(keywords, searchResults) {
  const keywordCount = keywords.length;
  const sourceCount = searchResults.length;
  const avgRelevance = searchResults.reduce((sum, result) => sum + result.relevance, 0) / sourceCount;
  
  return Math.min(1.0, (keywordCount * 0.1 + sourceCount * 0.05 + avgRelevance * 0.3));
}

// Enhanced Git integration
async function pushToGitEnhanced(subject, keywords, searchResults, targetAI) {
  try {
    console.log('[OATH_PAPERS] 🔄 Pushing learning updates to Git...');

    const commitMessage = `AI Learning Update: ${subject}\n\n` +
      `Keywords: ${keywords.slice(0, 5).join(', ')}\n` +
      `Sources: ${searchResults.length} internet sources\n` +
      `Target AI: ${targetAI || 'All AIs'}\n` +
      `Timestamp: ${new Date().toISOString()}`;

    const gitResult = await performGitCommitEnhanced(commitMessage, subject);
    
    console.log('[OATH_PAPERS] ✅ Git update completed');
    return gitResult;
  } catch (error) {
    console.error('[OATH_PAPERS] ❌ Git update failed:', error);
    throw error;
  }
}

// Enhanced Git commit with real Git operations
async function performGitCommitEnhanced(message, subject) {
  const gitRepoPath = process.env.GIT_REPO_PATH || path.join(__dirname, '../..');
  
  try {
    // Check if Git is available
    await executeGitCommand(['--version'], gitRepoPath);
    
    // Add files
    await executeGitCommand(['add', 'ai-backend/src/data/learning_data.json', 'ai-backend/src/data/ai_capabilities.json'], gitRepoPath);
    
    // Commit
    await executeGitCommand(['commit', '-m', message], gitRepoPath);
    
    // Push (if remote is configured)
    try {
      await executeGitCommand(['push'], gitRepoPath);
    } catch (error) {
      console.warn('[OATH_PAPERS] ⚠️ Git push failed (no remote configured):', error.message);
    }
    
    // Get commit hash
    const commitOutput = await executeGitCommand(['rev-parse', 'HEAD'], gitRepoPath);
    const commitHash = commitOutput.trim();
    
    return {
      commit: commitHash,
      message,
      timestamp: new Date().toISOString(),
      files: ['ai_learning_data.json', 'capabilities.json'],
      success: true,
    };
  } catch (error) {
    console.error('[OATH_PAPERS] ❌ Git operations failed:', error.message);
    return {
      commit: null,
      message,
      timestamp: new Date().toISOString(),
      error: error.message,
      success: false,
    };
  }
}

// Execute Git command
async function executeGitCommand(args, cwd) {
  return new Promise((resolve, reject) => {
    const git = spawn('git', args, { cwd, stdio: 'pipe' });
    
    let output = '';
    let errorOutput = '';
    
    git.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    git.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });
    
    git.on('close', (code) => {
      if (code === 0) {
        resolve(output);
      } else {
        reject(new Error(`Git command failed: ${errorOutput}`));
      }
    });
  });
}

// Error handling utilities
function isRetryableError(error) {
  const retryableErrors = [
    'ECONNRESET',
    'ETIMEDOUT',
    'ENOTFOUND',
    'ECONNREFUSED',
    'ENETUNREACH',
  ];
  
  return retryableErrors.some(retryableError => 
    error.code === retryableError || error.message.includes(retryableError)
  );
}

function getRetryDelay(error) {
  if (error.code === 'ETIMEDOUT') return 30; // 30 seconds
  if (error.code === 'ECONNRESET') return 10; // 10 seconds
  return 5; // Default 5 seconds
}

// Rate limiting middleware
const rateLimit = require('express-rate-limit');

const oathPapersLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10, // Limit each IP to 10 requests per windowMs
  message: {
    success: false,
    error: 'Too many oath paper requests, please try again later.',
    retryAfter: 15 * 60, // 15 minutes
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// Apply rate limiting to oath papers endpoints
router.use(oathPapersLimiter);

// Common words to filter out during keyword extraction
const commonWords = new Set([
  'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
  'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
  'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
  'might', 'can', 'this', 'that', 'these', 'those', 'a', 'an', 'as', 'if',
  'then', 'else', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
  'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
  'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'you',
  'your', 'yours', 'yourself', 'yourselves', 'i', 'me', 'my', 'myself',
  'we', 'our', 'ours', 'ourselves', 'what', 'which', 'who', 'whom',
]);

// Basic oath paper endpoint (fallback)
router.post('/', async (req, res) => {
  try {
    console.log('[OATH_PAPERS] 📜 Basic oath paper request received');
    
    const { subject, tags, description, code, targetAI } = req.body;

    // Use the enhanced service for basic processing too
    const result = await oathPapersService.processOathPaper({
      subject,
      tags,
      description,
      code,
      targetAI,
    });

    if (result.success) {
      console.log('[OATH_PAPERS] ✅ Basic processing completed');
      result.processingTime = Date.now() - req.startTime;
      res.json(result);
    } else {
      res.status(500).json(result);
    }

  } catch (error) {
    console.error('[OATH_PAPERS] ❌ Error in basic processing:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      retryable: oathPapersService.isRetryableError(error),
      retryAfter: oathPapersService.getRetryDelay(error),
      timestamp: new Date().toISOString(),
      processingTime: Date.now() - req.startTime,
    });
  }
});

module.exports = router; 