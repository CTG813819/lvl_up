require('dotenv').config();

console.log('🔍 Simple Environment Test\n');

const vars = ['GITHUB_TOKEN', 'GITHUB_REPO', 'GITHUB_USER', 'GITHUB_EMAIL'];

vars.forEach(varName => {
  const value = process.env[varName];
  if (value) {
    console.log(`✅ ${varName}: SET`);
    if (varName === 'GITHUB_TOKEN') {
      console.log(`   Value: ${value.substring(0, 10)}...`);
    } else {
      console.log(`   Value: ${value}`);
    }
  } else {
    console.log(`❌ ${varName}: NOT SET`);
  }
});

console.log('\n📋 All environment variables:');
Object.keys(process.env).filter(key => key.startsWith('GITHUB')).forEach(key => {
  console.log(`   ${key}: ${process.env[key] ? 'SET' : 'NOT SET'}`);
}); 