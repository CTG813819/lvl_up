const natural = require('natural');
const { TfIdf } = require('natural');
const fs = require('fs').promises;
const path = require('path');

class NLPService {
  constructor() {
    this.tfidf = new TfIdf();
    this.tokenizer = new natural.WordTokenizer();
    this.stemmer = natural.PorterStemmer;
    this.stopWords = this.loadStopWords();
    this.technicalTerms = this.loadTechnicalTerms();
    this.cache = new Map();
    this.cacheTimeout = 10 * 60 * 1000; // 10 minutes
  }

  // Enhanced keyword extraction with multiple algorithms
  async extractKeywords(text, options = {}) {
    const {
      maxKeywords = 15,
      minLength = 3,
      useStemming = true,
      useTFIDF = true,
      useTechnicalTerms = true,
      language = 'en',
    } = options;

    const cacheKey = this.generateCacheKey(text, options);
    const cached = this.getFromCache(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      // Multiple extraction methods
      const methods = [];
      
      if (useTFIDF) {
        methods.push(this.extractKeywordsTFIDF(text, maxKeywords, minLength));
      }
      
      methods.push(this.extractKeywordsFrequency(text, maxKeywords, minLength));
      methods.push(this.extractKeywordsTechnical(text, maxKeywords, minLength));
      
      if (useStemming) {
        methods.push(this.extractKeywordsStemmed(text, maxKeywords, minLength));
      }

      // Combine and rank results
      const allKeywords = await Promise.all(methods);
      const combinedKeywords = this.combineAndRankKeywords(allKeywords, maxKeywords);

      const result = {
        keywords: combinedKeywords,
        method: 'enhanced',
        confidence: this.calculateConfidence(combinedKeywords, text),
        extractionTime: Date.now(),
      };

      this.setCache(cacheKey, result);
      return result;

    } catch (error) {
      console.error('[NLP_SERVICE] ❌ Keyword extraction failed:', error.message);
      
      // Fallback to basic extraction
      return this.extractKeywordsBasic(text, maxKeywords, minLength);
    }
  }

  // TF-IDF based keyword extraction
  async extractKeywordsTFIDF(text, maxKeywords, minLength) {
    const words = this.tokenizer.tokenize(text.toLowerCase())
      .filter(word => word.length >= minLength)
      .filter(word => !this.stopWords.has(word));

    if (words.length === 0) return [];

    // Add document to TF-IDF
    this.tfidf.addDocument(words);

    // Get TF-IDF scores
    const scores = [];
    this.tfidf.listTerms(0).forEach(item => {
      if (item.term.length >= minLength) {
        scores.push({
          term: item.term,
          score: item.score,
          method: 'tfidf',
        });
      }
    });

    // Reset TF-IDF for next use
    this.tfidf = new TfIdf();

    return scores
      .sort((a, b) => b.score - a.score)
      .slice(0, maxKeywords)
      .map(item => item.term);
  }

  // Frequency-based keyword extraction
  extractKeywordsFrequency(text, maxKeywords, minLength) {
    const words = this.tokenizer.tokenize(text.toLowerCase())
      .filter(word => word.length >= minLength)
      .filter(word => !this.stopWords.has(word));

    const wordCount = {};
    words.forEach(word => {
      wordCount[word] = (wordCount[word] || 0) + 1;
    });

    return Object.entries(wordCount)
      .sort(([,a], [,b]) => b - a)
      .slice(0, maxKeywords)
      .map(([word]) => word);
  }

  // Technical terms extraction
  extractKeywordsTechnical(text, maxKeywords, minLength) {
    const words = this.tokenizer.tokenize(text.toLowerCase())
      .filter(word => word.length >= minLength);

    const technicalKeywords = words.filter(word => 
      this.technicalTerms.has(word) || 
      this.isTechnicalTerm(word)
    );

    return technicalKeywords.slice(0, maxKeywords);
  }

