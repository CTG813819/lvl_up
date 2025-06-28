const mongoose = require('mongoose');
const GitHubService = require('./githubService');
const BuildService = require('./buildService');

/**
 * User Approval Service
 * Manages the workflow for AI improvements requiring user approval
 */
class ApprovalService {
  constructor() {
    this.pendingApprovals = new Map();
  }

  /**
   * Submit AI improvement for user approval
   */
  async submitForApproval(aiType, updates, learningData, proposalId) {
    console.log(`[APPROVAL] 📋 Submitting AI improvement for ${aiType} approval`);
    
    try {
      // Push to GitHub and create PR
      const githubResult = await GitHubService.pushAICodeUpdates(aiType, updates, learningData);
      
      if (!githubResult.success) {
        throw new Error('Failed to create GitHub PR');
      }
      
      // Create approval record
      const approvalRecord = {
        id: `approval-${Date.now()}`,
        aiType,
        proposalId,
        prUrl: githubResult.prUrl,
        prNumber: githubResult.prNumber,
        branch: githubResult.branch,
        updates: updates,
        learningData: learningData,
        status: 'pending',
        submittedAt: new Date(),
        filePath: githubResult.filePath,
        isNewFile: githubResult.isNewFile || false,
        commitMessage: githubResult.commitMessage
      };
      
      // Store approval record
      this.pendingApprovals.set(approvalRecord.id, approvalRecord);
      
      console.log(`[APPROVAL] ✅ Approval submitted: ${approvalRecord.id}`);
      console.log(`[APPROVAL] 🔗 PR URL: ${approvalRecord.prUrl}`);
      
      return {
        success: true,
        approvalId: approvalRecord.id,
        prUrl: approvalRecord.prUrl,
        message: `AI improvement submitted for approval. PR created: ${approvalRecord.prUrl}`
      };
      
    } catch (error) {
      console.error(`[APPROVAL] ❌ Error submitting for approval:`, error);
      throw error;
    }
  }

  /**
   * Get pending approvals
   */
  async getPendingApprovals() {
    const pending = Array.from(this.pendingApprovals.values())
      .filter(approval => approval.status === 'pending');
    
    console.log(`[APPROVAL] 📋 Found ${pending.length} pending approvals`);
    return pending;
  }

  /**
   * Approve an AI improvement
   */
  async approveImprovement(approvalId, userId, comments = '') {
    console.log(`[APPROVAL] ✅ Approving improvement: ${approvalId}`);
    
    const approval = this.pendingApprovals.get(approvalId);
    if (!approval) {
      throw new Error(`Approval ${approvalId} not found`);
    }
    
    if (approval.status !== 'pending') {
      throw new Error(`Approval ${approvalId} is not pending`);
    }
    
    try {
      // Update approval status
      approval.status = 'approved';
      approval.approvedBy = userId;
      approval.approvedAt = new Date();
      approval.comments = comments;
      
      // Merge the PR
      console.log(`[APPROVAL] 🔄 Merging PR: ${approval.prNumber}`);
      await GitHubService.mergeAILearningPR(approval.prUrl);
      
      // Build the app if tests pass
      console.log(`[APPROVAL] 🏗️ Building app after approval`);
      const buildResult = await BuildService.buildApp(approval.aiType, approval.updates);
      
      approval.buildResult = buildResult;
      approval.status = 'completed';
      
      console.log(`[APPROVAL] 🎉 Improvement approved and app built successfully`);
      
      return {
        success: true,
        approvalId,
        prUrl: approval.prUrl,
        buildResult,
        message: 'AI improvement approved, PR merged, and app built successfully'
      };
      
    } catch (error) {
      approval.status = 'failed';
      approval.error = error.message;
      
      console.error(`[APPROVAL] ❌ Error approving improvement:`, error);
      throw error;
    }
  }

  /**
   * Reject an AI improvement
   */
  async rejectImprovement(approvalId, userId, reason = '') {
    console.log(`[APPROVAL] ❌ Rejecting improvement: ${approvalId}`);
    
    const approval = this.pendingApprovals.get(approvalId);
    if (!approval) {
      throw new Error(`Approval ${approvalId} not found`);
    }
    
    if (approval.status !== 'pending') {
      throw new Error(`Approval ${approvalId} is not pending`);
    }
    
    // Update approval status
    approval.status = 'rejected';
    approval.rejectedBy = userId;
    approval.rejectedAt = new Date();
    approval.rejectionReason = reason;
    
    // Close the PR
    try {
      await GitHubService.closePR(approval.prNumber);
      console.log(`[APPROVAL] 🔒 PR closed: ${approval.prNumber}`);
    } catch (error) {
      console.warn(`[APPROVAL] ⚠️ Could not close PR: ${error.message}`);
    }
    
    console.log(`[APPROVAL] ✅ Improvement rejected`);
    
    return {
      success: true,
      approvalId,
      message: 'AI improvement rejected'
    };
  }

  /**
   * Get approval details
   */
  async getApprovalDetails(approvalId) {
    const approval = this.pendingApprovals.get(approvalId);
    if (!approval) {
      throw new Error(`Approval ${approvalId} not found`);
    }
    
    return approval;
  }

  /**
   * Get approval statistics
   */
  async getApprovalStats() {
    const approvals = Array.from(this.pendingApprovals.values());
    
    const stats = {
      total: approvals.length,
      pending: approvals.filter(a => a.status === 'pending').length,
      approved: approvals.filter(a => a.status === 'approved' || a.status === 'completed').length,
      rejected: approvals.filter(a => a.status === 'rejected').length,
      failed: approvals.filter(a => a.status === 'failed').length
    };
    
    return stats;
  }
}

module.exports = new ApprovalService(); 