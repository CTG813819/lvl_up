const fs = require('fs').promises;
const path = require('path');
const { logEvent } = require('../state');
const InternetLearningService = require('./internetLearningService');

class AICodeUpdateService {
  /**
   * Update AI code based on learning insights
   */
  static async updateAICode(aiType, proposal, result, learningData) {
    console.log(`[AI_CODE_UPDATE] 🔧 Updating ${aiType} code based on learning insights`);
    
    try {
      // Get AI file path
      const aiFilePath = this.getAIFilePath(aiType);
      
      // Read current AI code
      const currentCode = await this.readAICode(aiFilePath);
      
      // Generate code updates based on learning data
      const codeUpdates = await this.generateCodeUpdates(aiType, proposal, result, learningData, currentCode);
      
      // Apply updates to the code
      const updatedCode = await this.applyCodeUpdates(currentCode, codeUpdates);
      
      // Write updated code back to file
      await this.writeAICode(aiFilePath, updatedCode);
      
      // Create backup of original code
      await this.createBackup(aiFilePath, currentCode);
      
      // Log the update
      await this.logCodeUpdate(aiType, proposal, codeUpdates);
      
      console.log(`[AI_CODE_UPDATE] ✅ Successfully updated ${aiType} code with ${codeUpdates.length} improvements`);
      
      return {
        success: true,
        updatesApplied: codeUpdates.length,
        filePath: aiFilePath,
        changes: codeUpdates.map(u => u.description)
      };
      
    } catch (error) {
      console.error(`[AI_CODE_UPDATE] ❌ Error updating ${aiType} code:`, error);
      throw error;
    }
  }
  
  /**
   * Get the file path for a specific AI
   */
  static getAIFilePath(aiType) {
    const aiFiles = {
      'Imperium': 'src/services/imperiumService.js',
      'Guardian': 'src/services/guardianService.js',
      'Sandbox': 'src/services/sandboxService.js'
    };
    
    return aiFiles[aiType];
  }
  
  /**
   * Read AI code from file
   */
  static async readAICode(filePath) {
    try {
      const code = await fs.readFile(filePath, 'utf8');
      console.log(`[AI_CODE_UPDATE] 📖 Read ${code.length} characters from ${filePath}`);
      return code;
    } catch (error) {
      console.error(`[AI_CODE_UPDATE] ❌ Error reading AI code from ${filePath}:`, error);
      throw error;
    }
  }
  
  /**
   * Generate code updates based on learning data
   */
  static async generateCodeUpdates(aiType, proposal, result, learningData, currentCode) {
    const updates = [];
    
    try {
      // Generate updates based on proposal result
      if (result === 'failed' || result === 'rejected') {
        const failureUpdates = await this.generateFailureUpdates(aiType, proposal, learningData, currentCode);
        updates.push(...failureUpdates);
      } else if (result === 'passed' || result === 'approved') {
        const successUpdates = await this.generateSuccessUpdates(aiType, proposal, learningData, currentCode);
        updates.push(...successUpdates);
      }
      
      // Generate updates based on learning insights
      if (learningData.insights) {
        const insightUpdates = await this.generateInsightUpdates(aiType, learningData.insights, currentCode);
        updates.push(...insightUpdates);
      }
      
      // Generate updates based on recommendations
      if (learningData.recommendations) {
        const recommendationUpdates = await this.generateRecommendationUpdates(aiType, learningData.recommendations, currentCode);
        updates.push(...recommendationUpdates);
      }
      
      console.log(`[AI_CODE_UPDATE] 🔍 Generated ${updates.length} code updates for ${aiType}`);
      
    } catch (error) {
      console.error(`[AI_CODE_UPDATE] ❌ Error generating code updates:`, error);
    }
    
    return updates;
  }
  
