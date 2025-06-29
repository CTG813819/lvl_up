#!/usr/bin/env node

/**
 * Chaos/Warp Production Testing Script
 * Tests Chaos/Warp functionality in production environment
 */

const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');

// Configuration
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:3000';
const PRODUCTION_MODE = process.env.PRODUCTION_MODE === 'true';

class ChaosWarpProductionTester {
  constructor(backendUrl) {
    this.backendUrl = backendUrl;
    this.testResults = [];
    this.productionIssues = [];
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
    this.productionIssues.push({
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

  async testProductionStatus() {
    this.log('🧪 Testing Production Status');
    
    const statusResult = await this.testEndpoint('/chaos-warp/status');
    if (statusResult.success) {
      const status = statusResult.data;
      this.log(`✅ Production Chaos/Warp status retrieved`);
      this.log(`   - Warp Mode: ${status.warpMode}`);
      this.log(`   - Chaos Mode: ${status.chaosMode}`);
      this.log(`   - Should Operate AI: ${status.operationStatus.canOperate}`);
      this.log(`   - Hierarchy: ${status.hierarchy}`);
      this.log(`   - Operational Hours: ${status.operationalHours.formatted}`);
      this.log(`   - Current Time: ${status.currentTime}`);
      
      this.addResult('Production Status', true, `Status: ${status.hierarchy}`);
      return true;
    } else {
      this.log(`❌ Failed to get production status: ${statusResult.error}`, 'ERROR');
      this.addResult('Production Status', false, `Status error: ${statusResult.error}`);
      return false;
    }
  }

  async testProductionPerformance() {
    this.log('🧪 Testing Production Performance');
    
    const performanceTests = [
      { name: 'Status Endpoint', endpoint: '/chaos-warp/status' },
      { name: 'Operational Hours', endpoint: '/operational-hours' },
      { name: 'System Status', endpoint: '/system-status' }
    ];
    
    let totalResponseTime = 0;
    let successfulRequests = 0;
    const maxAcceptableTime = PRODUCTION_MODE ? 1000 : 3000; // 1s for production, 3s for staging
    
    for (const test of performanceTests) {
      const startTime = Date.now();
      const result = await this.testEndpoint(test.endpoint);
      const responseTime = Date.now() - startTime;
      
      if (result.success) {
        totalResponseTime += responseTime;
        successfulRequests++;
        this.log(`✅ ${test.name}: ${responseTime}ms`);
        
        if (responseTime > maxAcceptableTime) {
          this.addIssue(`${test.name} response time (${responseTime}ms) exceeds production limit (${maxAcceptableTime}ms)`, 'WARNING');
        }
      } else {
        this.log(`❌ ${test.name}: Failed (${responseTime}ms)`);
      }
    }
    
    if (successfulRequests > 0) {
      const averageResponseTime = totalResponseTime / successfulRequests;
      this.log(`📊 Average response time: ${averageResponseTime.toFixed(2)}ms`);
      this.log(`📊 Production mode: ${PRODUCTION_MODE}`);
      this.log(`📊 Max acceptable: ${maxAcceptableTime}ms`);
      
      if (averageResponseTime <= maxAcceptableTime) {
        this.log(`✅ Production performance meets requirements`);
        this.addResult('Production Performance', true, `Average: ${averageResponseTime.toFixed(2)}ms (≤${maxAcceptableTime}ms)`);
        return true;
      } else {
        this.log(`⚠️ Production performance below requirements`, 'WARNING');
        this.addResult('Production Performance', false, `Average: ${averageResponseTime.toFixed(2)}ms (>${maxAcceptableTime}ms)`);
        return false;
      }
    } else {
      this.log(`❌ No successful requests to measure performance`, 'ERROR');
      this.addResult('Production Performance', false, 'No successful requests');
      return false;
    }
  }

  async testProductionReliability() {
    this.log('🧪 Testing Production Reliability');
    
    // Test multiple requests to ensure reliability
    const reliabilityTests = 5;
    let successfulTests = 0;
    
    for (let i = 0; i < reliabilityTests; i++) {
      const result = await this.testEndpoint('/chaos-warp/status');
      if (result.success) {
        successfulTests++;
        this.log(`✅ Reliability test ${i + 1}/${reliabilityTests}: Success`);
      } else {
        this.log(`❌ Reliability test ${i + 1}/${reliabilityTests}: Failed`, 'ERROR');
      }
      
      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    const reliabilityRate = (successfulTests / reliabilityTests) * 100;
    this.log(`📊 Reliability rate: ${reliabilityRate.toFixed(1)}% (${successfulTests}/${reliabilityTests})`);
    
    if (reliabilityRate >= 95) {
      this.log(`✅ Production reliability is excellent`);
      this.addResult('Production Reliability', true, `Reliability: ${reliabilityRate.toFixed(1)}%`);
      return true;
    } else if (reliabilityRate >= 80) {
      this.log(`⚠️ Production reliability is acceptable`, 'WARNING');
      this.addResult('Production Reliability', true, `Reliability: ${reliabilityRate.toFixed(1)}%`);
      return true;
    } else {
      this.log(`❌ Production reliability is poor`, 'ERROR');
      this.addResult('Production Reliability', false, `Reliability: ${reliabilityRate.toFixed(1)}%`);
      return false;
    }
  }

  async testProductionSecurity() {
    this.log('🧪 Testing Production Security');
    
    const securityTests = [
      { name: 'Invalid Endpoint', endpoint: '/chaos-warp/invalid-endpoint', expectedStatus: 404 },
      { name: 'Invalid Method', endpoint: '/chaos-warp/status', method: 'PUT', expectedStatus: 405 },
      { name: 'Malformed Data', endpoint: '/chaos-warp/status', method: 'POST', data: { invalid: 'data' }, expectedStatus: 400 }
    ];
    
    let securityScore = 0;
    let totalSecurityTests = securityTests.length;
    
    for (const test of securityTests) {
      const result = await this.testEndpoint(test.endpoint, test.method, test.data);
      
      if (!result.success && result.status === test.expectedStatus) {
        this.log(`✅ ${test.name}: Proper security response (${result.status})`);
        securityScore++;
      } else {
        this.log(`❌ ${test.name}: Unexpected security response (${result.status || 'N/A'})`, 'ERROR');
      }
    }
    
    this.log(`📊 Security Score: ${securityScore}/${totalSecurityTests}`);
    this.addResult('Production Security', securityScore === totalSecurityTests, `Security score: ${securityScore}/${totalSecurityTests}`);
    
    return securityScore === totalSecurityTests;
  }

  async testProductionMonitoring() {
    this.log('🧪 Testing Production Monitoring');
    
    const monitoringTests = [
      { name: 'System Status', endpoint: '/system-status' },
      { name: 'Operational Hours', endpoint: '/operational-hours' }
    ];
    
    let monitoringScore = 0;
    let totalMonitoringTests = monitoringTests.length;
    
    for (const test of monitoringTests) {
      const result = await this.testEndpoint(test.endpoint);
      if (result.success) {
        this.log(`✅ ${test.name}: Available for monitoring`);
        monitoringScore++;
      } else {
        this.log(`⚠️ ${test.name}: Not available for monitoring (${result.status || 'N/A'})`, 'WARNING');
        this.addIssue(`${test.name} not available - may affect production monitoring`, 'WARNING');
      }
    }
    
    this.log(`📊 Monitoring Score: ${monitoringScore}/${totalMonitoringTests}`);
    this.addResult('Production Monitoring', monitoringScore === totalMonitoringTests, `Monitoring score: ${monitoringScore}/${totalMonitoringTests}`);
    
    return monitoringScore === totalMonitoringTests;
  }

  async testProductionDataConsistency() {
    this.log('🧪 Testing Production Data Consistency');
    
    // Test that Chaos/Warp data is consistent across multiple requests
    const consistencyTests = 3;
    const results = [];
    
    for (let i = 0; i < consistencyTests; i++) {
      const result = await this.testEndpoint('/chaos-warp/status');
      if (result.success) {
        results.push(result.data);
        this.log(`✅ Consistency test ${i + 1}/${consistencyTests}: Data retrieved`);
      } else {
        this.log(`❌ Consistency test ${i + 1}/${consistencyTests}: Failed`, 'ERROR');
      }
      
      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    if (results.length === consistencyTests) {
      // Check if all results are consistent
      const firstResult = results[0];
      let isConsistent = true;
      
      for (let i = 1; i < results.length; i++) {
        const currentResult = results[i];
        
        if (currentResult.warpMode !== firstResult.warpMode ||
            currentResult.chaosMode !== firstResult.chaosMode ||
            currentResult.operationStatus.canOperate !== firstResult.operationStatus.canOperate) {
          isConsistent = false;
          break;
        }
      }
      
      if (isConsistent) {
        this.log(`✅ Production data consistency confirmed`);
        this.log(`   - Warp Mode: ${firstResult.warpMode}`);
        this.log(`   - Chaos Mode: ${firstResult.chaosMode}`);
        this.log(`   - Should Operate AI: ${firstResult.operationStatus.canOperate}`);
        this.addResult('Production Data Consistency', true, 'Data consistent across requests');
        return true;
      } else {
        this.log(`❌ Production data inconsistency detected`, 'ERROR');
        this.addResult('Production Data Consistency', false, 'Data inconsistent across requests');
        return false;
      }
    } else {
      this.log(`❌ Cannot test data consistency - not all requests succeeded`, 'ERROR');
      this.addResult('Production Data Consistency', false, 'Not all requests succeeded');
      return false;
    }
  }

  async testProductionErrorHandling() {
    this.log('🧪 Testing Production Error Handling');
    
    const errorTests = [
      { name: 'Invalid Chaos Action', endpoint: '/chaos/invalid-action', expectedStatus: 404 },
      { name: 'Invalid Warp Action', endpoint: '/warp/invalid-action', expectedStatus: 404 },
      { name: 'Invalid Status Path', endpoint: '/chaos-warp/invalid-status', expectedStatus: 404 }
    ];
    
    let properErrorHandling = 0;
    let totalErrorTests = errorTests.length;
    
    for (const test of errorTests) {
      const result = await this.testEndpoint(test.endpoint);
      
      if (!result.success && result.status === test.expectedStatus) {
        this.log(`✅ ${test.name}: Proper error handling (${result.status})`);
        properErrorHandling++;
      } else {
        this.log(`❌ ${test.name}: Unexpected error handling (${result.status || 'N/A'})`, 'ERROR');
      }
    }
    
    this.log(`📊 Error Handling: ${properErrorHandling}/${totalErrorTests} proper error handling`);
    this.addResult('Production Error Handling', properErrorHandling === totalErrorTests, `${properErrorHandling}/${totalErrorTests} proper error handling`);
    
    return properErrorHandling === totalErrorTests;
  }

  async runProductionTests() {
    this.log('🚀 Starting Chaos/Warp Production Testing');
    this.log('=========================================');
    this.log(`Backend URL: ${this.backendUrl}`);
    this.log(`Production Mode: ${PRODUCTION_MODE}`);
    
    const tests = [
      { name: 'Production Status', test: () => this.testProductionStatus() },
      { name: 'Production Performance', test: () => this.testProductionPerformance() },
      { name: 'Production Reliability', test: () => this.testProductionReliability() },
      { name: 'Production Security', test: () => this.testProductionSecurity() },
      { name: 'Production Monitoring', test: () => this.testProductionMonitoring() },
      { name: 'Production Data Consistency', test: () => this.testProductionDataConsistency() },
      { name: 'Production Error Handling', test: () => this.testProductionErrorHandling() }
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
    
    this.log('\n📊 Production Test Results Summary');
    this.log('==================================');
    this.log(`Total Tests: ${totalTests}`);
    this.log(`Passed: ${passedTests}`);
    this.log(`Failed: ${totalTests - passedTests}`);
    this.log(`Success Rate: ${((passedTests / totalTests) * 100).toFixed(1)}%`);
    
    if (this.productionIssues.length > 0) {
      this.log(`\n⚠️ Production Issues (${this.productionIssues.length}):`);
      this.productionIssues.forEach(issue => {
        this.log(`   [${issue.severity}] ${issue.message}`);
      });
    }
    
    this.log('\n📋 Detailed Results:');
    this.testResults.forEach(result => {
      const status = result.passed ? '✅' : '❌';
      this.log(`   ${status} ${result.test}: ${result.details}`);
    });
    
    if (passedTests === totalTests && this.productionIssues.filter(i => i.severity === 'ERROR').length === 0) {
      this.log('\n🎉 All production tests passed!');
      this.log('✅ Chaos/Warp system is production-ready');
      this.log('✅ All functionality working correctly in production');
      return true;
    } else if (this.productionIssues.filter(i => i.severity === 'ERROR').length === 0) {
      this.log('\n⚠️ Some production tests failed, but no critical errors');
      this.log('⚠️ Chaos/Warp system can operate in production with warnings');
      return true;
    } else {
      this.log('\n❌ Critical production issues found');
      this.log('❌ Chaos/Warp system is not production-ready');
      return false;
    }
  }

  getProductionReport() {
    return {
      timestamp: new Date().toISOString(),
      productionMode: PRODUCTION_MODE,
      backendUrl: this.backendUrl,
      results: this.testResults,
      issues: this.productionIssues,
      summary: {
        total: this.testResults.length,
        passed: this.testResults.filter(r => r.passed).length,
        failed: this.testResults.filter(r => !r.passed).length,
        errorCount: this.productionIssues.filter(i => i.severity === 'ERROR').length,
        warningCount: this.productionIssues.filter(i => i.severity === 'WARNING').length
      }
    };
  }
}

// Main execution
async function main() {
  const tester = new ChaosWarpProductionTester(BACKEND_URL);
  
  try {
    const isProductionReady = await tester.runProductionTests();
    
    // Save production report
    const report = tester.getProductionReport();
    const reportPath = path.join(process.cwd(), 'ai-backend', 'test-results', `chaos-warp-production-${Date.now()}.json`);
    
    try {
      await fs.mkdir(path.dirname(reportPath), { recursive: true });
      await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
      console.log(`📄 Production report saved to: ${reportPath}`);
    } catch (error) {
      console.warn(`⚠️ Could not save production report: ${error.message}`);
    }
    
    if (!isProductionReady) {
      process.exit(1);
    }
  } catch (error) {
    console.error('💥 Production testing failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { ChaosWarpProductionTester }; 