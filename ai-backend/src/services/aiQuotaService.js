const AIQuota = require('../models/aiQuota');
const Proposal = require('../models/proposal');
const { logEvent } = require('../state');

const AI_ORDER = ['Imperium', 'Sandbox', 'Guardian'];

// Import Chaos/Warp state (we'll need to access this from the routes)
let chaosMode = false;
let warpMode = false;

// Function to update Chaos/Warp state (called from routes)
function updateChaosWarpState(chaos, warp) {
  chaosMode = chaos;
  warpMode = warp;
  logEvent(`[QUOTA] Chaos mode: ${chaos}, Warp mode: ${warp}`);
}

class AIQuotaService {
  /**
   * Check if current time is within operating hours (5 AM to 9 PM)
   */
  static isWithinOperatingHours() {
    // If Chaos mode is active, ignore time restrictions
    if (chaosMode) {
      return true;
    }
    
    const now = new Date();
    const hour = now.getHours();
    return hour >= 5 && hour < 21; // 5 AM to 9 PM (21:00)
  }

  /**
   * Check if AI operations are allowed (considering Chaos/Warp modes)
   */
  static isAIOperationsAllowed() {
    // Warp mode completely stops all AI operations
    if (warpMode) {
      return false;
    }
    
    // Chaos mode allows operations regardless of time
    if (chaosMode) {
      return true;
    }
    
    // Normal operating hours check
    return this.isWithinOperatingHours();
  }

  /**
   * Get time until next operating period
   */
  static getTimeUntilOperating() {
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(5, 0, 0, 0); // 5 AM tomorrow
    
    const today5AM = new Date(now);
    today5AM.setHours(5, 0, 0, 0); // 5 AM today
    
    if (now.getHours() < 5) {
      return today5AM - now; // Time until 5 AM today
    } else {
      return tomorrow - now; // Time until 5 AM tomorrow
    }
  }

  /**
   * Initialize quota for an AI if it doesn't exist
   */
  static async initializeQuota(aiType) {
    try {
      let quota = await AIQuota.findOne({ aiType });
      
      if (!quota) {
        quota = new AIQuota({
          aiType,
          currentQuota: 50,
          proposalsSent: 0,
          proposalsProcessed: 0,
          learningCycles: 0,
          canSendProposals: true
        });
        await quota.save();
        logEvent(`[QUOTA] Initialized quota for ${aiType}: 50 proposals`);
      }
      
      return quota;
    } catch (error) {
      console.error(`[QUOTA] Error initializing quota for ${aiType}:`, error);
      throw error;
    }
  }

  /**
   * Check if an AI can send more proposals
   */
  static async canSendProposals(aiType) {
    try {
      const quota = await this.initializeQuota(aiType);
      return quota.canSendMoreProposals();
    } catch (error) {
      console.error(`[QUOTA] Error checking if ${aiType} can send proposals:`, error);
      return false;
    }
  }

  /**
   * Increment proposals sent count and check if quota is reached
   */
  static async incrementProposalsSent(aiType) {
    try {
      const quota = await this.initializeQuota(aiType);
      await quota.incrementProposalsSent();
      
      logEvent(`[QUOTA] ${aiType} sent proposal ${quota.proposalsSent}/${quota.currentQuota}`);
      
      // If quota is reached, trigger learning state
      if (!quota.canSendProposals) {
        logEvent(`[QUOTA] ${aiType} quota reached (${quota.currentQuota}). Entering learning mode.`);
        const { aiStatus } = require('../state');
        aiStatus[aiType] = { ...aiStatus[aiType], isLearning: true };
      }
      
      return quota;
    } catch (error) {
      console.error(`[QUOTA] Error incrementing proposals sent for ${aiType}:`, error);
      throw error;
    }
  }

