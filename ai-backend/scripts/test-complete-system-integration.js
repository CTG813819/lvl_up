#!/usr/bin/env node

/**
 * Complete System Integration Test
 * Tests the entire system: Chaos/Warp + GitHub Workflow + Proposal Management
 */

const axios = require('axios');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:3000';
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_REPO = process.env.GITHUB_REPO;
const TEST_TIMEOUT = 120000; // 2 minutes

// Test results
const testResults = {
  timestamp: new Date().toISOString(),
  tests: [],
  overall: 'PASSED',
  summary: {
    total: 0,
    passed: 0,
    failed: 0,
    skipped: 0
  },
  systemStatus: {
    chaosWarp: 'UNKNOWN',
    githubWorkflow: 'UNKNOWN',
    proposalSystem: 'UNKNOWN',
    backend: 'UNKNOWN',
    flutter: 'UNKNOWN'
  }
};

/**
 * Test 1: Verify backend connectivity
 */
async function testBackendConnectivity() {
  try {
    console.log('1️⃣ Testing backend connectivity...');
    
    const response = await axios.get(`${BACKEND_URL}/api/health`, {
      timeout: TEST_TIMEOUT
    });
    
    if (response.status === 200) {
      testResults.tests.push({
        test: 'backend_connectivity',
        status: 'PASSED',
        message: 'Backend is accessible and responding',
        details: { status: response.status, data: response.data }
      });
      testResults.summary.passed++;
      testResults.systemStatus.backend = 'ONLINE';
      return true;
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'backend_connectivity',
      status: 'FAILED',
      message: error.message,
      error: error.toString()
    });
    testResults.summary.failed++;
    testResults.overall = 'FAILED';
    testResults.systemStatus.backend = 'OFFLINE';
    return false;
  }
}

/**
 * Test 2: Verify Chaos/Warp system functionality
 */
async function testChaosWarpSystem() {
  try {
    console.log('2️⃣ Testing Chaos/Warp system functionality...');
    
    // Test operational hours
    const operationalResponse = await axios.get(`${BACKEND_URL}/api/chaos-warp/operational-hours`, {
      timeout: TEST_TIMEOUT
    });
    
    if (operationalResponse.status !== 200) {
      throw new Error('Operational hours endpoint not accessible');
    }
    
    // Test status endpoint
    const statusResponse = await axios.get(`${BACKEND_URL}/api/chaos-warp/status`, {
      timeout: TEST_TIMEOUT
    });
    
    if (statusResponse.status !== 200) {
      throw new Error('Status endpoint not accessible');
    }
    
    const statusData = statusResponse.data;
    
    // Verify required fields
    const requiredFields = [
      'chaosMode', 'warpMode', 'operationStatus', 'operationalHours', 'hierarchy'
    ];
    
    const missingFields = requiredFields.filter(field => 
      !(field in statusData)
    );
    
    if (missingFields.length === 0) {
      testResults.tests.push({
        test: 'chaos_warp_system',
        status: 'PASSED',
        message: 'Chaos/Warp system is fully functional',
        details: {
          chaosMode: statusData.chaosMode,
          warpMode: statusData.warpMode,
          hierarchy: statusData.hierarchy,
          operationalHours: statusData.operationalHours
        }
      });
      testResults.summary.passed++;
      testResults.systemStatus.chaosWarp = 'FUNCTIONAL';
      return true;
    } else {
      throw new Error(`Missing fields: ${missingFields.join(', ')}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'chaos_warp_system',
      status: 'FAILED',
      message: error.message,
      error: error.toString()
    });
    testResults.summary.failed++;
    testResults.overall = 'FAILED';
    testResults.systemStatus.chaosWarp = 'FAILED';
    return false;
  }
}

/**
 * Test 3: Verify proposal system functionality
 */
async function testProposalSystem() {
  try {
    console.log('3️⃣ Testing proposal system functionality...');
    
    // Test proposals endpoint
    const response = await axios.get(`${BACKEND_URL}/api/proposals`, {
      timeout: TEST_TIMEOUT
    });
    
    if (response.status === 200) {
      testResults.tests.push({
        test: 'proposal_system',
        status: 'PASSED',
        message: 'Proposal system is accessible',
        details: { 
          status: response.status,
          proposalsCount: Array.isArray(response.data) ? response.data.length : 'N/A'
        }
      });
      testResults.summary.passed++;
      testResults.systemStatus.proposalSystem = 'FUNCTIONAL';
      return true;
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'proposal_system',
      status: 'FAILED',
      message: error.message,
      error: error.toString()
    });
    testResults.summary.failed++;
    testResults.overall = 'FAILED';
    testResults.systemStatus.proposalSystem = 'FAILED';
    return false;
  }
}

/**
 * Test 4: Verify GitHub workflow configuration
 */
async function testGitHubWorkflowConfiguration() {
  try {
    console.log('4️⃣ Testing GitHub workflow configuration...');
    
    const workflowPath = '.github/workflows/ci-cd-pipeline.yml';
    
    if (!fs.existsSync(workflowPath)) {
      throw new Error('GitHub workflow file not found');
    }
    
    const workflowContent = fs.readFileSync(workflowPath, 'utf8');
    
    // Check for required components
    const requiredComponents = [
      'proposal-test',
      'backend-test',
      'flutter-test',
      'security-scan',
      'deploy-production'
    ];
    
    const missingComponents = requiredComponents.filter(component => 
      !workflowContent.includes(component)
    );
    
    if (missingComponents.length === 0) {
      testResults.tests.push({
        test: 'github_workflow_configuration',
        status: 'PASSED',
        message: 'GitHub workflow configuration is complete',
        details: { components: requiredComponents }
      });
      testResults.summary.passed++;
      testResults.systemStatus.githubWorkflow = 'CONFIGURED';
      return true;
    } else {
      throw new Error(`Missing components: ${missingComponents.join(', ')}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'github_workflow_configuration',
      status: 'FAILED',
      message: error.message,
      error: error.toString()
    });
    testResults.summary.failed++;
    testResults.overall = 'FAILED';
    testResults.systemStatus.githubWorkflow = 'MISCONFIGURED';
    return false;
  }
}

