const mongoose = require('mongoose');

const proposalSchema = new mongoose.Schema({
  aiType: { type: String, required: true }, // 'Imperium', 'Guardian', 'Sandbox'
  filePath: { type: String, required: true },
  codeBefore: { type: String, required: true },
  codeAfter: { type: String, required: true },
  status: { type: String, enum: ['pending', 'approved', 'rejected', 'applied', 'test-passed', 'test-failed'], default: 'pending' },
  result: { type: String },
  createdAt: { type: Date, default: Date.now },
  userFeedback: { type: String, enum: ['approved', 'rejected', null], default: null },
  testStatus: { type: String, enum: ['not-run', 'passed', 'failed'], default: 'not-run' },
  testOutput: { type: String },
  
  // Advanced deduplication fields
  codeHash: { type: String }, // Hash of codeBefore + codeAfter for quick duplicate detection
  semanticHash: { type: String }, // Semantic similarity hash
  diffScore: { type: Number }, // Similarity score with existing proposals
  duplicateOf: { type: mongoose.Schema.Types.ObjectId, ref: 'Proposal' }, // Reference to original if duplicate
  
  // AI Learning fields
  aiReasoning: { type: String }, // Why the AI made this suggestion
  learningContext: { type: String }, // Context from previous feedback
  mistakePattern: { type: String }, // Pattern of mistakes to avoid
  improvementType: { type: String, enum: ['performance', 'readability', 'security', 'bug-fix', 'refactor', 'feature', 'system'] },
  confidence: { type: Number, min: 0, max: 1, default: 0.5 }, // AI confidence in this proposal
  
  // Feedback and learning
  userFeedbackReason: { type: String }, // Why user approved/rejected
  aiLearningApplied: { type: Boolean, default: false }, // Whether learning was applied
  previousMistakesAvoided: { type: [String] }, // List of previous mistakes this proposal avoids
});

// Index for efficient duplicate detection
proposalSchema.index({ codeHash: 1, aiType: 1 });
proposalSchema.index({ semanticHash: 1, aiType: 1 });
proposalSchema.index({ filePath: 1, aiType: 1, createdAt: -1 });

module.exports = mongoose.model('Proposal', proposalSchema);