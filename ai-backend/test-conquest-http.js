// Simple HTTP server to test Conquest endpoints
const express = require('express');
const conquestRouter = require('./src/routes/conquest');

// Add CORS middleware
function cors(req, res, next) {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  
  if (req.method === 'OPTIONS') {
    res.sendStatus(200);
  } else {
    next();
  }
}

const app = express();
const PORT = 4001;

// Middleware
app.use(express.json());
app.use(cors);

// Mount Conquest routes
app.use('/api/conquest', conquestRouter);

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    message: 'Conquest Test Server is running'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Conquest Test Server running on port ${PORT}`);
  console.log(`📡 Health check: http://localhost:${PORT}/health`);
  console.log(`🔗 Conquest API: http://localhost:${PORT}/api/conquest`);
  console.log('');
});

// Test the endpoints after server starts
setTimeout(async () => {
  console.log('🧪 Testing Conquest endpoints...\n');
  
  try {
    const axios = require('axios');
    const BASE_URL = `http://localhost:${PORT}/api/conquest`;

    // Test 1: Health check
    console.log('1. Testing health check');
    const healthResponse = await axios.get(`http://localhost:${PORT}/health`);
    console.log('✅ Health Response:', healthResponse.data);
    console.log('');

    // Test 2: Get Conquest status
    console.log('2. Testing GET /conquest/status');
    const statusResponse = await axios.get(`${BASE_URL}/status`);
    console.log('✅ Status Response:', statusResponse.data);
    console.log('');

    // Test 3: Get apps
    console.log('3. Testing GET /conquest/apps');
    const appsResponse = await axios.get(`${BASE_URL}/apps`);
    console.log('✅ Apps Response:', appsResponse.data);
    console.log('');

    // Test 4: Create app
    console.log('4. Testing POST /conquest/create-app');
    const createAppData = {
      name: 'Test Conquest App',
      description: 'A test app created by Conquest AI',
      keywords: 'test, conquest, ai, flutter'
    };
    const createAppResponse = await axios.post(`${BASE_URL}/create-app`, createAppData);
    console.log('✅ Create App Response:', createAppResponse.data);
    console.log('');

    // Test 5: Define requirements
    console.log('5. Testing POST /conquest/define-requirements');
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

    // Test 6: Build app
    console.log('6. Testing POST /conquest/build-app');
    const buildData = {
      appId: createAppResponse.data.data.id,
      requirements: requirementsResponse.data.data.requirements,
      learningData: requirementsData.learningData
    };
    const buildResponse = await axios.post(`${BASE_URL}/build-app`, buildData);
    console.log('✅ Build Response:', buildResponse.data);
    console.log('');

    // Test 7: Test app
    console.log('7. Testing POST /conquest/test-app');
    const testData = {
      appId: createAppResponse.data.data.id,
      appPath: buildResponse.data.data.appPath,
      requirements: requirementsResponse.data.data.requirements
    };
    const testResponse = await axios.post(`${BASE_URL}/test-app`, testData);
    console.log('✅ Test Response:', testResponse.data);
    console.log('');

    // Test 8: Deploy to GitHub
    console.log('8. Testing POST /conquest/deploy-to-github');
    const deployData = {
      appId: createAppResponse.data.data.id,
      appName: 'Test Conquest App',
      appPath: buildResponse.data.data.appPath,
      description: 'A test app created by Conquest AI'
    };
    const deployResponse = await axios.post(`${BASE_URL}/deploy-to-github`, deployData);
    console.log('✅ Deploy Response:', deployResponse.data);
    console.log('');

    // Test 9: Get debug logs
    console.log('9. Testing GET /conquest/debug-logs');
    const logsResponse = await axios.get(`${BASE_URL}/debug-logs`);
    console.log('✅ Debug Logs Response:', logsResponse.data);
    console.log('');

    // Test 10: Get learnings
    console.log('10. Testing GET /conquest/learnings');
    const learningsResponse = await axios.get(`${BASE_URL}/learnings`);
    console.log('✅ Learnings Response:', learningsResponse.data);
    console.log('');

    // Test 11: Update operational hours
    console.log('11. Testing POST /conquest/update-operational-hours');
    const hoursData = {
      start: '08:00',
      end: '20:00'
    };
    const hoursResponse = await axios.post(`${BASE_URL}/update-operational-hours`, hoursData);
    console.log('✅ Operational Hours Response:', hoursResponse.data);
    console.log('');

    console.log('🎉 All Conquest AI endpoint tests completed successfully!');
    console.log('');
    console.log('📊 Test Summary:');
    console.log('  ✅ Health check: Working');
    console.log('  ✅ Status endpoint: Working');
    console.log('  ✅ Apps endpoint: Working');
    console.log('  ✅ Create app: Working');
    console.log('  ✅ Define requirements: Working');
    console.log('  ✅ Build app: Working');
    console.log('  ✅ Test app: Working');
    console.log('  ✅ Deploy to GitHub: Working');
    console.log('  ✅ Debug logs: Working');
    console.log('  ✅ Learnings: Working');
    console.log('  ✅ Operational hours: Working');
    console.log('');
    console.log('🚀 Conquest AI system is fully operational!');

  } catch (error) {
    console.error('❌ Test failed:', error.response?.data || error.message);
    
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Headers:', error.response.headers);
    }
  }
}, 2000); 