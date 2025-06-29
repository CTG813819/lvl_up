const fs = require('fs').promises;
const path = require('path');
const { logEvent } = require('../state');

/**
 * App Feedback Service
 * Collects and processes user feedback and usage data from Conquest AI generated apps
 */
class AppFeedbackService {
  constructor() {
    this.feedbackData = [];
    this.usagePatterns = [];
    this.errorReports = [];
    this.performanceMetrics = [];
    this.userSatisfaction = [];
  }

  /**
   * Collect user feedback from a Conquest AI generated app
   */
  async collectUserFeedback(appId, feedbackData) {
    try {
      console.log(`[APP_FEEDBACK_SERVICE] 📊 Collecting user feedback for app ${appId}`);
      
      const feedback = {
        appId,
        timestamp: new Date().toISOString(),
        userId: feedbackData.userId || 'anonymous',
        feedbackType: feedbackData.type || 'general',
        rating: feedbackData.rating || 0,
        comment: feedbackData.comment || '',
        category: feedbackData.category || 'general',
        severity: feedbackData.severity || 'low',
        userAgent: feedbackData.userAgent || '',
        appVersion: feedbackData.appVersion || '1.0.0',
        platform: feedbackData.platform || 'unknown',
        sessionId: feedbackData.sessionId || null,
        features: feedbackData.features || [],
        issues: feedbackData.issues || [],
        suggestions: feedbackData.suggestions || []
      };

      // Store feedback locally
      this.feedbackData.push(feedback);
      
      // Send to Conquest AI learning system
      await this.sendToConquestLearning(appId, feedback);
      
      // Log the feedback collection
      await logEvent('app_feedback_collected', {
        appId,
        feedbackType: feedback.feedbackType,
        rating: feedback.rating,
        category: feedback.category
      });

      console.log(`[APP_FEEDBACK_SERVICE] ✅ User feedback collected for app ${appId}`);
      return feedback;
      
    } catch (error) {
      console.error(`[APP_FEEDBACK_SERVICE] ❌ Error collecting user feedback:`, error);
      throw error;
    }
  }

  /**
   * Collect usage patterns from app
   */
  async collectUsagePatterns(appId, usageData) {
    try {
      console.log(`[APP_FEEDBACK_SERVICE] 📈 Collecting usage patterns for app ${appId}`);
      
      const usage = {
        appId,
        timestamp: new Date().toISOString(),
        sessionId: usageData.sessionId,
        userId: usageData.userId || 'anonymous',
        screenViews: usageData.screenViews || [],
        featureUsage: usageData.featureUsage || {},
        timeSpent: usageData.timeSpent || 0,
        interactions: usageData.interactions || [],
        performance: usageData.performance || {},
        errors: usageData.errors || [],
        crashes: usageData.crashes || []
      };

      // Store usage patterns
      this.usagePatterns.push(usage);
      
      // Send to Conquest AI learning system
      await this.sendUsageToConquest(appId, usage);
      
      console.log(`[APP_FEEDBACK_SERVICE] ✅ Usage patterns collected for app ${appId}`);
      return usage;
      
    } catch (error) {
      console.error(`[APP_FEEDBACK_SERVICE] ❌ Error collecting usage patterns:`, error);
      throw error;
    }
  }

  /**
   * Collect error reports from app
   */
  async collectErrorReport(appId, errorData) {
    try {
      console.log(`[APP_FEEDBACK_SERVICE] 🐛 Collecting error report for app ${appId}`);
      
      const error = {
        appId,
        timestamp: new Date().toISOString(),
        errorType: errorData.type || 'unknown',
        errorMessage: errorData.message || '',
        stackTrace: errorData.stackTrace || '',
        severity: errorData.severity || 'medium',
        userId: errorData.userId || 'anonymous',
        sessionId: errorData.sessionId || null,
        appVersion: errorData.appVersion || '1.0.0',
        platform: errorData.platform || 'unknown',
        context: errorData.context || {},
        userAction: errorData.userAction || '',
        screen: errorData.screen || ''
      };

      // Store error report
      this.errorReports.push(error);
      
      // Send to Conquest AI learning system
      await this.sendErrorToConquest(appId, error);
      
      console.log(`[APP_FEEDBACK_SERVICE] ✅ Error report collected for app ${appId}`);
      return error;
      
    } catch (error) {
      console.error(`[APP_FEEDBACK_SERVICE] ❌ Error collecting error report:`, error);
      throw error;
    }
  }

