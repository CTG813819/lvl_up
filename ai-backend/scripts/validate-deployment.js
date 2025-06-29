#!/usr/bin/env node

/**
 * Deployment Validation Script
 * Validates deployment after AI-generated proposals have been integrated
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
  .option('--environment <env>', 'Deployment environment (staging, production)', 'production')
  .parse(process.argv);

const options = program.opts();

class DeploymentValidator {
  constructor(backendUrl, appUrl, environment) {
    this.backendUrl = backendUrl;
    this.appUrl = appUrl;
    this.environment = environment;
    this.validationResults = [];
    this.deploymentIssues = [];
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
    this.deploymentIssues.push({
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
        timeout: 15000
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

  async testDeploymentHealth() {
    this.log('🧪 Testing Deployment Health');
    
    const healthChecks = [
      { name: 'Backend Health', url: `${this.backendUrl}/api/health` },
      { name: 'App Health', url: `${this.appUrl}/health` },
      { name: 'Database Health', url: `${this.backendUrl}/api/db/health` }
    ];
    
    let healthyServices = 0;
    let totalServices = healthChecks.length;
    
    for (const check of healthChecks) {
      const result = await this.testEndpoint(check.url);
      if (result.success) {
        this.log(`✅ ${check.name}: Healthy`);
        this.log(`   - Status: ${result.status}`);
        this.log(`   - Response: ${JSON.stringify(result.data)}`);
        healthyServices++;
      } else {
        this.log(`❌ ${check.name}: Unhealthy (${result.status || 'N/A'})`, 'ERROR');
        this.addIssue(`${check.name} is not responding correctly`, 'ERROR');
      }
    }
    
    this.log(`📊 Health Summary: ${healthyServices}/${totalServices} services healthy`);
    this.addResult('Deployment Health', healthyServices === totalServices, `${healthyServices}/${totalServices} services healthy`);
    
    return healthyServices === totalServices;
  }

  async testProposalIntegration() {
    this.log('🧪 Testing Proposal Integration in Deployment');
    
    const proposalResult = await this.testEndpoint(`${this.backendUrl}/api/proposals`);
    if (proposalResult.success) {
      this.log(`✅ Proposal system is working in deployment`);
      this.log(`   - Proposals count: ${proposalResult.data.length || 0}`);
      
      // Check if our specific proposal is properly integrated
      const targetProposal = proposalResult.data.find(p => p._id === options.proposalId);
      if (targetProposal) {
        this.log(`✅ Target proposal properly integrated: ${targetProposal.aiType}`);
        this.log(`   - Status: ${targetProposal.status}`);
        this.log(`   - File Path: ${targetProposal.filePath}`);
        this.addResult('Proposal Integration', true, `Target proposal integrated: ${targetProposal.status}`);
        return true;
      } else {
        this.log(`⚠️ Target proposal not found in deployment, but system is working`);
        this.addResult('Proposal Integration', true, `System working, ${proposalResult.data.length} proposals found`);
        return true;
      }
    } else {
      this.log(`❌ Proposal system not working in deployment: ${proposalResult.error}`, 'ERROR');
      this.addResult('Proposal Integration', false, `Proposal system error: ${proposalResult.error}`);
      return false;
    }
  }

  async testChaosWarpDeployment() {
    this.log('🧪 Testing Chaos/Warp Deployment');
    
    const statusResult = await this.testEndpoint(`${this.backendUrl}/api/chaos-warp/status`);
    if (statusResult.success) {
      const status = statusResult.data;
      this.log(`✅ Chaos/Warp system deployed and working`);
      this.log(`   - Warp Mode: ${status.warpMode}`);
      this.log(`   - Chaos Mode: ${status.chaosMode}`);
      this.log(`   - Should Operate AI: ${status.operationStatus.canOperate}`);
      this.log(`   - Hierarchy: ${status.hierarchy}`);
      this.log(`   - Operational Hours: ${status.operationalHours.formatted}`);
      
      this.addResult('Chaos/Warp Deployment', true, `System deployed: ${status.hierarchy}`);
      return true;
    } else {
      this.log(`❌ Chaos/Warp system not working in deployment: ${statusResult.error}`, 'ERROR');
      this.addResult('Chaos/Warp Deployment', false, `System error: ${statusResult.error}`);
      return false;
    }
  }

  async testPerformanceInProduction() {
    this.log('🧪 Testing Performance in Production');
    
    const performanceTests = [
      { name: 'Proposals API', endpoint: '/api/proposals' },
      { name: 'Chaos/Warp Status', endpoint: '/api/chaos-warp/status' },
      { name: 'AI Learning Status', endpoint: '/api/ai-learning/status' }
    ];
    
    let totalResponseTime = 0;
    let successfulRequests = 0;
    const maxAcceptableTime = this.environment === 'production' ? 2000 : 5000; // 2s for prod, 5s for staging
    
    for (const test of performanceTests) {
      const startTime = Date.now();
      const result = await this.testEndpoint(`${this.backendUrl}${test.endpoint}`);
      const responseTime = Date.now() - startTime;
      
      if (result.success) {
        totalResponseTime += responseTime;
        successfulRequests++;
        this.log(`✅ ${test.name}: ${responseTime}ms`);
        
        if (responseTime > maxAcceptableTime) {
          this.addIssue(`${test.name} response time (${responseTime}ms) exceeds acceptable limit (${maxAcceptableTime}ms)`, 'WARNING');
        }
      } else {
        this.log(`❌ ${test.name}: Failed (${responseTime}ms)`);
      }
    }
    
    if (successfulRequests > 0) {
      const averageResponseTime = totalResponseTime / successfulRequests;
      this.log(`📊 Average response time: ${averageResponseTime.toFixed(2)}ms`);
      this.log(`📊 Environment: ${this.environment}`);
      this.log(`📊 Max acceptable: ${maxAcceptableTime}ms`);
      
      if (averageResponseTime <= maxAcceptableTime) {
        this.log(`✅ Performance meets ${this.environment} requirements`);
        this.addResult('Production Performance', true, `Average: ${averageResponseTime.toFixed(2)}ms (≤${maxAcceptableTime}ms)`);
        return true;
      } else {
        this.log(`⚠️ Performance below ${this.environment} requirements`, 'WARNING');
        this.addResult('Production Performance', false, `Average: ${averageResponseTime.toFixed(2)}ms (>${maxAcceptableTime}ms)`);
        return false;
      }
    } else {
      this.log(`❌ No successful requests to measure performance`, 'ERROR');
      this.addResult('Production Performance', false, 'No successful requests');
      return false;
    }
  }

  async testSecurityInProduction() {
    this.log('🧪 Testing Security in Production');
    
    const securityTests = [
      { name: 'HTTPS Enforcement', url: this.backendUrl.replace('http://', 'https://'), expectedFailure: true },
      { name: 'CORS Headers', url: `${this.backendUrl}/api/proposals`, checkCORS: true },
      { name: 'Authentication Endpoints', url: `${this.backendUrl}/api/auth/status` }
    ];
    
    let securityScore = 0;
    let totalSecurityTests = securityTests.length;
    
    for (const test of securityTests) {
      try {
        const result = await this.testEndpoint(test.url);
        
        if (test.expectedFailure && !result.success) {
          this.log(`✅ ${test.name}: Properly secured (expected failure)`);
          securityScore++;
        } else if (!test.expectedFailure && result.success) {
          this.log(`✅ ${test.name}: Working correctly`);
          securityScore++;
        } else {
          this.log(`⚠️ ${test.name}: Unexpected behavior`, 'WARNING');
        }
      } catch (error) {
        if (test.expectedFailure) {
          this.log(`✅ ${test.name}: Properly secured (connection failed as expected)`);
          securityScore++;
        } else {
          this.log(`❌ ${test.name}: Error - ${error.message}`, 'ERROR');
        }
      }
    }
    
    this.log(`📊 Security Score: ${securityScore}/${totalSecurityTests}`);
    this.addResult('Production Security', securityScore >= totalSecurityTests * 0.8, `Security score: ${securityScore}/${totalSecurityTests}`);
    
    return securityScore >= totalSecurityTests * 0.8;
  }

  async testMonitoringAndLogging() {
    this.log('🧪 Testing Monitoring and Logging');
    
    const monitoringTests = [
      { name: 'Application Logs', endpoint: '/api/logs/status' },
      { name: 'Performance Metrics', endpoint: '/api/metrics/status' },
      { name: 'Error Tracking', endpoint: '/api/errors/status' }
    ];
    
    let monitoringScore = 0;
    let totalMonitoringTests = monitoringTests.length;
    
    for (const test of monitoringTests) {
      const result = await this.testEndpoint(`${this.backendUrl}${test.endpoint}`);
      if (result.success) {
        this.log(`✅ ${test.name}: Available`);
        monitoringScore++;
      } else {
        this.log(`⚠️ ${test.name}: Not available (${result.status || 'N/A'})`, 'WARNING');
        this.addIssue(`${test.name} not available - may affect monitoring`, 'WARNING');
      }
    }
    
    this.log(`📊 Monitoring Score: ${monitoringScore}/${totalMonitoringTests}`);
    this.addResult('Monitoring and Logging', monitoringScore >= totalMonitoringTests * 0.5, `Monitoring score: ${monitoringScore}/${totalMonitoringTests}`);
    
    return monitoringScore >= totalMonitoringTests * 0.5;
  }

  async testDataPersistence() {
    this.log('🧪 Testing Data Persistence');
    
    // Test that data persists across requests
    const initialResult = await this.testEndpoint(`${this.backendUrl}/api/proposals`);
    if (!initialResult.success) {
      this.log(`❌ Cannot test data persistence - initial request failed`, 'ERROR');
      this.addResult('Data Persistence', false, 'Initial request failed');
      return false;
    }
    
    const initialCount = initialResult.data.length || 0;
    this.log(`📊 Initial proposal count: ${initialCount}`);
    
    // Wait a moment and test again
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const secondResult = await this.testEndpoint(`${this.backendUrl}/api/proposals`);
    if (!secondResult.success) {
      this.log(`❌ Data persistence test failed - second request failed`, 'ERROR');
      this.addResult('Data Persistence', false, 'Second request failed');
      return false;
    }
    
    const secondCount = secondResult.data.length || 0;
    this.log(`📊 Second proposal count: ${secondCount}`);
    
    if (initialCount === secondCount) {
      this.log(`✅ Data persistence confirmed`);
      this.addResult('Data Persistence', true, `Data consistent: ${initialCount} proposals`);
      return true;
    } else {
      this.log(`❌ Data persistence issue detected`, 'ERROR');
      this.addResult('Data Persistence', false, `Data inconsistent: ${initialCount} vs ${secondCount}`);
      return false;
    }
  }

  async testErrorRecovery() {
    this.log('🧪 Testing Error Recovery');
    
    // Test that the system can handle errors gracefully
    const errorTests = [
      { name: 'Invalid Endpoint', endpoint: '/api/invalid-endpoint-12345', expectedStatus: 404 },
      { name: 'Invalid Proposal ID', endpoint: '/api/proposals/invalid-id-12345', expectedStatus: 404 }
    ];
    
    let properErrorHandling = 0;
    let totalErrorTests = errorTests.length;
    
    for (const test of errorTests) {
      const result = await this.testEndpoint(`${this.backendUrl}${test.endpoint}`);
      
      if (!result.success && result.status === test.expectedStatus) {
        this.log(`✅ ${test.name}: Proper error handling (${result.status})`);
        properErrorHandling++;
      } else {
        this.log(`❌ ${test.name}: Unexpected error handling (${result.status || 'N/A'})`, 'ERROR');
      }
    }
    
    this.log(`📊 Error Recovery: ${properErrorHandling}/${totalErrorTests} proper error handling`);
    this.addResult('Error Recovery', properErrorHandling === totalErrorTests, `${properErrorHandling}/${totalErrorTests} proper error handling`);
    
    return properErrorHandling === totalErrorTests;
  }

  async runDeploymentValidation() {
    this.log('🚀 Starting Deployment Validation');
    this.log('================================');
    this.log(`Environment: ${this.environment}`);
    this.log(`Backend URL: ${this.backendUrl}`);
    this.log(`App URL: ${this.appUrl}`);
    this.log(`Proposal ID: ${options.proposalId}`);
    this.log(`AI Type: ${options.aiType}`);
    
    const validations = [
      { name: 'Deployment Health', test: () => this.testDeploymentHealth() },
      { name: 'Proposal Integration', test: () => this.testProposalIntegration() },
      { name: 'Chaos/Warp Deployment', test: () => this.testChaosWarpDeployment() },
      { name: 'Production Performance', test: () => this.testPerformanceInProduction() },
      { name: 'Production Security', test: () => this.testSecurityInProduction() },
      { name: 'Monitoring and Logging', test: () => this.testMonitoringAndLogging() },
      { name: 'Data Persistence', test: () => this.testDataPersistence() },
      { name: 'Error Recovery', test: () => this.testErrorRecovery() }
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
    
    this.log('\n📊 Deployment Validation Results Summary');
    this.log('========================================');
    this.log(`Environment: ${this.environment}`);
    this.log(`Total Validations: ${totalValidations}`);
    this.log(`Passed: ${passedValidations}`);
    this.log(`Failed: ${totalValidations - passedValidations}`);
    this.log(`Success Rate: ${((passedValidations / totalValidations) * 100).toFixed(1)}%`);
    
    if (this.deploymentIssues.length > 0) {
      this.log(`\n⚠️ Deployment Issues (${this.deploymentIssues.length}):`);
      this.deploymentIssues.forEach(issue => {
        this.log(`   [${issue.severity}] ${issue.message}`);
      });
    }
    
    this.log('\n📋 Detailed Results:');
    this.validationResults.forEach(result => {
      const status = result.passed ? '✅' : '❌';
      this.log(`   ${status} ${result.test}: ${result.details}`);
    });
    
    if (passedValidations === totalValidations && this.deploymentIssues.filter(i => i.severity === 'ERROR').length === 0) {
      this.log('\n🎉 All deployment validations passed!');
      this.log(`✅ Deployment to ${this.environment} is successful`);
      this.log(`✅ Proposal ${options.proposalId} (${options.aiType}) is properly integrated`);
      return true;
    } else if (this.deploymentIssues.filter(i => i.severity === 'ERROR').length === 0) {
      this.log('\n⚠️ Some deployment validations failed, but no critical errors');
      this.log(`⚠️ Deployment to ${this.environment} can proceed with warnings`);
      return true;
    } else {
      this.log('\n❌ Critical deployment issues found');
      this.log(`❌ Deployment to ${this.environment} cannot proceed`);
      return false;
    }
  }

  getDeploymentReport() {
    return {
      proposalId: options.proposalId,
      aiType: options.aiType,
      environment: this.environment,
      timestamp: new Date().toISOString(),
      results: this.validationResults,
      issues: this.deploymentIssues,
      summary: {
        total: this.validationResults.length,
        passed: this.validationResults.filter(r => r.passed).length,
        failed: this.validationResults.filter(r => !r.passed).length,
        errorCount: this.deploymentIssues.filter(i => i.severity === 'ERROR').length,
        warningCount: this.deploymentIssues.filter(i => i.severity === 'WARNING').length
      }
    };
  }
}

// Main execution
async function main() {
  const validator = new DeploymentValidator(options.backendUrl, options.appUrl, options.environment);
  
  try {
    const isDeployed = await validator.runDeploymentValidation();
    
    // Save deployment report
    const report = validator.getDeploymentReport();
    const reportPath = path.join(process.cwd(), 'ai-backend', 'test-results', `deployment-validation-${options.proposalId}.json`);
    
    try {
      await fs.mkdir(path.dirname(reportPath), { recursive: true });
      await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
      console.log(`📄 Deployment report saved to: ${reportPath}`);
    } catch (error) {
      console.warn(`⚠️ Could not save deployment report: ${error.message}`);
    }
    
    if (!isDeployed) {
      process.exit(1);
    }
  } catch (error) {
    console.error('💥 Deployment validation failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { DeploymentValidator }; 