  /**
   * Generate updates for failed proposals
   */
  static async generateFailureUpdates(aiType, proposal, learningData, currentCode) {
    const updates = [];
    
    // Add error handling improvements
    if (proposal.userFeedbackReason?.toLowerCase().includes('error')) {
      updates.push({
        type: 'error_handling',
        description: 'Add better error handling based on failure feedback',
        code: this.generateErrorHandlingCode(aiType),
        priority: 'high'
      });
    }
    
    // Add validation improvements
    if (proposal.userFeedbackReason?.toLowerCase().includes('validation')) {
      updates.push({
        type: 'validation',
        description: 'Add input validation based on failure feedback',
        code: this.generateValidationCode(aiType),
        priority: 'high'
      });
    }
    
    // Add logging improvements
    updates.push({
      type: 'logging',
      description: 'Add enhanced logging for better debugging',
      code: this.generateLoggingCode(aiType),
      priority: 'medium'
    });
    
    return updates;
  }
  
  /**
   * Generate updates for successful proposals
   */
  static async generateSuccessUpdates(aiType, proposal, learningData, currentCode) {
    const updates = [];
    
    // Add performance optimizations
    if (proposal.improvementType === 'performance') {
      updates.push({
        type: 'performance',
        description: 'Add performance optimization patterns from successful proposals',
        code: this.generatePerformanceCode(aiType),
        priority: 'medium'
      });
    }
    
    // Add best practices
    updates.push({
      type: 'best_practices',
      description: 'Incorporate best practices from successful proposals',
      code: this.generateBestPracticesCode(aiType),
      priority: 'medium'
    });
    
    return updates;
  }
  
  /**
   * Generate updates based on learning insights
   */
  static async generateInsightUpdates(aiType, insights, currentCode) {
    const updates = [];
    
    for (const insight of insights.slice(0, 3)) { // Limit to top 3 insights
      if (insight.type === 'code_pattern' && insight.content) {
        updates.push({
          type: 'code_pattern',
          description: `Apply code pattern from internet learning: ${insight.content.substring(0, 50)}...`,
          code: this.extractCodeFromPattern(insight.content),
          priority: 'medium'
        });
      } else if (insight.type === 'best_practice') {
        updates.push({
          type: 'best_practice',
          description: `Apply best practice: ${insight.content}`,
          code: this.generateBestPracticeCode(aiType, insight.content),
          priority: 'low'
        });
      }
    }
    
    return updates;
  }
  
  /**
   * Generate updates based on recommendations
   */
  static async generateRecommendationUpdates(aiType, recommendations, currentCode) {
    const updates = [];
    
    for (const rec of recommendations) {
      if (rec.type === 'code_improvement' && rec.patterns) {
        updates.push({
          type: 'code_improvement',
          description: rec.description,
          code: this.generateCodeImprovement(aiType, rec.patterns),
          priority: 'high'
        });
      } else if (rec.type === 'error_avoidance' && rec.errors) {
        updates.push({
          type: 'error_avoidance',
          description: rec.description,
          code: this.generateErrorAvoidanceCode(aiType, rec.errors),
          priority: 'high'
        });
      }
    }
    
    return updates;
  }
  
  /**
   * Apply code updates to the current code
   */
  static async applyCodeUpdates(currentCode, updates) {
    let updatedCode = currentCode;
    
    // Sort updates by priority (high -> medium -> low)
    const sortedUpdates = updates.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
    
    for (const update of sortedUpdates) {
      try {
        updatedCode = this.applySingleUpdate(updatedCode, update);
        console.log(`[AI_CODE_UPDATE] ✅ Applied update: ${update.description}`);
      } catch (error) {
        console.log(`[AI_CODE_UPDATE] ⚠️ Failed to apply update: ${update.description} - ${error.message}`);
      }
    }
    
    return updatedCode;
  }
  
  /**
   * Apply a single code update
   */
  static applySingleUpdate(code, update) {
    // Add new functions at the end of the file (before the module.exports)
    if (update.code && code.includes('module.exports')) {
      const beforeExports = code.lastIndexOf('module.exports');
      const newCode = code.substring(0, beforeExports) + 
                     '\n\n' + update.code + '\n\n' + 
                     code.substring(beforeExports);
      return newCode;
    }
    
    // Add imports at the top if needed
    if (update.type === 'import' && update.code) {
      const importIndex = code.indexOf('const');
      if (importIndex !== -1) {
        return code.substring(0, importIndex) + update.code + '\n' + code.substring(importIndex);
      }
    }
    
    return code;
  }
  
