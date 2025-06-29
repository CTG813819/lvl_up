const mongoose = require('mongoose');

const aiQuotaSchema = new mongoose.Schema({
  aiType: {
    type: String,
    required: true,
    enum: ['Imperium', 'Sandbox', 'Guardian']
  },
  currentPhase: {
    type: String,
    enum: ['proposing', 'testing', 'learning'],
    default: 'proposing'
  },
  phaseQuotas: {
    proposing: { type: Number, default: 5 },
    testing: { type: Number, default: 3 },
    learning: { type: Number, default: 3 }
  },
  phaseProgress: {
    proposing: { type: Number, default: 0 },
    testing: { type: Number, default: 0 },
    learning: { type: Number, default: 0 }
  },
  cycleActive: { type: Boolean, default: false },
  lastActive: { type: Date, default: null },
  aiOrder: { type: Number, default: 0 }, // 0: Imperium, 1: Sandbox, 2: Guardian
  currentQuota: {
    type: Number,
    required: true,
    default: 50 // Start with 50 proposals
  },
  proposalsSent: {
    type: Number,
    required: true,
    default: 0
  },
  proposalsProcessed: {
    type: Number,
    required: true,
    default: 0 // Count of proposals that have been approved/rejected/tested
  },
  learningCycles: {
    type: Number,
    required: true,
    default: 0 // Number of times this AI has completed a learning cycle
  },
  lastLearningCycle: {
    type: Date,
    default: null
  },
  isLearning: {
    type: Boolean,
    default: false
  },
  learningStartTime: {
    type: Date,
    default: null
  },
  canSendProposals: {
    type: Boolean,
    default: true
  },
  quotaResetDate: {
    type: Date,
    default: Date.now
  },
  // Learning effectiveness metrics
  learningEffectiveness: {
    type: Number,
    min: 0,
    max: 100,
    default: 0
  },
  successRate: {
    type: Number,
    min: 0,
    max: 100,
    default: 0
  },
  // Quota progression history
  quotaHistory: [{
    cycle: Number,
    quota: Number,
    proposalsSent: Number,
    proposalsProcessed: Number,
    successRate: Number,
    learningEffectiveness: Number,
    completedAt: Date
  }]
}, {
  timestamps: true
});

// Indexes for efficient queries
aiQuotaSchema.index({ aiType: 1 });
aiQuotaSchema.index({ canSendProposals: 1, aiType: 1 });

// Method to check if AI can send more proposals
aiQuotaSchema.methods.canSendMoreProposals = function() {
  return this.canSendProposals && this.proposalsSent < this.currentQuota;
};

// Method to increment proposals sent
aiQuotaSchema.methods.incrementProposalsSent = function() {
  this.proposalsSent += 1;
  
  // Check if quota is reached
  if (this.proposalsSent >= this.currentQuota) {
    this.canSendProposals = false;
    this.isLearning = true;
    this.learningStartTime = new Date();
  }
  
  return this.save();
};

// Method to increment processed proposals
aiQuotaSchema.methods.incrementProcessedProposals = function() {
  this.proposalsProcessed += 1;
  
  // Check if all proposals in current quota have been processed
  if (this.proposalsProcessed >= this.currentQuota) {
    this.completeLearningCycle();
  }
  
  return this.save();
};

// Method to complete a learning cycle
aiQuotaSchema.methods.completeLearningCycle = function() {
  this.learningCycles += 1;
  this.isLearning = false;
  this.learningStartTime = null;
  this.lastLearningCycle = new Date();
  this.canSendProposals = true;
  
  // Reset counters for next cycle
  this.proposalsSent = 0;
  this.proposalsProcessed = 0;
  
  // Calculate new quota based on learning cycles
  if (this.learningCycles === 1) {
    this.currentQuota = 30; // Second cycle: 30 proposals
  } else if (this.learningCycles >= 2) {
    this.currentQuota = 20; // Third cycle and beyond: 20 proposals
  }
  
  // Store history
  this.quotaHistory.push({
    cycle: this.learningCycles,
    quota: this.currentQuota,
    proposalsSent: this.proposalsSent,
    proposalsProcessed: this.proposalsProcessed,
    successRate: this.successRate,
    learningEffectiveness: this.learningEffectiveness,
    completedAt: new Date()
  });
  
  return this.save();
};

// Method to update learning effectiveness
aiQuotaSchema.methods.updateLearningEffectiveness = function(effectiveness) {
  this.learningEffectiveness = effectiveness;
  return this.save();
};

// Method to update success rate
aiQuotaSchema.methods.updateSuccessRate = function(successRate) {
  this.successRate = successRate;
  return this.save();
};

// Method to reset quota and learning state
aiQuotaSchema.methods.resetQuota = function() {
  this.currentQuota = 50;
  this.proposalsSent = 0;
  this.proposalsProcessed = 0;
  this.learningCycles = 0;
  this.isLearning = false;
  this.learningStartTime = null;
  this.canSendProposals = true;
  this.quotaResetDate = new Date();
  this.learningEffectiveness = 0;
  this.successRate = 0;
  this.currentPhase = 'proposing';
  this.phaseProgress = {
    proposing: 0,
    testing: 0,
    learning: 0
  };
  this.cycleActive = false;
  this.lastActive = null;
  
  return this.save();
};

module.exports = mongoose.model('AIQuota', aiQuotaSchema); 