  /**
   * Collect performance metrics from app
   */
  async collectPerformanceMetrics(appId, performanceData) {
    try {
      console.log(`[APP_FEEDBACK_SERVICE] ⚡ Collecting performance metrics for app ${appId}`);
      
      const metrics = {
        appId,
        timestamp: new Date().toISOString(),
        loadTime: performanceData.loadTime || 0,
        renderTime: performanceData.renderTime || 0,
        memoryUsage: performanceData.memoryUsage || 0,
        cpuUsage: performanceData.cpuUsage || 0,
        networkLatency: performanceData.networkLatency || 0,
        frameRate: performanceData.frameRate || 0,
        batteryUsage: performanceData.batteryUsage || 0,
        platform: performanceData.platform || 'unknown',
        appVersion: performanceData.appVersion || '1.0.0'
      };

      // Store performance metrics
      this.performanceMetrics.push(metrics);
      
      // Send to Conquest AI learning system
      await this.sendPerformanceToConquest(appId, metrics);
      
      console.log(`[APP_FEEDBACK_SERVICE] ✅ Performance metrics collected for app ${appId}`);
      return metrics;
      
    } catch (error) {
      console.error(`[APP_FEEDBACK_SERVICE] ❌ Error collecting performance metrics:`, error);
      throw error;
    }
  }

  /**
   * Send feedback to Conquest AI learning system
   */
  async sendToConquestLearning(appId, feedback) {
    try {
      // Create learning entry for Conquest AI
      const Learning = require('../models/learning');
      
      const learningEntry = new Learning({
        aiType: 'Conquest',
        learningKey: 'app-user-feedback',
        learningValue: `User feedback for app ${appId}: ${feedback.feedbackType} - Rating: ${feedback.rating}/5`,
        status: 'learning-completed',
        timestamp: new Date(),
        filePath: `conquest-apps/${appId}`,
        improvementType: 'user-feedback',
        metadata: {
          appId,
          feedback,
          feedbackType: feedback.feedbackType,
          rating: feedback.rating,
          category: feedback.category,
          severity: feedback.severity
        }
      });

      await learningEntry.save();
      
      console.log(`[APP_FEEDBACK_SERVICE] ✅ Feedback sent to Conquest learning system`);
      
    } catch (error) {
      console.error(`[APP_FEEDBACK_SERVICE] ❌ Error sending feedback to Conquest:`, error);
    }
  }

  /**
   * Send usage patterns to Conquest AI
   */
  async sendUsageToConquest(appId, usage) {
    try {
      const Learning = require('../models/learning');
      
      const learningEntry = new Learning({
        aiType: 'Conquest',
        learningKey: 'app-usage-patterns',
        learningValue: `Usage patterns for app ${appId}: ${Object.keys(usage.featureUsage).length} features used`,
        status: 'learning-completed',
        timestamp: new Date(),
        filePath: `conquest-apps/${appId}`,
        improvementType: 'usage-analysis',
        metadata: {
          appId,
          usage,
          featureCount: Object.keys(usage.featureUsage).length,
          timeSpent: usage.timeSpent,
          interactionCount: usage.interactions.length
        }
      });

      await learningEntry.save();
      
      console.log(`[APP_FEEDBACK_SERVICE] ✅ Usage patterns sent to Conquest learning system`);
      
    } catch (error) {
      console.error(`[APP_FEEDBACK_SERVICE] ❌ Error sending usage to Conquest:`, error);
    }
  }

  /**
   * Send error reports to Conquest AI
   */
  async sendErrorToConquest(appId, error) {
    try {
      const Learning = require('../models/learning');
      
      const learningEntry = new Learning({
        aiType: 'Conquest',
        learningKey: 'app-error-report',
        learningValue: `Error in app ${appId}: ${error.errorType} - ${error.errorMessage}`,
        status: 'learning-completed',
        timestamp: new Date(),
        filePath: `conquest-apps/${appId}`,
        improvementType: 'error-analysis',
        metadata: {
          appId,
          error,
          errorType: error.errorType,
          severity: error.severity,
          context: error.context
        }
      });

      await learningEntry.save();
      
      console.log(`[APP_FEEDBACK_SERVICE] ✅ Error report sent to Conquest learning system`);
      
    } catch (error) {
      console.error(`[APP_FEEDBACK_SERVICE] ❌ Error sending error to Conquest:`, error);
    }
  }

