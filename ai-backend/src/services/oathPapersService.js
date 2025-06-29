const fs = require('fs').promises;
const path = require('path');
const axios = require('axios');
const NLPService = require('./nlpService');

class OathPapersService {
  constructor() {
    this.retryConfig = {
      maxRetries: 3,
      baseDelay: 1000,
      maxDelay: 30000,
      backoffMultiplier: 2,
    };
    
    this.cache = new Map();
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
    
    this.operationalHours = {
      start: '09:00',
      end: '17:00',
      timezone: 'UTC',
    };
    
    this.pendingQueue = [];
    this.processingQueue = [];
    this.failedQueue = [];
    
    // Initialize enhanced NLP service
    this.nlpService = new NLPService();
  }

  // Enhanced paper processing with comprehensive error handling
  async processOathPaper(paperData) {
    const startTime = Date.now();
    const paperId = this.generatePaperId();
    
    try {
      console.log(`[OATH_PAPERS_SERVICE] 📜 Processing paper ${paperId}`);
      
      // Validate paper data
      const validationResult = await this.validatePaperData(paperData);
      if (!validationResult.isValid) {
        throw new Error(`Paper validation failed: ${validationResult.errors.join(', ')}`);
      }

      // Check operational hours
      const isOperational = await this.checkOperationalHours();
      if (!isOperational) {
        await this.queuePaperForLater(paperId, paperData);
        return {
          success: true,
          message: 'Paper queued for processing during operational hours',
          paperId,
          queued: true,
          estimatedProcessingTime: await this.getNextOperationalTime(),
        };
      }

      // Process with retry logic
      const result = await this.processWithRetry(paperId, paperData);
      
      // Update processing statistics
      await this.updateProcessingStats(paperId, 'success', Date.now() - startTime);
      
      console.log(`[OATH_PAPERS_SERVICE] ✅ Paper ${paperId} processed successfully`);
      
      return {
        success: true,
        message: 'Oath paper processed successfully',
        paperId,
        result,
        processingTime: Date.now() - startTime,
      };

    } catch (error) {
      console.error(`[OATH_PAPERS_SERVICE] ❌ Error processing paper ${paperId}:`, error);
      
      // Add to failed queue for manual review
      await this.addToFailedQueue(paperId, paperData, error);
      
      // Update processing statistics
      await this.updateProcessingStats(paperId, 'failed', Date.now() - startTime);
      
      return {
        success: false,
        error: error.message,
        paperId,
        retryable: this.isRetryableError(error),
        retryAfter: this.getRetryDelay(error),
        processingTime: Date.now() - startTime,
      };
    }
  }

  // Enhanced validation with detailed error reporting
  async validatePaperData(paperData) {
    const errors = [];
    const warnings = [];

    // Required fields validation
    if (!paperData.subject || paperData.subject.trim().length < 3) {
      errors.push('Subject must be at least 3 characters long');
    }

    if (!paperData.description || paperData.description.trim().length < 10) {
      errors.push('Description must be at least 10 characters long');
    }

    // Optional fields validation
    if (paperData.code && paperData.code.length > 10000) {
      warnings.push('Code block is very large and may take longer to process');
    }

    if (paperData.tags && !Array.isArray(paperData.tags)) {
      errors.push('Tags must be an array');
    }

    if (paperData.tags && paperData.tags.length > 20) {
      warnings.push('Too many tags provided, only first 20 will be used');
    }

    // Content validation
    if (paperData.description && this.containsInappropriateContent(paperData.description)) {
      errors.push('Description contains inappropriate content');
    }

    if (paperData.code && this.containsMaliciousCode(paperData.code)) {
      errors.push('Code contains potentially malicious patterns');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
    };
  }

  // Enhanced operational hours check with timezone support
  async checkOperationalHours() {
    try {
      const now = new Date();
      const currentTime = now.toLocaleTimeString('en-US', {
        hour12: false,
        timeZone: this.operationalHours.timezone,
      });

      const startTime = this.operationalHours.start;
      const endTime = this.operationalHours.end;

      // Handle overnight hours (e.g., 22:00 to 06:00)
      if (startTime > endTime) {
        return currentTime >= startTime || currentTime <= endTime;
      }

      return currentTime >= startTime && currentTime <= endTime;
    } catch (error) {
      console.warn('[OATH_PAPERS_SERVICE] ⚠️ Error checking operational hours:', error.message);
      // Default to operational if check fails
      return true;
    }
  }