  /**
   * Increment processed proposals count and check if learning cycle is complete
   */
  static async incrementProcessedProposals(aiType) {
    try {
      const quota = await this.initializeQuota(aiType);
      await quota.incrementProcessedProposals();
      
      logEvent(`[QUOTA] ${aiType} processed proposal ${quota.proposalsProcessed}/${quota.currentQuota}`);
      
      // If all proposals in current quota are processed, complete learning cycle
      if (quota.proposalsProcessed >= quota.currentQuota) {
        await this.completeLearningCycle(aiType);
      }
      
      return quota;
    } catch (error) {
      console.error(`[QUOTA] Error incrementing processed proposals for ${aiType}:`, error);
      throw error;
    }
  }

  /**
   * Complete a learning cycle and calculate new quota
   */
  static async completeLearningCycle(aiType) {
    try {
      const quota = await this.initializeQuota(aiType);
      
      // Calculate success rate from recent proposals
      const recentProposals = await Proposal.find({
        aiType,
        createdAt: { $gte: quota.quotaResetDate }
      }).sort({ createdAt: -1 }).limit(quota.currentQuota);
      
      const approvedCount = recentProposals.filter(p => p.status === 'approved').length;
      const successRate = recentProposals.length > 0 ? (approvedCount / recentProposals.length) * 100 : 0;
      
      // Calculate learning effectiveness based on improvement over time
      const learningEffectiveness = await this.calculateLearningEffectiveness(aiType, quota);
      
      // Update quota with metrics
      quota.successRate = successRate;
      quota.learningEffectiveness = learningEffectiveness;
      
      // Complete the cycle
      await quota.completeLearningCycle();
      
      // Update global state
      const { aiStatus } = require('../state');
      aiStatus[aiType] = { ...aiStatus[aiType], isLearning: false };
      
      logEvent(`[QUOTA] ${aiType} completed learning cycle ${quota.learningCycles}. New quota: ${quota.currentQuota}. Success rate: ${successRate.toFixed(1)}%. Learning effectiveness: ${learningEffectiveness.toFixed(1)}%`);
      
      return quota;
    } catch (error) {
      console.error(`[QUOTA] Error completing learning cycle for ${aiType}:`, error);
      throw error;
    }
  }

  /**
   * Calculate learning effectiveness based on improvement over time
   */
  static async calculateLearningEffectiveness(aiType, quota) {
    try {
      if (quota.learningCycles === 0) {
        return 0; // First cycle, no baseline to compare against
      }
      
      // Get proposals from current cycle
      const currentCycleProposals = await Proposal.find({
        aiType,
        createdAt: { $gte: quota.quotaResetDate }
      });
      
      // Get proposals from previous cycle for comparison
      const previousCycleStart = new Date(quota.quotaResetDate);
      previousCycleStart.setDate(previousCycleStart.getDate() - 30); // Approximate previous cycle
      
      const previousCycleProposals = await Proposal.find({
        aiType,
        createdAt: { $gte: previousCycleStart, $lt: quota.quotaResetDate }
      });
      
      // Calculate success rates
      const currentSuccessRate = currentCycleProposals.length > 0 
        ? (currentCycleProposals.filter(p => p.status === 'approved').length / currentCycleProposals.length) * 100 
        : 0;
      
      const previousSuccessRate = previousCycleProposals.length > 0 
        ? (previousCycleProposals.filter(p => p.status === 'approved').length / previousCycleProposals.length) * 100 
        : 0;
      
      // Calculate improvement
      const improvement = Math.max(0, currentSuccessRate - previousSuccessRate);
      
      // Normalize to 0-100 scale
      const effectiveness = Math.min(100, improvement * 2); // 50% improvement = 100% effectiveness
      
      return effectiveness;
    } catch (error) {
      console.error(`[QUOTA] Error calculating learning effectiveness for ${aiType}:`, error);
      return 0;
    }
  }

