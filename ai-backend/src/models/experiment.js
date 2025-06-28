const mongoose = require('mongoose');

const experimentSchema = new mongoose.Schema({
  aiName: { type: String, required: true },
  experimentType: { type: String, required: true },
  input: { type: mongoose.Schema.Types.Mixed, required: true },
  result: { type: mongoose.Schema.Types.Mixed, required: true },
  createdAt: { type: Date, default: Date.now },
  
  // AI Learning fields
  learningApplied: { type: Boolean, default: false },
  mistakePatterns: { type: [String] }, // Patterns of mistakes to avoid
  successPatterns: { type: [String] }, // Patterns that led to success
  userFeedback: { type: String, enum: ['positive', 'negative', 'neutral', null], default: null },
  feedbackReason: { type: String },
  
  // Performance tracking
  executionTime: { type: Number }, // Time taken in milliseconds
  tokensUsed: { type: Number }, // OpenAI tokens consumed
  cost: { type: Number }, // Estimated cost in USD
});

module.exports = mongoose.model('Experiment', experimentSchema);