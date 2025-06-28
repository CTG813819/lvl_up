const axios = require('axios');
const { logEvent } = require('../state');

class InternetLearningService {
  /**
   * Learn from internet sources based on proposal results
   */
  static async learnFromInternet(aiType, proposal, result) {
    console.log(`[INTERNET_LEARNING] 🌐 ${aiType} learning from internet for proposal result: ${result}`);
    
    try {
      // Generate search queries based on the proposal and result
      const searchQueries = this.generateSearchQueries(aiType, proposal, result);
      
      // Fetch information from multiple sources
      const learningData = await this.fetchLearningData(searchQueries);
      
      // Analyze and extract insights
      const insights = await this.analyzeLearningData(learningData, aiType, proposal);
      
      // Generate learning recommendations
      const recommendations = await this.generateRecommendations(insights, aiType, proposal);
      
      // Store learning data
      await this.storeLearningData(aiType, proposal, insights, recommendations);
      
      console.log(`[INTERNET_LEARNING] ✅ ${aiType} completed internet learning with ${insights.length} insights`);
      
      return {
        insights,
        recommendations,
        sources: learningData.map(d => d.source)
      };
      
    } catch (error) {
      console.error(`[INTERNET_LEARNING] ❌ Error in internet learning for ${aiType}:`, error);
      throw error;
    }
  }
  
  /**
   * Generate search queries based on proposal context
   */
  static generateSearchQueries(aiType, proposal, result) {
    const queries = [];
    
    // Base queries based on AI type
    const aiContext = {
      'Imperium': 'code optimization performance improvement',
      'Guardian': 'code security best practices error handling',
      'Sandbox': 'code refactoring clean code principles'
    };
    
    // Add AI-specific context
    queries.push(`${aiContext[aiType]} ${proposal.improvementType || 'code improvement'}`);
    
    // Add language-specific queries
    if (proposal.filePath?.includes('.dart')) {
      queries.push(`Dart Flutter ${proposal.improvementType || 'best practices'}`);
    }
    
    // Add result-specific queries
    if (result === 'failed' || result === 'rejected') {
      queries.push(`${proposal.userFeedbackReason || 'common coding mistakes'} ${aiContext[aiType]}`);
    } else if (result === 'passed' || result === 'approved') {
      queries.push(`${proposal.userFeedbackReason || 'successful code improvements'} ${aiContext[aiType]}`);
    }
    
    // Add specific improvement type queries
    if (proposal.improvementType) {
      queries.push(`${proposal.improvementType} programming best practices`);
    }
    
    return queries.slice(0, 5); // Limit to 5 queries
  }
  
  /**
   * Fetch learning data from internet sources
   */
  static async fetchLearningData(queries) {
    const learningData = [];
    
    for (const query of queries) {
      try {
        console.log(`[INTERNET_LEARNING] 🔍 Searching for: ${query}`);
        
        // Search multiple sources
        const sources = [
          { name: 'Stack Overflow', url: `https://stackoverflow.com/search?q=${encodeURIComponent(query)}` },
          { name: 'GitHub', url: `https://github.com/search?q=${encodeURIComponent(query)}&type=code` },
          { name: 'Medium', url: `https://medium.com/search?q=${encodeURIComponent(query)}` },
          { name: 'Dev.to', url: `https://dev.to/search?q=${encodeURIComponent(query)}` }
        ];
        
        for (const source of sources) {
          try {
            const data = await this.fetchFromSource(source, query);
            if (data) {
              learningData.push(data);
            }
          } catch (error) {
            console.log(`[INTERNET_LEARNING] ⚠️ Failed to fetch from ${source.name}: ${error.message}`);
          }
        }
        
      } catch (error) {
        console.log(`[INTERNET_LEARNING] ⚠️ Error fetching data for query "${query}": ${error.message}`);
      }
    }
    
    return learningData;
  }
  
  /**
   * Fetch data from a specific source
   */
  static async fetchFromSource(source, query) {
    try {
      const response = await axios.get(source.url, {
        timeout: 10000,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      });
      
      let content = '';
      
      // Extract relevant content based on source using simple text parsing
      const html = response.data;
      
      // Remove HTML tags and extract text content
      content = this.extractTextFromHTML(html);
      
      if (content && content.length > 50) {
        return {
          source: source.name,
          query,
          content: content.substring(0, 1000), // Limit content length
          url: source.url
        };
      }
      
    } catch (error) {
      console.log(`[INTERNET_LEARNING] ⚠️ Error fetching from ${source.name}: ${error.message}`);
    }
    
    return null;
  }
  
  /**
   * Extract text content from HTML using simple regex
   */
  static extractTextFromHTML(html) {
    // Remove script and style tags
    let text = html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '');
    text = text.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');
    
    // Remove HTML tags
    text = text.replace(/<[^>]*>/g, ' ');
    
    // Decode HTML entities
    text = text.replace(/&amp;/g, '&');
    text = text.replace(/&lt;/g, '<');
    text = text.replace(/&gt;/g, '>');
    text = text.replace(/&quot;/g, '"');
    text = text.replace(/&#39;/g, "'");
    text = text.replace(/&nbsp;/g, ' ');
    
    // Clean up whitespace
    text = text.replace(/\s+/g, ' ').trim();
    
    return text;
  }
  
