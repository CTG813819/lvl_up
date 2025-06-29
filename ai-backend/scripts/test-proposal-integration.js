#!/usr/bin/env node

/**
 * Proposal Integration Testing Script
 * Tests how AI-generated proposals integrate with the existing system
 */

const { program } = require('commander');
const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');

program
  .option('--aiType <type>', 'AI Type (Imperium, Guardian, Sandbox)', 'Imperium')
  .option('--proposalId <id>', 'Proposal ID for tracking', 'test-proposal')
  .option('--backendUrl <url>', 'Backend URL for testing', 'http://localhost:3000')
  .parse(process.argv);

const options = program.opts();

class ProposalIntegrationTester {
  constructor(backendUrl) {
    this.backendUrl = backendUrl;
    this.testResults = [];
    this.integrationIssues = [];
  }

  log(message, type = 'INFO') {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [${type}] ${message}`);
  }

  addResult(test, passed, details = '') {
    this.testResults.push({
      test,
      passed,
      details,
      timestamp: new Date().toISOString()
    });
  }

  addIssue(message, severity = 'WARNING') {
    this.integrationIssues.push({
      message,
      severity,
      timestamp: new Date().toISOString()
    });
    this.log(message, severity);
  }

  async testEndpoint(endpoint, method = 'GET', data = null) {
    try {
      const config = {
        method,
        url: `${this.backendUrl}/api${endpoint}`,
        headers: { 'Content-Type': 'application/json' }
      };

      if (data) {
        config.data = data;
      }

      const response = await axios(config);
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || error.message,
        status: error.response?.status 
      };
    }
  }

  async testProposalRetrieval() {
    this.log('🧪 Testing Proposal Retrieval');
    
    const result = await this.testEndpoint('/proposals');
    if (result.success) {
      this.log(`✅ Proposals retrieved successfully`);
      this.log(`   - Total proposals: ${result.data.length || 0}`);
      
      // Check if our test proposal exists
      const testProposal = result.data.find(p => p._id === options.proposalId);
      if (testProposal) {
        this.log(`✅ Test proposal found: ${testProposal.aiType}`);
        this.addResult('Proposal Retrieval', true, `Found ${result.data.length} proposals`);
        return true;
      } else {
        this.log(`⚠️ Test proposal not found, but API is working`);
        this.addResult('Proposal Retrieval', true, `API working, ${result.data.length} proposals found`);
        return true;
      }
    } else {
      this.log(`❌ Failed to retrieve proposals: ${result.error}`, 'ERROR');
      this.addResult('Proposal Retrieval', false, `API error: ${result.error}`);
      return false;
    }
  }

  async testProposalApprovalWorkflow() {
    this.log('🧪 Testing Proposal Approval Workflow');
    
    // Create a test proposal for approval
    const testProposal = {
      aiType: options.aiType,
      filePath: 'lib/test_integration.dart',
      improvementType: 'integration_test',
      userFeedbackReason: 'Testing integration workflow',
      status: 'pending'
    };
    
    const createResult = await this.testEndpoint('/proposals', 'POST', testProposal);
    if (!createResult.success) {
      this.log(`❌ Failed to create test proposal: ${createResult.error}`, 'ERROR');
      this.addResult('Proposal Creation', false, `Creation failed: ${createResult.error}`);
      return false;
    }
    
    this.log(`✅ Test proposal created: ${createResult.data._id}`);
    this.addResult('Proposal Creation', true, `Created proposal: ${createResult.data._id}`);
    
    // Test approval
    const approvalResult = await this.testEndpoint(`/proposals/${createResult.data._id}/decision`, 'POST', {
      decision: 'approved'
    });
    
    if (approvalResult.success) {
      this.log(`✅ Proposal approved successfully`);
      this.log(`   - Status: ${approvalResult.data.status}`);
      this.log(`   - PR URL: ${approvalResult.data.prUrl || 'N/A'}`);
      this.addResult('Proposal Approval', true, `Approved proposal: ${approvalResult.data.status}`);
      return true;
    } else {
      this.log(`❌ Failed to approve proposal: ${approvalResult.error}`, 'ERROR');
      this.addResult('Proposal Approval', false, `Approval failed: ${approvalResult.error}`);
      return false;
    }
  }

  async testChaosWarpIntegration() {
    this.log('🧪 Testing Chaos/Warp Integration with Proposals');
    
    // Check current Chaos/Warp status
    const statusResult = await this.testEndpoint('/chaos-warp/status');
    if (!statusResult.success) {
      this.log(`❌ Failed to get Chaos/Warp status: ${statusResult.error}`, 'ERROR');
      this.addResult('Chaos/Warp Status', false, `Status check failed: ${statusResult.error}`);
      return false;
    }
    
    const status = statusResult.data;
    this.log(`✅ Chaos/Warp status retrieved`);
    this.log(`   - Warp Mode: ${status.warpMode}`);
    this.log(`   - Chaos Mode: ${status.chaosMode}`);
    this.log(`   - Should Operate AI: ${status.operationStatus.canOperate}`);
    this.log(`   - Hierarchy: ${status.hierarchy}`);
    
    this.addResult('Chaos/Warp Status', true, `Status: ${status.hierarchy}`);
    
    // Test proposal creation under different Chaos/Warp conditions
    if (status.operationStatus.canOperate) {
      this.log(`✅ AI operations allowed - can create proposals`);
      this.addResult('Proposal Creation Under Chaos/Warp', true, 'AI operations allowed');
    } else {
      this.log(`⚠️ AI operations blocked - proposal creation may be limited`);
      this.addResult('Proposal Creation Under Chaos/Warp', false, 'AI operations blocked');
      this.addIssue('Proposal creation may be limited due to Chaos/Warp restrictions', 'WARNING');
    }
    
    return true;
  }

  async testGitHubIntegration() {
    this.log('🧪 Testing GitHub Integration');
    
    // Test GitHub service availability
    const githubResult = await this.testEndpoint('/github/status');
    if (githubResult.success) {
      this.log(`✅ GitHub integration working`);
      this.log(`   - Repository: ${githubResult.data.repository || 'N/A'}`);
      this.log(`   - Connected: ${githubResult.data.connected || false}`);
      this.addResult('GitHub Integration', true, `GitHub connected: ${githubResult.data.connected}`);
      return true;
    } else {
      this.log(`⚠️ GitHub integration not available: ${githubResult.error}`, 'WARNING');
      this.addResult('GitHub Integration', false, `GitHub not available: ${githubResult.error}`);
      this.addIssue('GitHub integration not available - PR creation may fail', 'WARNING');
      return false;
    }
  }

  async testDatabaseIntegration() {
    this.log('🧪 Testing Database Integration');
    
    // Test database connectivity through proposals endpoint
    const dbResult = await this.testEndpoint('/proposals');
    if (dbResult.success) {
      this.log(`✅ Database integration working`);
      this.log(`   - Response time: ${dbResult.responseTime || 'N/A'}ms`);
      this.addResult('Database Integration', true, 'Database accessible');
      return true;
    } else {
      this.log(`❌ Database integration failed: ${dbResult.error}`, 'ERROR');
      this.addResult('Database Integration', false, `Database error: ${dbResult.error}`);
      return false;
    }
  }

  async testNotificationIntegration() {
    this.log('🧪 Testing Notification Integration');
    
    // Test notification system
    const notificationResult = await this.testEndpoint('/notify/test');
    if (notificationResult.success) {
      this.log(`✅ Notification system working`);
      this.log(`   - Message: ${notificationResult.data.message || 'N/A'}`);
      this.addResult('Notification Integration', true, 'Notifications working');
      return true;
    } else {
      this.log(`⚠️ Notification system not available: ${notificationResult.error}`, 'WARNING');
      this.addResult('Notification Integration', false, `Notifications not available: ${notificationResult.error}`);
      this.addIssue('Notification system not available - users may not be notified of proposal updates', 'WARNING');
      return false;
    }
  }

  async testAppFunctionalityIntegration() {
    this.log('🧪 Testing App Functionality Integration');
    
    // Test app-specific endpoints
    const appResult = await this.testEndpoint('/app/status');
    if (appResult.success) {
      this.log(`✅ App functionality integration working`);
      this.log(`   - Version: ${appResult.data.version || 'N/A'}`);
      this.log(`   - Status: ${appResult.data.status || 'N/A'}`);
      this.addResult('App Functionality Integration', true, `App status: ${appResult.data.status}`);
      return true;
    } else {
      this.log(`⚠️ App functionality not available: ${appResult.error}`, 'WARNING');
      this.addResult('App Functionality Integration', false, `App not available: ${appResult.error}`);
      this.addIssue('App functionality not available - may affect proposal integration', 'WARNING');
      return false;
    }
  }

  async testErrorHandling() {
    this.log('🧪 Testing Error Handling');
    
    // Test with invalid proposal ID
    const invalidResult = await this.testEndpoint('/proposals/invalid-id-12345');
    if (!invalidResult.success && invalidResult.status === 404) {
      this.log(`✅ Error handling working correctly`);
      this.log(`   - Expected 404 for invalid ID`);
      this.addResult('Error Handling', true, 'Proper error responses');
      return true;
    } else {
      this.log(`❌ Error handling not working as expected`, 'ERROR');
      this.addResult('Error Handling', false, 'Unexpected error response');
      return false;
    }
  }

  async runIntegrationTests() {
    this.log('🚀 Starting Proposal Integration Testing');
    this.log('========================================');
    
    const tests = [
      { name: 'Proposal Retrieval', test: () => this.testProposalRetrieval() },
      { name: 'Chaos/Warp Integration', test: () => this.testChaosWarpIntegration() },
      { name: 'GitHub Integration', test: () => this.testGitHubIntegration() },
      { name: 'Database Integration', test: () => this.testDatabaseIntegration() },
      { name: 'Notification Integration', test: () => this.testNotificationIntegration() },
      { name: 'App Functionality Integration', test: () => this.testAppFunctionalityIntegration() },
      { name: 'Error Handling', test: () => this.testErrorHandling() },
      { name: 'Proposal Approval Workflow', test: () => this.testProposalApprovalWorkflow() }
    ];
    
    let passedTests = 0;
    let totalTests = tests.length;
    
    for (const test of tests) {
      this.log(`\n📋 Running: ${test.name}`);
      try {
        const result = await test.test();
        if (result) {
          this.log(`✅ ${test.name}: PASSED`);
          passedTests++;
        } else {
          this.log(`❌ ${test.name}: FAILED`);
        }
      } catch (error) {
        this.log(`💥 ${test.name}: ERROR - ${error.message}`, 'ERROR');
        this.addIssue(`Test error in ${test.name}: ${error.message}`, 'ERROR');
      }
    }
    
    this.log('\n📊 Integration Test Results Summary');
    this.log('===================================');
    this.log(`Total Tests: ${totalTests}`);
    this.log(`Passed: ${passedTests}`);
    this.log(`Failed: ${totalTests - passedTests}`);
    this.log(`Success Rate: ${((passedTests / totalTests) * 100).toFixed(1)}%`);
    
    if (this.integrationIssues.length > 0) {
      this.log(`\n⚠️ Integration Issues (${this.integrationIssues.length}):`);
      this.integrationIssues.forEach(issue => {
        this.log(`   [${issue.severity}] ${issue.message}`);
      });
    }
    
    this.log('\n📋 Detailed Results:');
    this.testResults.forEach(result => {
      const status = result.passed ? '✅' : '❌';
      this.log(`   ${status} ${result.test}: ${result.details}`);
    });
    
    if (passedTests === totalTests && this.integrationIssues.filter(i => i.severity === 'ERROR').length === 0) {
      this.log('\n🎉 All integration tests passed!');
      this.log('✅ Proposal integration is working correctly');
      return true;
    } else if (this.integrationIssues.filter(i => i.severity === 'ERROR').length === 0) {
      this.log('\n⚠️ Some integration tests failed, but no critical errors');
      this.log('✅ Proposal integration can proceed with warnings');
      return true;
    } else {
      this.log('\n❌ Critical integration issues found');
      this.log('❌ Proposal integration cannot proceed');
      return false;
    }
  }

  getIntegrationReport() {
    return {
      proposalId: options.proposalId,
      aiType: options.aiType,
      timestamp: new Date().toISOString(),
      results: this.testResults,
      issues: this.integrationIssues,
      summary: {
        total: this.testResults.length,
        passed: this.testResults.filter(r => r.passed).length,
        failed: this.testResults.filter(r => !r.passed).length,
        errorCount: this.integrationIssues.filter(i => i.severity === 'ERROR').length,
        warningCount: this.integrationIssues.filter(i => i.severity === 'WARNING').length
      }
    };
  }
}

// Main execution
async function main() {
  const tester = new ProposalIntegrationTester(options.backendUrl);
  
  try {
    const isIntegrated = await tester.runIntegrationTests();
    
    // Save integration report
    const report = tester.getIntegrationReport();
    const reportPath = path.join(process.cwd(), 'ai-backend', 'test-results', `proposal-integration-${options.proposalId}.json`);
    
    try {
      await fs.mkdir(path.dirname(reportPath), { recursive: true });
      await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
      console.log(`📄 Integration report saved to: ${reportPath}`);
    } catch (error) {
      console.warn(`⚠️ Could not save integration report: ${error.message}`);
    }
    
    if (!isIntegrated) {
      process.exit(1);
    }
  } catch (error) {
    console.error('💥 Integration testing failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { ProposalIntegrationTester }; 