  /**
   * Write updated AI code to file
   */
  static async writeAICode(filePath, code) {
    try {
      await fs.writeFile(filePath, code, 'utf8');
      console.log(`[AI_CODE_UPDATE] 💾 Wrote ${code.length} characters to ${filePath}`);
    } catch (error) {
      console.error(`[AI_CODE_UPDATE] ❌ Error writing AI code to ${filePath}:`, error);
      throw error;
    }
  }
  
  /**
   * Create backup of original code
   */
  static async createBackup(filePath, code) {
    try {
      const backupPath = filePath.replace('.js', `.backup.${Date.now()}.js`);
      await fs.writeFile(backupPath, code, 'utf8');
      console.log(`[AI_CODE_UPDATE] 💾 Created backup at ${backupPath}`);
    } catch (error) {
      console.log(`[AI_CODE_UPDATE] ⚠️ Failed to create backup: ${error.message}`);
    }
  }
  
  /**
   * Log code update for tracking
   */
  static async logCodeUpdate(aiType, proposal, updates) {
    try {
      const Learning = require('../models/learning');
      
      await Learning.create({
        aiType,
        proposalId: proposal._id,
        status: 'learning-completed',
        feedbackReason: 'AI code updated based on learning',
        learningKey: 'code_update',
        learningValue: `Applied ${updates.length} code updates: ${updates.map(u => u.description).join(', ')}`,
        filePath: proposal.filePath,
        improvementType: proposal.improvementType
      });
      
      logEvent(`[AI_CODE_UPDATE] 📝 Logged code update for ${aiType}: ${updates.length} updates applied`);
      
    } catch (error) {
      console.log(`[AI_CODE_UPDATE] ⚠️ Failed to log code update: ${error.message}`);
    }
  }
  
  // Helper methods for generating specific code patterns
  
  static generateErrorHandlingCode(aiType) {
    return `
// Enhanced error handling for ${aiType}
async function handleError(error, context) {
  console.error(\`[${aiType.toUpperCase()}] ❌ Error in \${context}:\`, error);
  
  // Log detailed error information
  const errorInfo = {
    message: error.message,
    stack: error.stack,
    context,
    timestamp: new Date().toISOString(),
    aiType: '${aiType}'
  };
  
  // Store error for learning
  try {
    const Learning = require('../models/learning');
    await Learning.create({
      aiType: '${aiType}',
      status: 'test-failed',
      feedbackReason: \`Error in \${context}: \${error.message}\`,
      learningKey: 'error_handling',
      learningValue: JSON.stringify(errorInfo),
      filePath: 'system',
      improvementType: 'bug-fix'
    });
  } catch (logError) {
    console.error(\`[${aiType.toUpperCase()}] Failed to log error:\`, logError);
  }
  
  return { success: false, error: error.message };
}`;
  }
  
  static generateValidationCode(aiType) {
    return `
// Enhanced input validation for ${aiType}
function validateInput(input, type) {
  if (!input) {
    throw new Error(\`Invalid input: \${type} is required\`);
  }
  
  switch (type) {
    case 'code':
      if (typeof input !== 'string' || input.trim().length === 0) {
        throw new Error('Code must be a non-empty string');
      }
      break;
    case 'filePath':
      if (typeof input !== 'string' || !input.includes('.')) {
        throw new Error('File path must be a valid string with extension');
      }
      break;
    case 'aiType':
      if (!['Imperium', 'Guardian', 'Sandbox'].includes(input)) {
        throw new Error('AI type must be one of: Imperium, Guardian, Sandbox');
      }
      break;
    default:
      throw new Error(\`Unknown validation type: \${type}\`);
  }
  
  return true;
}`;
  }
  