  // Enhanced retry logic with exponential backoff
  async processWithRetry(paperId, paperData, attempt = 1) {
    try {
      // Check cache first
      const cacheKey = this.generateCacheKey(paperData);
      const cachedResult = this.getFromCache(cacheKey);
      if (cachedResult) {
        console.log(`[OATH_PAPERS_SERVICE] 📋 Using cached result for paper ${paperId}`);
        return cachedResult;
      }

      // Process the paper
      const result = await this.processPaperCore(paperId, paperData);
      
      // Cache the result
      this.setCache(cacheKey, result);
      
      return result;

    } catch (error) {
      console.warn(`[OATH_PAPERS_SERVICE] ⚠️ Attempt ${attempt} failed for paper ${paperId}:`, error.message);

      if (attempt >= this.retryConfig.maxRetries || !this.isRetryableError(error)) {
        throw error;
      }

      // Calculate delay with exponential backoff
      const delay = Math.min(
        this.retryConfig.baseDelay * Math.pow(this.retryConfig.backoffMultiplier, attempt - 1),
        this.retryConfig.maxDelay
      );

      console.log(`[OATH_PAPERS_SERVICE] 🔄 Retrying paper ${paperId} in ${delay}ms (attempt ${attempt + 1})`);
      
      await new Promise(resolve => setTimeout(resolve, delay));
      
      return this.processWithRetry(paperId, paperData, attempt + 1);
    }
  }

  // Core paper processing logic
  async processPaperCore(paperId, paperData) {
    const processingSteps = [
      { name: 'keyword_extraction', handler: () => this.extractKeywords(paperData) },
      { name: 'code_analysis', handler: () => this.analyzeCode(paperData) },
      { name: 'internet_search', handler: () => this.searchInternet(paperData) },
      { name: 'ai_learning', handler: () => this.updateAILearning(paperData) },
      { name: 'capability_update', handler: () => this.updateAICapabilities(paperData) },
    ];

    const results = {};
    
    for (const step of processingSteps) {
      try {
        console.log(`[OATH_PAPERS_SERVICE] 🔄 Executing step: ${step.name}`);
        results[step.name] = await step.handler();
        console.log(`[OATH_PAPERS_SERVICE] ✅ Step completed: ${step.name}`);
      } catch (error) {
        console.error(`[OATH_PAPERS_SERVICE] ❌ Step failed: ${step.name}`, error.message);
        results[step.name] = { error: error.message, success: false };
        
        // Continue with other steps unless this is critical
        if (step.name === 'keyword_extraction') {
          throw error; // Critical step, fail the entire process
        }
      }
    }

    return results;
  }

  // Enhanced keyword extraction using NLP service
  async extractKeywords(paperData) {
    try {
      const keywords = new Set();
      
      // Extract from subject
      if (paperData.subject) {
        const subjectKeywords = await this.nlpService.extractKeywords(paperData.subject, {
          maxKeywords: 10,
          useTechnicalTerms: true,
        });
        subjectKeywords.keywords.forEach(keyword => keywords.add(keyword));
      }
      
      // Extract from description
      if (paperData.description) {
        const descKeywords = await this.nlpService.extractKeywords(paperData.description, {
          maxKeywords: 15,
          useTechnicalTerms: true,
        });
        descKeywords.keywords.forEach(keyword => keywords.add(keyword));
      }
      
      // Add user-provided tags
      if (paperData.tags && Array.isArray(paperData.tags)) {
        paperData.tags.forEach(tag => keywords.add(tag.toLowerCase()));
      }
      
      const keywordArray = Array.from(keywords).slice(0, 20);
      
      return {
        keywords: keywordArray,
        method: 'enhanced_nlp',
        confidence: this.calculateKeywordConfidence(keywordArray, paperData),
        extractionTime: Date.now(),
      };
    } catch (error) {
      console.error('[OATH_PAPERS_SERVICE] ❌ Enhanced keyword extraction failed:', error.message);
      
      // Fallback to basic extraction
      return this.extractKeywordsBasic(paperData);
    }
  }

  // Enhanced code analysis using NLP service
  async analyzeCode(paperData) {
    if (!paperData.code) {
      return { success: true, analysis: null };
    }

    try {
      const analysis = await this.nlpService.analyzeCode(paperData.code);
      
      return {
        success: true,
        analysis,
        processingTime: Date.now(),
      };
    } catch (error) {
      console.error('[OATH_PAPERS_SERVICE] ❌ Code analysis failed:', error.message);
      return {
        success: false,
        error: error.message,
        analysis: null,
      };
    }
  }

