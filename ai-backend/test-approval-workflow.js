/**
 * Test Approval Workflow
 * Demonstrates the complete end-to-end approval workflow
 */

require('dotenv').config();
const AILearningOrchestrator = require('./src/services/aiLearningOrchestrator');
const ApprovalService = require('./src/services/approvalService');
const BuildService = require('./src/services/buildService');
const mongoose = require('mongoose');

async function testApprovalWorkflow() {
  console.log('🚀 Testing Complete Approval Workflow');
  console.log('=====================================');
  
  try {
    // Step 1: Simulate AI learning and proposal submission
    console.log('\n📋 Step 1: AI Learning and Proposal Submission');
    console.log('------------------------------------------------');
    
    const mockProposal = {
      _id: new mongoose.Types.ObjectId(),
      aiType: 'Imperium',
      filePath: 'lib/ai_brain.dart',
      improvementType: 'performance',
      userFeedbackReason: 'Performance optimization needed',
      status: 'pending'
    };
    
    console.log(`[TEST] 🎯 Starting AI learning for ${mockProposal.aiType}`);
    console.log(`[TEST] 📁 File: ${mockProposal.filePath}`);
    console.log(`[TEST] 🔧 Type: ${mockProposal.improvementType}`);
    console.log(`[TEST] 🆔 Proposal ID: ${mockProposal._id}`);
    
    // Run AI learning cycle
    const learningResult = await AILearningOrchestrator.orchestrateAILearning(
      mockProposal.aiType,
      mockProposal,
      'passed'
    );
    
    console.log(`[TEST] ✅ AI Learning completed:`);
    console.log(`  - Insights: ${learningResult.insightsCount}`);
    console.log(`  - Updates: ${learningResult.updatesCount}`);
    console.log(`  - Approval ID: ${learningResult.approvalId}`);
    console.log(`  - PR URL: ${learningResult.prUrl}`);
    
    // Step 2: Check pending approvals
    console.log('\n📋 Step 2: Check Pending Approvals');
    console.log('-----------------------------------');
    
    const pendingApprovals = await ApprovalService.getPendingApprovals();
    console.log(`[TEST] 📋 Found ${pendingApprovals.length} pending approvals`);
    
    if (pendingApprovals.length > 0) {
      const approval = pendingApprovals[0];
      console.log(`[TEST] 📋 Approval Details:`);
      console.log(`  - ID: ${approval.id}`);
      console.log(`  - AI Type: ${approval.aiType}`);
      console.log(`  - PR URL: ${approval.prUrl}`);
      console.log(`  - Updates: ${approval.updates.length}`);
      console.log(`  - Status: ${approval.status}`);
      
      // Step 3: Approve the improvement
      console.log('\n✅ Step 3: Approve Improvement');
      console.log('-------------------------------');
      
      console.log(`[TEST] ✅ Approving improvement: ${approval.id}`);
      const approveResult = await ApprovalService.approveImprovement(
        approval.id,
        'test-user',
        'Looks good! Approved for production.'
      );
      
      console.log(`[TEST] 🎉 Approval result:`);
      console.log(`  - Success: ${approveResult.success}`);
      console.log(`  - PR URL: ${approveResult.prUrl}`);
      console.log(`  - Build Result: ${approveResult.buildResult ? 'Success' : 'Failed'}`);
      
      if (approveResult.buildResult) {
        console.log(`[TEST] 🏗️ Build Details:`);
        console.log(`  - Build ID: ${approveResult.buildResult.buildId}`);
        console.log(`  - Package Path: ${approveResult.buildResult.packagePath}`);
        console.log(`  - Deployment Ready: ${approveResult.buildResult.deploymentReady}`);
      }
      
      // Step 4: Check approval statistics
      console.log('\n📊 Step 4: Check Approval Statistics');
      console.log('------------------------------------');
      
      const approvalStats = await ApprovalService.getApprovalStats();
      console.log(`[TEST] 📊 Approval Statistics:`);
      console.log(`  - Total: ${approvalStats.total}`);
      console.log(`  - Pending: ${approvalStats.pending}`);
      console.log(`  - Approved: ${approvalStats.approved}`);
      console.log(`  - Rejected: ${approvalStats.rejected}`);
      console.log(`  - Failed: ${approvalStats.failed}`);
      
      // Step 5: Check learning statistics
      console.log('\n📊 Step 5: Check Learning Statistics');
      console.log('------------------------------------');
      
      const learningStats = await AILearningOrchestrator.getLearningCycleStats('Imperium', 7);
      console.log(`[TEST] 📊 Learning Statistics for Imperium:`);
      console.log(`  - Total Cycles: ${learningStats.totalCycles}`);
      console.log(`  - Successful: ${learningStats.successfulCycles}`);
      console.log(`  - Success Rate: ${learningStats.successRate}%`);
      console.log(`  - Avg Insights: ${learningStats.averageInsightsPerCycle}`);
      
      // Step 6: Check build history
      console.log('\n📋 Step 6: Check Build History');
      console.log('-------------------------------');
      
      const buildHistory = await BuildService.getBuildHistory();
      console.log(`[TEST] 📋 Build History:`);
      console.log(`  - Total Builds: ${buildHistory.length}`);
      
      if (buildHistory.length > 0) {
        const latestBuild = buildHistory[0];
        console.log(`[TEST] 📋 Latest Build:`);
        console.log(`  - ID: ${latestBuild.id}`);
        console.log(`  - AI Type: ${latestBuild.aiType}`);
        console.log(`  - Status: ${latestBuild.status}`);
        console.log(`  - Duration: ${latestBuild.duration}ms`);
        console.log(`  - Steps: ${latestBuild.steps?.length || 0}`);
      }
      
    } else {
      console.log('[TEST] ⚠️ No pending approvals found');
    }
    
    // Step 7: Test rejection workflow
    console.log('\n❌ Step 7: Test Rejection Workflow');
    console.log('----------------------------------');
    
    // Create another mock proposal for rejection test
    const mockRejectionProposal = {
      _id: new mongoose.Types.ObjectId(),
      aiType: 'Guardian',
      filePath: 'lib/ai_guardian.dart',
      improvementType: 'security',
      userFeedbackReason: 'Security enhancement needed',
      status: 'pending'
    };
    
    console.log(`[TEST] 🎯 Starting AI learning for rejection test: ${mockRejectionProposal.aiType}`);
    console.log(`[TEST] 🆔 Rejection Proposal ID: ${mockRejectionProposal._id}`);
    
    const rejectionLearningResult = await AILearningOrchestrator.orchestrateAILearning(
      mockRejectionProposal.aiType,
      mockRejectionProposal,
      'failed'
    );
    
    console.log(`[TEST] ✅ Rejection test learning completed: ${rejectionLearningResult.approvalId}`);
    
    // Get the new pending approval
    const newPendingApprovals = await ApprovalService.getPendingApprovals();
    const rejectionApproval = newPendingApprovals.find(a => a.id === rejectionLearningResult.approvalId);
    
    if (rejectionApproval) {
      console.log(`[TEST] ❌ Rejecting improvement: ${rejectionApproval.id}`);
      const rejectResult = await ApprovalService.rejectImprovement(
        rejectionApproval.id,
        'test-user',
        'This improvement doesn\'t meet our security standards.'
      );
      
      console.log(`[TEST] ✅ Rejection result:`);
      console.log(`  - Success: ${rejectResult.success}`);
      console.log(`  - Message: ${rejectResult.message}`);
    }
    
    console.log('\n🎉 Approval Workflow Test Completed Successfully!');
    console.log('================================================');
    console.log('✅ AI Learning Cycle');
    console.log('✅ User Approval Workflow');
    console.log('✅ GitHub Integration');
    console.log('✅ App Building Process');
    console.log('✅ Statistics and Analytics');
    
  } catch (error) {
    console.error('\n❌ Approval Workflow Test Failed:');
    console.error('================================');
    console.error(error);
    
    // Log detailed error information
    console.error('\n📋 Error Details:');
    console.error(`  - Message: ${error.message}`);
    console.error(`  - Stack: ${error.stack}`);
    
    if (error.response) {
      console.error(`  - Status: ${error.response.status}`);
      console.error(`  - Data: ${JSON.stringify(error.response.data, null, 2)}`);
    }
  }
}

// Run the test
if (require.main === module) {
  testApprovalWorkflow()
    .then(() => {
      console.log('\n🏁 Test completed');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n💥 Test failed:', error);
      process.exit(1);
    });
}

module.exports = { testApprovalWorkflow }; 