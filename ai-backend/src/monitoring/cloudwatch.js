const AWS = require('aws-sdk');

class MonitoringService {
  constructor() {
    this.cloudwatch = new AWS.CloudWatch({
      region: process.env.AWS_REGION || 'us-east-1'
    });
    this.enabled = process.env.ENABLE_CLOUDWATCH === 'true';
  }

  async logMetric(metricName, value, unit = 'Count') {
    if (!this.enabled) return;
    
    try {
      await this.cloudwatch.putMetricData({
        Namespace: 'AI-Learning-Backend',
        MetricData: [{
          MetricName: metricName,
          Value: value,
          Unit: unit,
          Timestamp: new Date()
        }]
      }).promise();
      
      console.log(`[CLOUDWATCH] 📊 Logged metric: ${metricName} = ${value} ${unit}`);
    } catch (error) {
      console.error('[CLOUDWATCH] ❌ Logging error:', error);
    }
  }
  
  async logMemoryUsage() {
    const memUsage = process.memoryUsage();
    await this.logMetric('MemoryUsage', memUsage.heapUsed / 1024 / 1024, 'Megabytes');
    await this.logMetric('MemoryRSS', memUsage.rss / 1024 / 1024, 'Megabytes');
  }
  
  async logCPUUsage() {
    const startUsage = process.cpuUsage();
    await new Promise(resolve => setTimeout(resolve, 100));
    const endUsage = process.cpuUsage(startUsage);
    
    const cpuPercent = (endUsage.user + endUsage.system) / 1000000; // Convert to seconds
    await this.logMetric('CPUUsage', cpuPercent, 'Seconds');
  }
  
  async logRequestMetrics(endpoint, responseTime, statusCode) {
    await this.logMetric('RequestCount', 1);
    await this.logMetric('ResponseTime', responseTime, 'Milliseconds');
    
    if (statusCode >= 400) {
      await this.logMetric('ErrorCount', 1);
    }
    
    // Log endpoint-specific metrics
    await this.logMetric(`${endpoint}Requests`, 1);
  }
  
  async logAIMetrics(aiName, action, success, duration) {
    await this.logMetric(`${aiName}${action}Count`, 1);
    await this.logMetric(`${aiName}${action}Duration`, duration, 'Milliseconds');
    
    if (!success) {
      await this.logMetric(`${aiName}${action}Errors`, 1);
    }
  }
  
  async logLearningMetrics(insightsCount, effectiveness) {
    await this.logMetric('LearningInsightsCount', insightsCount);
    await this.logMetric('LearningEffectiveness', effectiveness, 'Percent');
  }
}

module.exports = new MonitoringService(); 