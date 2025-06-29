#!/usr/bin/env node

/**
 * Comprehensive Chaos/Warp Functionality Test
 * Tests the complete hierarchy: WARP > CHAOS > OPERATIONAL_HOURS
 */

const axios = require('axios');
const { spawn } = require('child_process');

// Configuration
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:4000';
const TEST_TIMEOUT = 30000; // 30 seconds

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
 * Test 1: Verify operational hours configuration
 */
async function testOperationalHours() {
  try {
    console.log('1️⃣ Testing operational hours configuration...');
    
    const response = await axios.get(`${BACKEND_URL}/api/chaos-warp/operational-hours`, {
      timeout: TEST_TIMEOUT
    });
    
    if (response.status === 200) {
      const data = response.data;
      
      // Verify operational hours are set to 5 AM - 9 PM
      if (data.operationalHours.start === 5 && data.operationalHours.end === 21) {
        testResults.tests.push({
          test: 'operational_hours',
          status: 'PASSED',
          message: 'Operational hours correctly configured (5 AM - 9 PM)',
          details: data.operationalHours
        });
        testResults.summary.passed++;
        return true;
      } else {
        testResults.tests.push({
          test: 'operational_hours',
          status: 'FAILED',
          message: `Operational hours incorrect: ${data.operationalHours.start}:00 - ${data.operationalHours.end}:00`,
          expected: { start: 5, end: 21 },
          actual: data.operationalHours
        });
        testResults.summary.failed++;
        testResults.overall = 'FAILED';
        return false;
      }
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'operational_hours',
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
 * Test 2: Verify Chaos mode activation
 */
async function testChaosActivation() {
  try {
    console.log('2️⃣ Testing Chaos mode activation...');
    
    const response = await axios.post(`${BACKEND_URL}/api/chaos/activate`, {}, {
      timeout: TEST_TIMEOUT
    });
    
    if (response.status === 200) {
      const data = response.data;
      
      // Verify Chaos mode is activated
      if (data.success && data.operationStatus.reason === 'CHAOS_MODE_ACTIVE') {
        testResults.tests.push({
          test: 'chaos_activation',
          status: 'PASSED',
          message: 'Chaos mode successfully activated',
          details: {
            chaosStartTime: data.chaosStartTime,
            chaosEndTime: data.chaosEndTime,
            hierarchy: data.hierarchy
          }
        });
        testResults.summary.passed++;
        return true;
      } else {
        testResults.tests.push({
          test: 'chaos_activation',
          status: 'FAILED',
          message: 'Chaos mode not properly activated',
          details: data
        });
        testResults.summary.failed++;
        testResults.overall = 'FAILED';
        return false;
      }
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'chaos_activation',
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
 * Test 3: Verify Chaos mode overrides operational hours
 */
async function testChaosOverride() {
  try {
    console.log('3️⃣ Testing Chaos mode override of operational hours...');
    
    const response = await axios.get(`${BACKEND_URL}/api/chaos-warp/status`, {
      timeout: TEST_TIMEOUT
    });
    
    if (response.status === 200) {
      const data = response.data;
      
      // Verify Chaos mode is active and overrides operational hours
      if (data.chaosMode && data.operationStatus.reason === 'CHAOS_MODE_ACTIVE') {
        testResults.tests.push({
          test: 'chaos_override',
          status: 'PASSED',
          message: 'Chaos mode successfully overrides operational hours',
          details: {
            chaosMode: data.chaosMode,
            operationStatus: data.operationStatus,
            hierarchy: data.hierarchy
          }
        });
        testResults.summary.passed++;
        return true;
      } else {
        testResults.tests.push({
          test: 'chaos_override',
          status: 'FAILED',
          message: 'Chaos mode not properly overriding operational hours',
          details: data
        });
        testResults.summary.failed++;
        testResults.overall = 'FAILED';
        return false;
      }
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'chaos_override',
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
 * Test 4: Verify Warp mode activation overrides Chaos
 */
async function testWarpOverride() {
  try {
    console.log('4️⃣ Testing Warp mode activation overrides Chaos...');
    
    const response = await axios.post(`${BACKEND_URL}/api/warp/activate`, {}, {
      timeout: TEST_TIMEOUT
    });
    
    if (response.status === 200) {
      const data = response.data;
      
      // Verify Warp mode is activated and overrides Chaos
      if (data.success && data.operationStatus.reason === 'WARP_MODE_ACTIVE') {
        testResults.tests.push({
          test: 'warp_override',
          status: 'PASSED',
          message: 'Warp mode successfully overrides Chaos mode',
          details: {
            warpMode: data.warpMode,
            operationStatus: data.operationStatus,
            hierarchy: data.hierarchy
          }
        });
        testResults.summary.passed++;
        return true;
      } else {
        testResults.tests.push({
          test: 'warp_override',
          status: 'FAILED',
          message: 'Warp mode not properly overriding Chaos mode',
          details: data
        });
        testResults.summary.failed++;
        testResults.overall = 'FAILED';
        return false;
      }
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'warp_override',
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
 * Test 5: Verify Chaos cannot activate during Warp
 */
async function testChaosBlockedByWarp() {
  try {
    console.log('5️⃣ Testing Chaos mode blocked by Warp mode...');
    
    const response = await axios.post(`${BACKEND_URL}/api/chaos/activate`, {}, {
      timeout: TEST_TIMEOUT
    });
    
    if (response.status === 400) {
      const data = response.data;
      
      // Verify Chaos mode is blocked by Warp mode
      if (data.error && data.error.includes('Cannot activate Chaos while Warp mode is active')) {
        testResults.tests.push({
          test: 'chaos_blocked_by_warp',
          status: 'PASSED',
          message: 'Chaos mode correctly blocked by Warp mode',
          details: {
            error: data.error,
            hierarchy: data.hierarchy,
            currentStatus: data.currentStatus
          }
        });
        testResults.summary.passed++;
        return true;
      } else {
        testResults.tests.push({
          test: 'chaos_blocked_by_warp',
          status: 'FAILED',
          message: 'Chaos mode not properly blocked by Warp mode',
          details: data
        });
        testResults.summary.failed++;
        testResults.overall = 'FAILED';
        return false;
      }
    } else {
      throw new Error(`Expected HTTP 400, got ${response.status}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'chaos_blocked_by_warp',
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
 * Test 6: Verify Warp mode deactivation
 */
async function testWarpDeactivation() {
  try {
    console.log('6️⃣ Testing Warp mode deactivation...');
    
    const response = await axios.post(`${BACKEND_URL}/api/warp/deactivate`, {}, {
      timeout: TEST_TIMEOUT
    });
    
    if (response.status === 200) {
      const data = response.data;
      
      // Verify Warp mode is deactivated
      if (data.success && !data.warpMode) {
        testResults.tests.push({
          test: 'warp_deactivation',
          status: 'PASSED',
          message: 'Warp mode successfully deactivated',
          details: {
            warpMode: data.warpMode,
            operationStatus: data.operationStatus,
            hierarchy: data.hierarchy
          }
        });
        testResults.summary.passed++;
        return true;
      } else {
        testResults.tests.push({
          test: 'warp_deactivation',
          status: 'FAILED',
          message: 'Warp mode not properly deactivated',
          details: data
        });
        testResults.summary.failed++;
        testResults.overall = 'FAILED';
        return false;
      }
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'warp_deactivation',
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
 * Test 7: Verify AI operations resume after Warp
 */
async function testAIOperationsResume() {
  try {
    console.log('7️⃣ Testing AI operations resume after Warp...');
    
    const response = await axios.get(`${BACKEND_URL}/api/chaos-warp/status`, {
      timeout: TEST_TIMEOUT
    });
    
    if (response.status === 200) {
      const data = response.data;
      
      // Verify AI operations can resume (either Chaos mode or operational hours)
      if (data.operationStatus.canOperate || data.chaosMode) {
        testResults.tests.push({
          test: 'ai_operations_resume',
          status: 'PASSED',
          message: 'AI operations can resume after Warp mode',
          details: {
            canOperate: data.operationStatus.canOperate,
            chaosMode: data.chaosMode,
            operationStatus: data.operationStatus,
            hierarchy: data.hierarchy
          }
        });
        testResults.summary.passed++;
        return true;
      } else {
        testResults.tests.push({
          test: 'ai_operations_resume',
          status: 'FAILED',
          message: 'AI operations not resuming after Warp mode',
          details: data
        });
        testResults.summary.failed++;
        testResults.overall = 'FAILED';
        return false;
      }
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'ai_operations_resume',
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
 * Test 8: Verify AIQuotaService hierarchy compliance
 */
async function testAIQuotaServiceHierarchy() {
  try {
    console.log('8️⃣ Testing AIQuotaService hierarchy compliance...');
    
    const response = await axios.get(`${BACKEND_URL}/api/ai-quota/status`, {
      timeout: TEST_TIMEOUT
    });
    
    if (response.status === 200) {
      const data = response.data;
      
      // Verify AIQuotaService respects the hierarchy
      if (data.operationStatus && data.operationStatus.hierarchy) {
        testResults.tests.push({
          test: 'ai_quota_hierarchy',
          status: 'PASSED',
          message: 'AIQuotaService correctly implements hierarchy',
          details: {
            operationStatus: data.operationStatus,
            hierarchy: data.operationStatus.hierarchy
          }
        });
        testResults.summary.passed++;
        return true;
      } else {
        testResults.tests.push({
          test: 'ai_quota_hierarchy',
          status: 'FAILED',
          message: 'AIQuotaService not implementing hierarchy correctly',
          details: data
        });
        testResults.summary.failed++;
        testResults.overall = 'FAILED';
        return false;
      }
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'ai_quota_hierarchy',
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
 * Test 9: Verify Chaos mode auto-deactivation
 */
async function testChaosAutoDeactivation() {
  try {
    console.log('9️⃣ Testing Chaos mode auto-deactivation...');
    
    // Wait a moment for any auto-deactivation to occur
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const response = await axios.get(`${BACKEND_URL}/api/chaos-warp/status`, {
      timeout: TEST_TIMEOUT
    });
    
    if (response.status === 200) {
      const data = response.data;
      
      // Check if Chaos mode is still active or has been auto-deactivated
      if (data.chaosMode && data.isChaosActive) {
        testResults.tests.push({
          test: 'chaos_auto_deactivation',
          status: 'SKIPPED',
          message: 'Chaos mode still active (not yet time for auto-deactivation)',
          details: {
            chaosMode: data.chaosMode,
            isChaosActive: data.isChaosActive,
            remainingTime: data.remainingTime
          }
        });
        testResults.summary.skipped++;
        return true;
      } else if (!data.chaosMode) {
        testResults.tests.push({
          test: 'chaos_auto_deactivation',
          status: 'PASSED',
          message: 'Chaos mode auto-deactivated successfully',
          details: {
            chaosMode: data.chaosMode,
            isChaosActive: data.isChaosActive
          }
        });
        testResults.summary.passed++;
        return true;
      } else {
        testResults.tests.push({
          test: 'chaos_auto_deactivation',
          status: 'FAILED',
          message: 'Chaos mode auto-deactivation not working correctly',
          details: data
        });
        testResults.summary.failed++;
        testResults.overall = 'FAILED';
        return false;
      }
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (error) {
    testResults.tests.push({
      test: 'chaos_auto_deactivation',
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
      
      // Verify all required status fields are present
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
          message: 'Complete system status contains all required fields',
          details: {
            systemStatus: data.systemStatus,
            operationStatus: data.operationStatus,
            currentTime: data.currentTime
          }
        });
        testResults.summary.passed++;
        return true;
      } else {
        testResults.tests.push({
          test: 'complete_system_status',
          status: 'FAILED',
          message: `Missing required fields: ${missingFields.join(', ')}`,
          details: {
            missingFields,
            data
          }
        });
        testResults.summary.failed++;
        testResults.overall = 'FAILED';
        return false;
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
async function runComprehensiveTests() {
  console.log('🚀 Starting Comprehensive Chaos/Warp Functionality Tests');
  console.log('=======================================================');
  console.log(`Backend URL: ${BACKEND_URL}`);
  console.log(`Test Timeout: ${TEST_TIMEOUT}ms`);
  console.log('');
  
  const tests = [
    { name: 'Operational Hours Configuration', test: testOperationalHours },
    { name: 'Chaos Mode Activation', test: testChaosActivation },
    { name: 'Chaos Override Operational Hours', test: testChaosOverride },
    { name: 'Warp Mode Override Chaos', test: testWarpOverride },
    { name: 'Chaos Blocked by Warp', test: testChaosBlockedByWarp },
    { name: 'Warp Mode Deactivation', test: testWarpDeactivation },
    { name: 'AI Operations Resume', test: testAIOperationsResume },
    { name: 'AIQuotaService Hierarchy', test: testAIQuotaServiceHierarchy },
    { name: 'Chaos Auto-Deactivation', test: testChaosAutoDeactivation },
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
  const fs = require('fs');
  const resultsDir = './test-results';
  if (!fs.existsSync(resultsDir)) {
    fs.mkdirSync(resultsDir, { recursive: true });
  }
  
  const resultsFile = `${resultsDir}/chaos-warp-test-results-${Date.now()}.json`;
  fs.writeFileSync(resultsFile, JSON.stringify(testResults, null, 2));
  console.log(`\n💾 Test results saved to: ${resultsFile}`);
  
  // Exit with appropriate code
  if (testResults.overall === 'PASSED') {
    console.log('\n🎉 All Chaos/Warp tests passed!');
    console.log('✅ Hierarchy: WARP > CHAOS > OPERATIONAL_HOURS');
    console.log('✅ Operational hours: 05:00 - 21:00');
    console.log('✅ Chaos mode overrides operational hours');
    console.log('✅ Warp mode overrides Chaos mode');
    process.exit(0);
  } else {
    console.log('\n⚠️ Some tests failed. Please check the implementation.');
    process.exit(1);
  }
}

// Run tests if this script is executed directly
if (require.main === module) {
  runComprehensiveTests().catch(error => {
    console.error('💥 Test execution failed:', error);
    process.exit(1);
  });
}

module.exports = {
  runComprehensiveTests,
  testResults
}; 