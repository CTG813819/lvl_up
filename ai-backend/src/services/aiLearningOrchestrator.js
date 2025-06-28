const InternetLearningService = require('./internetLearningService');
const AICodeUpdateService = require('./aiCodeUpdateService');
const ApprovalService = require('./approvalService');
const AppFileMappingService = require('./appFileMappingService');
const Learning = require('../models/learning');

/**
 * AI Learning Orchestrator
 * Coordinates the complete AI learning cycle with user approval workflow
 */
class AILearningOrchestrator {
  /**
   * Orchestrate complete AI learning cycle with approval workflow
   */
  async orchestrateAILearning(aiType, proposal, result) {
    console.log(`[AI_LEARNING_ORCHESTRATOR] 🎯 Starting AI learning cycle for ${aiType} - Result: ${result}`);
    
    try {
      // Get AI-specific file information
      const aiFiles = AppFileMappingService.getAIFiles(aiType);
      console.log(`[AI_LEARNING_ORCHESTRATOR] 📁 ${aiType} should focus on ${aiFiles.length} files:`);
      aiFiles.forEach(file => {
        console.log(`  - ${file.path} (${file.priority} priority): ${file.description}`);
      });
      
      // Step 1: Learn from internet sources
      console.log(`[AI_LEARNING_ORCHESTRATOR] 🌐 Step 1: Learning from internet sources...`);
      const learningData = await InternetLearningService.learnFromInternet(aiType, proposal, result);
      
      // Step 2: Generate code updates
      console.log(`[AI_LEARNING_ORCHESTRATOR] 🔧 Step 2: Generating code updates...`);
      const codeUpdates = await this.generateCodeUpdatesFromLearning(aiType, proposal, result, learningData);
      
      // Step 3: Apply updates locally for testing
      console.log(`[AI_LEARNING_ORCHESTRATOR] 📝 Step 3: Applying updates locally...`);
      const codeUpdateResult = await AICodeUpdateService.updateAICode(aiType, proposal, result, learningData);
      
      // Step 4: Submit for user approval (instead of direct GitHub push)
      console.log(`[AI_LEARNING_ORCHESTRATOR] 📋 Step 4: Submitting for user approval...`);
      const approvalResult = await ApprovalService.submitForApproval(
        aiType, 
        codeUpdates, 
        learningData, 
        proposal._id
      );
      
      // Log the learning cycle
      await this.logLearningCycle(aiType, proposal, result, learningData, codeUpdates, 'submitted-for-approval');
      
      console.log(`[AI_LEARNING_ORCHESTRATOR] ✅ AI learning cycle completed successfully`);
      console.log(`[AI_LEARNING_ORCHESTRATOR] 🔗 PR created: ${approvalResult.prUrl}`);
      console.log(`[AI_LEARNING_ORCHESTRATOR] 📋 Approval ID: ${approvalResult.approvalId}`);
      
      return {
        success: true,
        insightsCount: learningData.insights?.length || 0,
        updatesCount: codeUpdates.length,
        fileUpdated: codeUpdateResult.success,
        approvalId: approvalResult.approvalId,
        prUrl: approvalResult.prUrl,
        message: 'AI improvement submitted for user approval',
        aiFiles: aiFiles.map(f => ({ path: f.path, priority: f.priority }))
      };
      
    } catch (error) {
      console.error(`[AI_LEARNING_ORCHESTRATOR] ❌ Error in AI learning cycle for ${aiType}:`, error);
      
      // Log the error
      await this.logLearningError(aiType, proposal, result, error);
      
      throw error;
    }
  }

  /**
   * Generate code updates from learning data with file context
   */
  async generateCodeUpdatesFromLearning(aiType, proposal, result, learningData) {
    console.log(`[AI_LEARNING_ORCHESTRATOR] 🔍 Generated ${learningData.insights?.length || 0} code updates for ${aiType}`);
    
    const updates = [];
    
    // Get AI-specific files for context
    const aiFiles = AppFileMappingService.getAIFiles(aiType);
    const highPriorityFiles = aiFiles.filter(f => f.priority === 'high');
    
    console.log(`[AI_LEARNING_ORCHESTRATOR] 🎯 High priority files for ${aiType}:`);
    highPriorityFiles.forEach(file => {
      console.log(`  - ${file.path}: ${file.description}`);
    });
    
    // Process insights with file context
    if (learningData.insights) {
      learningData.insights.forEach((insight, index) => {
        // Find appropriate file for this insight
        const targetFile = this.findBestFileForInsight(insight, aiFiles);
        
        updates.push({
          id: `update-${Date.now()}-${index}`,
          type: insight.type || 'improvement',
          priority: this.calculatePriority(insight),
          description: insight.content,
          source: insight.source,
          targetFile: targetFile?.path || 'unknown',
          applied: false
        });
      });
    }
    
    // Process recommendations with file context
    if (learningData.recommendations) {
      learningData.recommendations.forEach((rec, index) => {
        const targetFile = this.findBestFileForRecommendation(rec, aiFiles);
        
        updates.push({
          id: `rec-${Date.now()}-${index}`,
          type: rec.type || 'recommendation',
          priority: this.calculatePriority(rec),
          description: rec.description,
          source: rec.source,
          targetFile: targetFile?.path || 'unknown',
          applied: false
        });
      });
    }
    
    return updates;
  }

