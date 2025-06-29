const axios = require('axios');

const BASE_URL = 'http://localhost:4000/api/conquest';

async function testConquestEndpoints() {
  console.log('🧪 Testing Conquest AI Endpoints...\n');

  try {
    // Test 1: Get Conquest AI status
    console.log('1. Testing GET /conquest/status');
    const statusResponse = await axios.get(`${BASE_URL}/status`);
    console.log('✅ Status Response:', statusResponse.data);
    console.log('');

    // Test 2: Get current apps
    console.log('2. Testing GET /conquest/apps');
    const appsResponse = await axios.get(`${BASE_URL}/apps`);
    console.log('✅ Apps Response:', appsResponse.data);
    console.log('');

    // Test 3: Create a new app suggestion
    console.log('3. Testing POST /conquest/create-app');
    const createAppData = {
      name: 'Test Conquest App',
      description: 'A test app created by Conquest AI',
      keywords: 'test, conquest, ai, flutter'
    };
    const createAppResponse = await axios.post(`${BASE_URL}/create-app`, createAppData);
    console.log('✅ Create App Response:', createAppResponse.data);
    console.log('');

    // Test 4: Define app requirements
    console.log('4. Testing POST /conquest/define-requirements');
    const requirementsData = {
      appId: createAppResponse.data.data.id,
      name: 'Test Conquest App',
      description: 'A test app created by Conquest AI',
      keywords: 'test, conquest, ai, flutter',
      learningData: {
        fromImperium: ['Use Provider for state management'],
        fromGuardian: ['Implement proper error handling'],
        fromSandbox: ['Add unit tests']
      }
    };
    const requirementsResponse = await axios.post(`${BASE_URL}/define-requirements`, requirementsData);
    console.log('✅ Requirements Response:', requirementsResponse.data);
    console.log('');

    // Test 5: Build app
    console.log('5. Testing POST /conquest/build-app');
    const buildData = {
      appId: createAppResponse.data.data.id,
      requirements: requirementsResponse.data.data.requirements,
      learningData: requirementsData.learningData
    };
    const buildResponse = await axios.post(`${BASE_URL}/build-app`, buildData);
    console.log('✅ Build Response:', buildResponse.data);
    console.log('');

    // Test 6: Test app
    console.log('6. Testing POST /conquest/test-app');
    const testData = {
      appId: createAppResponse.data.data.id,
      appPath: buildResponse.data.data.appPath,
      requirements: requirementsResponse.data.data.requirements
    };
    const testResponse = await axios.post(`${BASE_URL}/test-app`, testData);
    console.log('✅ Test Response:', testResponse.data);
    console.log('');

    // Test 7: Deploy to GitHub
    console.log('7. Testing POST /conquest/deploy-to-github');
    const deployData = {
      appId: createAppResponse.data.data.id,
      appName: 'Test Conquest App',
      appPath: buildResponse.data.data.appPath,
      description: 'A test app created by Conquest AI'
    };
    const deployResponse = await axios.post(`${BASE_URL}/deploy-to-github`, deployData);
    console.log('✅ Deploy Response:', deployResponse.data);
    console.log('');

    // Test 8: Get debug logs
    console.log('8. Testing GET /conquest/debug-logs');
    const logsResponse = await axios.get(`${BASE_URL}/debug-logs`);
    console.log('✅ Debug Logs Response:', logsResponse.data);
    console.log('');

    // Test 9: Get learnings
    console.log('9. Testing GET /conquest/learnings');
    const learningsResponse = await axios.get(`${BASE_URL}/learnings`);
    console.log('✅ Learnings Response:', learningsResponse.data);
    console.log('');

    // Test 10: Update operational hours
    console.log('10. Testing POST /conquest/update-operational-hours');
    const hoursData = {
      start: '08:00',
      end: '20:00'
    };
    const hoursResponse = await axios.post(`${BASE_URL}/update-operational-hours`, hoursData);
    console.log('✅ Operational Hours Response:', hoursResponse.data);
    console.log('');

    console.log('🎉 All Conquest AI endpoint tests completed successfully!');

  } catch (error) {
    console.error('❌ Test failed:', error.response?.data || error.message);
    
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Headers:', error.response.headers);
    }
  }
}

// Run the tests
testConquestEndpoints(); 