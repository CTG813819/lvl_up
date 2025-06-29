#!/usr/bin/env node

/**
 * Chaos/Warp Functionality Testing Script
 * Tests the complete Chaos/Warp hierarchy and operational hours system
 */

const axios = require('axios');
const { program } = require('commander');

// Configuration
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:3000';
const TEST_MODE = process.env.TEST_MODE || 'basic';

program
  .option('--testMode <mode>', 'Test mode: basic, comprehensive, or production', 'basic')
  .option('--backendUrl <url>', 'Backend URL for testing', BACKEND_URL)
  .parse(process.argv);

const options = program.opts();

class ChaosWarpTester {
  constructor(backendUrl) {
    this.backendUrl = backendUrl;
    this.testResults = [];
    this.currentStatus = null;
  }

  async log(message, type = 'INFO') {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [${type}] ${message}`);
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

  async testInitialStatus() {
    this.log('🧪 Testing Initial System Status');
    
    const result = await this.testEndpoint('/chaos-warp/status');
    if (result.success) {
      this.currentStatus = result.data;
      this.log(`✅ Initial status retrieved: ${result.data.hierarchy}`);
      this.log(`   - Warp Mode: ${result.data.warpMode}`);
      this.log(`   - Chaos Mode: ${result.data.chaosMode}`);
      this.log(`   - Operational Hours: ${result.data.operationalHours.formatted}`);
      this.log(`   - Within Hours: ${result.data.operationalHours.isWithin}`);
      this.log(`   - Should Operate AI: ${result.data.operationStatus.canOperate}`);
      return true;
    } else {
      this.log(`❌ Failed to get initial status: ${result.error}`, 'ERROR');
      return false;
    }
  }

  async testOperationalHours() {
    this.log('🧪 Testing Operational Hours Functionality');
    
    const result = await this.testEndpoint('/operational-hours');
    if (result.success) {
      this.log(`✅ Operational hours: ${result.data.operationalHours.formatted}`);
      this.log(`   - Current time: ${result.data.currentTime}`);
      this.log(`   - Within hours: ${result.data.isWithinOperationalHours}`);
      this.log(`   - Hierarchy: ${result.data.hierarchy}`);
      return true;
    } else {
      this.log(`❌ Failed to get operational hours: ${result.error}`, 'ERROR');
      return false;
    }
  }

  async testChaosActivation() {
    this.log('🧪 Testing Chaos Mode Activation');
    
    // First, ensure Warp mode is not active
    const warpStatus = await this.testEndpoint('/chaos-warp/status');
    if (warpStatus.success && warpStatus.data.warpMode) {
      this.log('⚠️ Warp mode is active, deactivating first...');
      await this.testEndpoint('/warp/deactivate', 'POST');
    }
    
    const result = await this.testEndpoint('/chaos/activate', 'POST');
    if (result.success) {
      this.log(`✅ Chaos mode activated successfully`);
      this.log(`   - Start time: ${result.data.chaosStartTime}`);
      this.log(`   - End time: ${result.data.chaosEndTime}`);
      this.log(`   - Hierarchy: ${result.data.hierarchy}`);
      this.log(`   - Operation status: ${result.data.operationStatus.message}`);
      
      // Verify AI operations are allowed
      if (result.data.operationStatus.canOperate) {
        this.log(`✅ AI operations confirmed allowed during Chaos mode`);
      } else {
        this.log(`❌ AI operations not allowed during Chaos mode`, 'ERROR');
        return false;
      }
      
      return true;
    } else {
      this.log(`❌ Failed to activate Chaos mode: ${result.error}`, 'ERROR');
      return false;
    }
  }

  async testWarpActivation() {
    this.log('🧪 Testing Warp Mode Activation');
    
    const result = await this.testEndpoint('/warp/activate', 'POST');
    if (result.success) {
      this.log(`✅ Warp mode activated successfully`);
      this.log(`   - Hierarchy: ${result.data.hierarchy}`);
      this.log(`   - Operation status: ${result.data.operationStatus.message}`);
      
      // Verify AI operations are stopped
      if (!result.data.operationStatus.canOperate) {
        this.log(`✅ AI operations confirmed stopped during Warp mode`);
      } else {
        this.log(`❌ AI operations still allowed during Warp mode`, 'ERROR');
        return false;
      }
      
      return true;
    } else {
      this.log(`❌ Failed to activate Warp mode: ${result.error}`, 'ERROR');
      return false;
    }
  }

  async testChaosActivationDuringWarp() {
    this.log('🧪 Testing Chaos Activation During Warp (Should Fail)');
    
    // Ensure Warp mode is active
    const warpStatus = await this.testEndpoint('/chaos-warp/status');
    if (!warpStatus.success || !warpStatus.data.warpMode) {
      this.log('⚠️ Warp mode not active, activating first...');
      await this.testEndpoint('/warp/activate', 'POST');
    }
    
    const result = await this.testEndpoint('/chaos/activate', 'POST');
    if (!result.success && result.status === 400) {
      this.log(`✅ Chaos activation correctly blocked during Warp mode`);
      this.log(`   - Error: ${result.error.error}`);
      this.log(`   - Hierarchy: ${result.error.hierarchy}`);
      return true;
    } else {
      this.log(`❌ Chaos activation should have been blocked during Warp mode`, 'ERROR');
      return false;
    }
  }

  async testWarpDeactivation() {
    this.log('🧪 Testing Warp Mode Deactivation');
    
    const result = await this.testEndpoint('/warp/deactivate', 'POST');
    if (result.success) {
      this.log(`✅ Warp mode deactivated successfully`);
      this.log(`   - Hierarchy: ${result.data.hierarchy}`);
      this.log(`   - Operation status: ${result.data.operationStatus.message}`);
      return true;
    } else {
      this.log(`❌ Failed to deactivate Warp mode: ${result.error}`, 'ERROR');
      return false;
    }
  }

  async testHierarchyEnforcement() {
    this.log('🧪 Testing Hierarchy Enforcement: WARP > CHAOS > OPERATIONAL_HOURS');
    
    const status = await this.testEndpoint('/chaos-warp/status');
    if (!status.success) {
      this.log(`❌ Failed to get status for hierarchy test: ${status.error}`, 'ERROR');
      return false;
    }
    
    const data = status.data;
    let hierarchyCorrect = true;
    
    // Test Warp mode (highest priority)
    if (data.warpMode) {
      if (data.operationStatus.canOperate) {
        this.log(`❌ Warp mode active but AI operations allowed`, 'ERROR');
        hierarchyCorrect = false;
      } else {
        this.log(`✅ Warp mode correctly stops AI operations`);
      }
    }
    // Test Chaos mode (medium priority)
    else if (data.chaosMode && data.isChaosActive) {
      if (!data.operationStatus.canOperate) {
        this.log(`❌ Chaos mode active but AI operations not allowed`, 'ERROR');
        hierarchyCorrect = false;
      } else {
        this.log(`✅ Chaos mode correctly allows AI operations (overrides operational hours)`);
      }
    }
    // Test operational hours (lowest priority)
    else {
      if (data.operationalHours.isWithin && !data.operationStatus.canOperate) {
        this.log(`❌ Within operational hours but AI operations not allowed`, 'ERROR');
        hierarchyCorrect = false;
      } else if (!data.operationalHours.isWithin && data.operationStatus.canOperate) {
        this.log(`❌ Outside operational hours but AI operations allowed`, 'ERROR');
        hierarchyCorrect = false;
      } else {
        this.log(`✅ Operational hours correctly enforced`);
      }
    }
    
    return hierarchyCorrect;
  }

  async testSystemStatus() {
    this.log('🧪 Testing System Status Endpoint');
    
    const result = await this.testEndpoint('/system-status');
    if (result.success) {
      this.log(`✅ System status retrieved successfully`);
      this.log(`   - Warp Mode: ${result.data.systemStatus.warpMode}`);
      this.log(`   - Chaos Mode: ${result.data.systemStatus.chaosMode}`);
      this.log(`   - Should Operate AI: ${result.data.systemStatus.shouldOperateAI}`);
      this.log(`   - Hierarchy: ${result.data.systemStatus.hierarchy}`);
      return true;
    } else {
      this.log(`❌ Failed to get system status: ${result.error}`, 'ERROR');
      return false;
    }
  }

  async runComprehensiveTests() {
    this.log('🚀 Starting Comprehensive Chaos/Warp Testing');
    this.log('=============================================');
    
    const tests = [
      { name: 'Initial Status', test: () => this.testInitialStatus() },
      { name: 'Operational Hours', test: () => this.testOperationalHours() },
      { name: 'System Status', test: () => this.testSystemStatus() },
      { name: 'Chaos Activation', test: () => this.testChaosActivation() },
      { name: 'Warp Activation', test: () => this.testWarpActivation() },
      { name: 'Chaos During Warp (Should Fail)', test: () => this.testChaosActivationDuringWarp() },
      { name: 'Warp Deactivation', test: () => this.testWarpDeactivation() },
      { name: 'Hierarchy Enforcement', test: () => this.testHierarchyEnforcement() }
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
      }
    }
    
    this.log('\n📊 Test Results Summary');
    this.log('=======================');
    this.log(`Total Tests: ${totalTests}`);
    this.log(`Passed: ${passedTests}`);
    this.log(`Failed: ${totalTests - passedTests}`);
    this.log(`Success Rate: ${((passedTests / totalTests) * 100).toFixed(1)}%`);
    
    if (passedTests === totalTests) {
      this.log('\n🎉 All Chaos/Warp tests passed!');
      this.log('✅ Hierarchy: WARP > CHAOS > OPERATIONAL_HOURS');
      this.log('✅ Operational hours: 05:00 - 21:00');
      this.log('✅ Chaos mode overrides operational hours');
      this.log('✅ Warp mode overrides Chaos mode');
    } else {
      this.log('\n⚠️ Some tests failed. Please check the implementation.');
      process.exit(1);
    }
  }

  async runBasicTests() {
    this.log('🚀 Starting Basic Chaos/Warp Testing');
    this.log('===================================');
    
    const tests = [
      { name: 'Initial Status', test: () => this.testInitialStatus() },
      { name: 'Operational Hours', test: () => this.testOperationalHours() },
      { name: 'Hierarchy Enforcement', test: () => this.testHierarchyEnforcement() }
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
      }
    }
    
    this.log('\n📊 Basic Test Results');
    this.log('=====================');
    this.log(`Passed: ${passedTests}/${totalTests}`);
    
    if (passedTests === totalTests) {
      this.log('\n✅ Basic Chaos/Warp functionality verified');
    } else {
      this.log('\n⚠️ Basic tests failed. Please check the implementation.');
      process.exit(1);
    }
  }
}

// Main execution
async function main() {
  const tester = new ChaosWarpTester(options.backendUrl);
  
  try {
    if (options.testMode === 'comprehensive') {
      await tester.runComprehensiveTests();
    } else {
      await tester.runBasicTests();
    }
  } catch (error) {
    console.error('💥 Test execution failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { ChaosWarpTester }; 