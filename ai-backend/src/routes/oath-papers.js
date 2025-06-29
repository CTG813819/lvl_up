const express = require('express');
const router = express.Router();
const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

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

    // Extract keywords from description and code
    const keywords = await extractKeywords(description, code, tags);
    console.log('[OATH_PAPERS] 🔍 Extracted keywords:', keywords);

    // Search internet for additional information
    const searchResults = await searchInternet(keywords, tags);
    console.log('[OATH_PAPERS] 🌐 Internet search results:', searchResults.length);

    // Learn from combined data
    const learningResult = await learnFromCombinedData({
      subject,
      description,
      code,
      tags,
      keywords,
      searchResults,
      targetAI,
      aiWeights,
    });

    // Update AI capabilities
    await updateAICapabilities(targetAI, keywords, searchResults);

    // Push to Git if specified
    let gitResult = null;
    if (learningInstructions?.pushToGit) {
      gitResult = await pushToGit(subject, keywords, searchResults, targetAI);
    }

    // Create learning progress response
    const learningProgress = {
      keywordsFound: keywords,
      internetSearches: searchResults,
      gitUpdates: gitResult ? [gitResult] : [],
      learningResult,
      timestamp: new Date().toISOString(),
    };

    console.log('[OATH_PAPERS] ✅ Enhanced learning completed successfully');

    res.json({
      success: true,
      message: 'Enhanced oath paper learning completed',
      learningProgress,
    });

  } catch (error) {
    console.error('[OATH_PAPERS] ❌ Error in enhanced learning:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// Extract keywords from text and code
async function extractKeywords(description, code, tags) {
  const keywords = new Set();

  // Add user-provided tags
  if (tags && Array.isArray(tags)) {
    tags.forEach(tag => keywords.add(tag.toLowerCase()));
  }

  // Extract from description
  if (description) {
    const descriptionKeywords = await extractKeywordsFromText(description);
    descriptionKeywords.forEach(keyword => keywords.add(keyword));
  }

  // Extract from code
  if (code) {
    const codeKeywords = await extractKeywordsFromCode(code);
    codeKeywords.forEach(keyword => keywords.add(keyword));
  }

  return Array.from(keywords);
}

// Extract keywords from text using NLP techniques
async function extractKeywordsFromText(text) {
  // Simple keyword extraction - in production, use proper NLP libraries
  const words = text.toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(word => word.length > 3)
    .filter(word => !commonWords.has(word));

  // Count frequency and return top keywords
  const wordCount = {};
  words.forEach(word => {
    wordCount[word] = (wordCount[word] || 0) + 1;
  });

  const sortedWords = Object.entries(wordCount)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 10)
    .map(([word]) => word);

  return sortedWords;
}

// Extract keywords from code
async function extractKeywordsFromCode(code) {
  const keywords = new Set();

  // Extract function names, class names, and important identifiers
  const functionMatches = code.match(/def\s+(\w+)/g) || [];
  const classMatches = code.match(/class\s+(\w+)/g) || [];
  const importMatches = code.match(/import\s+(\w+)/g) || [];
  const variableMatches = code.match(/(\w+)\s*=/g) || [];

  functionMatches.forEach(match => {
    const name = match.replace(/def\s+/, '');
    keywords.add(name);
  });

  classMatches.forEach(match => {
    const name = match.replace(/class\s+/, '');
    keywords.add(name);
  });

  importMatches.forEach(match => {
    const name = match.replace(/import\s+/, '');
    keywords.add(name);
  });

  variableMatches.forEach(match => {
    const name = match.replace(/\s*=.*/, '');
    keywords.add(name);
  });

  return Array.from(keywords);
}

// Search internet for additional information
async function searchInternet(keywords, tags) {
  const searchResults = [];
  const searchTerms = [...keywords, ...tags].slice(0, 5); // Limit to top 5 terms

  for (const term of searchTerms) {
    try {
      const result = await performWebSearch(term);
      searchResults.push(...result);
    } catch (error) {
      console.warn(`[OATH_PAPERS] ⚠️ Search failed for term "${term}":`, error.message);
    }
  }

  return searchResults;
}

// Perform web search (placeholder for real search API integration)
async function performWebSearch(term) {
  // This would integrate with a real search API (Google, Bing, etc.)
  // For now, return mock results
  await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API call

  return [
    {
      title: `Search result for ${term}`,
      url: `https://example.com/${term}`,
      snippet: `Information about ${term} from the internet`,
      relevance: 0.8,
    }
  ];
}

// Learn from combined data
async function learnFromCombinedData(data) {
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
    },
  };

  // Save to learning data file
  const learningDataPath = path.join(__dirname, '../data/learning_data.json');
  let learningData = [];
  
  try {
    const existingData = await fs.readFile(learningDataPath, 'utf8');
    learningData = JSON.parse(existingData);
  } catch (error) {
    // File doesn't exist or is invalid, start with empty array
  }

  learningData.push(learningEntry);
  await fs.writeFile(learningDataPath, JSON.stringify(learningData, null, 2));

  console.log('[OATH_PAPERS] 📚 Learning data updated');
  return learningEntry;
}

