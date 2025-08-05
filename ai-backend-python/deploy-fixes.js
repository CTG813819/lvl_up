const { exec } = require('child_process');
const path = require('path');

// Configuration
const EC2_HOST = 'your-ec2-host'; // Replace with your actual EC2 host
const EC2_USER = 'ubuntu';
const REMOTE_PATH = '/home/ubuntu/ai-backend';
const LOCAL_PATH = './ai-backend';

// Files to deploy
const filesToDeploy = [
  'src/services/imperiumService.js',
  'src/services/aiLearningService.js'
];

console.log('🚀 Deploying proposal validation fixes to EC2...');

async function deployFiles() {
  try {
    // Create deployment package
    console.log('📦 Creating deployment package...');
    
    for (const file of filesToDeploy) {
      const localFile = path.join(LOCAL_PATH, file);
      const remoteFile = path.join(REMOTE_PATH, file);
      
      console.log(`📤 Uploading ${file}...`);
      
      const scpCommand = `scp -i ~/.ssh/your-key.pem ${localFile} ${EC2_USER}@${EC2_HOST}:${remoteFile}`;
      
      await new Promise((resolve, reject) => {
        exec(scpCommand, (error, stdout, stderr) => {
          if (error) {
            console.error(`❌ Error uploading ${file}:`, error.message);
            reject(error);
            return;
          }
          console.log(`✅ Uploaded ${file}`);
          resolve();
        });
      });
    }
    
    // Restart the backend
    console.log('🔄 Restarting backend service...');
    
    const restartCommand = `ssh -i ~/.ssh/your-key.pem ${EC2_USER}@${EC2_HOST} "cd ${REMOTE_PATH} && pm2 restart ai-learning-backend"`;
    
    await new Promise((resolve, reject) => {
      exec(restartCommand, (error, stdout, stderr) => {
        if (error) {
          console.error('❌ Error restarting backend:', error.message);
          reject(error);
          return;
        }
        console.log('✅ Backend restarted successfully');
        console.log('📋 Restart output:', stdout);
        resolve();
      });
    });
    
    console.log('🎉 Deployment completed successfully!');
    console.log('📊 The backend should now handle incomplete proposals gracefully');
    
  } catch (error) {
    console.error('❌ Deployment failed:', error.message);
    process.exit(1);
  }
}

// Manual deployment instructions
console.log('\n📋 MANUAL DEPLOYMENT INSTRUCTIONS:');
console.log('If you prefer to deploy manually, follow these steps:');
console.log('');
console.log('1. Upload the fixed files to your EC2 instance:');
console.log(`   scp -i ~/.ssh/your-key.pem ai-backend/src/services/imperiumService.js ${EC2_USER}@${EC2_HOST}:${REMOTE_PATH}/src/services/`);
console.log(`   scp -i ~/.ssh/your-key.pem ai-backend/src/services/aiLearningService.js ${EC2_USER}@${EC2_HOST}:${REMOTE_PATH}/src/services/`);
console.log('');
console.log('2. SSH into your EC2 instance:');
console.log(`   ssh -i ~/.ssh/your-key.pem ${EC2_USER}@${EC2_HOST}`);
console.log('');
console.log('3. Navigate to the backend directory:');
console.log(`   cd ${REMOTE_PATH}`);
console.log('');
console.log('4. Restart the backend service:');
console.log('   pm2 restart ai-learning-backend');
console.log('');
console.log('5. Check the logs to verify the fix:');
console.log('   pm2 logs ai-learning-backend --lines 50');
console.log('');

// Run deployment if this script is executed directly
if (require.main === module) {
  deployFiles();
}

module.exports = { deployFiles }; 