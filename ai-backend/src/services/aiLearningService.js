const Proposal = require('../models/proposal');
const Experiment = require('../models/experiment');
const Learning = require('../models/learning');
const { logEvent } = require('../state');

class AILearningService {
  /**
   * Analyze user feedback patterns
   */
  static async analyzeFeedbackPatterns(aiType, days = 30) {
    const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
    
    const feedback = await Proposal.find({
      aiType,
      userFeedback: { $in: ['approved', 'rejected'] },
      createdAt: { $gte: cutoffDate }
    }).select('userFeedback userFeedbackReason improvementType filePath');
    
    const patterns = {
      approved: [],
      rejected: [],
      commonMistakes: [],
      successPatterns: []
    };
    
    // Analyze approved proposals
    const approved = feedback.filter(p => p.userFeedback === 'approved');
    patterns.approved = this.extractPatterns(approved);
    
    // Analyze rejected proposals
    const rejected = feedback.filter(p => p.userFeedback === 'rejected');
    patterns.rejected = this.extractPatterns(rejected);
    
    // Identify common mistakes
    patterns.commonMistakes = this.identifyCommonMistakes(aiType);
    
    // Identify success patterns
    patterns.successPatterns = this.identifySuccessPatterns(approved);
    
    return patterns;
  }

  /**
   * Extract patterns from proposals
   */
  static extractPatterns(proposals) {
    const patterns = {
      improvementTypes: {},
      fileTypes: {},
      reasons: {}
    };
    
    proposals.forEach(proposal => {
      // Count improvement types
      if (proposal.improvementType) {
        patterns.improvementTypes[proposal.improvementType] = 
          (patterns.improvementTypes[proposal.improvementType] || 0) + 1;
      }
      
      // Count file types
      const fileExt = proposal.filePath.split('.').pop();
      patterns.fileTypes[fileExt] = (patterns.fileTypes[fileExt] || 0) + 1;
      
      // Count reasons
      if (proposal.userFeedbackReason) {
        const reason = proposal.userFeedbackReason.toLowerCase();
        patterns.reasons[reason] = (patterns.reasons[reason] || 0) + 1;
      }
    });
    
    return patterns;
  }

  /**
   * Identify common mistakes from rejected proposals
   */
  static async identifyCommonMistakes(aiType) {
    try {
      const rejectedProposals = await Proposal.find({ 
        aiType, 
        status: { $in: ['rejected', 'test-failed'] },
        userFeedbackReason: { $exists: true, $ne: '' }
      }).sort({ timestamp: -1 }).limit(50);
      
      const mistakeCounts = {};
      const flutterSpecificMistakes = {};
      
      rejectedProposals.forEach(proposal => {
        if (proposal.userFeedbackReason) {
          const reason = proposal.userFeedbackReason.toLowerCase();
          const testOutput = proposal.testOutput ? proposal.testOutput.toLowerCase() : '';
          
          // Flutter/Dart specific mistake patterns
          if (reason.includes('flutter sdk') || testOutput.includes('flutter sdk')) {
            flutterSpecificMistakes['flutter_sdk_issue'] = (flutterSpecificMistakes['flutter_sdk_issue'] || 0) + 1;
          }
          
          if (reason.includes('dart pub') || testOutput.includes('dart pub')) {
            flutterSpecificMistakes['dart_pub_usage'] = (flutterSpecificMistakes['dart_pub_usage'] || 0) + 1;
          }
          
          if (reason.includes('flutter_test') || testOutput.includes('flutter_test')) {
            flutterSpecificMistakes['flutter_test_dependency'] = (flutterSpecificMistakes['flutter_test_dependency'] || 0) + 1;
          }
          
          if (reason.includes('image decoder') || testOutput.includes('image decoder')) {
            flutterSpecificMistakes['image_decoder_issue'] = (flutterSpecificMistakes['image_decoder_issue'] || 0) + 1;
          }
          
          if (reason.includes('version solving') || testOutput.includes('version solving')) {
            flutterSpecificMistakes['version_solving_failed'] = (flutterSpecificMistakes['version_solving_failed'] || 0) + 1;
          }
          
          // Extract key phrases that indicate mistakes
          const mistakePhrases = [
            'already exists', 'duplicate', 'unnecessary', 'not needed',
            'breaks functionality', 'doesn\'t work', 'error', 'bug',
            'too complex', 'over-engineered', 'performance issue',
            'readability', 'style', 'formatting',
            // Test failure patterns
            'test failed', 'tests failed', 'compilation error', 'syntax error',
            'import error', 'undefined', 'null safety', 'type error',
            'build failed', 'compile error', 'runtime error'
          ];
          
          mistakePhrases.forEach(phrase => {
            if (reason.includes(phrase)) {
              mistakeCounts[phrase] = (mistakeCounts[phrase] || 0) + 1;
            }
          });
        }
      });
      
      // Convert to array and sort by frequency
      const generalMistakes = Object.entries(mistakeCounts)
        .map(([mistake, count]) => ({ mistake, count, frequency: count / rejectedProposals.length }))
        .sort((a, b) => b.count - a.count);
      
      // Convert Flutter-specific mistakes to array
      const flutterMistakes = Object.entries(flutterSpecificMistakes)
        .map(([mistake, count]) => ({ 
          mistake, 
          count, 
          frequency: count / rejectedProposals.length,
          type: 'flutter_specific',
          solution: this.getFlutterMistakeSolution(mistake)
        }))
        .sort((a, b) => b.count - a.count);
      
      return [...flutterMistakes, ...generalMistakes];
    } catch (error) {
      console.error('[AI_LEARNING_SERVICE] Error identifying common mistakes:', error);
      return [];
    }
  }