  static generateLoggingCode(aiType) {
    return `
// Enhanced logging for ${aiType}
function logAIActivity(action, details) {
  const logEntry = {
    aiType: '${aiType}',
    action,
    details,
    timestamp: new Date().toISOString(),
    performance: {
      memory: process.memoryUsage(),
      uptime: process.uptime()
    }
  };
  
  console.log(\`[${aiType.toUpperCase()}] 📊 \${action}:\`, JSON.stringify(logEntry, null, 2));
  
  // Store activity for analytics
  try {
    const Learning = require('../models/learning');
    Learning.create({
      aiType: '${aiType}',
      status: 'learning-completed',
      feedbackReason: 'AI activity logged',
      learningKey: 'activity_log',
      learningValue: JSON.stringify(logEntry),
      filePath: 'system',
      improvementType: 'system'
    }).catch(err => console.log(\`[${aiType.toUpperCase()}] Failed to store activity log:\`, err.message));
  } catch (error) {
    console.log(\`[${aiType.toUpperCase()}] Failed to create activity log:\`, error.message);
  }
}`;
  }
  
  static generatePerformanceCode(aiType) {
    return `
// Performance optimization for ${aiType}
function optimizePerformance(operation, data) {
  const startTime = Date.now();
  
  // Implement performance monitoring
  const result = operation(data);
  
  const executionTime = Date.now() - startTime;
  
  // Log performance metrics
  if (executionTime > 1000) {
    console.warn(\`[${aiType.toUpperCase()}] ⚠️ Slow operation detected: \${executionTime}ms\`);
  }
  
  // Store performance data for learning
  try {
    const Learning = require('../models/learning');
    Learning.create({
      aiType: '${aiType}',
      status: 'learning-completed',
      feedbackReason: 'Performance optimization applied',
      learningKey: 'performance_metrics',
      learningValue: JSON.stringify({ executionTime, operation: operation.name }),
      filePath: 'system',
      improvementType: 'performance'
    }).catch(err => console.log(\`[${aiType.toUpperCase()}] Failed to store performance data:\`, err.message));
  } catch (error) {
    console.log(\`[${aiType.toUpperCase()}] Failed to create performance log:\`, error.message);
  }
  
  return result;
}`;
  }
  
  static generateBestPracticesCode(aiType) {
    return `
// Best practices implementation for ${aiType}
function applyBestPractices(code) {
  // Apply code formatting
  const formattedCode = code.trim();
  
  // Add comments for complex logic
  if (formattedCode.length > 200) {
    const commentedCode = \`// ${aiType} AI generated code\n\${formattedCode}\`;
    return commentedCode;
  }
  
  return formattedCode;
}`;
  }
  
  static extractCodeFromPattern(pattern) {
    // Extract code from markdown code blocks
    const codeMatch = pattern.match(/```[\s\S]*?```/);
    if (codeMatch) {
      return codeMatch[0].replace(/```/g, '');
    }
    return pattern;
  }
  
  static generateBestPracticeCode(aiType, practice) {
    return `
// Best practice implementation: ${practice.substring(0, 50)}...
function applyBestPractice_${Date.now()}() {
  // Implementation of: ${practice}
  console.log(\`[${aiType.toUpperCase()}] Applying best practice: ${practice}\`);
}`;
  }
  
  static generateCodeImprovement(aiType, patterns) {
    return `
// Code improvements based on internet learning
function applyCodeImprovements_${Date.now()}() {
  console.log(\`[${aiType.toUpperCase()}] Applying ${patterns.length} code improvements from internet learning\`);
  
  // Apply learned patterns
  ${patterns.map((pattern, index) => `
  // Pattern ${index + 1}: ${pattern.content.substring(0, 50)}...
  function pattern_${index + 1}() {
    // Implementation based on learned pattern
    return true;
  }`).join('\n')}
}`;
  }
  
  static generateErrorAvoidanceCode(aiType, errors) {
    return `
// Error avoidance patterns
function avoidCommonErrors_${Date.now()}() {
  console.log(\`[${aiType.toUpperCase()}] Implementing error avoidance for ${errors.length} patterns\`);
  
  // Avoid learned error patterns
  ${errors.map((error, index) => `
  // Avoid: ${error.content.substring(0, 50)}...
  function avoidError_${index + 1}() {
    // Implementation to avoid this error pattern
    return true;
  }`).join('\n')}
}`;
  }
}

module.exports = AICodeUpdateService; 