  /**
   * Get quota status for an AI
   */
  static async getQuotaStatus(aiType) {
    try {
      const quota = await this.initializeQuota(aiType);
      
      return {
        aiType: quota.aiType,
        currentQuota: quota.currentQuota,
        proposalsSent: quota.proposalsSent,
        proposalsProcessed: quota.proposalsProcessed,
        remainingProposals: quota.currentQuota - quota.proposalsSent,
        learningCycles: quota.learningCycles,
        isLearning: quota.isLearning,
        canSendProposals: quota.canSendProposals,
        successRate: quota.successRate,
        learningEffectiveness: quota.learningEffectiveness,
        lastLearningCycle: quota.lastLearningCycle,
        quotaHistory: quota.quotaHistory.slice(-5) // Last 5 cycles
      };
    } catch (error) {
      console.error(`[QUOTA] Error getting quota status for ${aiType}:`, error);
      throw error;
    }
  }

  /**
   * Get quota status for all AIs
   */
  static async getAllQuotaStatus() {
    const quotas = await AIQuota.find({});
    const status = {};
    const isOperating = this.isWithinOperatingHours();
    const timeUntilOperating = this.getTimeUntilOperating();
    
    for (const quota of quotas) {
      status[quota.aiType] = {
        aiType: quota.aiType,
        currentPhase: quota.currentPhase,
        phaseQuotas: quota.phaseQuotas,
        phaseProgress: quota.phaseProgress,
        cycleActive: quota.cycleActive,
        lastActive: quota.lastActive,
        aiOrder: quota.aiOrder,
        isOperating: isOperating,
        timeUntilOperating: timeUntilOperating
      };
    }
    
    // Add global status
    status.global = {
      isOperating: isOperating,
      timeUntilOperating: timeUntilOperating,
      currentTime: new Date().toISOString(),
      operatingHours: "5:00 AM - 9:00 PM"
    };
    
    return status;
  }

  /**
   * Reset quota for an AI (for testing/debugging)
   */
  static async resetQuota(aiType) {
    try {
      await AIQuota.findOneAndUpdate(
        { aiType },
        {
          currentQuota: 50,
          proposalsSent: 0,
          proposalsProcessed: 0,
          learningCycles: 0,
          isLearning: false,
          canSendProposals: true,
          successRate: 0,
          learningEffectiveness: 0,
          quotaResetDate: new Date()
        },
        { upsert: true }
      );
      
      logEvent(`[QUOTA] Reset quota for ${aiType}`);
    } catch (error) {
      console.error(`[QUOTA] Error resetting quota for ${aiType}:`, error);
      throw error;
    }
  }

  static async initializeAllQuotas() {
    for (let i = 0; i < AI_ORDER.length; i++) {
      await AIQuota.findOneAndUpdate(
        { aiType: AI_ORDER[i] },
        { aiOrder: i },
        { upsert: true }
      );
    }
  }

  static async getCurrentAI() {
    // Check if AI operations are allowed
    if (!this.isAIOperationsAllowed()) {
      if (warpMode) {
        logEvent('[QUOTA] Warp mode active. AI operations completely stopped.');
      } else {
        logEvent('[QUOTA] Outside operating hours (5 AM - 9 PM). AI operations paused.');
      }
      return null;
    }

    const all = await AIQuota.find({}).sort({ aiOrder: 1 });
    let current = all.find(q => q.cycleActive);
    if (!current) {
      // Start with the first AI
      current = all[0];
      current.cycleActive = true;
      current.lastActive = new Date();
      await current.save();
    }
    return current;
  }