  /**
   * Get specific solutions for Flutter/Dart mistakes
   */
  static getFlutterMistakeSolution(mistakeType) {
    const solutions = {
      'flutter_sdk_issue': 'Ensure Flutter SDK is properly installed and in PATH. Use `flutter doctor` to verify installation.',
      'dart_pub_usage': 'Use `flutter pub` instead of `dart pub` for Flutter projects. Only use `dart pub` for pure Dart projects.',
      'flutter_test_dependency': 'Add flutter_test to dev_dependencies in pubspec.yaml, not dependencies.',
      'image_decoder_issue': 'This is a known Android emulator issue. Use real device for testing or add proper image handling.',
      'version_solving_failed': 'Check pubspec.yaml for conflicting dependencies. Use `flutter pub deps` to analyze dependency tree.'
    };
    
    return solutions[mistakeType] || 'Review the specific error and consult Flutter documentation.';
  }

  /**
   * Identify success patterns from approved proposals
   */
  static identifySuccessPatterns(approvedProposals) {
    const patterns = [];
    const patternCounts = {};
    
    approvedProposals.forEach(proposal => {
      if (proposal.userFeedbackReason) {
        const reason = proposal.userFeedbackReason.toLowerCase();
        
        // Extract key phrases that indicate success
        const successPhrases = [
          'good improvement', 'better performance', 'cleaner code',
          'more readable', 'bug fix', 'security improvement',
          'good refactor', 'useful feature', 'well done'
        ];
        
        successPhrases.forEach(phrase => {
          if (reason.includes(phrase)) {
            patternCounts[phrase] = (patternCounts[phrase] || 0) + 1;
          }
        });
      }
    });
    
    // Sort by frequency
    Object.entries(patternCounts)
      .sort(([,a], [,b]) => b - a)
      .forEach(([pattern, count]) => {
        patterns.push({ pattern, count, frequency: count / approvedProposals.length });
      });
    
    return patterns;
  }

  /**
   * Generate learning context for AI with Flutter-specific knowledge
   */
  static async generateLearningContext(aiType) {
    const patterns = await this.analyzeFeedbackPatterns(aiType);
    
    let context = `Based on recent feedback for ${aiType} AI in this Flutter/Dart project:\n\n`;
    
    // Add Flutter project context
    context += "FLUTTER PROJECT CONTEXT:\n";
    context += "- This is a Flutter/Dart project, not a pure Dart project\n";
    context += "- Always use 'flutter pub' instead of 'dart pub'\n";
    context += "- Add flutter_test to dev_dependencies, not dependencies\n";
    context += "- Image decoder warnings are normal in Android emulator\n";
    context += "- Check pubspec.yaml for dependency conflicts\n\n";
    
    // Add common mistakes to avoid
    if (patterns.commonMistakes.length > 0) {
      context += "AVOID these common mistakes:\n";
      patterns.commonMistakes.slice(0, 5).forEach(mistake => {
        if (mistake.type === 'flutter_specific') {
          context += `- ${mistake.mistake}: ${mistake.solution}\n`;
        } else {
          context += `- ${mistake.mistake} (${Math.round(mistake.frequency * 100)}% of rejections)\n`;
        }
      });
      context += "\n";
    }
    
    // Add success patterns to follow
    if (patterns.successPatterns.length > 0) {
      context += "FOLLOW these success patterns:\n";
      patterns.successPatterns.slice(0, 5).forEach(pattern => {
        context += `- ${pattern.pattern} (${Math.round(pattern.frequency * 100)}% of approvals)\n`;
      });
      context += "\n";
    }
    
    // Add improvement type preferences
    if (Object.keys(patterns.approved.improvementTypes).length > 0) {
      context += "PREFERRED improvement types:\n";
      Object.entries(patterns.approved.improvementTypes)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 3)
        .forEach(([type, count]) => {
          context += `- ${type}: ${count} approvals\n`;
        });
      context += "\n";
    }
    
