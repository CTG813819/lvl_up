const mongoose = require('mongoose');

const learningSchema = new mongoose.Schema({
  aiType: {
    type: String,
    required: true,
    enum: ['Imperium', 'Sandbox', 'Guardian']
  },
  proposalId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Proposal',
    required: false
  },
  status: {
    type: String,
    required: true,
    enum: ['approved', 'rejected', 'test-failed', 'test-passed', 'learning-triggered', 'learning-completed', 'learning-failed', 'submitted-for-approval']
  },
  feedbackReason: {
    type: String,
    required: true
  },
  learningKey: {
    type: String,
    required: true
  },
  learningValue: {
    type: String,
    required: true
  },
  timestamp: {
    type: Date,
    default: Date.now
  },
  filePath: {
    type: String,
    required: true
  },
  improvementType: {
    type: String,
    enum: ['readability', 'performance', 'bug-fix', 'refactor', 'feature', 'security', 'system']
  }
}, {
  timestamps: true
});

// Index for efficient queries
learningSchema.index({ aiType: 1, timestamp: -1 });
learningSchema.index({ learningKey: 1, aiType: 1 });

module.exports = mongoose.model('Learning', learningSchema); 