const Proposal = require('../models/proposal');
const Learning = require('../models/learning');

class LearningAnalyticsService {
  /**
   * Calculate learning metrics for each AI
   */
  static async calculateLearningMetrics() {
    try {
      console.log('[LEARNING_ANALYTICS] 🔍 Calculating learning metrics for all AIs...');
      
      const aiTypes = ['Imperium', 'Sandbox', 'Guardian'];
      const metrics = {};
      
      for (const aiType of aiTypes) {
        console.log(`[LEARNING_ANALYTICS] 📊 Analyzing ${aiType}...`);
        
        // Get all proposals for this AI
        const allProposals = await Proposal.find({ aiType }).sort({ timestamp: -1 });
        const totalProposals = allProposals.length;
        
        // Get proposals that failed tests
        const failedProposals = await Proposal.find({ 
          aiType, 
          status: { $in: ['rejected', 'test-failed'] }
        });
        
        // Get proposals that passed tests
        const passedProposals = await Proposal.find({ 
          aiType, 
          status: { $in: ['approved', 'test-passed', 'applied'] }
        });
        
        // Get learning entries for this AI
        const learningEntries = await Learning.find({ aiType }).sort({ timestamp: -1 });
        
        // Calculate learning effectiveness
        const recentProposals = allProposals.slice(0, 10); // Last 10 proposals
        const recentFailed = recentProposals.filter(p => 
          ['rejected', 'test-failed'].includes(p.status)
        );
        const recentPassed = recentProposals.filter(p => 
          ['approved', 'test-passed', 'applied'].includes(p.status)
        );
        
        // Calculate learning percentage (improvement over time)
        const earlyFailureRate = failedProposals.length / Math.max(totalProposals, 1);
        const recentFailureRate = recentFailed.length / Math.max(recentProposals.length, 1);
        const learningImprovement = Math.max(0, (earlyFailureRate - recentFailureRate) / Math.max(earlyFailureRate, 0.01)) * 100;
        
        // Check if AI is applying learned lessons
        const appliedLearning = await this.checkAppliedLearning(aiType, learningEntries);
        
        metrics[aiType] = {
          totalProposals,
          failedProposals: failedProposals.length,
          passedProposals: passedProposals.length,
          learningEntries: learningEntries.length,
          recentFailureRate: Math.round(recentFailureRate * 100),
          learningImprovement: Math.round(learningImprovement),
          appliedLearning,
          successRate: Math.round((passedProposals.length / Math.max(totalProposals, 1)) * 100),
          learningScore: Math.round(this.calculateLearningScore(learningEntries, recentProposals))
        };
        
        console.log(`[LEARNING_ANALYTICS] ✅ ${aiType} metrics calculated:`);
        console.log(`[LEARNING_ANALYTICS]   - Total proposals: ${totalProposals}`);
        console.log(`[LEARNING_ANALYTICS]   - Success rate: ${metrics[aiType].successRate}%`);
        console.log(`[LEARNING_ANALYTICS]   - Learning improvement: ${metrics[aiType].learningImprovement}%`);
        console.log(`[LEARNING_ANALYTICS]   - Learning score: ${metrics[aiType].learningScore}%`);
      }
      
      return metrics;
    } catch (error) {
      console.error('[LEARNING_ANALYTICS] ❌ Error calculating learning metrics:', error);
      return {};
    }
  }
  
  /**
   * Check if AI is applying learned lessons
   */
  static async checkAppliedLearning(aiType, learningEntries) {
    try {
      const recentLearning = learningEntries.slice(0, 5); // Last 5 learning entries
      let appliedCount = 0;
      
      for (const learning of recentLearning) {
        // Check if subsequent proposals avoid the same mistake
        const subsequentProposals = await Proposal.find({
          aiType,
          timestamp: { $gt: learning.timestamp }
        }).limit(5);
        
        const avoidsMistake = subsequentProposals.every(proposal => {
          const feedback = proposal.userFeedbackReason?.toLowerCase() || '';
          const learningKey = learning.learningKey;
          
          // Check if proposal avoids the learned mistake
          if (learningKey === 'flutter_sdk_dependency_error') {
            return !feedback.includes('flutter_test') && !feedback.includes('dart pub');
          } else if (learningKey === 'dependency_resolution_error') {
            return !feedback.includes('version solving failed');
          } else if (learningKey === 'compilation_error') {
            return !feedback.includes('compilation error') && !feedback.includes('syntax error');
          }
          
          return true; // Default to true if we can't determine
        });
        
        if (avoidsMistake) {
          appliedCount++;
        }
      }
      
      return Math.round((appliedCount / Math.max(recentLearning.length, 1)) * 100);
    } catch (error) {
      console.error('[LEARNING_ANALYTICS] ❌ Error checking applied learning:', error);
      return 0;
    }
  }
  