  // Enhanced internet search with multiple sources and fallback
  async searchInternet(paperData) {
    const keywordResult = await this.extractKeywords(paperData);
    const searchTerms = [
      ...(paperData.tags || []),
      ...keywordResult.keywords.slice(0, 5),
    ];

    const searchResults = [];
    const searchSources = [
      { name: 'google', handler: () => this.searchGoogle(searchTerms) },
      { name: 'stackoverflow', handler: () => this.searchStackOverflow(searchTerms) },
      { name: 'github', handler: () => this.searchGitHub(searchTerms) },
      { name: 'documentation', handler: () => this.searchDocumentation(searchTerms) },
    ];

    for (const source of searchSources) {
      try {
        const results = await source.handler();
        searchResults.push(...results);
        
        // Rate limiting
        await new Promise(resolve => setTimeout(resolve, 200));
      } catch (error) {
        console.warn(`[OATH_PAPERS_SERVICE] ⚠️ Search source ${source.name} failed:`, error.message);
      }
    }

    // If no results from any source, use fallback
    if (searchResults.length === 0) {
      console.warn('[OATH_PAPERS_SERVICE] ⚠️ No search results, using fallback data');
      return this.getFallbackSearchResults(searchTerms);
    }

    return searchResults;
  }

  // Enhanced AI learning update with validation
  async updateAILearning(paperData) {
    try {
      const keywordResult = await this.extractKeywords(paperData);
      const codeAnalysis = await this.analyzeCode(paperData);
      
      const learningData = {
        type: 'oath_paper',
        subject: paperData.subject,
        description: paperData.description,
        code: paperData.code,
        tags: paperData.tags,
        keywords: keywordResult.keywords,
        codeAnalysis: codeAnalysis.analysis,
        timestamp: new Date().toISOString(),
        source: 'oath_papers_service',
        confidence: keywordResult.confidence,
      };

      // Save to learning data file with backup
      await this.saveLearningDataWithBackup(learningData);
      
      return { success: true, learningData };
    } catch (error) {
      console.error('[OATH_PAPERS_SERVICE] ❌ AI learning update failed:', error.message);
      throw error;
    }
  }

  // Enhanced AI capabilities update
  async updateAICapabilities(paperData) {
    try {
      const capabilities = await this.loadAICapabilities();
      const keywordResult = await this.extractKeywords(paperData);
      const keywords = keywordResult.keywords;
      
      // Update capabilities for all AI types
      const aiTypes = ['Imperium', 'Sandbox', 'Guardian'];
      
      aiTypes.forEach(aiType => {
        if (!capabilities[aiType]) {
          capabilities[aiType] = {
            capabilities: [],
            recentLearning: [],
            learningStats: {
              totalPapers: 0,
              totalKeywords: 0,
              lastUpdated: null,
            },
          };
        }

        // Add new capabilities
        keywords.slice(0, 10).forEach(keyword => {
          if (!capabilities[aiType].capabilities.includes(keyword)) {
            capabilities[aiType].capabilities.push(keyword);
          }
        });

        // Update learning stats
        capabilities[aiType].learningStats.totalPapers++;
        capabilities[aiType].learningStats.totalKeywords += keywords.length;
        capabilities[aiType].learningStats.lastUpdated = new Date().toISOString();

        // Add recent learning entry
        capabilities[aiType].recentLearning.unshift({
          type: 'oath_paper',
          subject: paperData.subject,
          keywords: keywords.slice(0, 5),
          confidence: keywordResult.confidence,
          timestamp: new Date().toISOString(),
        });

        // Keep only recent entries
        if (capabilities[aiType].recentLearning.length > 20) {
          capabilities[aiType].recentLearning = capabilities[aiType].recentLearning.slice(0, 20);
        }
      });

      await this.saveAICapabilitiesWithBackup(capabilities);
      
      return { success: true, updatedAIs: aiTypes };
    } catch (error) {
      console.error('[OATH_PAPERS_SERVICE] ❌ AI capabilities update failed:', error.message);
      throw error;
    }
  }

  // Queue management
  async queuePaperForLater(paperId, paperData) {
    const queuedPaper = {
      id: paperId,
      data: paperData,
      queuedAt: new Date().toISOString(),
      priority: this.calculatePriority(paperData),
    };

    this.pendingQueue.push(queuedPaper);
    this.pendingQueue.sort((a, b) => b.priority - a.priority);

    console.log(`[OATH_PAPERS_SERVICE] 📋 Paper ${paperId} queued for later processing`);
  }