  /**
   * Send performance metrics to Conquest AI
   */
  async sendPerformanceToConquest(appId, metrics) {
    try {
      const Learning = require('../models/learning');
      
      const learningEntry = new Learning({
        aiType: 'Conquest',
        learningKey: 'app-performance-metrics',
        learningValue: `Performance metrics for app ${appId}: Load time ${metrics.loadTime}ms, Memory ${metrics.memoryUsage}MB`,
        status: 'learning-completed',
        timestamp: new Date(),
        filePath: `conquest-apps/${appId}`,
        improvementType: 'performance-analysis',
        metadata: {
          appId,
          metrics,
          loadTime: metrics.loadTime,
          memoryUsage: metrics.memoryUsage,
          frameRate: metrics.frameRate
        }
      });

      await learningEntry.save();
      
      console.log(`[APP_FEEDBACK_SERVICE] ✅ Performance metrics sent to Conquest learning system`);
      
    } catch (error) {
      console.error(`[APP_FEEDBACK_SERVICE] ❌ Error sending performance to Conquest:`, error);
    }
  }

  /**
   * Get feedback analytics for an app
   */
  async getFeedbackAnalytics(appId) {
    try {
      const appFeedback = this.feedbackData.filter(f => f.appId === appId);
      const appUsage = this.usagePatterns.filter(u => u.appId === appId);
      const appErrors = this.errorReports.filter(e => e.appId === appId);
      const appPerformance = this.performanceMetrics.filter(p => p.appId === appId);

      const analytics = {
        appId,
        totalFeedback: appFeedback.length,
        averageRating: appFeedback.length > 0 
          ? appFeedback.reduce((sum, f) => sum + f.rating, 0) / appFeedback.length 
          : 0,
        feedbackByCategory: this.groupBy(appFeedback, 'category'),
        feedbackBySeverity: this.groupBy(appFeedback, 'severity'),
        usagePatterns: {
          totalSessions: appUsage.length,
          averageTimeSpent: appUsage.length > 0 
            ? appUsage.reduce((sum, u) => sum + u.timeSpent, 0) / appUsage.length 
            : 0,
          mostUsedFeatures: this.getMostUsedFeatures(appUsage)
        },
        errorAnalysis: {
          totalErrors: appErrors.length,
          errorsByType: this.groupBy(appErrors, 'errorType'),
          errorsBySeverity: this.groupBy(appErrors, 'severity')
        },
        performanceAnalysis: {
          averageLoadTime: appPerformance.length > 0 
            ? appPerformance.reduce((sum, p) => sum + p.loadTime, 0) / appPerformance.length 
            : 0,
          averageMemoryUsage: appPerformance.length > 0 
            ? appPerformance.reduce((sum, p) => sum + p.memoryUsage, 0) / appPerformance.length 
            : 0
        }
      };

      return analytics;
      
    } catch (error) {
      console.error(`[APP_FEEDBACK_SERVICE] ❌ Error getting feedback analytics:`, error);
      throw error;
    }
  }

  /**
   * Helper method to group data by property
   */
  groupBy(array, property) {
    return array.reduce((groups, item) => {
      const value = item[property];
      groups[value] = groups[value] || [];
      groups[value].push(item);
      return groups;
    }, {});
  }

  /**
   * Get most used features from usage patterns
   */
  getMostUsedFeatures(usagePatterns) {
    const featureCounts = {};
    
    usagePatterns.forEach(usage => {
      Object.keys(usage.featureUsage).forEach(feature => {
        featureCounts[feature] = (featureCounts[feature] || 0) + usage.featureUsage[feature];
      });
    });

    return Object.entries(featureCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([feature, count]) => ({ feature, count }));
  }
}

module.exports = new AppFeedbackService(); 