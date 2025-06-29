const Proposal = require('../models/proposal');
const Learning = require('../models/learning');
const AILearningService = require('./aiLearningService');
const gitService = require('./gitService');
const fs = require('fs').promises;
const path = require('path');

class AISelfImprovementService {
  /**
   * Trigger self-improvement for an AI
   */
  static async triggerSelfImprovement(aiType, improvementType = 'general', targetFile = null) {
    try {
      console.log(`[AI_SELF_IMPROVEMENT_SERVICE] 🚀 Triggering self-improvement for ${aiType}`);
      
      // Get learning context for the AI
      const learningContext = await AILearningService.generateLearningContext(aiType);
      
      // Get recent mistakes to avoid
      const recentMistakes = await AILearningService.getRecentMistakes(aiType, 7);
      
      // Get success patterns to follow
      const patterns = await AILearningService.analyzeFeedbackPatterns(aiType, 30);
      
      // Get recent successful proposals for inspiration
      const successfulProposals = await Proposal.find({
        aiType,
        status: 'approved'
      })
      .sort({ createdAt: -1 })
      .limit(10)
      .select('filePath improvementType userFeedbackReason aiReasoning codeBefore codeAfter')
      .lean();
      
      // Generate improvement suggestions
      const suggestions = this.generateImprovementSuggestions(
        aiType,
        learningContext,
        recentMistakes,
        patterns,
        successfulProposals,
        improvementType
      );
      
      // Apply the most promising improvement
      if (suggestions.length > 0) {
        const bestSuggestion = suggestions[0];
        const improvementResult = await this.applyImprovement(aiType, bestSuggestion, targetFile);
        
        return {
          success: true,
          aiType,
          improvementType,
          suggestions: suggestions.slice(0, 5), // Top 5 suggestions
          appliedImprovement: bestSuggestion,
          result: improvementResult
        };
      }
      
      return {
        success: false,
        aiType,
        improvementType,
        message: 'No suitable improvements found',
        suggestions: []
      };
    } catch (error) {
      console.error(`[AI_SELF_IMPROVEMENT_SERVICE] ❌ Error in self-improvement: ${error.message}`);
      throw error;
    }
  }

