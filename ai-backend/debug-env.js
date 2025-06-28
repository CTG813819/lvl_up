const fs = require('fs');
const path = require('path');

console.log('🔍 Debugging Environment Variables...\n');

// Check if .env file exists
const envPath = path.join(__dirname, '.env');
console.log(`1️⃣ Checking for .env file at: ${envPath}`);
console.log(`   File exists: ${fs.existsSync(envPath) ? '✅ Yes' : '❌ No'}`);

if (fs.existsSync(envPath)) {
  console.log('\n2️⃣ .env file contents:');
  const envContent = fs.readFileSync(envPath, 'utf8');
  console.log('--- START OF .env FILE ---');
  console.log(envContent);
  console.log('--- END OF .env FILE ---');
  
  // Count lines
  const lines = envContent.split('\n').filter(line => line.trim() !== '');
  console.log(`\n   Total non-empty lines: ${lines.length}`);
  
  // Check for GitHub variables
  const githubVars = ['GITHUB_TOKEN', 'GITHUB_REPO', 'GITHUB_USER', 'GITHUB_EMAIL'];
  console.log('\n3️⃣ Checking for GitHub variables:');
  githubVars.forEach(varName => {
    const hasVar = envContent.includes(varName + '=');
    console.log(`   ${varName}: ${hasVar ? '✅ Found' : '❌ Missing'}`);
  });
}

// Try to load dotenv
console.log('\n4️⃣ Attempting to load dotenv...');
try {
  require('dotenv').config();
  console.log('   ✅ dotenv loaded successfully');
} catch (error) {
  console.log(`   ❌ Error loading dotenv: ${error.message}`);
}

// Check environment variables
console.log('\n5️⃣ Current environment variables:');
const requiredVars = ['GITHUB_TOKEN', 'GITHUB_REPO', 'GITHUB_USER', 'GITHUB_EMAIL'];
requiredVars.forEach(varName => {
  const value = process.env[varName];
  if (value) {
    // Mask sensitive values
    const maskedValue = varName === 'GITHUB_TOKEN' ? 
      value.substring(0, 10) + '...' : 
      value;
    console.log(`   ${varName}: ✅ Set (${maskedValue})`);
  } else {
    console.log(`   ${varName}: ❌ Not set`);
  }
});

console.log('\n🔧 Troubleshooting tips:');
console.log('   - Make sure .env file has no extra extensions (.txt, etc.)');
console.log('   - Check for extra spaces or special characters');
console.log('   - Try restarting your terminal/editor');
console.log('   - Ensure file is saved with UTF-8 encoding'); 