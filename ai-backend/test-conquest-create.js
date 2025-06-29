const axios = require('axios');

async function testConquestCreate() {
  try {
    console.log('Testing Conquest create-app endpoint...');
    
    const response = await axios.post('http://localhost:4000/api/conquest/create-app', {
      name: 'Test App',
      description: 'A test app for learning',
      keywords: 'flutter,ai,learning'
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log('✅ Success!');
    console.log('Response:', JSON.stringify(response.data, null, 2));
  } catch (error) {
    console.error('❌ Error:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Status:', error.response.status);
    }
  }
}

testConquestCreate(); 