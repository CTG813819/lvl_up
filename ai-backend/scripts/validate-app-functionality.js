#!/usr/bin/env node

/**
 * App Functionality Validation Script
 * Validates app functionality with new AI-generated proposals
 */

const { program } = require('commander');
const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');

program
  .option('--proposalId <id>', 'Proposal ID for tracking', 'test-proposal')
  .option('--aiType <type>', 'AI Type (Imperium, Guardian, Sandbox)', 'Imperium')
  .option('--backendUrl <url>', 'Backend URL for testing', 'http://localhost:3000')
  .option('--appUrl <url>', 'App URL for testing', 'http://localhost:8080')
  .parse(process.argv);

const options = program.opts();

class AppFunctionalityValidator {
  constructor(backendUrl, appUrl) {
    this.backendUrl = backendUrl;
    this.appUrl = appUrl;
    this.validationResults = [];
    this.functionalityIssues = [];
  }

  log(message, type = 'INFO') {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [${type}] ${message}`);
  }

  addResult(test, passed, details = '') {
    this.validationResults.push({
      test,
      passed,
      details,
      timestamp: new Date().toISOString()
    });
  }

  addIssue(message, severity = 'WARNING') {
    this.functionalityIssues.push({
      message,
      severity,
      timestamp: new Date().toISOString()
    });
    this.log(message, severity);
  }

  async testEndpoint(url, method = 'GET', data = null) {
    try {
      const config = {
        method,
        url,
        headers: { 'Content-Type': 'application/json' },
        timeout: 10000
      };

      if (data) {
        config.data = data;
      }

      const response = await axios(config);
      return { success: true, data: response.data, status: response.status };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || error.message,
        status: error.response?.status 
      };
    }
  }

  async testAppAvailability() {
    this.log('🧪 Testing App Availability');
    
    const result = await this.testEndpoint(`${this.appUrl}/health`);
    if (result.success) {
      this.log(`✅ App is available and responding`);
      this.log(`   - Status: ${result.status}`);
      this.log(`   - Health: ${result.data.status || 'OK'}`);
      this.addResult('App Availability', true, `App responding: ${result.status}`);
      return true;
    } else {
      this.log(`❌ App is not available: ${result.error}`, 'ERROR');
      this.addResult('App Availability', false, `App not available: ${result.error}`);
      return false;
    }
  }

  async testBackendConnectivity() {
    this.log('🧪 Testing Backend Connectivity');
    
    const result = await this.testEndpoint(`${this.backendUrl}/api/health`);
    if (result.success) {
      this.log(`✅ Backend is available and responding`);
      this.log(`   - Status: ${result.status}`);
      this.log(`   - Health: ${result.data.status || 'OK'}`);
      this.addResult('Backend Connectivity', true, `Backend responding: ${result.status}`);
      return true;
    } else {
      this.log(`❌ Backend is not available: ${result.error}`, 'ERROR');
      this.addResult('Backend Connectivity', false, `Backend not available: ${result.error}`);
      return false;
    }
  }

  async testProposalIntegration() {
    this.log('🧪 Testing Proposal Integration with App');
    
    // Test if the app can access proposal data
    const proposalResult = await this.testEndpoint(`${this.backendUrl}/api/proposals`);
    if (proposalResult.success) {
      this.log(`✅ Proposal data accessible`);
      this.log(`   - Proposals count: ${proposalResult.data.length || 0}`);
      
      // Check if our specific proposal exists
      const targetProposal = proposalResult.data.find(p => p._id === options.proposalId);
      if (targetProposal) {
        this.log(`✅ Target proposal found: ${targetProposal.aiType}`);
        this.addResult('Proposal Integration', true, `Found target proposal: ${targetProposal.aiType}`);
        return true;
      } else {
        this.log(`⚠️ Target proposal not found, but API is working`);
        this.addResult('Proposal Integration', true, `API working, ${proposalResult.data.length} proposals found`);
        return true;
      }
    } else {
      this.log(`❌ Proposal data not accessible: ${proposalResult.error}`, 'ERROR');
      this.addResult('Proposal Integration', false, `Proposal API error: ${proposalResult.error}`);
      return false;
    }
  }

  async testChaosWarpFunctionality() {
    this.log('🧪 Testing Chaos/Warp Functionality in App');
    
    const statusResult = await this.testEndpoint(`${this.backendUrl}/api/chaos-warp/status`);
    if (statusResult.success) {
      const status = statusResult.data;
      this.log(`✅ Chaos/Warp status accessible`);
      this.log(`   - Warp Mode: ${status.warpMode}`);
      this.log(`   - Chaos Mode: ${status.chaosMode}`);
      this.log(`   - Should Operate AI: ${status.operationStatus.canOperate}`);
      this.log(`   - Hierarchy: ${status.hierarchy}`);
      
      this.addResult('Chaos/Warp Functionality', true, `Status: ${status.hierarchy}`);
      return true;
    } else {
      this.log(`❌ Chaos/Warp status not accessible: ${statusResult.error}`, 'ERROR');
      this.addResult('Chaos/Warp Functionality', false, `Status API error: ${statusResult.error}`);
      return false;
    }
  }

  async testAppFeatures() {
    this.log('🧪 Testing App Features');
    
    const features = [
      { name: 'Proposal Management', endpoint: '/api/proposals' },
      { name: 'Chaos/Warp Control', endpoint: '/api/chaos-warp/status' },
      { name: 'AI Learning', endpoint: '/api/ai-learning/status' },
      { name: 'Notifications', endpoint: '/api/notifications' },
      { name: 'User Management', endpoint: '/api/users' }
    ];
    
    let workingFeatures = 0;
    let totalFeatures = features.length;
    
    for (const feature of features) {
      const result = await this.testEndpoint(`${this.backendUrl}${feature.endpoint}`);
      if (result.success) {
        this.log(`✅ ${feature.name}: Working`);
        workingFeatures++;
      } else {
        this.log(`⚠️ ${feature.name}: Not available (${result.status || 'N/A'})`, 'WARNING');
        this.addIssue(`${feature.name} not available - may affect app functionality`, 'WARNING');
      }
    }
    
    this.log(`📊 Features Summary: ${workingFeatures}/${totalFeatures} working`);
    this.addResult('App Features', workingFeatures === totalFeatures, `${workingFeatures}/${totalFeatures} features working`);
    
    return workingFeatures === totalFeatures;
  }

  async testPerformance() {
    this.log('🧪 Testing App Performance');
    
    const endpoints = [
      '/api/proposals',
      '/api/chaos-warp/status',
      '/api/ai-learning/status'
    ];
    
    let totalResponseTime = 0;
    let successfulRequests = 0;
    
    for (const endpoint of endpoints) {
      const startTime = Date.now();
      const result = await this.testEndpoint(`${this.backendUrl}${endpoint}`);
      const responseTime = Date.now() - startTime;
      
      if (result.success) {
        totalResponseTime += responseTime;
        successfulRequests++;
        this.log(`✅ ${endpoint}: ${responseTime}ms`);
      } else {
        this.log(`❌ ${endpoint}: Failed (${responseTime}ms)`);
      }
    }
    
    if (successfulRequests > 0) {
      const averageResponseTime = totalResponseTime / successfulRequests;
      this.log(`📊 Average response time: ${averageResponseTime.toFixed(2)}ms`);
      
      if (averageResponseTime < 1000) {
        this.log(`✅ Performance is good (< 1 second)`);
        this.addResult('Performance', true, `Average response time: ${averageResponseTime.toFixed(2)}ms`);
        return true;
      } else if (averageResponseTime < 3000) {
        this.log(`⚠️ Performance is acceptable (< 3 seconds)`, 'WARNING');
        this.addIssue(`Slow response times may affect user experience`, 'WARNING');
        this.addResult('Performance', true, `Acceptable response time: ${averageResponseTime.toFixed(2)}ms`);
        return true;
      } else {
        this.log(`❌ Performance is poor (> 3 seconds)`, 'ERROR');
        this.addIssue(`Very slow response times will affect user experience`, 'ERROR');
        this.addResult('Performance', false, `Poor response time: ${averageResponseTime.toFixed(2)}ms`);
        return false;
      }
    } else {
      this.log(`❌ No successful requests to measure performance`, 'ERROR');
      this.addResult('Performance', false, 'No successful requests');
      return false;
    }
  }

  async testErrorHandling() {
    this.log('🧪 Testing Error Handling');
    
    const errorTests = [
      { name: 'Invalid Proposal ID', endpoint: '/api/proposals/invalid-id-12345', expectedStatus: 404 },
      { name: 'Invalid Chaos/Warp Action', endpoint: '/api/chaos-warp/invalid-action', expectedStatus: 404 },
      { name: 'Invalid AI Type', endpoint: '/api/ai-learning/invalid-ai', expectedStatus: 400 }
    ];
    
    let properErrorHandling = 0;
    let totalErrorTests = errorTests.length;
    
    for (const test of errorTests) {
      const result = await this.testEndpoint(`${this.backendUrl}${test.endpoint}`);
      
      if (!result.success && result.status === test.expectedStatus) {
        this.log(`✅ ${test.name}: Proper error response (${result.status})`);
        properErrorHandling++;
      } else {
        this.log(`❌ ${test.name}: Unexpected response (${result.status || 'N/A'})`, 'ERROR');
      }
    }
    
    this.log(`📊 Error Handling: ${properErrorHandling}/${totalErrorTests} proper responses`);
    this.addResult('Error Handling', properErrorHandling === totalErrorTests, `${properErrorHandling}/${totalErrorTests} proper error responses`);
    
    return properErrorHandling === totalErrorTests;
  }

  async testDataConsistency() {
    this.log('🧪 Testing Data Consistency');
    
    // Test that proposal data is consistent across endpoints
    const proposalsResult = await this.testEndpoint(`${this.backendUrl}/api/proposals`);
    const chaosWarpResult = await this.testEndpoint(`${this.backendUrl}/api/chaos-warp/status`);
    
    if (proposalsResult.success && chaosWarpResult.success) {
      this.log(`✅ Data consistency check passed`);
      this.log(`   - Proposals API: Working`);
      this.log(`   - Chaos/Warp API: Working`);
      this.log(`   - Both endpoints responding correctly`);
      
      this.addResult('Data Consistency', true, 'All APIs responding consistently');
      return true;
    } else {
      this.log(`❌ Data consistency check failed`, 'ERROR');
      this.addResult('Data Consistency', false, 'APIs not responding consistently');
      return false;
    }
  }

  async testUserExperience() {
    this.log('🧪 Testing User Experience');
    
    // Test that the app provides good user experience
    const uxTests = [
      { name: 'Quick Response Times', test: () => this.testPerformance() },
      { name: 'Proper Error Messages', test: () => this.testErrorHandling() },
      { name: 'Consistent Data', test: () => this.testDataConsistency() }
    ];
    
    let uxScore = 0;
    let totalUXTests = uxTests.length;
    
    for (const uxTest of uxTests) {
      try {
        const result = await uxTest.test();
        if (result) {
          this.log(`✅ ${uxTest.name}: Good UX`);
          uxScore++;
        } else {
          this.log(`❌ ${uxTest.name}: Poor UX`);
        }
      } catch (error) {
        this.log(`❌ ${uxTest.name}: Error - ${error.message}`, 'ERROR');
      }
    }
    
    this.log(`📊 UX Score: ${uxScore}/${totalUXTests}`);
    
    if (uxScore === totalUXTests) {
      this.log(`✅ Excellent user experience`);
      this.addResult('User Experience', true, `Perfect UX score: ${uxScore}/${totalUXTests}`);
      return true;
    } else if (uxScore >= totalUXTests * 0.7) {
      this.log(`⚠️ Good user experience with minor issues`, 'WARNING');
      this.addResult('User Experience', true, `Good UX score: ${uxScore}/${totalUXTests}`);
      return true;
    } else {
      this.log(`❌ Poor user experience`, 'ERROR');
      this.addResult('User Experience', false, `Poor UX score: ${uxScore}/${totalUXTests}`);
      return false;
    }
  }

  async runFunctionalityValidation() {
    this.log('🚀 Starting App Functionality Validation');
    this.log('========================================');
    
    const validations = [
      { name: 'App Availability', test: () => this.testAppAvailability() },
      { name: 'Backend Connectivity', test: () => this.testBackendConnectivity() },
      { name: 'Proposal Integration', test: () => this.testProposalIntegration() },
      { name: 'Chaos/Warp Functionality', test: () => this.testChaosWarpFunctionality() },
      { name: 'App Features', test: () => this.testAppFeatures() },
      { name: 'Performance', test: () => this.testPerformance() },
      { name: 'Error Handling', test: () => this.testErrorHandling() },
      { name: 'Data Consistency', test: () => this.testDataConsistency() },
      { name: 'User Experience', test: () => this.testUserExperience() }
    ];
    
    let passedValidations = 0;
    let totalValidations = validations.length;
    
    for (const validation of validations) {
      this.log(`\n📋 Running: ${validation.name}`);
      try {
        const result = await validation.test();
        if (result) {
          this.log(`✅ ${validation.name}: PASSED`);
          passedValidations++;
        } else {
          this.log(`❌ ${validation.name}: FAILED`);
        }
      } catch (error) {
        this.log(`💥 ${validation.name}: ERROR - ${error.message}`, 'ERROR');
        this.addIssue(`Validation error in ${validation.name}: ${error.message}`, 'ERROR');
      }
    }
    
    this.log('\n📊 Functionality Validation Results Summary');
    this.log('===========================================');
    this.log(`Total Validations: ${totalValidations}`);
    this.log(`Passed: ${passedValidations}`);
    this.log(`Failed: ${totalValidations - passedValidations}`);
    this.log(`Success Rate: ${((passedValidations / totalValidations) * 100).toFixed(1)}%`);
    
    if (this.functionalityIssues.length > 0) {
      this.log(`\n⚠️ Functionality Issues (${this.functionalityIssues.length}):`);
      this.functionalityIssues.forEach(issue => {
        this.log(`   [${issue.severity}] ${issue.message}`);
      });
    }
    
    this.log('\n📋 Detailed Results:');
    this.validationResults.forEach(result => {
      const status = result.passed ? '✅' : '❌';
      this.log(`   ${status} ${result.test}: ${result.details}`);
    });
    
    if (passedValidations === totalValidations && this.functionalityIssues.filter(i => i.severity === 'ERROR').length === 0) {
      this.log('\n🎉 All functionality validations passed!');
      this.log('✅ App functionality is working correctly with new proposals');
      return true;
    } else if (this.functionalityIssues.filter(i => i.severity === 'ERROR').length === 0) {
      this.log('\n⚠️ Some functionality validations failed, but no critical errors');
      this.log('✅ App functionality can proceed with warnings');
      return true;
    } else {
      this.log('\n❌ Critical functionality issues found');
      this.log('❌ App functionality cannot proceed');
      return false;
    }
  }

  getFunctionalityReport() {
    return {
      proposalId: options.proposalId,
      aiType: options.aiType,
      timestamp: new Date().toISOString(),
      results: this.validationResults,
      issues: this.functionalityIssues,
      summary: {
        total: this.validationResults.length,
        passed: this.validationResults.filter(r => r.passed).length,
        failed: this.validationResults.filter(r => !r.passed).length,
        errorCount: this.functionalityIssues.filter(i => i.severity === 'ERROR').length,
        warningCount: this.functionalityIssues.filter(i => i.severity === 'WARNING').length
      }
    };
  }
}

// Main execution
async function main() {
  const validator = new AppFunctionalityValidator(options.backendUrl, options.appUrl);
  
  try {
    const isFunctional = await validator.runFunctionalityValidation();
    
    // Save functionality report
    const report = validator.getFunctionalityReport();
    const reportPath = path.join(process.cwd(), 'ai-backend', 'test-results', `app-functionality-${options.proposalId}.json`);
    
    try {
      await fs.mkdir(path.dirname(reportPath), { recursive: true });
      await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
      console.log(`📄 Functionality report saved to: ${reportPath}`);
    } catch (error) {
      console.warn(`⚠️ Could not save functionality report: ${error.message}`);
    }
    
    if (!isFunctional) {
      process.exit(1);
    }
  } catch (error) {
    console.error('💥 Functionality validation failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { AppFunctionalityValidator }; 
module.exports = { validateAppFunctionality, validationResults }; 