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

// Operational hours configuration
const OPERATIONAL_START_HOUR = 5; // 5 AM
const OPERATIONAL_END_HOUR = 21; // 9 PM

class AIQuotaService {
  /**
   * Check if current time is within operating hours (5 AM to 9 PM)
   */
  static isWithinOperatingHours() {
    const now = new Date();
    const hour = now.getHours();
    return hour >= OPERATIONAL_START_HOUR && hour < OPERATIONAL_END_HOUR;
  }

  /**
   * Check if AI operations are allowed (considering Chaos/Warp modes with hierarchy)
   * Hierarchy: Warp > Chaos > Operational Hours
   */
  static isAIOperationsAllowed() {
    // Warp mode completely stops all AI operations (highest priority)
    if (warpMode) {
      logEvent(`[QUOTA] AI operations blocked by Warp mode (Warp > Chaos > Operational Hours)`);
      return false;
    }
    
    // Chaos mode allows operations regardless of operational hours (overrides operational hours)
    if (chaosMode) {
      logEvent(`[QUOTA] AI operations allowed by Chaos mode (overrides operational hours)`);
      return true;
    }
    
    // Normal operating hours check (lowest priority)
    const withinHours = this.isWithinOperatingHours();
    if (withinHours) {
      logEvent(`[QUOTA] AI operations allowed during operational hours`);
    } else {
      logEvent(`[QUOTA] AI operations paused outside operational hours`);
    }
    return withinHours;
  }

  /**
   * Get AI operation status with detailed information
   */
  static getAIOperationStatus() {
    // Warp mode completely stops all AI operations (highest priority)
    if (warpMode) {
      return {
        canOperate: false,
        reason: 'WARP_MODE_ACTIVE',
        message: 'All AI operations stopped by Warp mode',
        hierarchy: 'WARP > CHAOS > OPERATIONAL_HOURS',
        priority: 1,
        details: {
          warpMode: true,
          chaosMode: false,
          operationalHours: this.isWithinOperatingHours()
        }
      };
    }
    
    // Chaos mode allows operations regardless of operational hours (overrides operational hours)
    if (chaosMode) {
      return {
        canOperate: true,
        reason: 'CHAOS_MODE_ACTIVE',
        message: 'AI operations allowed by Chaos mode (overrides operational hours)',
        hierarchy: 'CHAOS > OPERATIONAL_HOURS',
        priority: 2,
        details: {
          warpMode: false,
          chaosMode: true,
          operationalHours: this.isWithinOperatingHours()
        }
      };
    }
    
    // Normal operational hours check (lowest priority)
    const withinHours = this.isWithinOperatingHours();
    return {
      canOperate: withinHours,
      reason: withinHours ? 'OPERATIONAL_HOURS' : 'OUTSIDE_OPERATIONAL_HOURS',
      message: withinHours ? 'AI operations allowed during operational hours' : 'AI operations paused outside operational hours',
      hierarchy: 'OPERATIONAL_HOURS',
      priority: 3,
      details: {
        warpMode: false,
        chaosMode: false,
        operationalHours: withinHours
      }
    };
  }

  /**
   * Get current hierarchy status
   */
  static getCurrentHierarchyStatus() {
    if (warpMode) {
      return 'WARP (AI stopped)';
    } else if (chaosMode) {
      return 'CHAOS (AI allowed - overrides operational hours)';
    } else if (this.isWithinOperatingHours()) {
      return 'OPERATIONAL HOURS (AI allowed)';
    } else {
      return 'OUTSIDE HOURS (AI stopped)';
    }
  }

  /**
   * Get time until next operating period
   */
  static getTimeUntilOperating() {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const today5AM = new Date(today);
    today5AM.setHours(OPERATIONAL_START_HOUR, 0, 0, 0); // 5 AM today
    
    const tomorrow5AM = new Date(tomorrow);
    tomorrow5AM.setHours(OPERATIONAL_START_HOUR, 0, 0, 0); // 5 AM tomorrow
    
    if (now.getHours() < OPERATIONAL_START_HOUR) {
      return today5AM.getTime() - now.getTime();
    } else {
      return tomorrow5AM.getTime() - now.getTime();
    }
  }