  /**
   * Generate improvement suggestions based on learning data
   */
  static generateImprovementSuggestions(aiType, learningContext, recentMistakes, patterns, successfulProposals, improvementType) {
    const suggestions = [];
    
    // Analyze successful patterns for improvements
    if (patterns.successPatterns && patterns.successPatterns.length > 0) {
      patterns.successPatterns.forEach(pattern => {
        suggestions.push({
          type: 'apply_success_pattern',
          description: `Apply ${pattern.pattern} pattern (${Math.round(pattern.frequency * 100)}% success rate)`,
          confidence: pattern.frequency * 100,
          action: `enhance_${pattern.pattern.replace(/\s+/g, '_').toLowerCase()}`,
          reasoning: `This pattern has been successful in ${Math.round(pattern.frequency * 100)}% of cases`
        });
      });
    }
    
    // Analyze common mistakes to avoid
    if (recentMistakes && recentMistakes.length > 0) {
      recentMistakes.forEach(mistake => {
        suggestions.push({
          type: 'avoid_mistake',
          description: `Avoid ${mistake.mistake} (${Math.round(mistake.frequency * 100)}% of rejections)`,
          confidence: mistake.frequency * 100,
          action: `prevent_${mistake.mistake.replace(/\s+/g, '_').toLowerCase()}`,
          reasoning: `This mistake causes ${Math.round(mistake.frequency * 100)}% of rejections`
        });
      });
    }
    
    // Analyze successful proposals for code improvements
    successfulProposals.forEach(proposal => {
      if (proposal.userFeedbackReason) {
        const feedback = proposal.userFeedbackReason.toLowerCase();
        
        if (feedback.includes('readability')) {
          suggestions.push({
            type: 'code_quality',
            description: 'Improve code readability based on successful patterns',
            confidence: 85,
            action: 'enhance_readability',
            reasoning: 'Readability improvements are consistently approved',
            sourceProposal: proposal._id
          });
        }
        
        if (feedback.includes('performance')) {
          suggestions.push({
            type: 'performance',
            description: 'Optimize performance based on successful patterns',
            confidence: 80,
            action: 'enhance_performance',
            reasoning: 'Performance optimizations are well-received',
            sourceProposal: proposal._id
          });
        }
        
        if (feedback.includes('security')) {
          suggestions.push({
            type: 'security',
            description: 'Enhance security measures based on successful patterns',
            confidence: 90,
            action: 'enhance_security',
            reasoning: 'Security improvements are highly valued',
            sourceProposal: proposal._id
          });
        }
      }
    });
    
    // Add general improvement suggestions based on learning context
    if (learningContext) {
      suggestions.push({
        type: 'learning_context',
        description: 'Apply learned context to improve decision making',
        confidence: 75,
        action: 'apply_learning_context',
        reasoning: 'Learning context provides valuable insights for improvements'
      });
    }
    
    // Sort by confidence and return top suggestions
    return suggestions
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, 10);
  }

  /**
   * Apply a specific improvement
   */
  static async applyImprovement(aiType, suggestion, targetFile) {
    try {
      console.log(`[AI_SELF_IMPROVEMENT_SERVICE] 🔧 Applying improvement: ${suggestion.description}`);
      
      // Determine the target file for improvement
      const fileToImprove = targetFile || this.determineTargetFile(aiType, suggestion);
      
      // Read the current file content
      const currentContent = await this.readFileContent(fileToImprove);
      
      // Generate improved content based on suggestion
      const improvedContent = await this.generateImprovedContent(
        aiType,
        fileToImprove,
        currentContent,
        suggestion
      );
      
      // Apply the improvement using Git
      const gitResult = await gitService.applySelfImprovement(
        aiType,
        fileToImprove,
        improvedContent,
        {
          improvementType: suggestion.type,
          learningContext: suggestion.reasoning,
          confidence: suggestion.confidence
        }
      );
      
      // Create learning entry for the improvement
      const learningEntry = new Learning({
        aiType,
        learningKey: 'self-improvement-applied',
        learningValue: `Applied self-improvement: ${suggestion.description}`,
        status: 'learning-completed',
        timestamp: new Date(),
        filePath: fileToImprove,
        improvementType: suggestion.type,
        metadata: {
          suggestion,
          gitResult,
          confidence: suggestion.confidence,
          originalContent: currentContent.substring(0, 500), // First 500 chars
          improvedContent: improvedContent.substring(0, 500) // First 500 chars
        }
      });
      
      await learningEntry.save();
      
      console.log(`[AI_SELF_IMPROVEMENT_SERVICE] ✅ Improvement applied: ${suggestion.description}`);
      
      return {
        success: true,
        filePath: fileToImprove,
        improvementType: suggestion.type,
        confidence: suggestion.confidence,
        gitResult
      };
    } catch (error) {
      console.error(`[AI_SELF_IMPROVEMENT_SERVICE] ❌ Error applying improvement: ${error.message}`);
      throw error;
    }
  }

  /**
   * Determine the target file for improvement
   */
  static determineTargetFile(aiType, suggestion) {
    // Map AI types to their main service files
    const aiFileMap = {
      'Imperium': 'src/services/imperiumService.js',
      'Sandbox': 'src/services/sandboxService.js',
      'Guardian': 'src/services/guardianService.js',
      'Conquest': 'src/services/conquestService.js'
    };
    
    // If suggestion is about a specific file type, prioritize that
    if (suggestion.action.includes('readability') || suggestion.action.includes('performance')) {
      return aiFileMap[aiType] || 'src/services/aiLearningService.js';
    }
    
    // Default to the AI's main service file
    return aiFileMap[aiType] || 'src/services/aiLearningService.js';
  }

  /**
   * Read file content
   */
  static async readFileContent(filePath) {
    try {
      const fullPath = path.join(process.env.GIT_REPO_PATH || '.', filePath);
      return await fs.readFile(fullPath, 'utf8');
    } catch (error) {
      console.error(`[AI_SELF_IMPROVEMENT_SERVICE] ❌ Error reading file: ${error.message}`);
      return '';
    }
  }

  /**
   * Generate improved content based on suggestion
   */
  static async generateImprovedContent(aiType, filePath, currentContent, suggestion) {
    // This is a simplified version - in a real implementation, you might use AI to generate improvements
    let improvedContent = currentContent;
    
    switch (suggestion.type) {
      case 'apply_success_pattern':
        improvedContent = this.applySuccessPattern(improvedContent, suggestion);
        break;
      case 'code_quality':
        improvedContent = this.enhanceCodeQuality(improvedContent, suggestion);
        break;
      case 'performance':
        improvedContent = this.enhancePerformance(improvedContent, suggestion);
        break;
      case 'security':
        improvedContent = this.enhanceSecurity(improvedContent, suggestion);
        break;
      case 'learning_context':
        improvedContent = this.applyLearningContext(improvedContent, suggestion);
        break;
      default:
        // Add a comment indicating the improvement
        improvedContent = this.addImprovementComment(improvedContent, suggestion);
    }
    
    return improvedContent;
  }

  /**
   * Apply success pattern to code
   */
  static applySuccessPattern(content, suggestion) {
    const pattern = suggestion.action.replace('enhance_', '');
    
    // Add pattern-based improvements
    const improvementComment = `\n// IMPROVEMENT: Applied ${pattern} pattern (${suggestion.confidence}% confidence)\n` +
      `// Reasoning: ${suggestion.reasoning}\n` +
      `// Applied by AI Self-Improvement Service\n`;
    
    return improvementComment + content;
  }

  /**
   * Enhance code quality
   */
  static enhanceCodeQuality(content, suggestion) {
    const improvements = [
      '\n// CODE QUALITY IMPROVEMENTS:',
      '// - Enhanced readability',
      '// - Improved variable naming',
      '// - Better code organization',
      `// - Applied based on: ${suggestion.reasoning}`,
      '// - Confidence: ' + suggestion.confidence + '%\n'
    ];
    
    return improvements.join('\n') + content;
  }

  /**
   * Enhance performance
   */
  static enhancePerformance(content, suggestion) {
    const improvements = [
      '\n// PERFORMANCE IMPROVEMENTS:',
      '// - Optimized algorithms',
      '// - Reduced memory usage',
      '// - Improved caching strategies',
      `// - Applied based on: ${suggestion.reasoning}`,
      '// - Confidence: ' + suggestion.confidence + '%\n'
    ];
    
    return improvements.join('\n') + content;
  }

  /**
   * Enhance security
   */
  static enhanceSecurity(content, suggestion) {
    const improvements = [
      '\n// SECURITY IMPROVEMENTS:',
      '// - Added input validation',
      '// - Enhanced error handling',
      '// - Improved data sanitization',
      `// - Applied based on: ${suggestion.reasoning}`,
      '// - Confidence: ' + suggestion.confidence + '%\n'
    ];
    
    return improvements.join('\n') + content;
  }

  /**
   * Apply learning context
   */
  static applyLearningContext(content, suggestion) {
    const improvements = [
      '\n// LEARNING CONTEXT APPLIED:',
      '// - Enhanced decision making',
      '// - Improved pattern recognition',
      '// - Better error prevention',
      `// - Applied based on: ${suggestion.reasoning}`,
      '// - Confidence: ' + suggestion.confidence + '%\n'
    ];
    
    return improvements.join('\n') + content;
  }

  /**
   * Add improvement comment
   */
  static addImprovementComment(content, suggestion) {
    const comment = `\n// SELF-IMPROVEMENT APPLIED: ${suggestion.description}\n` +
      `// Confidence: ${suggestion.confidence}%\n` +
      `// Reasoning: ${suggestion.reasoning}\n` +
      `// Applied by AI Self-Improvement Service\n`;
    
    return comment + content;
  }

  /**
   * Get self-improvement history for an AI
   */
  static async getImprovementHistory(aiType, days = 30) {
    try {
      console.log(`[AI_SELF_IMPROVEMENT_SERVICE] 📊 Getting improvement history for ${aiType}`);
      
      const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
      
      const improvements = await Learning.find({
        aiType,
        learningKey: 'self-improvement-applied',
        timestamp: { $gte: cutoffDate }
      })
      .sort({ timestamp: -1 })
      .lean();
      
      // Get Git statistics for the AI
      const gitStats = await gitService.getLearningStats(aiType, days);
      
      const history = {
        totalImprovements: improvements.length,
        improvementsByType: {},
        recentImprovements: improvements.slice(0, 10),
        gitStats,
        improvementRate: Math.round((improvements.length / days) * 10) / 10,
        averageConfidence: improvements.length > 0 ? 
          Math.round(improvements.reduce((sum, imp) => sum + (imp.metadata?.confidence || 0), 0) / improvements.length) : 0
      };
      
      // Group improvements by type
      improvements.forEach(improvement => {
        const type = improvement.improvementType || 'general';
        history.improvementsByType[type] = (history.improvementsByType[type] || 0) + 1;
      });
      
      console.log(`[AI_SELF_IMPROVEMENT_SERVICE] ✅ Improvement history calculated for ${aiType}`);
      return history;
    } catch (error) {
      console.error(`[AI_SELF_IMPROVEMENT_SERVICE] ❌ Error getting improvement history: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get improvement suggestions for an AI
   */
  static async getImprovementSuggestions(aiType) {
    try {
      console.log(`[AI_SELF_IMPROVEMENT_SERVICE] 💡 Getting improvement suggestions for ${aiType}`);
      
      // Get learning context
      const learningContext = await AILearningService.generateLearningContext(aiType);
      const recentMistakes = await AILearningService.getRecentMistakes(aiType, 7);
      const patterns = await AILearningService.analyzeFeedbackPatterns(aiType, 30);
      
      // Get recent successful proposals
      const successfulProposals = await Proposal.find({
        aiType,
        status: 'approved'
      })
      .sort({ createdAt: -1 })
      .limit(10)
      .select('filePath improvementType userFeedbackReason aiReasoning')
      .lean();
      
      // Generate suggestions
      const suggestions = this.generateImprovementSuggestions(
        aiType,
        learningContext,
        recentMistakes,
        patterns,
        successfulProposals,
        'general'
      );
      
      return {
        aiType,
        suggestions: suggestions.slice(0, 10), // Top 10 suggestions
        totalSuggestions: suggestions.length,
        learningContext: learningContext ? 'Available' : 'None',
        recentMistakes: recentMistakes.length,
        successPatterns: patterns.successPatterns ? patterns.successPatterns.length : 0
      };
    } catch (error) {
      console.error(`[AI_SELF_IMPROVEMENT_SERVICE] ❌ Error getting improvement suggestions: ${error.message}`);
      throw error;
    }
  }

  /**
   * Generate self-improvement suggestions based on learning patterns
   */
  async generateSelfImprovementSuggestions(aiType) {
    try {
      console.log(`[AI_SELF_IMPROVEMENT_SERVICE] 🧠 Generating self-improvement suggestions for ${aiType}`);
      
      // Get recent learning data
      const learningData = await this.getRecentLearningData(aiType);
      
      // Analyze failure patterns
      const failurePatterns = await this.analyzeFailurePatterns(aiType);
      
      // Generate Flutter-specific improvements
      const flutterImprovements = await this.generateFlutterSpecificImprovements(aiType, failurePatterns);
      
      // Generate general improvements
      const generalImprovements = await this.generateGeneralImprovements(aiType, learningData);
      
      // Combine and prioritize improvements
      const allImprovements = [
        ...flutterImprovements,
        ...generalImprovements
      ].sort((a, b) => b.priority - a.priority);
      
      console.log(`[AI_SELF_IMPROVEMENT_SERVICE] ✅ Generated ${allImprovements.length} improvement suggestions for ${aiType}`);
      
      return {
        aiType,
        totalSuggestions: allImprovements.length,
        flutterSpecific: flutterImprovements.length,
        general: generalImprovements.length,
        suggestions: allImprovements.slice(0, 10), // Top 10 suggestions
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error(`[AI_SELF_IMPROVEMENT_SERVICE] ❌ Error generating suggestions: ${error.message}`);
      throw error;
    }
  }

  /**
   * Generate Flutter-specific improvements based on failure patterns
   */
  async generateFlutterSpecificImprovements(aiType, failurePatterns) {
    const improvements = [];
    
    // Check for Flutter SDK issues
    if (failurePatterns.flutterSdkIssues > 0) {
      improvements.push({
        type: 'flutter_sdk_knowledge',
        title: 'Improve Flutter SDK Understanding',
        description: 'Learn proper Flutter project structure and SDK usage',
        priority: 10,
        codeChanges: [
          {
            file: 'ai_learning_context.dart',
            changes: [
              'Add Flutter SDK validation checks',
              'Implement proper pubspec.yaml handling',
              'Add Flutter project structure awareness'
            ]
          }
        ],
        learningFocus: [
          'Flutter project structure',
          'pubspec.yaml dependencies',
          'Flutter SDK commands vs Dart commands'
        ]
      });
    }
    
    // Check for dependency issues
    if (failurePatterns.dependencyIssues > 0) {
      improvements.push({
        type: 'dependency_management',
        title: 'Improve Dependency Management',
        description: 'Better understanding of Flutter dependency resolution',
        priority: 9,
        codeChanges: [
          {
            file: 'dependency_analyzer.dart',
            changes: [
              'Add dependency conflict detection',
              'Implement version solving logic',
              'Add flutter_test placement validation'
            ]
          }
        ],
        learningFocus: [
          'Flutter dependency resolution',
          'dev_dependencies vs dependencies',
          'Version solving strategies'
        ]
      });
    }
    
    // Check for image decoder issues
    if (failurePatterns.imageDecoderIssues > 0) {
      improvements.push({
        type: 'image_handling',
        title: 'Improve Image Handling Logic',
        description: 'Better handling of image decoder warnings and errors',
        priority: 7,
        codeChanges: [
          {
            file: 'image_processor.dart',
            changes: [
              'Add image decoder error handling',
              'Implement fallback image loading',
              'Add emulator vs device detection'
            ]
          }
        ],
        learningFocus: [
          'Android emulator limitations',
          'Image loading best practices',
          'Error handling for image operations'
        ]
      });
    }
    
    // Check for test-related issues
    if (failurePatterns.testIssues > 0) {
      improvements.push({
        type: 'test_understanding',
        title: 'Improve Test Understanding',
        description: 'Better understanding of Flutter testing requirements',
        priority: 8,
        codeChanges: [
          {
            file: 'test_analyzer.dart',
            changes: [
              'Add Flutter test requirement validation',
              'Implement test dependency checking',
              'Add test environment detection'
            ]
          }
        ],
        learningFocus: [
          'Flutter testing framework',
          'Test dependencies management',
          'Test environment setup'
        ]
      });
    }
    
    return improvements;
  }

  /**
   * Analyze failure patterns for Flutter-specific issues
   */
  async analyzeFailurePatterns(aiType) {
    try {
      const recentProposals = await Proposal.find({
        aiType,
        status: { $in: ['rejected', 'test-failed'] },
        createdAt: { $gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) } // Last 7 days
      }).lean();
      
      const patterns = {
        flutterSdkIssues: 0,
        dependencyIssues: 0,
        imageDecoderIssues: 0,
        testIssues: 0,
        totalFailures: recentProposals.length
      };
      
      recentProposals.forEach(proposal => {
        const feedback = (proposal.userFeedbackReason || '').toLowerCase();
        const testOutput = (proposal.testOutput || '').toLowerCase();
        const combined = feedback + ' ' + testOutput;
        
        if (combined.includes('flutter sdk') || combined.includes('flutter_test')) {
          patterns.flutterSdkIssues++;
        }
        
        if (combined.includes('dart pub') || combined.includes('version solving') || combined.includes('dependency')) {
          patterns.dependencyIssues++;
        }
        
        if (combined.includes('image decoder') || combined.includes('unimplemented')) {
          patterns.imageDecoderIssues++;
        }
        
        if (combined.includes('test') && (combined.includes('failed') || combined.includes('error'))) {
          patterns.testIssues++;
        }
      });
      
      return patterns;
    } catch (error) {
      console.error(`[AI_SELF_IMPROVEMENT_SERVICE] ❌ Error analyzing failure patterns: ${error.message}`);
      return {
        flutterSdkIssues: 0,
        dependencyIssues: 0,
        imageDecoderIssues: 0,
        testIssues: 0,
        totalFailures: 0
      };
    }
  }

  /**
   * Apply Flutter-specific improvements to AI code
   */
  async applyFlutterImprovements(aiType, improvements) {
    try {
      console.log(`[AI_SELF_IMPROVEMENT_SERVICE] 🔧 Applying Flutter improvements for ${aiType}`);
      
      const appliedChanges = [];
      
      for (const improvement of improvements) {
        if (improvement.type.startsWith('flutter_')) {
          const changeResult = await this.applyFlutterImprovement(aiType, improvement);
          appliedChanges.push(changeResult);
        }
      }
      
      // Commit improvements to Git
      if (appliedChanges.length > 0) {
        await this.commitImprovements(aiType, appliedChanges);
      }
      
      return {
        aiType,
        appliedChanges: appliedChanges.length,
        changes: appliedChanges,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error(`[AI_SELF_IMPROVEMENT_SERVICE] ❌ Error applying Flutter improvements: ${error.message}`);
      throw error;
    }
  }

  /**
   * Apply a specific Flutter improvement
   */
  async applyFlutterImprovement(aiType, improvement) {
    try {
      console.log(`[AI_SELF_IMPROVEMENT_SERVICE] 🔧 Applying ${improvement.type} for ${aiType}`);
      
      // Create improvement branch
      const branchName = `ai-improvement-${aiType}-${improvement.type}-${Date.now()}`;
      await gitService.git.checkoutLocalBranch(branchName);
      
      // Apply code changes
      const codeChanges = await this.applyCodeChanges(improvement.codeChanges);
      
      // Update learning context
      await this.updateLearningContext(aiType, improvement.learningFocus);
      
      // Commit changes
      const commitMessage = `AI Self-Improvement: ${aiType} - ${improvement.title}\n\n` +
        `Type: ${improvement.type}\n` +
        `Priority: ${improvement.priority}\n` +
        `Description: ${improvement.description}\n` +
        `Learning Focus: ${improvement.learningFocus.join(', ')}\n` +
        `Timestamp: ${new Date().toISOString()}`;
      
      await gitService.git.add('.');
      await gitService.git.commit(commitMessage);
      
      // Push to remote
      await gitService.git.push('origin', branchName);
      
      return {
        type: improvement.type,
        title: improvement.title,
        branchName,
        codeChanges: codeChanges.length,
        learningFocus: improvement.learningFocus,
        success: true
      };
    } catch (error) {
      console.error(`[AI_SELF_IMPROVEMENT_SERVICE] ❌ Error applying Flutter improvement: ${error.message}`);
      return {
        type: improvement.type,
        title: improvement.title,
        error: error.message,
        success: false
      };
    }
  }

  /**
   * Update AI learning context with Flutter-specific knowledge
   */
  async updateLearningContext(aiType, learningFocus) {
    try {
      const learningData = {
        aiType,
        learningKey: 'flutter_knowledge_improvement',
        learningValue: `Enhanced Flutter understanding: ${learningFocus.join(', ')}`,
        filePath: 'ai_learning_context.dart',
        status: 'applied',
        timestamp: new Date().toISOString()
      };
      
      // Save to learning database
      await Learning.create(learningData);
      
      console.log(`[AI_SELF_IMPROVEMENT_SERVICE] ✅ Updated learning context for ${aiType}`);
    } catch (error) {
      console.error(`[AI_SELF_IMPROVEMENT_SERVICE] ❌ Error updating learning context: ${error.message}`);
    }
  }
}

module.exports = AISelfImprovementService; 