  // Stemmed keyword extraction
  extractKeywordsStemmed(text, maxKeywords, minLength) {
    const words = this.tokenizer.tokenize(text.toLowerCase())
      .filter(word => word.length >= minLength)
      .filter(word => !this.stopWords.has(word));

    const stemmedWords = words.map(word => this.stemmer.stem(word));
    const stemmedCount = {};

    stemmedWords.forEach((stemmed, index) => {
      const original = words[index];
      if (!stemmedCount[stemmed]) {
        stemmedCount[stemmed] = { count: 0, original: original };
      }
      stemmedCount[stemmed].count++;
    });

    return Object.entries(stemmedCount)
      .sort(([,a], [,b]) => b.count - a.count)
      .slice(0, maxKeywords)
      .map(([,data]) => data.original);
  }

  // Basic keyword extraction (fallback)
  extractKeywordsBasic(text, maxKeywords, minLength) {
    const words = this.tokenizer.tokenize(text.toLowerCase())
      .filter(word => word.length >= minLength)
      .filter(word => !this.stopWords.has(word));

    const wordCount = {};
    words.forEach(word => {
      wordCount[word] = (wordCount[word] || 0) + 1;
    });

    return Object.entries(wordCount)
      .sort(([,a], [,b]) => b - a)
      .slice(0, maxKeywords)
      .map(([word]) => word);
  }

  // Enhanced code analysis
  async analyzeCode(code, language = 'auto') {
    const analysis = {
      keywords: [],
      functions: [],
      classes: [],
      imports: [],
      variables: [],
      patterns: [],
      complexity: 0,
      language: language === 'auto' ? this.detectLanguage(code) : language,
    };

    if (!code) return analysis;

    try {
      // Extract code elements based on detected language
      const patterns = this.getLanguagePatterns(analysis.language);
      
      for (const [type, pattern] of Object.entries(patterns)) {
        const matches = code.match(pattern) || [];
        matches.forEach(match => {
          const cleanMatch = this.cleanCodeMatch(match, type);
          if (cleanMatch && cleanMatch.length > 2) {
            analysis[type].push(cleanMatch);
          }
        });
      }

      // Extract keywords from code
      analysis.keywords = await this.extractKeywords(code, {
        maxKeywords: 20,
        minLength: 2,
        useTechnicalTerms: true,
      });

      // Calculate complexity
      analysis.complexity = this.calculateCodeComplexity(code);

      return analysis;

    } catch (error) {
      console.error('[NLP_SERVICE] ❌ Code analysis failed:', error.message);
      return analysis;
    }
  }

