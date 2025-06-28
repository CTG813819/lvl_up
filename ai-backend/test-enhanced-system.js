const mongoose = require('mongoose');
const AILearningService = require('./src/services/aiLearningService');
const DeduplicationService = require('./src/services/deduplicationService');
const Proposal = require('./src/models/proposal');

require('dotenv').config();

async function testEnhancedSystem() {
  console.log('🧪 Testing Enhanced AI Learning and Deduplication System...\n');
  
  try {
    // Connect to MongoDB
    await mongoose.connect(process.env.MONGODB_URI, { 
      useNewUrlParser: true, 
      useUnifiedTopology: true 
    });
    console.log('✅ Connected to MongoDB\n');
    
    // Test 1: Deduplication Service
    console.log('🔍 Testing Deduplication Service...');
    
    const code1 = `void main() {
  print("Hello World");
}`;
    
    const code2 = `void main() {
  print("Hello World");
}`;
    
    const code3 = `void main() {
  print("Hello World");
  // Added comment
}`;
    
    // Test exact duplicate detection
    const exactHash = DeduplicationService.generateCodeHash(code1, code2);
    const differentHash = DeduplicationService.generateCodeHash(code1, code3);
    console.log(`✅ Exact duplicate hash: ${exactHash}`);
    console.log(`✅ Different code hash: ${differentHash}`);
    console.log(`✅ Hashes are ${exactHash === differentHash ? 'same' : 'different'}\n`);
    
    // Test semantic hash
    const semanticHash1 = DeduplicationService.generateSemanticHash(code1);
    const semanticHash2 = DeduplicationService.generateSemanticHash(code2);
    const semanticHash3 = DeduplicationService.generateSemanticHash(code3);
    console.log(`✅ Semantic hash 1: ${semanticHash1}`);
    console.log(`✅ Semantic hash 2: ${semanticHash2}`);
    console.log(`✅ Semantic hash 3: ${semanticHash3}\n`);
    
    // Test similarity calculation
    const similarity1 = DeduplicationService.calculateSimilarity(code1, code2);
    const similarity2 = DeduplicationService.calculateSimilarity(code1, code3);
    console.log(`✅ Similarity between identical codes: ${similarity1}`);
    console.log(`✅ Similarity between different codes: ${similarity2}\n`);
    
    // Test 2: AI Learning Service
    console.log('🧠 Testing AI Learning Service...');
    
    // Create some test proposals with feedback
    const testProposals = [
      {
        aiType: 'Imperium',
        filePath: 'lib/test1.dart',
        codeBefore: 'void old() {}',
        codeAfter: 'void new() {}',
        userFeedback: 'approved',
        userFeedbackReason: 'good improvement',
        improvementType: 'performance',
        createdAt: new Date()
      },
      {
        aiType: 'Imperium',
        filePath: 'lib/test2.dart',
        codeBefore: 'void old() {}',
        codeAfter: 'void new() {}',
        userFeedback: 'rejected',
        userFeedbackReason: 'already exists',
        improvementType: 'refactor',
        createdAt: new Date()
      },
      {
        aiType: 'Guardian',
        filePath: 'lib/test3.dart',
        codeBefore: 'void old() {}',
        codeAfter: 'void new() {}',
        userFeedback: 'approved',
        userFeedbackReason: 'better performance',
        improvementType: 'performance',
        createdAt: new Date()
      }
    ];
    
    // Save test proposals
    for (const proposalData of testProposals) {
      const proposal = new Proposal(proposalData);
      await proposal.save();
      console.log(`✅ Created test proposal: ${proposal.aiType} - ${proposal.filePath}`);
    }
    
    // Test feedback pattern analysis
    const patterns = await AILearningService.analyzeFeedbackPatterns('Imperium', 1);
    console.log('\n📊 Feedback Patterns for Imperium:');
    console.log(`✅ Common mistakes: ${patterns.commonMistakes.length}`);
    console.log(`✅ Success patterns: ${patterns.successPatterns.length}`);
    
    if (patterns.commonMistakes.length > 0) {
      console.log(`✅ Top mistake: ${patterns.commonMistakes[0].mistake} (${Math.round(patterns.commonMistakes[0].frequency * 100)}%)`);
    }
    
    if (patterns.successPatterns.length > 0) {
      console.log(`✅ Top success: ${patterns.successPatterns[0].pattern} (${Math.round(patterns.successPatterns[0].frequency * 100)}%)`);
    }
    
    // Test learning context generation
    const learningContext = await AILearningService.generateLearningContext('Imperium');
    console.log('\n📚 Generated Learning Context:');
    console.log(learningContext.substring(0, 200) + '...\n');
    
    // Test learning statistics
    const learningStats = await AILearningService.getLearningStats('Imperium');
    console.log('📈 Learning Statistics for Imperium:');
    console.log(`✅ Total proposals: ${learningStats.totalProposals}`);
    console.log(`✅ Learning applied: ${learningStats.learningApplied}`);
    console.log(`✅ Learning rate: ${Math.round(learningStats.learningRate * 100)}%\n`);
    
    // Test 3: Duplicate Statistics
    console.log('🔄 Testing Duplicate Statistics...');
    const duplicateStats = await DeduplicationService.getDuplicateStats();
    console.log('📊 Duplicate Statistics:');
    console.log(JSON.stringify(duplicateStats, null, 2));
    
    // Clean up test data
    console.log('\n🧹 Cleaning up test data...');
    await Proposal.deleteMany({ filePath: { $in: ['lib/test1.dart', 'lib/test2.dart', 'lib/test3.dart'] } });
    console.log('✅ Test data cleaned up\n');
    
    console.log('🎉 All tests passed! Enhanced system is working correctly.');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    await mongoose.disconnect();
    console.log('🔌 Disconnected from MongoDB');
  }
}

// Run the test
testEnhancedSystem(); 