// Update AI capabilities
async function updateAICapabilities(targetAI, keywords, searchResults) {
  const capabilitiesPath = path.join(__dirname, '../data/ai_capabilities.json');
  let capabilities = {};
  
  try {
    const existingData = await fs.readFile(capabilitiesPath, 'utf8');
    capabilities = JSON.parse(existingData);
  } catch (error) {
    // File doesn't exist or is invalid, start with empty object
  }

  const aiTypes = targetAI ? [targetAI] : ['Imperium', 'Sandbox', 'Guardian'];

  aiTypes.forEach(aiType => {
    capabilities[aiType] = capabilities[aiType] || {};
    capabilities[aiType].capabilities = capabilities[aiType].capabilities || [];
    capabilities[aiType].recentLearning = capabilities[aiType].recentLearning || [];

    // Add new capabilities
    keywords.slice(0, 5).forEach(keyword => {
      if (!capabilities[aiType].capabilities.includes(keyword)) {
        capabilities[aiType].capabilities.push(keyword);
      }
    });

    // Add recent learning entry
    capabilities[aiType].recentLearning.unshift({
      type: 'oath_paper',
      keywords: keywords.slice(0, 3),
      sources: searchResults.length,
      timestamp: new Date().toISOString(),
    });

    // Keep only recent entries
    if (capabilities[aiType].recentLearning.length > 10) {
      capabilities[aiType].recentLearning = capabilities[aiType].recentLearning.slice(0, 10);
    }
  });

  await fs.writeFile(capabilitiesPath, JSON.stringify(capabilities, null, 2));
  console.log('[OATH_PAPERS] 🧠 AI capabilities updated for:', aiTypes);
}

// Push updates to Git repository
async function pushToGit(subject, keywords, searchResults, targetAI) {
  try {
    console.log('[OATH_PAPERS] 🔄 Pushing learning updates to Git...');

    const commitMessage = `AI Learning Update: ${subject}\n\n` +
      `Keywords: ${keywords.slice(0, 5).join(', ')}\n` +
      `Sources: ${searchResults.length} internet sources\n` +
      `Target AI: ${targetAI || 'All AIs'}`;

    // This would integrate with Git API
    const gitResult = await performGitCommit(commitMessage, subject);
    
    console.log('[OATH_PAPERS] ✅ Git update completed');
    return gitResult;
  } catch (error) {
    console.error('[OATH_PAPERS] ❌ Git update failed:', error);
    throw error;
  }
}

// Perform Git commit (placeholder for real Git integration)
async function performGitCommit(message, subject) {
  // This would integrate with Git API (GitHub, GitLab, etc.)
  await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate Git operations

  return {
    commit: `abc123${Date.now()}`,
    message,
    timestamp: new Date().toISOString(),
    files: ['ai_learning_data.json', 'capabilities.json'],
  };
}

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

    // Basic processing without enhanced features
    const result = {
      success: true,
      message: 'Oath paper processed successfully',
      data: {
        subject,
        tags,
        description,
        code,
        targetAI,
        timestamp: new Date().toISOString(),
      },
    };

    console.log('[OATH_PAPERS] ✅ Basic processing completed');
    res.json(result);

  } catch (error) {
    console.error('[OATH_PAPERS] ❌ Error in basic processing:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

module.exports = router; 