    return context;
  }

  /**
   * Apply learning to a new proposal
   */
  static async applyLearning(proposal, aiType) {
    const learningContext = await this.generateLearningContext(aiType);
    
    // Get recent mistakes to avoid
    const recentMistakes = await this.getRecentMistakes(aiType, 7); // Last 7 days
    
    proposal.learningContext = learningContext;
    proposal.previousMistakesAvoided = recentMistakes.map(m => m.mistake);
    proposal.aiLearningApplied = true;
    
    // Adjust confidence based on learning
    proposal.confidence = this.calculateConfidence(proposal, recentMistakes);
    
    return proposal;
  }

  /**
   * Get recent mistakes from the last N days
   */
  static async getRecentMistakes(aiType, days) {
    const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
    
    const recentRejected = await Proposal.find({
      aiType,
      userFeedback: 'rejected',
      createdAt: { $gte: cutoffDate }
    }).select('userFeedbackReason');
    
    return this.identifyCommonMistakes(aiType);
  }

  /**
   * Calculate confidence score based on learning
   */
  static calculateConfidence(proposal, recentMistakes) {
    let confidence = 0.5; // Base confidence
    
    // Check if proposal avoids recent mistakes
    const avoidsMistakes = recentMistakes.every(mistake => {
      const proposalText = (proposal.codeAfter + proposal.aiReasoning).toLowerCase();
      return !proposalText.includes(mistake.mistake);
    });
    
    if (avoidsMistakes) {
      confidence += 0.2;
    }
    
    // Check improvement type preference
    if (proposal.improvementType) {
      // This would be enhanced with actual preference data
      const preferredTypes = ['bug-fix', 'performance', 'readability'];
      if (preferredTypes.includes(proposal.improvementType)) {
        confidence += 0.1;
      }
    }
    
    // Check file type preference
    const fileExt = proposal.filePath.split('.').pop();
    const preferredFiles = ['dart', 'js', 'ts', 'py'];
    if (preferredFiles.includes(fileExt)) {
      confidence += 0.1;
    }
    
    return Math.min(confidence, 1.0);
  }

  /**
   * Learn from a proposal approval/rejection with internet learning
   */
  static async learnFromProposal(proposal, status, feedbackReason) {
    console.log(`[AI_LEARNING_SERVICE] 🧠 Learning from proposal: ${status} for ${proposal.aiType}`);
    
    try {
      // Update proposal status
      proposal.status = status;
      proposal.userFeedback = status;
      proposal.userFeedbackReason = feedbackReason;
      await proposal.save();
      
      // Store learning entry
      await Learning.create({
        aiType: proposal.aiType,
        proposalId: proposal._id,
        status: status === 'approved' ? 'approved' : 'rejected',
        feedbackReason,
        learningKey: 'proposal_feedback',
        learningValue: `Proposal ${status}: ${feedbackReason}`,
        filePath: proposal.filePath,
        improvementType: proposal.improvementType
      });
      
      // Trigger comprehensive AI learning cycle with internet research
      await this.triggerComprehensiveLearning(proposal, status, feedbackReason);
      
      console.log(`[AI_LEARNING_SERVICE] ✅ Learning from proposal completed for ${proposal.aiType}`);
      
    } catch (error) {
      console.error(`[AI_LEARNING_SERVICE] ❌ Error learning from proposal:`, error);
      throw error;
    }
  }
  
  /**
   * Trigger comprehensive AI learning cycle including internet research
   */
  static async triggerComprehensiveLearning(proposal, status, feedbackReason) {
    try {
      console.log(`[AI_LEARNING_SERVICE] 🎯 Triggering comprehensive learning for ${proposal.aiType}`);
      
      // Import the orchestrator
      const AILearningOrchestrator = require('./aiLearningOrchestrator');
      
      // Determine result based on status
      const result = status === 'approved' ? 'passed' : 'failed';
      
      // Trigger the complete learning cycle
      const learningResult = await AILearningOrchestrator.orchestrateAILearning(
        proposal.aiType, 
        proposal, 
        result
      );
      
      console.log(`[AI_LEARNING_SERVICE] ✅ Comprehensive learning cycle completed for ${proposal.aiType}`);
      console.log(`[AI_LEARNING_SERVICE] 📊 Learning summary:`, {
        insights: learningResult.learningData.insights?.length || 0,
        codeUpdates: learningResult.codeUpdates.updatesApplied || 0,
        githubPR: learningResult.githubResult.success ? 'Created' : 'Failed'
      });
      
      // Store orchestrator result
      await Learning.create({
        aiType: proposal.aiType,
        proposalId: proposal._id,
        status: 'learning-completed',
        feedbackReason: 'Comprehensive AI learning cycle completed',
        learningKey: 'orchestrator_result',
        learningValue: JSON.stringify({
          success: learningResult.success,
          insightsCount: learningResult.learningData.insights?.length || 0,
          codeUpdatesApplied: learningResult.codeUpdates.updatesApplied || 0,
          githubPRCreated: learningResult.githubResult.success,
          timestamp: learningResult.timestamp
        }),
        filePath: proposal.filePath,
        improvementType: proposal.improvementType
      });
      
      return learningResult;
      
    } catch (error) {
      console.error(`[AI_LEARNING_SERVICE] ❌ Error in comprehensive learning:`, error);
      
      // Store error for learning
      await Learning.create({
        aiType: proposal.aiType,
        proposalId: proposal._id,
        status: 'learning-failed',
        feedbackReason: `Comprehensive learning failed: ${error.message}`,
        learningKey: 'orchestrator_error',
        learningValue: JSON.stringify({
          error: error.message,
          timestamp: new Date().toISOString()
        }),
        filePath: proposal.filePath,
        improvementType: proposal.improvementType
      });
      
      throw error;
    }
  }

  /**
   * Update AI learning with feedback from test results
   */
  static async updateLearning(proposalId, status, feedbackReason) {
    try {
      console.log(`[AI_LEARNING_SERVICE] 📚 Updating AI learning for proposal ${proposalId}`);
      console.log(`[AI_LEARNING_SERVICE] Status: ${status}, Feedback: ${feedbackReason}`);
      
      // Get the proposal to find the AI type
      const proposal = await Proposal.findById(proposalId);
      if (!proposal) {
        console.log(`[AI_LEARNING_SERVICE] ❌ Proposal ${proposalId} not found`);
        return;
      }
      
      const aiType = proposal.aiType;
      console.log(`[AI_LEARNING_SERVICE] AI Type: ${aiType}`);
      
      // Extract key learning from test failure
      let learningKey = '';
      let learningValue = '';
      
      if (status === 'rejected' && feedbackReason.includes('Test failed')) {
        // Extract specific test failure patterns
        if (feedbackReason.includes('flutter_test') || feedbackReason.includes('dart pub')) {
          learningKey = 'flutter_sdk_dependency_error';
          learningValue = 'Use "flutter pub" instead of "dart pub" and ensure Flutter SDK is available';
        } else if (feedbackReason.includes('version solving failed')) {
          learningKey = 'dependency_resolution_error';
          learningValue = 'Check dependency compatibility and ensure all required packages are available';
        } else if (feedbackReason.includes('compilation error') || feedbackReason.includes('syntax error')) {
          learningKey = 'compilation_error';
          learningValue = 'Verify code compiles correctly before suggesting changes';
        } else {
          learningKey = 'test_failure';
          learningValue = feedbackReason.substring(0, 100);
        }
      } else if (status === 'approved') {
        learningKey = 'test_success';
        learningValue = 'Proposed changes passed all tests successfully';
      }
      
      console.log(`[AI_LEARNING_SERVICE] Extracted learning - Key: ${learningKey}, Value: ${learningValue}`);
      
      // Store the learning
      const learning = {
        aiType,
        proposalId,
        status,
        feedbackReason,
        learningKey,
        learningValue,
        timestamp: new Date(),
        filePath: proposal.filePath,
        improvementType: proposal.improvementType
      };
      
      await Learning.create(learning);
      console.log(`[AI_LEARNING_SERVICE] ✅ Learning stored for ${aiType}: ${learningKey}`);
      
      // Update proposal with learning reference
      proposal.learningApplied = true;
      proposal.learningKey = learningKey;
      await proposal.save();
      console.log(`[AI_LEARNING_SERVICE] ✅ Proposal ${proposalId} updated with learning reference`);
      
      // Emit learning event
      if (global.io) {
        global.io.emit('ai:learning-updated', {
          aiType,
          learningKey,
          learningValue,
          filePath: proposal.filePath,
          status
        });
        console.log(`[AI_LEARNING_SERVICE] 📡 Emitted learning event for ${aiType}`);
      }
      
    } catch (error) {
      console.error(`[AI_LEARNING_SERVICE] ❌ Error updating learning:`, error);
      console.error(`[AI_LEARNING_SERVICE] Stack trace:`, error.stack);
    }
  }

  /**
   * Get learning statistics
   */
  static async getLearningStats(aiType) {
    const stats = await Proposal.aggregate([
      { $match: { aiType } },
      {
        $group: {
          _id: '$userFeedback',
          count: { $sum: 1 },
          avgConfidence: { $avg: '$confidence' }
        }
      }
    ]);
    
    const totalProposals = await Proposal.countDocuments({ aiType });
    const learningApplied = await Proposal.countDocuments({ 
      aiType, 
      aiLearningApplied: true 
    });
    
    return {
      totalProposals,
      learningApplied,
      learningRate: learningApplied / totalProposals,
      feedbackStats: stats
    };
  }

  /**
   * Get learning insights for AI system prompts
   */
  static async getLearningInsights(aiType) {
    try {
      console.log(`[AI_LEARNING_SERVICE] 🔍 Getting learning insights for ${aiType}`);
      
      // Get recent rejected proposals with feedback
      const rejectedProposals = await Proposal.find({ 
        aiType, 
        status: { $in: ['rejected', 'test-failed'] },
        userFeedbackReason: { $exists: true, $ne: '' }
      }).sort({ createdAt: -1 }).limit(10);
      
      console.log(`[AI_LEARNING_SERVICE] Found ${rejectedProposals.length} rejected proposals for ${aiType}`);
      
      const insights = [];
      const seen = new Set();
      
      // Analyze each rejected proposal for specific insights
      for (let i = 0; i < rejectedProposals.length; i++) {
        const proposal = rejectedProposals[i];
        console.log(`[AI_LEARNING_SERVICE] 📋 Analyzing proposal ${i + 1}: ${proposal.status}...`);
        
        if (proposal.userFeedbackReason) {
          const reason = proposal.userFeedbackReason.toLowerCase();
          const filePath = proposal.filePath || '';
          const improvementType = proposal.improvementType || '';
          
          // Extract specific insights based on feedback patterns
          let insight = null;
          
          // Duplicate detection patterns
          if (reason.includes('duplicate') || reason.includes('similar') || reason.includes('already exists')) {
            insight = `Avoid generating duplicate proposals for ${filePath.split('/').pop() || 'files'}. Check existing proposals before suggesting changes.`;
          }
          // Test failure patterns
          else if (reason.includes('test failed') || reason.includes('tests failed') || reason.includes('compilation error')) {
            insight = `Always test code compilation before suggesting changes to ${filePath.split('/').pop() || 'files'}. Ensure syntax is correct.`;
          }
          // Flutter-specific patterns
          else if (reason.includes('flutter sdk') || reason.includes('dart pub') || reason.includes('version solving')) {
            insight = `Use 'flutter pub' instead of 'dart pub' for package management. Ensure Flutter SDK is properly configured.`;
          }
          // Null safety patterns
          else if (reason.includes('null safety') || reason.includes('null check') || reason.includes('nullable')) {
            insight = `Consider null safety when modifying Dart code in ${filePath.split('/').pop() || 'files'}. Handle nullable types properly.`;
          }
          // Performance patterns
          else if (reason.includes('performance') || reason.includes('slow') || reason.includes('inefficient')) {
            insight = `Focus on performance improvements when suggesting changes to ${filePath.split('/').pop() || 'files'}. Avoid unnecessary complexity.`;
          }
          // Readability patterns
          else if (reason.includes('readability') || reason.includes('unclear') || reason.includes('confusing')) {
            insight = `Prioritize code readability when suggesting improvements to ${filePath.split('/').pop() || 'files'}. Make code self-documenting.`;
          }
          // Import patterns
          else if (reason.includes('import') || reason.includes('dependency') || reason.includes('package')) {
            insight = `Be careful with import statements and dependencies. Only suggest necessary imports and compatible package versions.`;
          }
          // File-specific patterns
          else if (filePath.includes('main.dart')) {
            insight = `Be extra careful when suggesting changes to main.dart. Ensure the app entry point remains functional.`;
          }
          else if (filePath.includes('pubspec.yaml')) {
            insight = `When modifying pubspec.yaml, ensure all dependencies are compatible and the file structure is valid.`;
          }
          else if (filePath.includes('widget')) {
            insight = `For widget files, ensure proper Flutter widget structure and lifecycle management.`;
          }
          // Generic but specific patterns
          else if (reason.includes('breaks') || reason.includes('doesn\'t work') || reason.includes('error')) {
            insight = `Test that suggested changes don't break existing functionality in ${filePath.split('/').pop() || 'files'}.`;
          }
          else if (reason.includes('unnecessary') || reason.includes('not needed') || reason.includes('redundant')) {
            insight = `Only suggest changes that provide clear value. Avoid unnecessary modifications to ${filePath.split('/').pop() || 'files'}.`;
          }
          else {
            // Fallback: extract key phrases from the feedback
            const words = reason.split(' ').filter(word => word.length > 3);
            const keyPhrases = words.slice(0, 3).join(' ');
            insight = `Learn from feedback: "${keyPhrases}" when working with ${filePath.split('/').pop() || 'files'}.`;
          }
          
          if (insight && !seen.has(insight)) {
            seen.add(insight);
            insights.push({
              lesson: insight,
              source: 'rejected_proposal',
              timestamp: proposal.createdAt,
              filePath: proposal.filePath,
              improvementType: proposal.improvementType
            });
          }
        }
      }
      
      // Add some common lessons if we don't have enough specific insights
      const commonLessons = [
        'Always test that code compiles before suggesting changes',
        'Use Flutter-specific patterns and conventions',
        'Consider the impact of changes on existing functionality',
        'Ensure proper error handling in suggested code',
        'Follow Dart and Flutter best practices'
      ];
      
      for (const lesson of commonLessons) {
        if (insights.length < 8 && !seen.has(lesson)) {
          seen.add(lesson);
          insights.push({
            lesson: lesson,
            source: 'common',
            timestamp: new Date(),
            filePath: 'general',
            improvementType: 'general'
          });
        }
      }
      
      const finalInsights = insights.slice(0, 8); // Limit to 8 most important insights to avoid token limit
      
      console.log(`[AI_LEARNING_SERVICE] ✅ Generated ${finalInsights.length} unique learning insights for ${aiType}`);
      finalInsights.forEach((insight, index) => {
        console.log(`[AI_LEARNING_SERVICE] 📖 Insight ${index + 1}: ${insight.lesson} (source: ${insight.source})`);
      });
      
      return finalInsights;
    } catch (error) {
      console.error('[AI_LEARNING_SERVICE] ❌ Error getting learning insights:', error);
      return [];
    }
  }

  /**
   * Get learning context for AI system prompts
   */
  static async getLearningContext(aiType) {
    try {
      const insights = await this.getLearningInsights(aiType);
      const mistakes = await this.identifyCommonMistakes(aiType);
      
      let context = `LEARNING FROM PREVIOUS EXPERIENCE:\n`;
      
      if (insights.length > 0) {
        context += `Key lessons learned:\n`;
        insights.forEach(insight => {
          context += `- ${insight.lesson}\n`;
        });
      }
      
      if (mistakes.length > 0) {
        context += `\nCommon mistakes to avoid:\n`;
        mistakes.slice(0, 5).forEach(mistake => {
          context += `- ${mistake.mistake} (occurred ${mistake.count} times)\n`;
        });
      }
      
      return context;
    } catch (error) {
      console.error('[AI_LEARNING_SERVICE] Error getting learning context:', error);
      return 'LEARNING FROM PREVIOUS EXPERIENCE:\n- Always test code before suggesting changes\n- Use Flutter-specific commands and patterns';
    }
  }

  /**
   * Set AI learning state (pause/resume actions)
   */
  static setLearningState(aiType, isLearning) {
    const { aiStatus } = require('../state');
    if (aiStatus[aiType]) {
      aiStatus[aiType].isLearning = isLearning;
      logEvent(`[AI_LEARNING_SERVICE] ${aiType} learning state changed: isLearning=${isLearning}`);
      if (global.io) {
        global.io.emit('ai:learning-state', { aiType, isLearning });
      }
    }
  }

  /**
   * Check if AI should automatically enter learning state
   */
  static async checkForLearningTrigger(aiType) {
    try {
      console.log(`[AI_LEARNING_SERVICE] 🔍 Checking learning trigger for ${aiType}...`);
      
      // Get recent proposals (last 24 hours)
      const cutoffDate = new Date(Date.now() - 24 * 60 * 60 * 1000);
      const recentProposals = await Proposal.find({ 
        aiType, 
        createdAt: { $gte: cutoffDate }
      }).sort({ createdAt: -1 }).limit(10);
      
      if (recentProposals.length < 3) {
        console.log(`[AI_LEARNING_SERVICE] ⚠️ Not enough recent proposals for ${aiType} (${recentProposals.length})`);
        return;
      }
      
      const failures = recentProposals.filter(p => 
        ['rejected', 'test-failed'].includes(p.status)
      );
      
      const failureRate = failures.length / recentProposals.length;
      console.log(`[AI_LEARNING_SERVICE] 📊 ${aiType} failure rate: ${Math.round(failureRate * 100)}% (${failures.length}/${recentProposals.length})`);
      
      // Trigger learning if 3+ failures or 50%+ failure rate
      if (failures.length >= 3 || failureRate >= 0.5) {
        console.log(`[AI_LEARNING_SERVICE] 🚨 Learning trigger activated for ${aiType}`);
        this.setLearningState(aiType, true);
        logEvent(`[AUTO] ${aiType} entered learning state due to ${failures.length} recent failures (${Math.round(failureRate * 100)}% failure rate)`);
        
        // Store learning trigger event
        try {
          await Learning.create({
            aiType,
            proposalId: recentProposals.length > 0 ? recentProposals[0]._id : null,
            status: 'learning-triggered',
            feedbackReason: `Automatic learning trigger: ${failures.length} failures in last ${recentProposals.length} proposals`,
            learningKey: 'automatic_learning_trigger',
            learningValue: `Failure rate ${Math.round(failureRate * 100)}% exceeded threshold`,
            filePath: 'system',
            improvementType: 'system'
          });
          console.log(`[AI_LEARNING_SERVICE] ✅ Learning trigger event stored for ${aiType}`);
        } catch (learningError) {
          console.error(`[AI_LEARNING_SERVICE] ❌ Error storing learning trigger event:`, learningError);
        }
      }
    } catch (error) {
      console.error(`[AI_LEARNING_SERVICE] ❌ Error checking learning trigger for ${aiType}:`, error);
    }
  }

  /**
   * Check if AI should automatically exit learning state
   */
  static async checkLearningCompletion(aiType) {
    try {
      console.log(`[AI_LEARNING_SERVICE] 🔍 Checking learning completion for ${aiType}...`);
      
      const { aiStatus } = require('../state');
      if (!aiStatus[aiType]?.isLearning) {
        return; // Not in learning state
      }
      
      // Get recent learning entries
      const recentLearning = await Learning.find({ aiType })
        .sort({ timestamp: -1 })
        .limit(10);
      
      if (recentLearning.length < 1) {
        console.log(`[AI_LEARNING_SERVICE] ⚠️ No learning entries for ${aiType}`);
        return;
      }
      
      // Check if we have recent successful proposals after learning
      const latestLearning = recentLearning[0];
      const subsequentProposals = await Proposal.find({
        aiType,
        createdAt: { $gt: latestLearning.timestamp }
      }).sort({ createdAt: -1 }).limit(10);
      
      // More lenient completion criteria
      let shouldComplete = false;
      let completionReason = '';
      
      if (subsequentProposals.length >= 3) {
        const recentSuccesses = subsequentProposals.filter(p => 
          ['approved', 'test-passed', 'applied'].includes(p.status)
        );
        
        const successRate = recentSuccesses.length / subsequentProposals.length;
        console.log(`[AI_LEARNING_SERVICE] 📊 ${aiType} post-learning success rate: ${Math.round(successRate * 100)}% (${recentSuccesses.length}/${subsequentProposals.length})`);
        
        // Exit learning if 50%+ success rate or 2+ consecutive successes (more lenient)
        if (successRate >= 0.5 || recentSuccesses.length >= 2) {
          shouldComplete = true;
          completionReason = `Success rate ${Math.round(successRate * 100)}% achieved after learning`;
        }
      } else if (subsequentProposals.length >= 1) {
        // Even if only 1-2 proposals, check if any succeeded
        const recentSuccesses = subsequentProposals.filter(p => 
          ['approved', 'test-passed', 'applied'].includes(p.status)
        );
        
        if (recentSuccesses.length >= 1) {
          shouldComplete = true;
          completionReason = `At least one successful proposal after learning`;
        }
      }
      
      // Timeout mechanism: exit learning after 30 minutes regardless
      const learningStartTime = latestLearning.timestamp;
      const timeSinceLearning = Date.now() - learningStartTime;
      const thirtyMinutes = 30 * 60 * 1000; // 30 minutes in milliseconds
      
      if (timeSinceLearning > thirtyMinutes) {
        shouldComplete = true;
        completionReason = `Learning timeout after ${Math.round(timeSinceLearning / (1000 * 60))} minutes`;
      }
      
      // Force completion if stuck for too long (additional safety)
      const totalLearningEntries = await Learning.countDocuments({ 
        aiType, 
        status: 'learning-triggered',
        timestamp: { $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) } // Last 24 hours
      });
      
      if (totalLearningEntries >= 3) {
        shouldComplete = true;
        completionReason = `Force completion after ${totalLearningEntries} learning triggers in 24 hours`;
      }
      
      if (shouldComplete) {
        console.log(`[AI_LEARNING_SERVICE] ✅ Learning completion triggered for ${aiType}: ${completionReason}`);
        this.setLearningState(aiType, false);
        logEvent(`[AUTO] ${aiType} completed learning phase: ${completionReason}`);
        
        // Store learning completion event
        try {
          await Learning.create({
            aiType,
            proposalId: subsequentProposals.length > 0 ? subsequentProposals[0]._id : null,
            status: 'learning-completed',
            feedbackReason: `Automatic learning completion: ${completionReason}`,
            learningKey: 'automatic_learning_completion',
            learningValue: completionReason,
            filePath: 'system',
            improvementType: 'system'
          });
          console.log(`[AI_LEARNING_SERVICE] ✅ Learning completion event stored for ${aiType}`);
        } catch (learningError) {
          console.error(`[AI_LEARNING_SERVICE] ❌ Error storing learning completion event:`, learningError);
        }
      } else {
        console.log(`[AI_LEARNING_SERVICE] ⏳ ${aiType} still in learning mode (${subsequentProposals.length} subsequent proposals, ${Math.round(timeSinceLearning / (1000 * 60))} minutes elapsed)`);
      }
    } catch (error) {
      console.error(`[AI_LEARNING_SERVICE] ❌ Error checking learning completion for ${aiType}:`, error);
    }
  }

  /**
   * Clean up old learning data to prevent memory accumulation
   */
  static async cleanupOldData() {
    try {
      console.log('[AI_LEARNING_SERVICE] 🧹 Cleaning up old learning data...');
      
      // Remove learning entries older than 30 days
      const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
      const deletedLearning = await Learning.deleteMany({
        timestamp: { $lt: thirtyDaysAgo }
      });
      
      // Remove proposals older than 30 days (keep only recent ones)
      const deletedProposals = await Proposal.deleteMany({
        createdAt: { $lt: thirtyDaysAgo }
      });
      
      // Remove experiments older than 30 days
      const deletedExperiments = await Experiment.deleteMany({
        createdAt: { $lt: thirtyDaysAgo }
      });
      
      console.log(`[AI_LEARNING_SERVICE] ✅ Cleanup completed: ${deletedLearning.deletedCount} learning entries, ${deletedProposals.deletedCount} proposals, ${deletedExperiments.deletedCount} experiments removed`);
      
      // Force garbage collection if available
      if (global.gc) {
        global.gc();
      }
    } catch (error) {
      console.error('[AI_LEARNING_SERVICE] ❌ Error during data cleanup:', error);
    }
  }

  /**
   * Run learning checks for all AIs
   */
  static async runLearningChecks() {
    const aiTypes = ['Imperium', 'Sandbox', 'Guardian'];
    
    for (const aiType of aiTypes) {
      await this.checkForLearningTrigger(aiType);
      await this.checkLearningCompletion(aiType);
    }
    
    // Run cleanup every 10th check (approximately every 50 minutes)
    const cleanupCounter = (Date.now() / (5 * 60 * 1000)) % 10;
    if (cleanupCounter < 1) {
      await this.cleanupOldData();
    }
  }

  /**
   * Process oath paper with enhanced learning capabilities
   * @param {Object} oathPaper - The oath paper data
   * @returns {Promise<Object>} Learning results
   */
  async processOathPaper(oathPaper) {
    console.log('[AI_LEARNING_SERVICE] 🧠 Processing oath paper:', oathPaper.subject);
    
    try {
      // Extract keywords from description and code
      const keywords = await this.extractKeywords(oathPaper);
      console.log('[AI_LEARNING_SERVICE] 🔍 Extracted keywords:', keywords);
      
      // Search internet for additional information
      const searchResults = await this.searchInternet(keywords, oathPaper.tags);
      console.log('[AI_LEARNING_SERVICE] 🌐 Internet search results:', searchResults.length);
      
      // Learn from combined data
      const learningResult = await this.learnFromCombinedData(oathPaper, keywords, searchResults);
      
      // Update AI capabilities
      await this.updateAICapabilities(oathPaper.targetAI, keywords, searchResults);
      
      // Push to Git if specified
      let gitResult = null;
      if (oathPaper.gitIntegration) {
        gitResult = await this.pushToGit(oathPaper, keywords, searchResults);
      }
      
      console.log('[AI_LEARNING_SERVICE] ✅ Oath paper processing completed');
      
      return {
        success: true,
        keywords,
        searchResults,
        learningResult,
        gitResult,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('[AI_LEARNING_SERVICE] ❌ Error processing oath paper:', error);
      throw error;
    }
  }

  /**
   * Extract keywords from oath paper content
   * @param {Object} oathPaper - The oath paper data
   * @returns {Promise<Array>} Extracted keywords
   */
  async extractKeywords(oathPaper) {
    const keywords = new Set();
    
    // Add user-provided tags
    if (oathPaper.tags && Array.isArray(oathPaper.tags)) {
      oathPaper.tags.forEach(tag => keywords.add(tag.toLowerCase()));
    }
    
    // Extract from description
    if (oathPaper.description) {
      const descriptionKeywords = await this.extractKeywordsFromText(oathPaper.description);
      descriptionKeywords.forEach(keyword => keywords.add(keyword));
    }
    
    // Extract from code
    if (oathPaper.code) {
      const codeKeywords = await this.extractKeywordsFromCode(oathPaper.code);
      codeKeywords.forEach(keyword => keywords.add(keyword));
    }
    
    return Array.from(keywords);
  }

  /**
   * Extract keywords from text using NLP techniques
   * @param {string} text - The text to analyze
   * @returns {Promise<Array>} Extracted keywords
   */
  async extractKeywordsFromText(text) {
    // Simple keyword extraction - in production, use proper NLP libraries
    const words = text.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 3)
      .filter(word => !this.commonWords.has(word));
    
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

  /**
   * Extract keywords from code
   * @param {string} code - The code to analyze
   * @returns {Promise<Array>} Extracted keywords
   */
  async extractKeywordsFromCode(code) {
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

  /**
   * Search internet for additional information
   * @param {Array} keywords - Extracted keywords
   * @param {Array} tags - User-provided tags
   * @returns {Promise<Array>} Search results
   */
  async searchInternet(keywords, tags) {
    const searchResults = [];
    const searchTerms = [...keywords, ...tags].slice(0, 5); // Limit to top 5 terms
    
    for (const term of searchTerms) {
      try {
        const result = await this.performWebSearch(term);
        searchResults.push(...result);
      } catch (error) {
        console.warn(`[AI_LEARNING_SERVICE] ⚠️ Search failed for term "${term}":`, error.message);
      }
    }
    
    return searchResults;
  }

  /**
   * Perform web search (placeholder for real search API integration)
   * @param {string} term - Search term
   * @returns {Promise<Array>} Search results
   */
  async performWebSearch(term) {
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

  /**
   * Learn from combined data (oath paper + internet search)
   * @param {Object} oathPaper - The oath paper data
   * @param {Array} keywords - Extracted keywords
   * @param {Array} searchResults - Internet search results
   * @returns {Promise<Object>} Learning result
   */
  async learnFromCombinedData(oathPaper, keywords, searchResults) {
    const learningEntry = {
      type: 'oath_paper_learning',
      subject: oathPaper.subject,
      keywords,
      searchResults,
      targetAI: oathPaper.targetAI,
      aiWeights: oathPaper.aiWeights,
      timestamp: new Date().toISOString(),
      learningData: {
        description: oathPaper.description,
        code: oathPaper.code,
        tags: oathPaper.tags,
        extractedKeywords: keywords,
        internetSources: searchResults.length,
      },
    };
    
    // Save to learning data
    await this.saveLearningData(learningEntry);
    
    console.log('[AI_LEARNING_SERVICE] 📚 Learning data updated');
    return learningEntry;
  }

  /**
   * Update AI capabilities based on learned information
   * @param {string} targetAI - Target AI type
   * @param {Array} keywords - Extracted keywords
   * @param {Array} searchResults - Internet search results
   * @returns {Promise<void>}
   */
  async updateAICapabilities(targetAI, keywords, searchResults) {
    const aiTypes = targetAI ? [targetAI] : ['Imperium', 'Sandbox', 'Guardian'];
    
    for (const aiType of aiTypes) {
      // Update capabilities in the learning data
      if (!this.learningData[aiType]) {
        this.learningData[aiType] = {};
      }
      
      if (!this.learningData[aiType].capabilities) {
        this.learningData[aiType].capabilities = [];
      }
      
      if (!this.learningData[aiType].recentLearning) {
        this.learningData[aiType].recentLearning = [];
      }
      
      // Add new capabilities
      for (const keyword of keywords.slice(0, 5)) {
        if (!this.learningData[aiType].capabilities.includes(keyword)) {
          this.learningData[aiType].capabilities.push(keyword);
        }
      }
      
      // Add recent learning entry
      this.learningData[aiType].recentLearning.unshift({
        type: 'oath_paper',
        keywords: keywords.slice(0, 3),
        sources: searchResults.length,
        timestamp: new Date().toISOString(),
      });
      
      // Keep only recent entries
      if (this.learningData[aiType].recentLearning.length > 10) {
        this.learningData[aiType].recentLearning = 
            this.learningData[aiType].recentLearning.slice(0, 10);
      }
    }
    
    console.log('[AI_LEARNING_SERVICE] 🧠 AI capabilities updated for:', aiTypes);
  }

  /**
   * Push updates to Git repository
   * @param {Object} oathPaper - The oath paper data
   * @param {Array} keywords - Extracted keywords
   * @param {Array} searchResults - Internet search results
   * @returns {Promise<Object>} Git result
   */
  async pushToGit(oathPaper, keywords, searchResults) {
    try {
      console.log('[AI_LEARNING_SERVICE] 🔄 Pushing learning updates to Git...');
      
      const commitMessage = `AI Learning Update: ${oathPaper.subject}\n\n` +
        `Keywords: ${keywords.slice(0, 5).join(', ')}\n` +
        `Sources: ${searchResults.length} internet sources\n` +
        `Target AI: ${oathPaper.targetAI || 'All AIs'}`;
      
      // This would integrate with Git API
      const gitResult = await this.performGitCommit(commitMessage, oathPaper);
      
      console.log('[AI_LEARNING_SERVICE] ✅ Git update completed');
      return gitResult;
    } catch (error) {
      console.error('[AI_LEARNING_SERVICE] ❌ Git update failed:', error);
      throw error;
    }
  }

  /**
   * Perform Git commit (placeholder for real Git integration)
   * @param {string} message - Commit message
   * @param {Object} oathPaper - The oath paper data
   * @returns {Promise<Object>} Git commit result
   */
  async performGitCommit(message, oathPaper) {
    // This would integrate with Git API (GitHub, GitLab, etc.)
    await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate Git operations
    
    return {
      commit: `abc123${Date.now()}`,
      message,
      timestamp: new Date().toISOString(),
      files: ['ai_learning_data.json', 'capabilities.json'],
    };
  }

  /**
   * Save learning data to persistent storage
   * @param {Object} learningEntry - Learning entry to save
   * @returns {Promise<void>}
   */
  async saveLearningData(learningEntry) {
    // Add to in-memory learning data
    if (!this.learningData.oathPapers) {
      this.learningData.oathPapers = [];
    }
    
    this.learningData.oathPapers.push(learningEntry);
    
    // In a real implementation, this would save to a database or file
    console.log('[AI_LEARNING_SERVICE] 💾 Learning data saved');
  }

  // Common words to filter out during keyword extraction
  commonWords = new Set([
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
}

module.exports = AILearningService; 