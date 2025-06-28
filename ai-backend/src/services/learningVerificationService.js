const Proposal = require('../models/proposal');
const Learning = require('../models/learning');

class LearningVerificationService {
  /**
   * Verify if an AI has learned from test failures
   */
  static async verifyAILearning(aiType) {
    try {
      console.log(`[LEARNING_VERIFICATION] 🔍 Verifying learning for ${aiType}...`);
      
      // Get recent learning entries
      const recentLearning = await Learning.find({ aiType })
        .sort({ timestamp: -1 })
        .limit(10);
      
      if (recentLearning.length === 0) {
        console.log(`[LEARNING_VERIFICATION] ⚠️ No learning entries found for ${aiType}`);
        return {
          aiType,
          hasLearned: false,
          learningEntries: 0,
          recentProposals: 0,
          mistakesAvoided: 0,
          learningScore: 0,
          verification: 'No learning data available'
        };
      }
      
      // Get proposals after the most recent learning
      const latestLearning = recentLearning[0];
      const subsequentProposals = await Proposal.find({
        aiType,
        timestamp: { $gt: latestLearning.timestamp }
      }).sort({ timestamp: -1 });
      
      console.log(`[LEARNING_VERIFICATION] Found ${subsequentProposals.length} proposals after learning for ${aiType}`);
      
      // Check if AI is avoiding learned mistakes
      let mistakesAvoided = 0;
      let totalChecked = 0;
      
      for (const learning of recentLearning.slice(0, 5)) { // Check last 5 learning entries
        const proposalsAfterLearning = await Proposal.find({
          aiType,
          timestamp: { $gt: learning.timestamp }
        }).limit(3); // Check next 3 proposals
        
        for (const proposal of proposalsAfterLearning) {
          totalChecked++;
          const feedback = proposal.userFeedbackReason?.toLowerCase() || '';
          const avoidsMistake = this.checkIfMistakeAvoided(learning.learningKey, feedback);
          
          if (avoidsMistake) {
            mistakesAvoided++;
            console.log(`[LEARNING_VERIFICATION] ✅ ${aiType} avoided mistake: ${learning.learningKey}`);
          } else {
            console.log(`[LEARNING_VERIFICATION] ❌ ${aiType} repeated mistake: ${learning.learningKey}`);
          }
        }
      }
      
      const learningScore = totalChecked > 0 ? Math.round((mistakesAvoided / totalChecked) * 100) : 0;
      const hasLearned = learningScore >= 70; // Consider learned if 70%+ mistakes avoided
      
      console.log(`[LEARNING_VERIFICATION] 📊 ${aiType} learning verification:`);
      console.log(`[LEARNING_VERIFICATION]   - Mistakes avoided: ${mistakesAvoided}/${totalChecked}`);
      console.log(`[LEARNING_VERIFICATION]   - Learning score: ${learningScore}%`);
      console.log(`[LEARNING_VERIFICATION]   - Has learned: ${hasLearned}`);
      
      return {
        aiType,
        hasLearned,
        learningEntries: recentLearning.length,
        recentProposals: subsequentProposals.length,
        mistakesAvoided,
        totalChecked,
        learningScore,
        verification: hasLearned ? 'AI is learning effectively' : 'AI needs more learning',
        recentLearning: recentLearning.map(l => ({
          key: l.learningKey,
          value: l.learningValue,
          timestamp: l.timestamp
        }))
      };
    } catch (error) {
      console.error(`[LEARNING_VERIFICATION] ❌ Error verifying learning for ${aiType}:`, error);
      return {
        aiType,
        hasLearned: false,
        learningEntries: 0,
        recentProposals: 0,
        mistakesAvoided: 0,
        learningScore: 0,
        verification: 'Error during verification'
      };
    }
  }
  
  /**
   * Check if a specific mistake was avoided
   */
  static checkIfMistakeAvoided(learningKey, feedback) {
    switch (learningKey) {
      case 'flutter_sdk_dependency_error':
        return !feedback.includes('flutter_test') && 
               !feedback.includes('dart pub') && 
               !feedback.includes('sdk which doesn\'t exist');
        
      case 'dependency_resolution_error':
        return !feedback.includes('version solving failed') && 
               !feedback.includes('dependency');
        
      case 'compilation_error':
        return !feedback.includes('compilation error') && 
               !feedback.includes('syntax error') && 
               !feedback.includes('compile error');
        
      case 'test_failure':
        return !feedback.includes('test failed') && 
               !feedback.includes('tests failed');
        
      default:
        return true; // Default to true if we can't determine
    }
  }
  
  /**
   * Run comprehensive learning verification for all AIs
   */
  static async verifyAllAILearning() {
    try {
      console.log('[LEARNING_VERIFICATION] 🔍 Running comprehensive learning verification...');
      
      const aiTypes = ['Imperium', 'Sandbox', 'Guardian'];
      const results = {};
      
      for (const aiType of aiTypes) {
        const result = await this.verifyAILearning(aiType);
        results[aiType] = result;
      }
      
      // Calculate overall learning effectiveness
      const totalLearningScore = Object.values(results)
        .reduce((sum, r) => sum + r.learningScore, 0);
      const averageLearningScore = Math.round(totalLearningScore / aiTypes.length);
      
      const overallResult = {
        timestamp: new Date().toISOString(),
        averageLearningScore,
        totalAIs: aiTypes.length,
        learningAIs: Object.values(results).filter(r => r.hasLearned).length,
        results
      };
      
      console.log('[LEARNING_VERIFICATION] 📊 Overall learning verification results:');
      console.log(`[LEARNING_VERIFICATION]   - Average learning score: ${averageLearningScore}%`);
      console.log(`[LEARNING_VERIFICATION]   - AIs learning effectively: ${overallResult.learningAIs}/${aiTypes.length}`);
      
      return overallResult;
    } catch (error) {
      console.error('[LEARNING_VERIFICATION] ❌ Error in comprehensive verification:', error);
      return {
        timestamp: new Date().toISOString(),
        averageLearningScore: 0,
        totalAIs: 0,
        learningAIs: 0,
        results: {},
        error: error.message
      };
    }
  }
  
  /**
   * Generate learning recommendations based on verification results
   */
  static generateLearningRecommendations(verificationResults) {
    const recommendations = [];
    
    for (const [aiType, result] of Object.entries(verificationResults.results)) {
      if (result.learningScore < 50) {
        recommendations.push({
          aiType,
          priority: 'high',
          recommendation: `${aiType} needs immediate attention - only ${result.learningScore}% learning effectiveness`,
          action: 'Review recent proposals and strengthen learning prompts'
        });
      } else if (result.learningScore < 70) {
        recommendations.push({
          aiType,
          priority: 'medium',
          recommendation: `${aiType} is learning but could improve - ${result.learningScore}% learning effectiveness`,
          action: 'Monitor performance and adjust learning parameters'
        });
      } else {
        recommendations.push({
          aiType,
          priority: 'low',
          recommendation: `${aiType} is learning effectively - ${result.learningScore}% learning effectiveness`,
          action: 'Continue current learning approach'
        });
      }
    }
    
    return recommendations;
  }
}

module.exports = LearningVerificationService; 