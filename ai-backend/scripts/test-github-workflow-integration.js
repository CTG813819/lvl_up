#!/usr/bin/env node

/**
 * GitHub Workflow Integration Test
 * Tests the complete proposal validation, integration, and deployment workflow
 */

const axios = require('axios');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:3000';
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_REPO = process.env.GITHUB_REPO;
const TEST_TIMEOUT = 60000; // 60 seconds

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
  }
};

/**
 * Test 1: Verify GitHub workflow configuration
 */
async function testWorkflowConfiguration() {
  try {
    console.log('1️⃣ Testing GitHub workflow configuration...');
    
    const workflowPath = '.github/workflows/ci-cd-pipeline.yml';
    
    if (!fs.existsSync(workflowPath)) {
      testResults.tests.push({
        test: 'workflow_configuration',
        status: 'FAILED',
        message: 'GitHub workflow file not found',
        details: { expectedPath: workflowPath }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
    
    const workflowContent = fs.readFileSync(workflowPath, 'utf8');
    
    // Check for required workflow components
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
        test: 'workflow_configuration',
        status: 'PASSED',
        message: 'GitHub workflow contains all required components',
        details: { components: requiredComponents }
      });
      testResults.summary.passed++;
      return true;
    } else {
      testResults.tests.push({
        test: 'workflow_configuration',
        status: 'FAILED',
        message: `Missing workflow components: ${missingComponents.join(', ')}`,
        details: { missingComponents }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
  } catch (error) {
    testResults.tests.push({
      test: 'workflow_configuration',
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
 * Test 2: Verify proposal validation script
 */
async function testProposalValidationScript() {
  try {
    console.log('2️⃣ Testing proposal validation script...');
    
    const scriptPath = 'ai-backend/scripts/validate-proposal.js';
    
    if (!fs.existsSync(scriptPath)) {
      testResults.tests.push({
        test: 'proposal_validation_script',
        status: 'FAILED',
        message: 'Proposal validation script not found',
        details: { expectedPath: scriptPath }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
    
    // Test script execution
    const result = await new Promise((resolve, reject) => {
      const child = spawn('node', [scriptPath, '--aiType=Imperium', '--proposalId=test-123'], {
        cwd: process.cwd(),
        stdio: ['pipe', 'pipe', 'pipe']
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
        test: 'proposal_validation_script',
        status: 'PASSED',
        message: 'Proposal validation script executes successfully',
        details: { exitCode: result.code, output: result.stdout.substring(0, 200) }
      });
      testResults.summary.passed++;
      return true;
    } else {
      testResults.tests.push({
        test: 'proposal_validation_script',
        status: 'FAILED',
        message: 'Proposal validation script failed to execute',
        details: { exitCode: result.code, stderr: result.stderr }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
  } catch (error) {
    testResults.tests.push({
      test: 'proposal_validation_script',
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
 * Test 3: Verify proposal integration script
 */
async function testProposalIntegrationScript() {
  try {
    console.log('3️⃣ Testing proposal integration script...');
    
    const scriptPath = 'ai-backend/scripts/test-proposal-integration.js';
    
    if (!fs.existsSync(scriptPath)) {
      testResults.tests.push({
        test: 'proposal_integration_script',
        status: 'FAILED',
        message: 'Proposal integration script not found',
        details: { expectedPath: scriptPath }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
    
    // Test script execution
    const result = await new Promise((resolve, reject) => {
      const child = spawn('node', [scriptPath, '--aiType=Imperium', '--proposalId=test-123'], {
        cwd: process.cwd(),
        stdio: ['pipe', 'pipe', 'pipe']
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
    
    if (result.code === 0 || result.stdout.includes('Integration test completed')) {
      testResults.tests.push({
        test: 'proposal_integration_script',
        status: 'PASSED',
        message: 'Proposal integration script executes successfully',
        details: { exitCode: result.code, output: result.stdout.substring(0, 200) }
      });
      testResults.summary.passed++;
      return true;
    } else {
      testResults.tests.push({
        test: 'proposal_integration_script',
        status: 'FAILED',
        message: 'Proposal integration script failed to execute',
        details: { exitCode: result.code, stderr: result.stderr }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
  } catch (error) {
    testResults.tests.push({
      test: 'proposal_integration_script',
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
 * Test 4: Verify app functionality validation script
 */
async function testAppFunctionalityScript() {
  try {
    console.log('4️⃣ Testing app functionality validation script...');
    
    const scriptPath = 'ai-backend/scripts/validate-app-functionality.js';
    
    if (!fs.existsSync(scriptPath)) {
      testResults.tests.push({
        test: 'app_functionality_script',
        status: 'FAILED',
        message: 'App functionality validation script not found',
        details: { expectedPath: scriptPath }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
    
    // Test script execution
    const result = await new Promise((resolve, reject) => {
      const child = spawn('node', [scriptPath, '--proposalId=test-123'], {
        cwd: process.cwd(),
        stdio: ['pipe', 'pipe', 'pipe']
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
    
    if (result.code === 0 || result.stdout.includes('Functionality validation completed')) {
      testResults.tests.push({
        test: 'app_functionality_script',
        status: 'PASSED',
        message: 'App functionality validation script executes successfully',
        details: { exitCode: result.code, output: result.stdout.substring(0, 200) }
      });
      testResults.summary.passed++;
      return true;
    } else {
      testResults.tests.push({
        test: 'app_functionality_script',
        status: 'FAILED',
        message: 'App functionality validation script failed to execute',
        details: { exitCode: result.code, stderr: result.stderr }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
  } catch (error) {
    testResults.tests.push({
      test: 'app_functionality_script',
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
 * Test 5: Verify deployment validation script
 */
async function testDeploymentValidationScript() {
  try {
    console.log('5️⃣ Testing deployment validation script...');
    
    const scriptPath = 'ai-backend/scripts/validate-deployment.js';
    
    if (!fs.existsSync(scriptPath)) {
      testResults.tests.push({
        test: 'deployment_validation_script',
        status: 'FAILED',
        message: 'Deployment validation script not found',
        details: { expectedPath: scriptPath }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
    
    // Test script execution
    const result = await new Promise((resolve, reject) => {
      const child = spawn('node', [scriptPath, '--proposalId=test-123', '--aiType=Imperium'], {
        cwd: process.cwd(),
        stdio: ['pipe', 'pipe', 'pipe']
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
    
    if (result.code === 0 || result.stdout.includes('Deployment validation completed')) {
      testResults.tests.push({
        test: 'deployment_validation_script',
        status: 'PASSED',
        message: 'Deployment validation script executes successfully',
        details: { exitCode: result.code, output: result.stdout.substring(0, 200) }
      });
      testResults.summary.passed++;
      return true;
    } else {
      testResults.tests.push({
        test: 'deployment_validation_script',
        status: 'FAILED',
        message: 'Deployment validation script failed to execute',
        details: { exitCode: result.code, stderr: result.stderr }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
  } catch (error) {
    testResults.tests.push({
      test: 'deployment_validation_script',
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
 * Test 6: Verify Flutter build configuration
 */
async function testFlutterBuildConfiguration() {
  try {
    console.log('6️⃣ Testing Flutter build configuration...');
    
    const pubspecPath = 'pubspec.yaml';
    
    if (!fs.existsSync(pubspecPath)) {
      testResults.tests.push({
        test: 'flutter_build_configuration',
        status: 'FAILED',
        message: 'Flutter pubspec.yaml not found',
        details: { expectedPath: pubspecPath }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
    
    const pubspecContent = fs.readFileSync(pubspecPath, 'utf8');
    
    // Check for required Flutter dependencies
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
        test: 'flutter_build_configuration',
        status: 'PASSED',
        message: 'Flutter build configuration is valid',
        details: { dependencies: requiredDependencies }
      });
      testResults.summary.passed++;
      return true;
    } else {
      testResults.tests.push({
        test: 'flutter_build_configuration',
        status: 'FAILED',
        message: `Missing Flutter dependencies: ${missingDependencies.join(', ')}`,
        details: { missingDependencies }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
  } catch (error) {
    testResults.tests.push({
      test: 'flutter_build_configuration',
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
 * Test 7: Verify backend build configuration
 */
async function testBackendBuildConfiguration() {
  try {
    console.log('7️⃣ Testing backend build configuration...');
    
    const packagePath = 'ai-backend/package.json';
    
    if (!fs.existsSync(packagePath)) {
      testResults.tests.push({
        test: 'backend_build_configuration',
        status: 'FAILED',
        message: 'Backend package.json not found',
        details: { expectedPath: packagePath }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
    
    const packageContent = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    
    // Check for required scripts
    const requiredScripts = ['test', 'build', 'start'];
    const missingScripts = requiredScripts.filter(script => 
      !packageContent.scripts || !packageContent.scripts[script]
    );
    
    if (missingScripts.length === 0) {
      testResults.tests.push({
        test: 'backend_build_configuration',
        status: 'PASSED',
        message: 'Backend build configuration is valid',
        details: { scripts: requiredScripts }
      });
      testResults.summary.passed++;
      return true;
    } else {
      testResults.tests.push({
        test: 'backend_build_configuration',
        status: 'FAILED',
        message: `Missing backend scripts: ${missingScripts.join(', ')}`,
        details: { missingScripts }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
  } catch (error) {
    testResults.tests.push({
      test: 'backend_build_configuration',
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
          visibility: response.data.visibility
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
 * Test 9: Verify workflow trigger configuration
 */
async function testWorkflowTriggerConfiguration() {
  try {
    console.log('9️⃣ Testing workflow trigger configuration...');
    
    const workflowPath = '.github/workflows/ci-cd-pipeline.yml';
    
    if (!fs.existsSync(workflowPath)) {
      testResults.tests.push({
        test: 'workflow_trigger_configuration',
        status: 'FAILED',
        message: 'GitHub workflow file not found',
        details: { expectedPath: workflowPath }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
    
    const workflowContent = fs.readFileSync(workflowPath, 'utf8');
    
    // Check for required triggers
    const requiredTriggers = [
      'workflow_dispatch:',
      'push:',
      'pull_request:'
    ];
    
    const missingTriggers = requiredTriggers.filter(trigger => 
      !workflowContent.includes(trigger)
    );
    
    if (missingTriggers.length === 0) {
      testResults.tests.push({
        test: 'workflow_trigger_configuration',
        status: 'PASSED',
        message: 'Workflow trigger configuration is valid',
        details: { triggers: requiredTriggers }
      });
      testResults.summary.passed++;
      return true;
    } else {
      testResults.tests.push({
        test: 'workflow_trigger_configuration',
        status: 'FAILED',
        message: `Missing workflow triggers: ${missingTriggers.join(', ')}`,
        details: { missingTriggers }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
  } catch (error) {
    testResults.tests.push({
      test: 'workflow_trigger_configuration',
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
 * Test 10: Verify artifact configuration
 */
async function testArtifactConfiguration() {
  try {
    console.log('🔟 Testing artifact configuration...');
    
    const workflowPath = '.github/workflows/ci-cd-pipeline.yml';
    
    if (!fs.existsSync(workflowPath)) {
      testResults.tests.push({
        test: 'artifact_configuration',
        status: 'FAILED',
        message: 'GitHub workflow file not found',
        details: { expectedPath: workflowPath }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
    
    const workflowContent = fs.readFileSync(workflowPath, 'utf8');
    
    // Check for required artifacts
    const requiredArtifacts = [
      'app-release.apk',
      'app-release.aab',
      'backend-build',
      'web-build'
    ];
    
    const missingArtifacts = requiredArtifacts.filter(artifact => 
      !workflowContent.includes(artifact)
    );
    
    if (missingArtifacts.length === 0) {
      testResults.tests.push({
        test: 'artifact_configuration',
        status: 'PASSED',
        message: 'Artifact configuration is valid',
        details: { artifacts: requiredArtifacts }
      });
      testResults.summary.passed++;
      return true;
    } else {
      testResults.tests.push({
        test: 'artifact_configuration',
        status: 'FAILED',
        message: `Missing artifacts: ${missingArtifacts.join(', ')}`,
        details: { missingArtifacts }
      });
      testResults.summary.failed++;
      testResults.overall = 'FAILED';
      return false;
    }
  } catch (error) {
    testResults.tests.push({
      test: 'artifact_configuration',
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
async function runWorkflowIntegrationTests() {
  console.log('🚀 Starting GitHub Workflow Integration Tests');
  console.log('=============================================');
  console.log(`Backend URL: ${BACKEND_URL}`);
  console.log(`GitHub Repo: ${GITHUB_REPO || 'Not configured'}`);
  console.log(`Test Timeout: ${TEST_TIMEOUT}ms`);
  console.log('');
  
  const tests = [
    { name: 'Workflow Configuration', test: testWorkflowConfiguration },
    { name: 'Proposal Validation Script', test: testProposalValidationScript },
    { name: 'Proposal Integration Script', test: testProposalIntegrationScript },
    { name: 'App Functionality Script', test: testAppFunctionalityScript },
    { name: 'Deployment Validation Script', test: testDeploymentValidationScript },
    { name: 'Flutter Build Configuration', test: testFlutterBuildConfiguration },
    { name: 'Backend Build Configuration', test: testBackendBuildConfiguration },
    { name: 'GitHub API Connectivity', test: testGitHubAPIConnectivity },
    { name: 'Workflow Trigger Configuration', test: testWorkflowTriggerConfiguration },
    { name: 'Artifact Configuration', test: testArtifactConfiguration }
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
  
  const resultsFile = `${resultsDir}/github-workflow-test-results-${Date.now()}.json`;
  fs.writeFileSync(resultsFile, JSON.stringify(testResults, null, 2));
  console.log(`\n💾 Test results saved to: ${resultsFile}`);
  
  // Exit with appropriate code
  if (testResults.overall === 'PASSED') {
    console.log('\n🎉 All GitHub workflow integration tests passed!');
    console.log('✅ Workflow configuration is valid');
    console.log('✅ All validation scripts are functional');
    console.log('✅ Build configurations are correct');
    console.log('✅ Artifact handling is configured');
    process.exit(0);
  } else {
    console.log('\n⚠️ Some tests failed. Please check the workflow configuration.');
    process.exit(1);
  }
}

// Run tests if this script is executed directly
if (require.main === module) {
  runWorkflowIntegrationTests().catch(error => {
    console.error('💥 Test execution failed:', error);
    process.exit(1);
  });
}

module.exports = {
  runWorkflowIntegrationTests,
  testResults
}; 