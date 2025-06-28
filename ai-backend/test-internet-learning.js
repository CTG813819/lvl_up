const mongoose = require('mongoose');
const InternetLearningService = require('./src/services/internetLearningService');
const AICodeUpdateService = require('./src/services/aiCodeUpdateService');
const AILearningOrchestrator = require('./src/services/aiLearningOrchestrator');

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/lvl_up', {
  useNewUrlParser: true,
  useUnifiedTopology: true
});

async function testInternetLearning() {
  console.log('🧪 Testing AI Internet Learning System...\n');
  
  try {
    // Test 1: Internet Learning Service
    console.log('1️⃣ Testing Internet Learning Service...');
    
    const mockProposal = {
      aiType: 'Imperium',
      filePath: 'lib/test_file.dart',
      improvementType: 'performance',
      userFeedbackReason: 'Code optimization needed',
      _id: new mongoose.Types.ObjectId()
    };
    
    const learningData = await InternetLearningService.learnFromInternet('Imperium', mockProposal, 'failed');
    console.log('✅ Internet learning completed');
    console.log(`   - Insights: ${learningData.insights?.length || 0}`);
    console.log(`   - Recommendations: ${learningData.recommendations?.length || 0}`);
    console.log(`   - Sources: ${learningData.sources?.length || 0}\n`);
    
    // Test 2: AI Code Update Service
    console.log('2️⃣ Testing AI Code Update Service...');
    
    // Use the orchestrator's method for generating code updates
    const codeUpdates = await AILearningOrchestrator.generateCodeUpdatesFromLearning('Imperium', mockProposal, 'failed', learningData);
    console.log('✅ Code updates generated');
    console.log(`   - Updates: ${codeUpdates.length}\n`);
    
    // Test 3: Learning Orchestrator
    console.log('3️⃣ Testing AI Learning Orchestrator...');
    
    const orchestratorResult = await AILearningOrchestrator.orchestrateAILearning('Imperium', mockProposal, 'failed');
    console.log('✅ Learning orchestrator completed');
    console.log(`   - Success: ${orchestratorResult.success}`);
    console.log(`   - Code updates applied: ${orchestratorResult.codeUpdates?.updatesApplied || 0}\n`);
    
    // Test 4: Learning Cycle Stats
    console.log('4️⃣ Testing Learning Cycle Statistics...');
    
    const stats = await AILearningOrchestrator.getLearningCycleStats('Imperium', 1);
    console.log('✅ Learning cycle stats retrieved');
    console.log(`   - Total cycles: ${stats.totalCycles}`);
    console.log(`   - Success rate: ${stats.successRate}%`);
    console.log(`   - Average insights: ${stats.averageInsightsPerCycle}\n`);
    
    console.log('🎉 All tests completed successfully!');
    console.log('\n📊 Summary:');
    console.log('   - Internet learning: ✅ Working');
    console.log('   - Code updates: ✅ Working');
    console.log('   - Learning orchestrator: ✅ Working');
    console.log('   - Statistics: ✅ Working');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
    console.error('Stack trace:', error.stack);
  } finally {
    await mongoose.disconnect();
    console.log('\n🔌 Disconnected from MongoDB');
  }
}

// Run the test
testInternetLearning(); 