/**
 * Test 5: Verify Flutter configuration
 */
async function testFlutterConfiguration() {
  try {
    console.log('5️⃣ Testing Flutter configuration...');
    
    const pubspecPath = 'pubspec.yaml';
    
    if (!fs.existsSync(pubspecPath)) {
      throw new Error('Flutter pubspec.yaml not found');
    }
    
    const pubspecContent = fs.readFileSync(pubspecPath, 'utf8');
    
    // Check for required dependencies
    const requiredDependencies = [
      'flutter:',
      'provider:',
      'http:',
      'shared_preferences:'
    ];
    
    const missingDependencies = requiredDependencies.filter(dep => 
      !pubspecContent.includes(dep)
    );
    
    if (missingDependencies.length === 0) {
      testResults.tests.push({
        test: 'flutter_configuration',
        status: 'PASSED',
        message: 'Flutter configuration is valid',
        details: { dependencies: requiredDependencies }
      });
      testResults.summary.passed++;
      testResults.systemStatus.flutter = 'CONFIGURED';
      return true;
    } else {
      throw new Error(`Missing dependencies: ${missingDependencies.join(', ')}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'flutter_configuration',
      status: 'FAILED',
      message: error.message,
      error: error.toString()
    });
    testResults.summary.failed++;
    testResults.overall = 'FAILED';
    testResults.systemStatus.flutter = 'MISCONFIGURED';
    return false;
  }
}

/**
 * Test 6: Verify Chaos/Warp hierarchy enforcement
 */
async function testChaosWarpHierarchy() {
  try {
    console.log('6️⃣ Testing Chaos/Warp hierarchy enforcement...');
    
    // Get initial status
    const initialStatus = await axios.get(`${BACKEND_URL}/api/chaos-warp/status`, {
      timeout: TEST_TIMEOUT
    });
    
    // Test Chaos mode activation
    const chaosResponse = await axios.post(`${BACKEND_URL}/api/chaos/activate`, {}, {
      timeout: TEST_TIMEOUT
    });
    
    if (chaosResponse.status !== 200) {
      throw new Error('Chaos mode activation failed');
    }
    
    // Verify Chaos mode is active
    const chaosStatus = await axios.get(`${BACKEND_URL}/api/chaos-warp/status`, {
      timeout: TEST_TIMEOUT
    });
    
    if (!chaosStatus.data.chaosMode || chaosStatus.data.operationStatus.reason !== 'CHAOS_MODE_ACTIVE') {
      throw new Error('Chaos mode not properly activated');
    }
    
    // Test Warp mode activation (should override Chaos)
    const warpResponse = await axios.post(`${BACKEND_URL}/api/warp/activate`, {}, {
      timeout: TEST_TIMEOUT
    });
    
    if (warpResponse.status !== 200) {
      throw new Error('Warp mode activation failed');
    }
    
    // Verify Warp mode overrides Chaos
    const warpStatus = await axios.get(`${BACKEND_URL}/api/chaos-warp/status`, {
      timeout: TEST_TIMEOUT
    });
    
    if (!warpStatus.data.warpMode || warpStatus.data.operationStatus.reason !== 'WARP_MODE_ACTIVE') {
      throw new Error('Warp mode not properly overriding Chaos');
    }
    
    // Test Chaos mode blocked by Warp
    try {
      await axios.post(`${BACKEND_URL}/api/chaos/activate`, {}, {
        timeout: TEST_TIMEOUT
      });
      throw new Error('Chaos mode should be blocked by Warp mode');
    } catch (error) {
      if (error.response && error.response.status === 400) {
        // Expected behavior - Chaos blocked by Warp
      } else {
        throw error;
      }
    }
    
    // Deactivate Warp mode
    await axios.post(`${BACKEND_URL}/api/warp/deactivate`, {}, {
      timeout: TEST_TIMEOUT
    });
    
    testResults.tests.push({
      test: 'chaos_warp_hierarchy',
      status: 'PASSED',
      message: 'Chaos/Warp hierarchy is properly enforced',
      details: {
        chaosActivation: 'SUCCESS',
        warpOverride: 'SUCCESS',
        chaosBlocked: 'SUCCESS',
        warpDeactivation: 'SUCCESS'
      }
    });
    testResults.summary.passed++;
    return true;
  } catch (error) {
    testResults.tests.push({
      test: 'chaos_warp_hierarchy',
      status: 'FAILED',
      message: error.message,
      error: error.toString()
    });
    testResults.summary.failed++;
    testResults.overall = 'FAILED';
    return false;
  }
}

/**
 * Test 7: Verify proposal validation scripts
 */
async function testProposalValidationScripts() {
  try {
    console.log('7️⃣ Testing proposal validation scripts...');
    
    const scripts = [
      'ai-backend/scripts/validate-proposal.js',
      'ai-backend/scripts/test-proposal-integration.js',
      'ai-backend/scripts/validate-app-functionality.js',
      'ai-backend/scripts/validate-deployment.js'
    ];
    
    const missingScripts = scripts.filter(script => !fs.existsSync(script));
    
    if (missingScripts.length > 0) {
      throw new Error(`Missing scripts: ${missingScripts.join(', ')}`);
    }
    
    // Test script execution (basic test)
    const testScript = 'ai-backend/scripts/validate-proposal.js';
    const result = await new Promise((resolve, reject) => {
      const child = spawn('node', [testScript, '--aiType=Imperium', '--proposalId=test-123'], {
        cwd: process.cwd(),
        stdio: ['pipe', 'pipe', 'pipe'],
        timeout: 30000
      });
      
      let stdout = '';
      let stderr = '';
      
      child.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      child.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      child.on('close', (code) => {
        resolve({ code, stdout, stderr });
      });
      
      child.on('error', (error) => {
        reject(error);
      });
    });
    
    if (result.code === 0 || result.stdout.includes('Validation completed')) {
      testResults.tests.push({
        test: 'proposal_validation_scripts',
        status: 'PASSED',
        message: 'Proposal validation scripts are functional',
        details: { 
          scriptsFound: scripts.length,
          testScript: testScript,
          exitCode: result.code
        }
      });
      testResults.summary.passed++;
      return true;
    } else {
      throw new Error(`Script execution failed: ${result.stderr}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'proposal_validation_scripts',
      status: 'FAILED',
      message: error.message,
      error: error.toString()
    });
    testResults.summary.failed++;
    testResults.overall = 'FAILED';
    return false;
  }
}