  /**
   * Calculate learning score based on learning entries and recent performance
   */
  static calculateLearningScore(learningEntries, recentProposals) {
    try {
      if (learningEntries.length === 0) return 0;
      
      // Base score from number of learning entries
      const baseScore = Math.min(learningEntries.length * 10, 50);
      
      // Performance improvement score
      const recentSuccessRate = recentProposals.filter(p => 
        ['approved', 'test-passed', 'applied'].includes(p.status)
      ).length / Math.max(recentProposals.length, 1);
      
      const performanceScore = recentSuccessRate * 50;
      
      return Math.min(baseScore + performanceScore, 100);
    } catch (error) {
      console.error('[LEARNING_ANALYTICS] ❌ Error calculating learning score:', error);
      return 0;
    }
  }
  
  /**
   * Get detailed learning analysis for a specific AI
   */
  static async getDetailedLearningAnalysis(aiType) {
    try {
      console.log(`[LEARNING_ANALYTICS] 🔍 Getting detailed analysis for ${aiType}...`);
      
      // Get all learning entries
      const learningEntries = await Learning.find({ aiType }).sort({ timestamp: -1 });
      
      // Get learning triggers and completions
      const learningTriggers = learningEntries.filter(l => l.status === 'learning-triggered');
      const learningCompletions = learningEntries.filter(l => l.status === 'learning-completed');
      
      // Calculate learning effectiveness
      const learningSessions = [];
      for (let i = 0; i < learningTriggers.length; i++) {
        const trigger = learningTriggers[i];
        const completion = learningCompletions.find(c => c.timestamp > trigger.timestamp);
        
        if (completion) {
          const duration = completion.timestamp - trigger.timestamp;
          learningSessions.push({
            triggerTime: trigger.timestamp,
            completionTime: completion.timestamp,
            duration: duration,
            durationHours: Math.round(duration / (1000 * 60 * 60) * 100) / 100
          });
        }
      }
      
      // Calculate success rate improvement
      const recentProposals = await Proposal.find({ aiType })
        .sort({ createdAt: -1 })
        .limit(20);
      
      const earlyProposals = recentProposals.slice(10);
      const lateProposals = recentProposals.slice(0, 10);
      
      const earlySuccessRate = earlyProposals.length > 0 ? 
        earlyProposals.filter(p => ['approved', 'test-passed', 'applied'].includes(p.status)).length / earlyProposals.length : 0;
      const lateSuccessRate = lateProposals.length > 0 ? 
        lateProposals.filter(p => ['approved', 'test-passed', 'applied'].includes(p.status)).length / lateProposals.length : 0;
      
      const improvement = lateSuccessRate - earlySuccessRate;
      
      return {
        aiType,
        totalLearningEntries: learningEntries.length,
        learningTriggers: learningTriggers.length,
        learningCompletions: learningCompletions.length,
        completionRate: learningTriggers.length > 0 ? 
          Math.round((learningCompletions.length / learningTriggers.length) * 100) : 0,
        averageLearningDuration: learningSessions.length > 0 ? 
          Math.round(learningSessions.reduce((sum, s) => sum + s.durationHours, 0) / learningSessions.length * 100) / 100 : 0,
        learningSessions: learningSessions,
        successRateImprovement: Math.round(improvement * 100),
        earlySuccessRate: Math.round(earlySuccessRate * 100),
        lateSuccessRate: Math.round(lateSuccessRate * 100),
        recentLearningEntries: learningEntries.slice(0, 10).map(l => ({
          status: l.status,
          learningKey: l.learningKey,
          timestamp: l.timestamp,
          feedbackReason: l.feedbackReason
        }))
      };
    } catch (error) {
      console.error(`[LEARNING_ANALYTICS] ❌ Error getting detailed analysis for ${aiType}:`, error);
      return {
        aiType,
        error: error.message
      };
    }
  }

  /**
   * Get learning effectiveness metrics
   */
  static async getLearningEffectiveness() {
    try {
      console.log('[LEARNING_ANALYTICS] 📊 Calculating learning effectiveness...');
      
      const aiTypes = ['Imperium', 'Sandbox', 'Guardian'];
      const effectiveness = {};
      
      for (const aiType of aiTypes) {
        const analysis = await this.getDetailedLearningAnalysis(aiType);
        effectiveness[aiType] = {
          completionRate: analysis.completionRate,
          averageDuration: analysis.averageLearningDuration,
          successImprovement: analysis.successRateImprovement,
          learningSessions: analysis.learningSessions.length
        };
      }
      
      // Calculate overall effectiveness
      const overallCompletionRate = Math.round(
        Object.values(effectiveness).reduce((sum, e) => sum + e.completionRate, 0) / aiTypes.length
      );
      
      const overallImprovement = Math.round(
        Object.values(effectiveness).reduce((sum, e) => sum + e.successImprovement, 0) / aiTypes.length
      );
      
      return {
        overall: {
          completionRate: overallCompletionRate,
          averageImprovement: overallImprovement,
          totalLearningSessions: Object.values(effectiveness).reduce((sum, e) => sum + e.learningSessions, 0)
        },
        byAI: effectiveness
      };
    } catch (error) {
      console.error('[LEARNING_ANALYTICS] ❌ Error calculating learning effectiveness:', error);
      return { error: error.message };
    }
  }
}

module.exports = LearningAnalyticsService; 