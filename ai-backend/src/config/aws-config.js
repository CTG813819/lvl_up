module.exports = {
  // AWS Configuration
  aws: {
    region: process.env.AWS_REGION || 'us-east-1',
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  },
  
  // Application Configuration
  app: {
    port: process.env.PORT || 4000,
    environment: process.env.NODE_ENV || 'production',
    corsOrigin: process.env.CORS_ORIGIN || '*',
  },
  
  // Database Configuration
  database: {
    uri: process.env.MONGODB_URI || 'mongodb://localhost:27017/ai-learning',
  },
  
  // Memory Configuration
  memory: {
    maxHeapSize: '4096m',
    enableGC: true,
  },
  
  // Monitoring Configuration
  monitoring: {
    enableCloudWatch: process.env.ENABLE_CLOUDWATCH === 'true',
    logLevel: process.env.LOG_LEVEL || 'info',
  }
}; 