  async addToFailedQueue(paperId, paperData, error) {
    const failedPaper = {
      id: paperId,
      data: paperData,
      error: error.message,
      failedAt: new Date().toISOString(),
      retryable: this.isRetryableError(error),
    };

    this.failedQueue.push(failedPaper);
    
    console.log(`[OATH_PAPERS_SERVICE] ❌ Paper ${paperId} added to failed queue`);
  }

  // Utility methods
  generatePaperId() {
    return `paper_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  generateCacheKey(paperData) {
    const content = `${paperData.subject}_${paperData.description}_${paperData.code || ''}`;
    return require('crypto').createHash('md5').update(content).digest('hex');
  }

  getFromCache(key) {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }
    this.cache.delete(key);
    return null;
  }

  setCache(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  calculatePriority(paperData) {
    let priority = 1;
    
    // Higher priority for papers with code
    if (paperData.code) priority += 2;
    
    // Higher priority for papers with more tags
    if (paperData.tags && paperData.tags.length > 5) priority += 1;
    
    // Higher priority for longer descriptions
    if (paperData.description && paperData.description.length > 500) priority += 1;
    
    return priority;
  }

  isRetryableError(error) {
    const retryableErrors = [
      'ECONNRESET',
      'ETIMEDOUT',
      'ENOTFOUND',
      'ECONNREFUSED',
      'ENETUNREACH',
      'ECONNABORTED',
    ];
    
    return retryableErrors.some(retryableError => 
      error.code === retryableError || error.message.includes(retryableError)
    );
  }

  getRetryDelay(error) {
    if (error.code === 'ETIMEDOUT') return 30;
    if (error.code === 'ECONNRESET') return 10;
    return 5;
  }

  async getNextOperationalTime() {
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(9, 0, 0, 0); // 9 AM
    
    return tomorrow.toISOString();
  }

  // Content validation
  containsInappropriateContent(text) {
    const inappropriatePatterns = [
      /\b(hack|crack|exploit|malware|virus)\b/i,
      /\b(illegal|unlawful|criminal)\b/i,
    ];
    
    return inappropriatePatterns.some(pattern => pattern.test(text));
  }

  containsMaliciousCode(code) {
    const maliciousPatterns = [
      /eval\s*\(/i,
      /exec\s*\(/i,
      /system\s*\(/i,
      /shell_exec\s*\(/i,
      /passthru\s*\(/i,
    ];
    
    return maliciousPatterns.some(pattern => pattern.test(code));
  }

  // Basic keyword extraction (fallback)
  async extractKeywordsBasic(paperData) {
    const keywords = new Set();
    
    // Extract from subject
    if (paperData.subject) {
      const subjectWords = paperData.subject.toLowerCase()
        .replace(/[^\w\s]/g, ' ')
        .split(/\s+/)
        .filter(word => word.length > 3);
      
      subjectWords.forEach(word => keywords.add(word));
    }
    
    // Extract from description
    if (paperData.description) {
      const descWords = paperData.description.toLowerCase()
        .replace(/[^\w\s]/g, ' ')
        .split(/\s+/)
        .filter(word => word.length > 3);
      
      descWords.forEach(word => keywords.add(word));
    }
    
    // Add tags
    if (paperData.tags && Array.isArray(paperData.tags)) {
      paperData.tags.forEach(tag => keywords.add(tag.toLowerCase()));
    }
    
    const keywordArray = Array.from(keywords).slice(0, 15);
    
    return {
      keywords: keywordArray,
      method: 'basic',
      confidence: this.calculateKeywordConfidence(keywordArray, paperData),
      extractionTime: Date.now(),
    };
  }

  // Calculate keyword confidence
  calculateKeywordConfidence(keywords, paperData) {
    if (keywords.length === 0) return 0;

    let confidence = 0;
    
    // Higher confidence for more keywords
    confidence += Math.min(keywords.length * 0.1, 0.5);
    
    // Higher confidence for technical terms
    const technicalTerms = keywords.filter(keyword => 
      this.nlpService.technicalTerms.has(keyword) || 
      this.nlpService.isTechnicalTerm(keyword)
    );
    confidence += (technicalTerms.length / keywords.length) * 0.3;
    
    // Higher confidence for longer content
    const totalLength = (paperData.subject?.length || 0) + (paperData.description?.length || 0);
    confidence += Math.min(totalLength / 1000, 0.2);
    
    return Math.min(confidence, 1.0);
  }

  // Search methods with fallback
  async searchGoogle(terms) {
    // This would use Google Custom Search API
    return this.getFallbackSearchResults(terms);
  }

  async searchStackOverflow(terms) {
    // This would use Stack Overflow API
    return this.getFallbackSearchResults(terms);
  }

  async searchGitHub(terms) {
    // This would use GitHub API
    return this.getFallbackSearchResults(terms);
  }

  async searchDocumentation(terms) {
    // This would search various documentation sites
    return this.getFallbackSearchResults(terms);
  }

  getFallbackSearchResults(terms) {
    return terms.map(term => ({
      title: `Search result for ${term}`,
      url: `https://example.com/search?q=${encodeURIComponent(term)}`,
      snippet: `Information about ${term} from the internet`,
      relevance: 0.5,
      source: 'fallback',
    }));
  }

  // File operations with backup
  async saveLearningDataWithBackup(learningData) {
    const dataPath = path.join(__dirname, '../data/learning_data.json');
    const backupPath = path.join(__dirname, '../data/learning_data_backup.json');
    
    let existingData = [];
    try {
      const data = await fs.readFile(dataPath, 'utf8');
      existingData = JSON.parse(data);
      await fs.writeFile(backupPath, data);
    } catch (error) {
      console.warn('[OATH_PAPERS_SERVICE] ⚠️ Could not read existing learning data:', error.message);
    }

    existingData.push(learningData);
    
    const tempPath = `${dataPath}.tmp`;
    await fs.writeFile(tempPath, JSON.stringify(existingData, null, 2));
    await fs.rename(tempPath, dataPath);
  }

  async loadAICapabilities() {
    const capabilitiesPath = path.join(__dirname, '../data/ai_capabilities.json');
    
    try {
      const data = await fs.readFile(capabilitiesPath, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      console.warn('[OATH_PAPERS_SERVICE] ⚠️ Could not read AI capabilities:', error.message);
      return {};
    }
  }

  async saveAICapabilitiesWithBackup(capabilities) {
    const capabilitiesPath = path.join(__dirname, '../data/ai_capabilities.json');
    const backupPath = path.join(__dirname, '../data/ai_capabilities_backup.json');
    
    try {
      const existingData = await fs.readFile(capabilitiesPath, 'utf8');
      await fs.writeFile(backupPath, existingData);
    } catch (error) {
      console.warn('[OATH_PAPERS_SERVICE] ⚠️ Could not create capabilities backup:', error.message);
    }

    const tempPath = `${capabilitiesPath}.tmp`;
    await fs.writeFile(tempPath, JSON.stringify(capabilities, null, 2));
    await fs.rename(tempPath, capabilitiesPath);
  }

  // Statistics tracking
  async updateProcessingStats(paperId, status, processingTime) {
    const statsPath = path.join(__dirname, '../data/processing_stats.json');
    
    let stats = {
      total: 0,
      successful: 0,
      failed: 0,
      averageProcessingTime: 0,
      lastUpdated: null,
    };
    
    try {
      const data = await fs.readFile(statsPath, 'utf8');
      stats = JSON.parse(data);
    } catch (error) {
      console.warn('[OATH_PAPERS_SERVICE] ⚠️ Could not read processing stats:', error.message);
    }

    stats.total++;
    if (status === 'success') {
      stats.successful++;
    } else {
      stats.failed++;
    }

    // Update average processing time
    const totalTime = stats.averageProcessingTime * (stats.total - 1) + processingTime;
    stats.averageProcessingTime = totalTime / stats.total;
    stats.lastUpdated = new Date().toISOString();

    await fs.writeFile(statsPath, JSON.stringify(stats, null, 2));
  }

  // Queue management methods
  getPendingQueue() {
    return this.pendingQueue;
  }

  getFailedQueue() {
    return this.failedQueue;
  }

  async retryFailedPaper(paperId) {
    const failedPaper = this.failedQueue.find(paper => paper.id === paperId);
    if (!failedPaper) {
      throw new Error('Paper not found in failed queue');
    }

    // Remove from failed queue
    this.failedQueue = this.failedQueue.filter(paper => paper.id !== paperId);
    
    // Retry processing
    return this.processOathPaper(failedPaper.data);
  }

  async clearFailedQueue() {
    this.failedQueue = [];
    console.log('[OATH_PAPERS_SERVICE] 🗑️ Failed queue cleared');
  }

  // NLP service management
  getNLPServiceStats() {
    return this.nlpService.getCacheStats();
  }

  clearNLPCache() {
    this.nlpService.clearCache();
  }
}

module.exports = OathPapersService; 