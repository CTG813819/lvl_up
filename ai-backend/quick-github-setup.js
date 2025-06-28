const fs = require('fs');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

async function question(prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, resolve);
  });
}

async function setupGitHub() {
  console.log('🚀 Quick GitHub Setup for AI Internet Learning System\n');
  
  // Check if .env exists
  if (!fs.existsSync('.env')) {
    console.log('❌ .env file not found. Creating one...\n');
    
    // Create basic .env template
    const envContent = `# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/lvl_up

# GitHub Configuration (REQUIRED for AI learning system)
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=your_github_username/your_repository_name
GITHUB_USER=your_github_username
GITHUB_EMAIL=your_github_email@example.com

# Server Configuration
PORT=4000
NODE_ENV=production
CORS_ORIGIN=*

# Logging
LOG_LEVEL=info
`;
    
    fs.writeFileSync('.env', envContent);
    console.log('✅ .env file created!\n');
  }
  
  // Read current .env
  let envContent = fs.readFileSync('.env', 'utf8');
  
  console.log('🔧 Let\'s configure your GitHub settings:\n');
  
  // Get GitHub username
  const username = await question('Enter your GitHub username: ');
  envContent = envContent.replace(/GITHUB_USER=.*/g, `GITHUB_USER=${username}`);
  
  // Get GitHub email
  const email = await question('Enter your GitHub email: ');
  envContent = envContent.replace(/GITHUB_EMAIL=.*/g, `GITHUB_EMAIL=${email}`);
  
  // Get repository name
  console.log('\n📁 For the repository, you have two options:');
  console.log('1. Use an existing repository (format: username/repository)');
  console.log('2. Create a new repository and use it');
  
  const repoChoice = await question('\nDo you want to use an existing repository? (y/n): ');
  
  let repoName;
  if (repoChoice.toLowerCase() === 'y' || repoChoice.toLowerCase() === 'yes') {
    repoName = await question('Enter your repository (format: username/repository): ');
  } else {
    console.log('\n📝 To create a new repository:');
    console.log('1. Go to https://github.com/new');
    console.log('2. Create a new repository');
    console.log('3. Copy your AI backend files to it');
    console.log('4. Enter the repository name below');
    repoName = await question('\nEnter your new repository (format: username/repository): ');
  }
  
  envContent = envContent.replace(/GITHUB_REPO=.*/g, `GITHUB_REPO=${repoName}`);
  
  // Check if token is already set
  if (envContent.includes('GITHUB_TOKEN=your_github_token_here')) {
    console.log('\n🔑 You need to add your GitHub token to the .env file.');
    console.log('1. Go to https://github.com/settings/tokens');
    console.log('2. Generate a new token with "repo" permissions');
    console.log('3. Copy the token (starts with ghp_)');
    console.log('4. Replace "your_github_token_here" in the .env file');
  }
  
  // Write updated .env
  fs.writeFileSync('.env', envContent);
  
  console.log('\n✅ GitHub configuration updated!');
  console.log(`   - Username: ${username}`);
  console.log(`   - Email: ${email}`);
  console.log(`   - Repository: ${repoName}`);
  
  console.log('\n🧪 Testing configuration...');
  
  // Test the configuration
  try {
    require('dotenv').config();
    const requiredVars = ['GITHUB_TOKEN', 'GITHUB_REPO', 'GITHUB_USER', 'GITHUB_EMAIL'];
    const missingVars = requiredVars.filter(varName => !process.env[varName] || process.env[varName].includes('your_'));
    
    if (missingVars.length > 0) {
      console.log('\n⚠️ Still missing or incomplete:');
      missingVars.forEach(varName => console.log(`   - ${varName}`));
      console.log('\nPlease complete these in your .env file and run the test again.');
    } else {
      console.log('\n✅ All GitHub variables configured!');
      console.log('\n🚀 Ready to test the complete AI Internet Learning System!');
      console.log('Run: node test-github-integration.js');
    }
  } catch (error) {
    console.log('\n⚠️ Error testing configuration:', error.message);
  }
  
  rl.close();
}

setupGitHub().catch(console.error); 