  /**
   * Format time until operating as string
   */
  static formatTimeUntilOperating(milliseconds) {
    if (!milliseconds || milliseconds <= 0) return 'Now';
    
    const hours = Math.floor(milliseconds / (1000 * 60 * 60));
    const minutes = Math.floor((milliseconds % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  }

  /**
   * Get operational hours as formatted string
   */
  static getOperationalHoursFormatted() {
    return `${OPERATIONAL_START_HOUR.toString().padStart(2, '0')}:00 - ${OPERATIONAL_END_HOUR.toString().padStart(2, '0')}:00`;
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
      // First check if AI operations are allowed
      if (!this.isAIOperationsAllowed()) {
        logEvent(`[QUOTA] ${aiType} cannot send proposals - AI operations not allowed`);
        return false;
      }
      
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
      // Check if AI operations are allowed before incrementing
      if (!this.isAIOperationsAllowed()) {
        logEvent(`[QUOTA] Cannot increment proposals for ${aiType} - AI operations not allowed`);
        return null;
      }
      
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
        return 0; // No baseline for first cycle
      }
      
      // Get proposals from previous cycle for comparison
      const previousCycleDate = new Date(quota.quotaResetDate);
      previousCycleDate.setDate(previousCycleDate.getDate() - 7); // Rough estimate of previous cycle
      
      const previousProposals = await Proposal.find({
        aiType,
        createdAt: { $gte: previousCycleDate, $lt: quota.quotaResetDate }
      }).sort({ createdAt: -1 }).limit(quota.currentQuota);
      
      if (previousProposals.length === 0) {
        return 0; // No previous data
      }
      
      const previousApprovedCount = previousProposals.filter(p => p.status === 'approved').length;
      const previousSuccessRate = (previousApprovedCount / previousProposals.length) * 100;
      
      // Calculate improvement
      const currentSuccessRate = quota.successRate || 0;
      const improvement = currentSuccessRate - previousSuccessRate;
      
      // Normalize to 0-100 scale
      const effectiveness = Math.max(0, Math.min(100, 50 + improvement));
      
      return effectiveness;
    } catch (error) {
      console.error(`[QUOTA] Error calculating learning effectiveness for ${aiType}:`, error);
      return 0;
    }
  }

  /**
   * Get quota status for a specific AI
   */
  static async getQuotaStatus(aiType) {
    try {
      const quota = await this.initializeQuota(aiType);
      const operationStatus = this.getAIOperationStatus();
      
      return {
        aiType: quota.aiType,
        currentQuota: quota.currentQuota,
        proposalsSent: quota.proposalsSent,
        proposalsProcessed: quota.proposalsProcessed,
        canSendProposals: quota.canSendMoreProposals() && operationStatus.canOperate,
        learningCycles: quota.learningCycles,
        successRate: quota.successRate,
        learningEffectiveness: quota.learningEffectiveness,
        operationStatus: operationStatus,
        operationalHours: this.getOperationalHoursFormatted(),
        timeUntilOperating: this.formatTimeUntilOperating(this.getTimeUntilOperating())
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
    const operationStatus = this.getAIOperationStatus();
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
        operationStatus: operationStatus,
        operationalHours: this.getOperationalHoursFormatted(),
        timeUntilOperating: this.formatTimeUntilOperating(timeUntilOperating)
      };
    }
    
    // Add global status
    status.global = {
      operationStatus: operationStatus,
      timeUntilOperating: this.formatTimeUntilOperating(timeUntilOperating),
      currentTime: new Date().toISOString(),
      operationalHours: this.getOperationalHoursFormatted(),
      chaosMode: chaosMode,
      warpMode: warpMode
    };
    
    return status;
  }

