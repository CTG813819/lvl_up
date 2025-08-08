// check-env-and-services.js
// Checks MongoDB, backend, GitHub, and required environment variables

require('dotenv').config({ path: 'ai-backend/.env' });

const http = require('http');
const https = require('https');
const { MongoClient } = require('mongodb');

const REQUIRED_ENV = [
  'MONGODB_URI',
  'GITHUB_TOKEN',
  'GITHUB_REPO',
];

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:4000/api/health';
const MONGODB_URI = process.env.MONGODB_URI;
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_REPO = process.env.GITHUB_REPO;

function checkEnvVars() {
  let allSet = true;
  console.log('Checking required environment variables...');
  for (const key of REQUIRED_ENV) {
    if (!process.env[key]) {
      console.log(`❌ ${key} is NOT set`);
      allSet = false;
    } else {
      console.log(`✅ ${key} is set`);
    }
  }
  return allSet;
}

async function checkMongo() {
  if (!MONGODB_URI) {
    console.log('❌ MONGODB_URI not set, skipping MongoDB check.');
    return false;
  }
  try {
    const client = new MongoClient(MONGODB_URI, { serverSelectionTimeoutMS: 3000 });
    await client.connect();
    await client.db().admin().ping();
    await client.close();
    console.log('✅ MongoDB connection: SUCCESS');
    return true;
  } catch (err) {
    console.log('❌ MongoDB connection: FAILED');
    console.log('   ', err.message);
    return false;
  }
}

function checkBackend() {
  return new Promise((resolve) => {
    console.log(`Checking backend health at ${BACKEND_URL} ...`);
    http.get(BACKEND_URL, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200 && data.includes('ok')) {
          console.log('✅ Backend health: PASS');
          resolve(true);
        } else {
          console.log('❌ Backend health: FAIL');
          console.log('   Response:', data);
          resolve(false);
        }
      });
    }).on('error', (err) => {
      console.log('❌ Backend health: FAIL');
      console.log('   ', err.message);
      resolve(false);
    });
  });
}

function checkGitHub() {
  return new Promise((resolve) => {
    if (!GITHUB_TOKEN || !GITHUB_REPO) {
      console.log('❌ GITHUB_TOKEN or GITHUB_REPO not set, skipping GitHub check.');
      return resolve(false);
    }
    const options = {
      hostname: 'api.github.com',
      path: `/repos/${GITHUB_REPO}`,
      method: 'GET',
      headers: {
        'User-Agent': 'lvl-up-check-script',
        'Authorization': `token ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
      },
    };
    https.get(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          console.log('✅ GitHub API access: PASS');
          resolve(true);
        } else {
          console.log('❌ GitHub API access: FAIL');
          console.log('   Status:', res.statusCode, data);
          resolve(false);
        }
      });
    }).on('error', (err) => {
      console.log('❌ GitHub API access: FAIL');
      console.log('   ', err.message);
      resolve(false);
    });
  });
}

(async () => {
  console.log('--- lvl_up Environment & Service Check ---');
  const envOk = checkEnvVars();
  const mongoOk = await checkMongo();
  const backendOk = await checkBackend();
  const githubOk = await checkGitHub();

  if (envOk && mongoOk && backendOk && githubOk) {
    console.log('\n🎉 All checks PASSED! You are ready to run your tests.');
    process.exit(0);
  } else {
    console.log('\n⚠️  One or more checks FAILED. Please fix the above issues before running tests.');
    process.exit(1);
  }
})(); 