/**
 * Test 8: Verify GitHub API connectivity
 */
async function testGitHubAPIConnectivity() {
  try {
    console.log('8️⃣ Testing GitHub API connectivity...');
    
    if (!GITHUB_TOKEN || !GITHUB_REPO) {
      testResults.tests.push({
        test: 'github_api_connectivity',
        status: 'SKIPPED',
        message: 'GitHub token or repo not configured',
        details: { 
          hasToken: !!GITHUB_TOKEN, 
          hasRepo: !!GITHUB_REPO 
        }
      });
      testResults.summary.skipped++;
      return true;
    }
    
    const [owner, repo] = GITHUB_REPO.split('/');
    const url = `https://api.github.com/repos/${owner}/${repo}`;
    
    const response = await axios.get(url, {
      headers: {
        'Authorization': `Bearer ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json'
      },
      timeout: TEST_TIMEOUT
    });
    
    if (response.status === 200) {
      testResults.tests.push({
        test: 'github_api_connectivity',
        status: 'PASSED',
        message: 'GitHub API connectivity successful',
        details: { 
          repo: response.data.full_name,
          visibility: response.data.visibility,
          permissions: response.data.permissions
        }
      });
      testResults.summary.passed++;
      return true;
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'github_api_connectivity',
      status: 'FAILED',
      message: error.message,
      error: error.toString()
    });
    testResults.summary.failed++;
    testResults.overall = 'FAILED';
    return false;
  }
}

/**
 * Test 9: Verify AI quota service integration
 */
async function testAIQuotaServiceIntegration() {
  try {
    console.log('9️⃣ Testing AI quota service integration...');
    
    const response = await axios.get(`${BACKEND_URL}/api/ai-quota/status`, {
      timeout: TEST_TIMEOUT
    });
    
    if (response.status === 200) {
      const data = response.data;
      
      // Verify AI quota service respects Chaos/Warp hierarchy
      if (data.operationStatus && data.operationStatus.hierarchy) {
        testResults.tests.push({
          test: 'ai_quota_service_integration',
          status: 'PASSED',
          message: 'AI quota service integrates with Chaos/Warp hierarchy',
          details: {
            hierarchy: data.operationStatus.hierarchy,
            canOperate: data.operationStatus.canOperate,
            reason: data.operationStatus.reason
          }
        });
        testResults.summary.passed++;
        return true;
      } else {
        throw new Error('AI quota service not implementing hierarchy');
      }
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'ai_quota_service_integration',
      status: 'FAILED',
      message: error.message,
      error: error.toString()
    });
    testResults.summary.failed++;
    testResults.overall = 'FAILED';
    return false;
  }
}

/**
 * Test 10: Verify complete system status
 */
async function testCompleteSystemStatus() {
  try {
    console.log('🔟 Testing complete system status...');
    
    const response = await axios.get(`${BACKEND_URL}/api/chaos-warp/system-status`, {
      timeout: TEST_TIMEOUT
    });
    
    if (response.status === 200) {
      const data = response.data;
      
      // Verify all required status fields
      const requiredFields = [
        'systemStatus', 'operationStatus', 'currentTime',
        'systemStatus.warpMode', 'systemStatus.chaosMode',
        'systemStatus.shouldOperateAI', 'systemStatus.hierarchy'
      ];
      
      const missingFields = [];
      for (const field of requiredFields) {
        const value = field.split('.').reduce((obj, key) => obj?.[key], data);
        if (value === undefined) {
          missingFields.push(field);
        }
      }
      
      if (missingFields.length === 0) {
        testResults.tests.push({
          test: 'complete_system_status',
          status: 'PASSED',
          message: 'Complete system status is available',
          details: {
            systemStatus: data.systemStatus,
            operationStatus: data.operationStatus,
            currentTime: data.currentTime
          }
        });
        testResults.summary.passed++;
        return true;
      } else {
        throw new Error(`Missing fields: ${missingFields.join(', ')}`);
      }
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'complete_system_status',
      status: 'FAILED',
      message: error.message,
      error: error.toString()
    });
    testResults.summary.failed++;
    testResults.overall = 'FAILED';
    return false;
  }
}

/**
 * Run all tests
 */
async function runCompleteSystemIntegrationTests() {
  console.log('🚀 Starting Complete System Integration Tests');
  console.log('=============================================');
  console.log(`Backend URL: ${BACKEND_URL}`);
  console.log(`GitHub Repo: ${GITHUB_REPO || 'Not configured'}`);
  console.log(`Test Timeout: ${TEST_TIMEOUT}ms`);
  console.log('');
  
  const tests = [
    { name: 'Backend Connectivity', test: testBackendConnectivity },
    { name: 'Chaos/Warp System', test: testChaosWarpSystem },
    { name: 'Proposal System', test: testProposalSystem },
    { name: 'GitHub Workflow Configuration', test: testGitHubWorkflowConfiguration },
    { name: 'Flutter Configuration', test: testFlutterConfiguration },
    { name: 'Chaos/Warp Hierarchy', test: testChaosWarpHierarchy },
    { name: 'Proposal Validation Scripts', test: testProposalValidationScripts },
    { name: 'GitHub API Connectivity', test: testGitHubAPIConnectivity },
    { name: 'AI Quota Service Integration', test: testAIQuotaServiceIntegration },
    { name: 'Complete System Status', test: testCompleteSystemStatus }
  ];
  
  testResults.summary.total = tests.length;
  
  for (const test of tests) {
    try {
      await test.test();
    } catch (error) {
      console.error(`❌ Error in ${test.name}:`, error.message);
      testResults.tests.push({
        test: test.name.toLowerCase().replace(/\s+/g, '_'),
        status: 'FAILED',
        message: `Test error: ${error.message}`,
        error: error.toString()
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
    }
  }
  
  // Print results
  console.log('\n📊 Test Results Summary');
  console.log('=======================');
  console.log(`Total Tests: ${testResults.summary.total}`);
  console.log(`Passed: ${testResults.summary.passed}`);
  console.log(`Failed: ${testResults.summary.failed}`);
  console.log(`Skipped: ${testResults.summary.skipped}`);
  console.log(`Overall: ${testResults.overall}`);
  
  console.log('\n🔧 System Status');
  console.log('================');
  Object.entries(testResults.systemStatus).forEach(([component, status]) => {
    const emoji = status === 'FUNCTIONAL' || status === 'CONFIGURED' || status === 'ONLINE' ? '✅' : '❌';
    console.log(`${emoji} ${component}: ${status}`);
  });
  
  console.log('\n📋 Detailed Results');
  console.log('==================');
  testResults.tests.forEach((result, index) => {
    const emoji = result.status === 'PASSED' ? '✅' : result.status === 'SKIPPED' ? '⏭️' : '❌';
    console.log(`${emoji} ${index + 1}. ${result.test}: ${result.status}`);
    if (result.message) {
      console.log(`   ${result.message}`);
    }
  });
  
  // Save results to file
  const resultsDir = './test-results';
  if (!fs.existsSync(resultsDir)) {
    fs.mkdirSync(resultsDir, { recursive: true });
  }
  
  const resultsFile = `${resultsDir}/complete-system-integration-test-results-${Date.now()}.json`;
  fs.writeFileSync(resultsFile, JSON.stringify(testResults, null, 2));
  console.log(`\n💾 Test results saved to: ${resultsFile}`);
  
  // Exit with appropriate code
  if (testResults.overall === 'PASSED') {
    console.log('\n🎉 Complete system integration tests passed!');
    console.log('✅ Chaos/Warp system is functional');
    console.log('✅ GitHub workflow is configured');
    console.log('✅ Proposal system is operational');
    console.log('✅ All components are integrated');
    console.log('✅ System is ready for production');
    process.exit(0);
  } else {
    console.log('\n⚠️ Some tests failed. Please check the system configuration.');
    process.exit(1);
  }
}

// Run tests if this script is executed directly
if (require.main === module) {
  runCompleteSystemIntegrationTests().catch(error => {
    console.error('💥 Test execution failed:', error);
    process.exit(1);
  });
}

module.exports = {
  runCompleteSystemIntegrationTests,
  testResults
}; 