  /**
   * Find the best file for an insight
   */
  findBestFileForInsight(insight, aiFiles) {
    // Try to match insight content with file purposes
    const insightText = insight.content.toLowerCase();
    
    // Look for specific keywords that match file purposes
    for (const file of aiFiles) {
      const purpose = file.purpose.toLowerCase();
      const description = file.description.toLowerCase();
      
      if (insightText.includes('performance') && (purpose.includes('performance') || description.includes('performance'))) {
        return file;
      }
      if (insightText.includes('security') && (purpose.includes('security') || description.includes('security'))) {
        return file;
      }
      if (insightText.includes('learning') && (purpose.includes('learning') || description.includes('learning'))) {
        return file;
      }
      if (insightText.includes('notification') && (purpose.includes('notification') || description.includes('notification'))) {
        return file;
      }
    }
    
    // Default to high priority backend service file
    return aiFiles.find(f => f.type === 'backend' && f.priority === 'high') || aiFiles[0];
  }

  /**
   * Find the best file for a recommendation
   */
  findBestFileForRecommendation(recommendation, aiFiles) {
    const recText = recommendation.description.toLowerCase();
    
    // Similar logic to insight matching
    for (const file of aiFiles) {
      const purpose = file.purpose.toLowerCase();
      const description = file.description.toLowerCase();
      
      if (recText.includes('performance') && (purpose.includes('performance') || description.includes('performance'))) {
        return file;
      }
      if (recText.includes('security') && (purpose.includes('security') || description.includes('security'))) {
        return file;
      }
      if (recText.includes('learning') && (purpose.includes('learning') || description.includes('learning'))) {
        return file;
      }
    }
    
    return aiFiles.find(f => f.type === 'backend' && f.priority === 'high') || aiFiles[0];
  }

  /**
   * Calculate update priority
   */
  calculatePriority(item) {
    if (item.type === 'error_pattern' || item.type === 'security') return 'high';
    if (item.type === 'performance' || item.type === 'best_practice') return 'medium';
    return 'low';
  }

  /**
   * Log learning cycle
   */
  async logLearningCycle(aiType, proposal, result, learningData, updates, status) {
    try {
      const learning = new Learning({
        aiType,
        proposalId: proposal._id,
        status,
        feedbackReason: proposal.userFeedbackReason || 'AI learning cycle',
        learningKey: 'internet_learning',
        learningValue: JSON.stringify({
          insights: learningData.insights?.length || 0,
          recommendations: learningData.recommendations?.length || 0,
          updates: updates.length,
          sources: learningData.sources?.length || 0
        }),
        filePath: proposal.filePath,
        improvementType: proposal.improvementType
      });
      
      await learning.save();
      console.log(`[AI_LEARNING_ORCHESTRATOR] 📝 Logged learning cycle for ${aiType}: ${updates.length} updates applied`);
      
    } catch (error) {
      console.error(`[AI_LEARNING_ORCHESTRATOR] ❌ Failed to log learning cycle:`, error);
    }
  }

  /**
   * Log learning error
   */
  async logLearningError(aiType, proposal, result, error) {
    try {
      const learning = new Learning({
        aiType,
        proposalId: proposal._id,
        status: 'learning-failed',
        feedbackReason: error.message,
        learningKey: 'error',
        learningValue: JSON.stringify({
          error: error.message,
          stack: error.stack
        }),
        filePath: proposal.filePath,
        improvementType: proposal.improvementType
      });
      
      await learning.save();
      console.log(`[AI_LEARNING_ORCHESTRATOR] ❌ Learning cycle failed for ${aiType}: ${error.message}`);
      
    } catch (logError) {
      console.error(`[AI_LEARNING_ORCHESTRATOR] ❌ Failed to log learning error:`, logError);
    }
  }

  /**
   * Get learning cycle statistics
   */
  async getLearningCycleStats(aiType, days = 7) {
    try {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - days);
      
      const cycles = await Learning.find({
        aiType,
        createdAt: { $gte: cutoffDate }
      }).sort({ createdAt: -1 });
      
      const totalCycles = cycles.length;
      const successfulCycles = cycles.filter(c => c.status === 'submitted-for-approval').length;
      const successRate = totalCycles > 0 ? Math.round((successfulCycles / totalCycles) * 100) : 0;
      
      // Calculate average insights per cycle
      let totalInsights = 0;
      cycles.forEach(cycle => {
        try {
          const data = JSON.parse(cycle.learningValue);
          totalInsights += data.insights || 0;
        } catch (e) {
          // Ignore parsing errors
        }
      });
      
      const averageInsightsPerCycle = totalCycles > 0 ? Math.round(totalInsights / totalCycles) : 0;
      
      // Get recent activity
      const recentActivity = cycles.slice(0, 5).map(cycle => ({
        date: cycle.createdAt,
        status: cycle.status,
        insights: (() => {
          try {
            const data = JSON.parse(cycle.learningValue);
            return data.insights || 0;
          } catch (e) {
            return 0;
          }
        })()
      }));
      
      return {
        totalCycles,
        successfulCycles,
        successRate,
        averageInsightsPerCycle,
        recentActivity
      };
      
    } catch (error) {
      console.error(`[AI_LEARNING_ORCHESTRATOR] ❌ Error getting learning stats:`, error);
      return {
        totalCycles: 0,
        successfulCycles: 0,
        successRate: 0,
        averageInsightsPerCycle: 0,
        recentActivity: []
      };
    }
  }

  /**
   * Get pending approvals
   */
  async getPendingApprovals() {
    return await ApprovalService.getPendingApprovals();
  }

  /**
   * Approve an improvement
   */
  async approveImprovement(approvalId, userId, comments = '') {
    return await ApprovalService.approveImprovement(approvalId, userId, comments);
  }

  /**
   * Reject an improvement
   */
  async rejectImprovement(approvalId, userId, reason = '') {
    return await ApprovalService.rejectImprovement(approvalId, userId, reason);
  }
}

module.exports = new AILearningOrchestrator(); 