  static async rotateToNextAI() {
    // Check if AI operations are allowed
    if (!this.isAIOperationsAllowed()) {
      if (warpMode) {
        logEvent('[QUOTA] Warp mode active. AI rotation stopped.');
      } else {
        logEvent('[QUOTA] Outside operating hours. AI rotation paused.');
      }
      return null;
    }

    const all = await AIQuota.find({}).sort({ aiOrder: 1 });
    let currentIdx = all.findIndex(q => q.cycleActive);
    if (currentIdx === -1) currentIdx = 0;
    all[currentIdx].cycleActive = false;
    await all[currentIdx].save();
    const nextIdx = (currentIdx + 1) % all.length;
    all[nextIdx].cycleActive = true;
    all[nextIdx].lastActive = new Date();
    all[nextIdx].currentPhase = 'proposing';
    all[nextIdx].phaseProgress = { proposing: 0, testing: 0, learning: 0 };
    await all[nextIdx].save();
    
    logEvent(`[QUOTA] Rotated to ${all[nextIdx].aiType} for ${all[nextIdx].currentPhase} phase`);
    return all[nextIdx];
  }

  static async canProcess(aiType, phase) {
    // Check if AI operations are allowed (considering Chaos/Warp modes)
    if (!this.isAIOperationsAllowed()) {
      if (warpMode) {
        logEvent(`[QUOTA] ${aiType} cannot process ${phase} - Warp mode active (all operations stopped)`);
      } else {
        logEvent(`[QUOTA] ${aiType} cannot process ${phase} - outside operating hours (5 AM - 9 PM)`);
      }
      return false;
    }

    const quota = await AIQuota.findOne({ aiType });
    if (!quota) {
      logEvent(`[QUOTA] No quota found for ${aiType}`);
      return false;
    }
    if (!quota.cycleActive) {
      logEvent(`[QUOTA] ${aiType} cannot process ${phase} - not active AI`);
      return false;
    }
    if (quota.currentPhase !== phase) {
      logEvent(`[QUOTA] ${aiType} cannot process ${phase} - current phase is ${quota.currentPhase}`);
      return false;
    }
    if (quota.phaseProgress[phase] >= quota.phaseQuotas[phase]) {
      logEvent(`[QUOTA] ${aiType} cannot process ${phase} - quota met (${quota.phaseProgress[phase]}/${quota.phaseQuotas[phase]})`);
      return false;
    }
    return true;
  }

  static async incrementPhaseProgress(aiType, phase) {
    const quota = await AIQuota.findOne({ aiType });
    quota.phaseProgress[phase] += 1;
    
    logEvent(`[QUOTA] ${aiType} ${phase} progress: ${quota.phaseProgress[phase]}/${quota.phaseQuotas[phase]}`);
    
    // If phase quota met, rotate to next phase
    if (quota.phaseProgress[phase] >= quota.phaseQuotas[phase]) {
      if (phase === 'proposing') {
        quota.currentPhase = 'testing';
        logEvent(`[QUOTA] ${aiType} completed proposing phase, moving to testing`);
      } else if (phase === 'testing') {
        quota.currentPhase = 'learning';
        logEvent(`[QUOTA] ${aiType} completed testing phase, moving to learning`);
      } else if (phase === 'learning') {
        quota.currentPhase = 'proposing';
        quota.phaseProgress = { proposing: 0, testing: 0, learning: 0 };
        quota.cycleActive = false;
        await quota.save();
        logEvent(`[QUOTA] ${aiType} completed full cycle, rotating to next AI`);
        await AIQuotaService.rotateToNextAI();
        return;
      }
    }
    await quota.save();
  }

  /**
   * Get current operating status
   */
  static getOperatingStatus() {
    const isOperating = this.isWithinOperatingHours();
    const timeUntilOperating = this.getTimeUntilOperating();
    const now = new Date();
    
    return {
      isOperating: isOperating,
      currentTime: now.toISOString(),
      operatingHours: "5:00 AM - 9:00 PM",
      timeUntilOperating: timeUntilOperating,
      timeUntilOperatingFormatted: this.formatTimeUntilOperating(timeUntilOperating)
    };
  }

  /**
   * Format time until operating in human-readable format
   */
  static formatTimeUntilOperating(milliseconds) {
    const hours = Math.floor(milliseconds / (1000 * 60 * 60));
    const minutes = Math.floor((milliseconds % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  }
}

module.exports = { AIQuotaService, updateChaosWarpState }; 