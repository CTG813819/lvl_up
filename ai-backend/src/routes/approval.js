const express = require('express');
const router = express.Router();
const ApprovalService = require('../services/approvalService');
const AILearningOrchestrator = require('../services/aiLearningOrchestrator');

/**
 * Get all pending approvals
 */
router.get('/pending', async (req, res) => {
  try {
    console.log(`[APPROVAL_ROUTE] 📋 Getting pending approvals`);
    
    const pendingApprovals = await ApprovalService.getPendingApprovals();
    
    console.log(`[APPROVAL_ROUTE] ✅ Found ${pendingApprovals.length} pending approvals`);
    
    res.json({
      success: true,
      approvals: pendingApprovals,
      count: pendingApprovals.length
    });
    
  } catch (error) {
    console.error(`[APPROVAL_ROUTE] ❌ Error getting pending approvals:`, error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get approval details
 */
router.get('/:approvalId', async (req, res) => {
  try {
    const { approvalId } = req.params;
    console.log(`[APPROVAL_ROUTE] 📋 Getting approval details: ${approvalId}`);
    
    const approval = await ApprovalService.getApprovalDetails(approvalId);
    
    if (!approval) {
      return res.status(404).json({
        success: false,
        error: 'Approval not found'
      });
    }
    
    console.log(`[APPROVAL_ROUTE] ✅ Found approval: ${approvalId}`);
    
    res.json({
      success: true,
      approval
    });
    
  } catch (error) {
    console.error(`[APPROVAL_ROUTE] ❌ Error getting approval details:`, error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Approve an improvement
 */
router.post('/:approvalId/approve', async (req, res) => {
  try {
    const { approvalId } = req.params;
    const { userId, comments } = req.body;
    
    console.log(`[APPROVAL_ROUTE] ✅ Approving improvement: ${approvalId}`);
    console.log(`[APPROVAL_ROUTE] 👤 User: ${userId}`);
    console.log(`[APPROVAL_ROUTE] 💬 Comments: ${comments || 'None'}`);
    
    const result = await ApprovalService.approveImprovement(approvalId, userId, comments);
    
    console.log(`[APPROVAL_ROUTE] 🎉 Improvement approved successfully`);
    console.log(`[APPROVAL_ROUTE] 🏗️ Build result: ${result.buildResult ? 'Success' : 'Failed'}`);
    
    res.json({
      success: true,
      message: 'Improvement approved and app built successfully',
      result
    });
    
  } catch (error) {
    console.error(`[APPROVAL_ROUTE] ❌ Error approving improvement:`, error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Reject an improvement
 */
router.post('/:approvalId/reject', async (req, res) => {
  try {
    const { approvalId } = req.params;
    const { userId, reason } = req.body;
    
    console.log(`[APPROVAL_ROUTE] ❌ Rejecting improvement: ${approvalId}`);
    console.log(`[APPROVAL_ROUTE] 👤 User: ${userId}`);
    console.log(`[APPROVAL_ROUTE] 📝 Reason: ${reason || 'No reason provided'}`);
    
    const result = await ApprovalService.rejectImprovement(approvalId, userId, reason);
    
    console.log(`[APPROVAL_ROUTE] ✅ Improvement rejected successfully`);
    
    res.json({
      success: true,
      message: 'Improvement rejected',
      result
    });
    
  } catch (error) {
    console.error(`[APPROVAL_ROUTE] ❌ Error rejecting improvement:`, error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get approval statistics
 */
router.get('/stats/overview', async (req, res) => {
  try {
    console.log(`[APPROVAL_ROUTE] 📊 Getting approval statistics`);
    
    const stats = await ApprovalService.getApprovalStats();
    
    console.log(`[APPROVAL_ROUTE] ✅ Approval stats:`, stats);
    
    res.json({
      success: true,
      stats
    });
    
  } catch (error) {
    console.error(`[APPROVAL_ROUTE] ❌ Error getting approval stats:`, error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get learning cycle statistics
 */
router.get('/stats/learning/:aiType', async (req, res) => {
  try {
    const { aiType } = req.params;
    const { days } = req.query;
    
    console.log(`[APPROVAL_ROUTE] 📊 Getting learning stats for ${aiType} (${days || 7} days)`);
    
    const stats = await AILearningOrchestrator.getLearningCycleStats(aiType, parseInt(days) || 7);
    
    console.log(`[APPROVAL_ROUTE] ✅ Learning stats for ${aiType}:`, stats);
    
    res.json({
      success: true,
      aiType,
      stats
    });
    
  } catch (error) {
    console.error(`[APPROVAL_ROUTE] ❌ Error getting learning stats:`, error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get build history
 */
router.get('/builds/history', async (req, res) => {
  try {
    console.log(`[APPROVAL_ROUTE] 📋 Getting build history`);
    
    const BuildService = require('../services/buildService');
    const buildHistory = await BuildService.getBuildHistory();
    
    console.log(`[APPROVAL_ROUTE] ✅ Found ${buildHistory.length} builds`);
    
    res.json({
      success: true,
      builds: buildHistory,
      count: buildHistory.length
    });
    
  } catch (error) {
    console.error(`[APPROVAL_ROUTE] ❌ Error getting build history:`, error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get build details
 */
router.get('/builds/:buildId', async (req, res) => {
  try {
    const { buildId } = req.params;
    console.log(`[APPROVAL_ROUTE] 📋 Getting build details: ${buildId}`);
    
    const BuildService = require('../services/buildService');
    const build = await BuildService.getBuildDetails(buildId);
    
    if (!build) {
      return res.status(404).json({
        success: false,
        error: 'Build not found'
      });
    }
    
    console.log(`[APPROVAL_ROUTE] ✅ Found build: ${buildId}`);
    
    res.json({
      success: true,
      build
    });
    
  } catch (error) {
    console.error(`[APPROVAL_ROUTE] ❌ Error getting build details:`, error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

module.exports = router; 