  // Language detection
  detectLanguage(code) {
    const indicators = {
      javascript: [/\b(function|const|let|var)\b/g, /\bconsole\.log\b/g, /\.js$/],
      python: [/\bdef\b/g, /\bimport\b/g, /\bclass\b/g],
      java: [/\bpublic\b/g, /\bprivate\b/g, /\bclass\b/g, /\.java$/],
      cpp: [/\b#include\b/g, /\bstd::\b/g, /\.cpp$/],
      csharp: [/\busing\b/g, /\bnamespace\b/g, /\.cs$/],
      php: [/\b<?php\b/g, /\bfunction\b/g, /\.php$/],
      ruby: [/\bdef\b/g, /\bend\b/g, /\.rb$/],
      go: [/\bfunc\b/g, /\bpackage\b/g, /\.go$/],
      rust: [/\bfn\b/g, /\blet\b/g, /\.rs$/],
    };

    let maxScore = 0;
    let detectedLanguage = 'unknown';

    for (const [language, patterns] of Object.entries(indicators)) {
      let score = 0;
      patterns.forEach(pattern => {
        const matches = code.match(pattern);
        if (matches) {
          score += matches.length;
        }
      });
      
      if (score > maxScore) {
        maxScore = score;
        detectedLanguage = language;
      }
    }

    return detectedLanguage;
  }

  // Get language-specific patterns
  getLanguagePatterns(language) {
    const patterns = {
      javascript: {
        function: /(?:function|const|let|var)\s+(\w+)/gi,
        class: /class\s+(\w+)/gi,
        import: /(?:import|require)\s+[\w\.\/]+/gi,
        variable: /(?:const|let|var)\s+(\w+)/gi,
        method: /(\w+)\s*\([^)]*\)\s*{/gi,
      },
      python: {
        function: /def\s+(\w+)/gi,
        class: /class\s+(\w+)/gi,
        import: /(?:import|from)\s+[\w\.]+/gi,
        variable: /(\w+)\s*=/gi,
        method: /def\s+(\w+)/gi,
      },
      java: {
        function: /(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(/gi,
        class: /class\s+(\w+)/gi,
        import: /import\s+[\w\.]+/gi,
        variable: /(?:int|String|boolean|double|float)\s+(\w+)/gi,
        method: /(?:public|private|protected)?\s*\w+\s+(\w+)\s*\(/gi,
      },
      default: {
        function: /(?:def|function|func|fn)\s+(\w+)/gi,
        class: /(?:class|struct|interface)\s+(\w+)/gi,
        import: /(?:import|from|require|using)\s+[\w\.]+/gi,
        variable: /(?:const|let|var|final)\s+(\w+)/gi,
        method: /(\w+)\s*\([^)]*\)\s*{/gi,
      },
    };

    return patterns[language] || patterns.default;
  }

  // Clean code match
  cleanCodeMatch(match, type) {
    const cleaned = match.replace(/[^\w]/g, ' ').trim();
    return cleaned.length > 2 ? cleaned : null;
  }

  // Calculate code complexity
  calculateCodeComplexity(code) {
    let complexity = 0;
    
    // Count control structures
    const controlPatterns = [
      /\bif\b/g,
      /\bfor\b/g,
      /\bwhile\b/g,
      /\bswitch\b/g,
      /\bcase\b/g,
      /\bcatch\b/g,
      /\btry\b/g,
    ];

    controlPatterns.forEach(pattern => {
      const matches = code.match(pattern);
      if (matches) {
        complexity += matches.length;
      }
    });

    // Count nested structures
    const lines = code.split('\n');
    let maxNesting = 0;
    let currentNesting = 0;

    lines.forEach(line => {
      const openBraces = (line.match(/{/g) || []).length;
      const closeBraces = (line.match(/}/g) || []).length;
      
      currentNesting += openBraces - closeBraces;
      maxNesting = Math.max(maxNesting, currentNesting);
    });

    complexity += maxNesting * 2;

    return Math.min(complexity, 100); // Cap at 100
  }

  // Combine and rank keywords from multiple methods
  combineAndRankKeywords(keywordArrays, maxKeywords) {
    const keywordScores = new Map();

    keywordArrays.forEach((keywords, methodIndex) => {
      keywords.forEach((keyword, index) => {
        const score = keywordScores.get(keyword) || 0;
        // Higher score for earlier position and method diversity
        const newScore = score + (keywords.length - index) + (methodIndex + 1);
        keywordScores.set(keyword, newScore);
      });
    });

    return Array.from(keywordScores.entries())
      .sort(([,a], [,b]) => b - a)
      .slice(0, maxKeywords)
      .map(([keyword]) => keyword);
  }

  // Calculate confidence score
  calculateConfidence(keywords, text) {
    if (keywords.length === 0) return 0;

    const textLength = text.length;
    const keywordDensity = keywords.reduce((sum, keyword) => {
      const regex = new RegExp(keyword, 'gi');
      const matches = text.match(regex);
      return sum + (matches ? matches.length : 0);
    }, 0) / textLength;

    const diversity = new Set(keywords).size / keywords.length;
    
    return Math.min(1.0, (keywordDensity * 100 + diversity * 50) / 150);
  }

  // Check if word is technical term
  isTechnicalTerm(word) {
    const technicalPatterns = [
      /^[A-Z][a-z]+(?:[A-Z][a-z]+)*$/, // CamelCase
      /^[a-z]+_[a-z]+$/, // snake_case
      /^[A-Z]+$/, // CONSTANTS
      /^[a-z]+[A-Z]/, // camelCase
    ];

    return technicalPatterns.some(pattern => pattern.test(word));
  }

  // Load stop words
  loadStopWords() {
    const stopWords = new Set([
      'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
      'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
      'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
      'might', 'can', 'this', 'that', 'these', 'those', 'a', 'an', 'as', 'if',
      'then', 'else', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
      'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
      'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'you',
      'your', 'yours', 'yourself', 'yourselves', 'i', 'me', 'my', 'myself',
      'we', 'our', 'ours', 'ourselves', 'what', 'which', 'who', 'whom',
      'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
      'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
    ]);

    return stopWords;
  }

  // Load technical terms
  loadTechnicalTerms() {
    const technicalTerms = new Set([
      // Programming concepts
      'function', 'class', 'method', 'variable', 'constant', 'parameter',
      'argument', 'return', 'import', 'export', 'module', 'package',
      'interface', 'abstract', 'static', 'public', 'private', 'protected',
      'final', 'const', 'let', 'var', 'def', 'func', 'fn', 'async', 'await',
      'promise', 'callback', 'closure', 'lambda', 'arrow', 'generator',
      'iterator', 'stream', 'pipe', 'map', 'filter', 'reduce', 'forEach',
      
      // Data structures
      'array', 'object', 'string', 'number', 'boolean', 'null', 'undefined',
      'list', 'set', 'map', 'dictionary', 'hash', 'tree', 'graph', 'stack',
      'queue', 'heap', 'linked', 'binary', 'trie', 'matrix', 'vector',
      
      // Web technologies
      'html', 'css', 'javascript', 'react', 'vue', 'angular', 'node',
      'express', 'api', 'rest', 'graphql', 'http', 'https', 'json', 'xml',
      'dom', 'ajax', 'fetch', 'axios', 'jquery', 'bootstrap', 'tailwind',
      
      // Databases
      'database', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis',
      'elasticsearch', 'index', 'query', 'schema', 'table', 'collection',
      'document', 'field', 'primary', 'foreign', 'key', 'join', 'select',
      
      // DevOps
      'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'ci', 'cd', 'git',
      'github', 'gitlab', 'jenkins', 'travis', 'deploy', 'build', 'test',
      'lint', 'format', 'compile', 'bundle', 'webpack', 'rollup', 'vite',
      
      // Frameworks and libraries
      'express', 'koa', 'fastify', 'nestjs', 'django', 'flask', 'spring',
      'laravel', 'rails', 'asp', 'dotnet', 'jvm', 'clr', 'runtime',
      'framework', 'library', 'sdk', 'api', 'plugin', 'extension',
    ]);

    return technicalTerms;
  }

  // Cache management
  generateCacheKey(text, options) {
    const content = `${text}_${JSON.stringify(options)}`;
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

  // Clear cache
  clearCache() {
    this.cache.clear();
    console.log('[NLP_SERVICE] 🗑️ Cache cleared');
  }

  // Get cache statistics
  getCacheStats() {
    const now = Date.now();
    let validEntries = 0;
    let expiredEntries = 0;

    this.cache.forEach((value, key) => {
      if (now - value.timestamp < this.cacheTimeout) {
        validEntries++;
      } else {
        expiredEntries++;
        this.cache.delete(key);
      }
    });

    return {
      validEntries,
      expiredEntries,
      totalEntries: validEntries + expiredEntries,
      cacheTimeout: this.cacheTimeout,
    };
  }
}

module.exports = NLPService; 