  /**
   * Analyze learning data to extract insights
   */
  static async analyzeLearningData(learningData, aiType, proposal) {
    const insights = [];
    
    for (const data of learningData) {
      try {
        // Extract key insights from content
        const contentInsights = this.extractInsightsFromContent(data.content, aiType, proposal);
        insights.push(...contentInsights);
      } catch (error) {
        console.log(`[INTERNET_LEARNING] ⚠️ Error analyzing data from ${data.source}: ${error.message}`);
      }
    }
    
    // Remove duplicates and rank by relevance
    const uniqueInsights = this.deduplicateInsights(insights);
    const rankedInsights = this.rankInsightsByRelevance(uniqueInsights, proposal);
    
    return rankedInsights.slice(0, 10); // Return top 10 insights
  }
  
  /**
   * Extract insights from content
   */
  static extractInsightsFromContent(content, aiType, proposal) {
    const insights = [];
    
    // Extract code patterns (simple regex for code blocks)
    const codePatterns = content.match(/```[\s\S]*?```/g) || [];
    codePatterns.forEach(pattern => {
      insights.push({
        type: 'code_pattern',
        content: pattern,
        relevance: this.calculateRelevance(pattern, proposal),
        source: 'code_block'
      });
    });
    
    // Extract best practices
    const bestPractices = content.match(/(?:best practice|recommended|should|avoid|never|always)[^.!?]*[.!?]/gi) || [];
    bestPractices.forEach(practice => {
      insights.push({
        type: 'best_practice',
        content: practice.trim(),
        relevance: this.calculateRelevance(practice, proposal),
        source: 'text_analysis'
      });
    });
    
    // Extract error patterns
    const errorPatterns = content.match(/(?:error|bug|issue|problem|fail)[^.!?]*[.!?]/gi) || [];
    errorPatterns.forEach(error => {
      insights.push({
        type: 'error_pattern',
        content: error.trim(),
        relevance: this.calculateRelevance(error, proposal),
        source: 'text_analysis'
      });
    });
    
    return insights;
  }
  
  /**
   * Calculate relevance score for an insight
   */
  static calculateRelevance(content, proposal) {
    let score = 0;
    
    // Check for improvement type match
    if (proposal.improvementType && content.toLowerCase().includes(proposal.improvementType.toLowerCase())) {
      score += 3;
    }
    
    // Check for language match
    if (proposal.filePath?.includes('.dart') && content.toLowerCase().includes('dart')) {
      score += 2;
    }
    
    // Check for feedback reason match
    if (proposal.userFeedbackReason) {
      const reason = proposal.userFeedbackReason.toLowerCase();
      const reasonWords = reason.split(' ');
      reasonWords.forEach(word => {
        if (word.length > 3 && content.toLowerCase().includes(word)) {
          score += 1;
        }
      });
    }
    
    return score;
  }
  
  /**
   * Remove duplicate insights
   */
  static deduplicateInsights(insights) {
    const seen = new Set();
    return insights.filter(insight => {
      const key = insight.content.substring(0, 100).toLowerCase();
      if (seen.has(key)) {
        return false;
      }
      seen.add(key);
      return true;
    });
  }
  
  /**
   * Rank insights by relevance
   */
  static rankInsightsByRelevance(insights, proposal) {
    return insights.sort((a, b) => b.relevance - a.relevance);
  }
  
  /**
   * Generate learning recommendations
   */
  static async generateRecommendations(insights, aiType, proposal) {
    const recommendations = [];
    
    // Group insights by type
    const codePatterns = insights.filter(i => i.type === 'code_pattern');
    const bestPractices = insights.filter(i => i.type === 'best_practice');
    const errorPatterns = insights.filter(i => i.type === 'error_pattern');
    
    // Generate code improvement recommendations
    if (codePatterns.length > 0) {
      recommendations.push({
        type: 'code_improvement',
        priority: 'high',
        description: `Apply ${codePatterns.length} new code patterns from internet sources`,
        patterns: codePatterns.slice(0, 3)
      });
    }
    
    // Generate best practice recommendations
    if (bestPractices.length > 0) {
      recommendations.push({
        type: 'best_practice',
        priority: 'medium',
        description: `Incorporate ${bestPractices.length} best practices from community`,
        practices: bestPractices.slice(0, 3)
      });
    }
    
    // Generate error avoidance recommendations
    if (errorPatterns.length > 0) {
      recommendations.push({
        type: 'error_avoidance',
        priority: 'high',
        description: `Learn to avoid ${errorPatterns.length} common error patterns`,
        errors: errorPatterns.slice(0, 3)
      });
    }
    
    return recommendations;
  }
  
  /**
   * Store learning data for future reference
   */
  static async storeLearningData(aiType, proposal, insights, recommendations) {
    try {
      const Learning = require('../models/learning');
      
      // Store insights
      for (const insight of insights.slice(0, 5)) {
        await Learning.create({
          aiType,
          proposalId: proposal._id,
          status: 'learning-completed',
          feedbackReason: 'Internet learning insight',
          learningKey: `internet_${insight.type}`,
          learningValue: insight.content,
          filePath: proposal.filePath,
          improvementType: proposal.improvementType
        });
      }
      
      // Store recommendations
      for (const rec of recommendations) {
        await Learning.create({
          aiType,
          proposalId: proposal._id,
          status: 'learning-completed',
          feedbackReason: 'Internet learning recommendation',
          learningKey: `internet_recommendation_${rec.type}`,
          learningValue: rec.description,
          filePath: proposal.filePath,
          improvementType: proposal.improvementType
        });
      }
      
      console.log(`[INTERNET_LEARNING] 💾 Stored ${insights.length} insights and ${recommendations.length} recommendations for ${aiType}`);
      
    } catch (error) {
      console.error(`[INTERNET_LEARNING] ❌ Error storing learning data:`, error);
    }
  }
}

module.exports = InternetLearningService; 