  /**
   * Reset quota for an AI
   */
  static async resetQuota(aiType) {
    try {
      const quota = await this.initializeQuota(aiType);
      await quota.resetQuota();
      
      logEvent(`[QUOTA] Reset quota for ${aiType}`);
      
      return quota;
    } catch (error) {
      console.error(`[QUOTA] Error resetting quota for ${aiType}:`, error);
      throw error;
    }
  }

  /**
   * Initialize quotas for all AIs
   */
  static async initializeAllQuotas() {
    try {
      for (const aiType of AI_ORDER) {
        await this.initializeQuota(aiType);
      }
      logEvent(`[QUOTA] Initialized quotas for all AIs`);
    } catch (error) {
      console.error(`[QUOTA] Error initializing all quotas:`, error);
      throw error;
    }
  }

  /**
   * Get current AI based on rotation
   */
  static async getCurrentAI() {
    try {
      const quotas = await AIQuota.find({}).sort({ lastActive: 1 });
      
      if (quotas.length === 0) {
        await this.initializeAllQuotas();
        return AI_ORDER[0];
      }
      
      // Find the AI that hasn't been active the longest
      const oldestActive = quotas[0];
      return oldestActive.aiType;
    } catch (error) {
      console.error(`[QUOTA] Error getting current AI:`, error);
      return AI_ORDER[0]; // Fallback to first AI
    }
  }

  /**
   * Rotate to next AI in the order
   */
  static async rotateToNextAI() {
    try {
      const currentAI = await this.getCurrentAI();
      const currentIndex = AI_ORDER.indexOf(currentAI);
      const nextIndex = (currentIndex + 1) % AI_ORDER.length;
      const nextAI = AI_ORDER[nextIndex];
      
      // Update last active time for current AI
      const quota = await this.initializeQuota(currentAI);
      quota.lastActive = new Date();
      await quota.save();
      
      logEvent(`[QUOTA] Rotated from ${currentAI} to ${nextAI}`);
      
      return nextAI;
    } catch (error) {
      console.error(`[QUOTA] Error rotating to next AI:`, error);
      return AI_ORDER[0]; // Fallback to first AI
    }
  }

  /**
   * Check if an AI can process in a specific phase
   */
  static async canProcess(aiType, phase) {
    try {
      // Check if AI operations are allowed
      if (!this.isAIOperationsAllowed()) {
        return false;
      }
      
      const quota = await this.initializeQuota(aiType);
      return quota.canProcessPhase(phase);
    } catch (error) {
      console.error(`[QUOTA] Error checking if ${aiType} can process phase ${phase}:`, error);
      return false;
    }
  }

  /**
   * Increment phase progress for an AI
   */
  static async incrementPhaseProgress(aiType, phase) {
    try {
      const quota = await this.initializeQuota(aiType);
      await quota.incrementPhaseProgress(phase);
      
      logEvent(`[QUOTA] ${aiType} phase ${phase} progress: ${quota.phaseProgress[phase]}/${quota.phaseQuotas[phase]}`);
      
      return quota;
    } catch (error) {
      console.error(`[QUOTA] Error incrementing phase progress for ${aiType} phase ${phase}:`, error);
      throw error;
    }
  }

  /**
   * Get current operating status
   */
  static getOperatingStatus() {
    const operationStatus = this.getAIOperationStatus();
    const timeUntilOperating = this.getTimeUntilOperating();
    const now = new Date();
    
    return {
      operationStatus: operationStatus,
      currentTime: now.toISOString(),
      operationalHours: this.getOperationalHoursFormatted(),
      timeUntilOperating: this.formatTimeUntilOperating(timeUntilOperating),
      chaosMode: chaosMode,
      warpMode: warpMode
    };
  }
}

module.exports = { AIQuotaService, updateChaosWarpState }; 