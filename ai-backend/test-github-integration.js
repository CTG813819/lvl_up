require('dotenv').config();
const mongoose = require('mongoose');
const AILearningOrchestrator = require('./src/services/aiLearningOrchestrator');
const GitHubService = require('./src/services/githubService');

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/lvl_up', {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

async function testGitHubIntegration() {
  console.log('🧪 Testing GitHub Integration for Conquest AI...\n');

  try {
    // Test 1: Check if GitHub service is properly exported
    console.log('1. Testing GitHub service exports');
    console.log('✅ Available methods:', Object.keys(GitHubService));
    console.log('');

    // Test 2: Test createRepository method exists
    console.log('2. Testing createRepository method');
    if (typeof GitHubService.createRepository === 'function') {
      console.log('✅ createRepository method exists');
    } else {
      console.log('❌ createRepository method missing');
    }
    console.log('');

    // Test 3: Test pushToRepository method exists
    console.log('3. Testing pushToRepository method');
    if (typeof GitHubService.pushToRepository === 'function') {
      console.log('✅ pushToRepository method exists');
    } else {
      console.log('❌ pushToRepository method missing');
    }
    console.log('');

    // Test 4: Test getRepositoryStatus method
    console.log('4. Testing getRepositoryStatus method');
    if (typeof GitHubService.getRepositoryStatus === 'function') {
      console.log('✅ getRepositoryStatus method exists');
    } else {
      console.log('❌ getRepositoryStatus method missing');
    }
    console.log('');

    // Test 5: Test applyProposalAndPR method
    console.log('5. Testing applyProposalAndPR method');
    if (typeof GitHubService.applyProposalAndPR === 'function') {
      console.log('✅ applyProposalAndPR method exists');
    } else {
      console.log('❌ applyProposalAndPR method missing');
    }
    console.log('');

    // Test 6: Test pushAICodeUpdates method
    console.log('6. Testing pushAICodeUpdates method');
    if (typeof GitHubService.pushAICodeUpdates === 'function') {
      console.log('✅ pushAICodeUpdates method exists');
    } else {
      console.log('❌ pushAICodeUpdates method missing');
    }
    console.log('');

    // Test 7: Test mergeAILearningPR method
    console.log('7. Testing mergeAILearningPR method');
    if (typeof GitHubService.mergeAILearningPR === 'function') {
      console.log('✅ mergeAILearningPR method exists');
    } else {
      console.log('❌ mergeAILearningPR method missing');
    }
    console.log('');

    // Test 8: Test closePR method
    console.log('8. Testing closePR method');
    if (typeof GitHubService.closePR === 'function') {
      console.log('✅ closePR method exists');
    } else {
      console.log('❌ closePR method missing');
    }
    console.log('');

    console.log('🎉 All GitHub integration method tests completed successfully!');
    console.log('');
    console.log('📋 Summary of available methods:');
    Object.keys(GitHubService).forEach(method => {
      console.log(`  - ${method}`);
    });

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error('Stack trace:', error.stack);
  }
}

// Run the tests
testGitHubIntegration(); 