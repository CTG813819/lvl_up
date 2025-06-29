const simpleGit = require('simple-git');
const fs = require('fs');
const path = require('path');

// Validate required environment variables
if (!process.env.GITHUB_REPO) {
  throw new Error('GITHUB_REPO environment variable is required. Please set it in your .env file (e.g., GITHUB_REPO=yourusername/yourrepo)');
}
if (!process.env.GITHUB_TOKEN) {
  throw new Error('GITHUB_TOKEN environment variable is required. Please set it in your .env file');
}
if (!process.env.GITHUB_USER) {
  throw new Error('GITHUB_USER environment variable is required. Please set it in your .env file');
}
if (!process.env.GITHUB_EMAIL) {
  throw new Error('GITHUB_EMAIL environment variable is required. Please set it in your .env file');
}

// Dynamic import for ES module
let octokit;
(async () => {
  const { Octokit } = await import('@octokit/rest');
  octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
})();

const REPO = process.env.GITHUB_REPO;
const USER = process.env.GITHUB_USER;
const EMAIL = process.env.GITHUB_EMAIL;
const LOCAL_PATH = path.join(process.cwd(), 'temp-repo'); // Use local temp directory

console.log(`[GITHUB] ✅ Environment validated:`);
console.log(`  - Repository: ${REPO}`);
console.log(`  - User: ${USER}`);
console.log(`  - Email: ${EMAIL}`);
console.log(`  - Local Path: ${LOCAL_PATH}`);

async function cloneOrPullRepo() {
  console.log(`[GITHUB] 📁 Setting up repository at: ${LOCAL_PATH}`);
  
  if (!fs.existsSync(LOCAL_PATH)) {
    console.log(`[GITHUB] 🔄 Cloning repository: ${REPO}`);
    await simpleGit().clone(`https://github.com/${REPO}.git`, LOCAL_PATH);
    console.log(`[GITHUB] ✅ Repository cloned successfully`);
  } else {
    console.log(`[GITHUB] 🔄 Pulling latest changes`);
    const git = simpleGit(LOCAL_PATH);
    await git.pull('origin', 'main');
    console.log(`[GITHUB] ✅ Repository updated`);
  }
  
  // Configure Git user identity
  const git = simpleGit(LOCAL_PATH);
  await git.addConfig('user.name', USER);
  await git.addConfig('user.email', EMAIL);
  console.log(`[GITHUB] ⚙️ Configured Git user: ${USER} <${EMAIL}>`);
}

async function applyProposalAndPR({ filePath, codeAfter, proposalId }) {
  console.log(`[GITHUB] Starting to apply proposal ${proposalId} for file: ${filePath}`);
  
  try {
    // Ensure octokit is initialized
    if (!octokit) {
      const { Octokit } = await import('@octokit/rest');
      octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
    }
    
    await cloneOrPullRepo();
    console.log(`[GITHUB] Repository updated for proposal ${proposalId}`);
    
    const absPath = path.join(LOCAL_PATH, filePath);
    console.log(`[GITHUB] Writing code to: ${absPath}`);

    // Write the new code to the file
    fs.writeFileSync(absPath, codeAfter, 'utf8');
    console.log(`[GITHUB] Code written to file for proposal ${proposalId}`);

    const branch = `ai-proposal-${proposalId}`;
    console.log(`[GITHUB] Creating branch: ${branch}`);
    
    const git = simpleGit(LOCAL_PATH);
    
    console.log(`[GITHUB] Checking out new branch for proposal ${proposalId}`);
    await git.checkoutLocalBranch(branch);
    
    console.log(`[GITHUB] Adding file to git for proposal ${proposalId}`);
    await git.add(filePath);
    
    console.log(`[GITHUB] Committing changes for proposal ${proposalId}`);
    await git.commit(`AI Proposal ${proposalId}: Automated code improvement`);
    
    console.log(`[GITHUB] Pushing branch to origin for proposal ${proposalId}`);
    await git.push('origin', branch);
    console.log(`[GITHUB] Branch pushed successfully for proposal ${proposalId}`);

    // Create PR
    console.log(`[GITHUB] Creating pull request for proposal ${proposalId}`);
    const pr = await octokit.pulls.create({
      owner: REPO.split('/')[0],
      repo: REPO.split('/')[1],
      title: `AI Proposal ${proposalId}`,
      head: branch,
      base: 'main',
      body: 'Automated code improvement by AI.',
    });

    console.log(`[GITHUB] ✅ Successfully created PR for proposal ${proposalId}: ${pr.data.html_url}`);
    return pr.data.html_url;
    
  } catch (error) {
    console.error(`[GITHUB] ❌ Error applying proposal ${proposalId}:`, error);
    console.error(`[GITHUB] Error details:`, error.message);
    console.error(`[GITHUB] Stack trace:`, error.stack);
    throw error;
  }
}

/**
 * Push AI code updates to GitHub repository with proper workflow
 */
async function pushAICodeUpdates(aiType, updates, learningData) {
  console.log(`[GITHUB] 🚀 Pushing AI code updates for ${aiType} to GitHub`);
  
  try {
    // Ensure octokit is initialized
    if (!octokit) {
      const { Octokit } = await import('@octokit/rest');
      octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
    }
    
    await cloneOrPullRepo();
    const git = simpleGit(LOCAL_PATH);
    
    // Create a unique branch for AI learning updates
    const timestamp = Date.now();
    const branch = `ai-learning-${aiType.toLowerCase()}-${timestamp}`;
    console.log(`[GITHUB] 🌿 Creating AI learning branch: ${branch}`);
    
    // Create and checkout new branch
    await git.checkoutLocalBranch(branch);
    
    // Get AI file path and update it
    const aiFilePath = getAIFilePath(aiType);
    const absPath = path.join(LOCAL_PATH, aiFilePath);
    
    if (fs.existsSync(absPath)) {
      // Read current file content
      const currentContent = fs.readFileSync(absPath, 'utf8');
      
      // Apply updates to the file
      const updatedContent = applyUpdatesToFile(currentContent, updates);
      
      // Write updated content back
      fs.writeFileSync(absPath, updatedContent, 'utf8');
      console.log(`[GITHUB] ✅ Updated AI file: ${aiFilePath}`);
      
      // Add and commit the changes
      await git.add(aiFilePath);
      
      // Create detailed commit message
      const commitMessage = createAILearningCommitMessage(aiType, updates, learningData);
      await git.commit(commitMessage);
      
      // Push the branch to origin
      console.log(`[GITHUB] 📤 Pushing branch to GitHub...`);
      await git.push('origin', branch);
      console.log(`[GITHUB] ✅ Branch pushed successfully: ${branch}`);
      
      // Create pull request
      const pr = await createAILearningPR(aiType, branch, updates, learningData);
      
      console.log(`[GITHUB] 🎉 Successfully created PR for ${aiType}: ${pr.data.html_url}`);
      
      return {
        success: true,
        branch,
        prUrl: pr.data.html_url,
        prNumber: pr.data.number,
        updatesApplied: updates.length,
        filePath: aiFilePath,
        commitMessage
      };
      
    } else {
      console.log(`[GITHUB] ⚠️ AI file not found at ${absPath}, creating new file`);
      
      // Create new file if it doesn't exist
      const newContent = createNewAIFile(aiType, updates, learningData);
      
      // Ensure directory exists
      const dir = path.dirname(absPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      
      fs.writeFileSync(absPath, newContent, 'utf8');
      console.log(`[GITHUB] ✅ Created new AI file: ${aiFilePath}`);
      
      // Add and commit the new file
      await git.add(aiFilePath);
      const commitMessage = `AI Learning: Create new ${aiType} service with improvements`;
      await git.commit(commitMessage);
      
      // Push the branch
      await git.push('origin', branch);
      
      // Create pull request
      const pr = await createAILearningPR(aiType, branch, updates, learningData);
      
      return {
        success: true,
        branch,
        prUrl: pr.data.html_url,
        prNumber: pr.data.number,
        updatesApplied: updates.length,
        filePath: aiFilePath,
        isNewFile: true,
        commitMessage
      };
    }
    
  } catch (error) {
    console.error(`[GITHUB] ❌ Error pushing AI code updates for ${aiType}:`, error);
    throw error;
  }
}

/**
 * Get AI file path
 */
function getAIFilePath(aiType) {
  const aiFiles = {
    'Imperium': 'src/services/imperiumService.js',
    'Guardian': 'src/services/guardianService.js',
    'Sandbox': 'src/services/sandboxService.js'
  };
  
  return aiFiles[aiType];
}

/**
 * Apply updates to file content
 */
function applyUpdatesToFile(content, updates) {
  let updatedContent = content;
  
  // Sort updates by priority
  const sortedUpdates = updates.sort((a, b) => {
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    return priorityOrder[b.priority] - priorityOrder[a.priority];
  });
  
  for (const update of sortedUpdates) {
    if (update.code) {
      // Add new functions before module.exports
      if (updatedContent.includes('module.exports')) {
        const beforeExports = updatedContent.lastIndexOf('module.exports');
        updatedContent = updatedContent.substring(0, beforeExports) + 
                        '\n\n' + update.code + '\n\n' + 
                        updatedContent.substring(beforeExports);
      } else {
        // Add at the end if no module.exports found
        updatedContent += '\n\n' + update.code;
      }
    }
  }
  
  return updatedContent;
}

/**
 * Create detailed commit message for AI learning
 */
function createAILearningCommitMessage(aiType, updates, learningData) {
  const timestamp = new Date().toISOString();
  let message = `🤖 AI Learning Update: ${aiType}\n\n`;
  
  message += `📅 Timestamp: ${timestamp}\n`;
  message += `🔧 Updates Applied: ${updates.length}\n\n`;
  
  // Add update details
  message += `### Code Updates:\n`;
  updates.forEach((update, index) => {
    message += `${index + 1}. **${update.type}** (${update.priority} priority): ${update.description}\n`;
  });
  
  // Add learning insights if available
  if (learningData.insights && learningData.insights.length > 0) {
    message += `\n### Learning Insights:\n`;
    learningData.insights.slice(0, 3).forEach((insight, index) => {
      message += `${index + 1}. ${insight.type}: ${insight.content.substring(0, 100)}...\n`;
    });
  }
  
  // Add recommendations if available
  if (learningData.recommendations && learningData.recommendations.length > 0) {
    message += `\n### Recommendations Applied:\n`;
    learningData.recommendations.forEach((rec, index) => {
      message += `${index + 1}. ${rec.type}: ${rec.description}\n`;
    });
  }
  
  // Add sources if available
  if (learningData.sources && learningData.sources.length > 0) {
    message += `\n### Learning Sources:\n`;
    learningData.sources.forEach(source => {
      message += `- ${source}\n`;
    });
  }
  
  message += `\n---\n*This update was automatically generated by the AI learning system based on proposal feedback and internet research.*`;
  
  return message;
}

/**
 * Create pull request for AI learning updates
 */
async function createAILearningPR(aiType, branch, updates, learningData) {
  const title = `🤖 AI Learning Update: ${aiType} - ${updates.length} improvements`;
  
  let body = `## AI Learning Update for ${aiType}\n\n`;
  body += `This pull request contains automated code improvements for the ${aiType} AI based on:\n`;
  body += `- Proposal feedback analysis\n`;
  body += `- Internet research and best practices\n`;
  body += `- Learning pattern recognition\n\n`;
  
  body += `### Summary\n`;
  body += `- **Updates Applied**: ${updates.length}\n`;
  body += `- **Learning Sources**: ${learningData.sources?.length || 0}\n`;
  body += `- **Insights Generated**: ${learningData.insights?.length || 0}\n`;
  body += `- **Recommendations**: ${learningData.recommendations?.length || 0}\n\n`;
  
  body += `### Update Details\n`;
  updates.forEach((update, index) => {
    body += `#### ${index + 1}. ${update.type} (${update.priority} priority)\n`;
    body += `- **Description**: ${update.description}\n`;
    body += `- **Impact**: Code quality and performance improvement\n\n`;
  });
  
  if (learningData.insights && learningData.insights.length > 0) {
    body += `### Key Learning Insights\n`;
    learningData.insights.slice(0, 5).forEach((insight, index) => {
      body += `${index + 1}. **${insight.type}**: ${insight.content.substring(0, 150)}...\n`;
    });
    body += `\n`;
  }
  
  body += `### Testing\n`;
  body += `- [ ] Code compiles without errors\n`;
  body += `- [ ] Existing functionality preserved\n`;
  body += `- [ ] New features work as expected\n`;
  body += `- [ ] Performance improvements verified\n\n`;
  
  body += `### Notes\n`;
  body += `This is an automated update generated by the AI learning system. The changes are based on:\n`;
  body += `1. Analysis of proposal success/failure patterns\n`;
  body += `2. Research from programming communities and documentation\n`;
  body += `3. Best practices identified through machine learning\n\n`;
  body += `**Please review the changes carefully before merging.**\n\n`;
  body += `---\n*Generated by AI Learning System at ${new Date().toISOString()}*`;
  
  const pr = await octokit.pulls.create({
    owner: REPO.split('/')[0],
    repo: REPO.split('/')[1],
    title,
    head: branch,
    base: 'main',
    body
  });
  
  console.log(`[GITHUB] Created AI learning PR: ${pr.data.html_url}`);
  return pr;
}

/**
 * Create new AI file with improvements
 */
function createNewAIFile(aiType, updates, learningData) {
  const baseContent = `/**
 * ${aiType} AI Service
 * Generated by AI Internet Learning System
 * Learning Insights: ${learningData.insights?.length || 0}
 * Recommendations: ${learningData.recommendations?.length || 0}
 */

const mongoose = require('mongoose');

class ${aiType}Service {
  constructor() {
    this.name = '${aiType}';
    this.version = '1.0.0';
    this.learningData = ${JSON.stringify(learningData, null, 2)};
  }

  /**
   * Initialize the service
   */
  async initialize() {
    console.log(\`[${aiType.toUpperCase()}] 🚀 Initializing ${aiType} AI Service\`);
    
    // Apply learned improvements
    ${updates.map(update => `// ${update.description}`).join('\n    ')}
    
    console.log(\`[${aiType.toUpperCase()}] ✅ ${aiType} AI Service initialized with ${updates.length} improvements\`);
  }

  /**
   * Process a request
   */
  async processRequest(request) {
    console.log(\`[${aiType.toUpperCase()}] 📝 Processing request\`);
    
    // Apply learned best practices
    ${updates.filter(u => u.type === 'best_practice').map(update => 
      `// ${update.description}`
    ).join('\n    ')}
    
    return {
      success: true,
      aiType: '${aiType}',
      improvements: ${updates.length},
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Get learning insights
   */
  getLearningInsights() {
    return this.learningData;
  }
}

module.exports = new ${aiType}Service();
`;

  return baseContent;
}

/**
 * Merge AI learning PR
 */
async function mergeAILearningPR(prUrl) {
  try {
    // Extract PR number from URL
    const prNumber = extractPRNumber(prUrl);
    if (!prNumber) {
      throw new Error('Invalid PR URL');
    }
    
    console.log(`[GITHUB] 🔄 Merging PR: ${prNumber}`);
    
    // Merge the PR
    const mergeResult = await octokit.pulls.merge({
      owner: REPO.split('/')[0],
      repo: REPO.split('/')[1],
      pull_number: prNumber,
      merge_method: 'squash',
      commit_title: `AI Learning: Merge improvements`,
      commit_message: 'AI improvements approved and merged'
    });
    
    console.log(`[GITHUB] ✅ PR merged successfully: ${prNumber}`);
    
    return {
      success: true,
      prNumber,
      mergeResult: mergeResult.data
    };
    
  } catch (error) {
    console.error(`[GITHUB] ❌ Error merging PR:`, error);
    throw error;
  }
}

/**
 * Close PR
 */
async function closePR(prNumber) {
  try {
    console.log(`[GITHUB] 🔒 Closing PR: ${prNumber}`);
    
    // Close the PR
    const closeResult = await octokit.pulls.update({
      owner: REPO.split('/')[0],
      repo: REPO.split('/')[1],
      pull_number: prNumber,
      state: 'closed'
    });
    
    console.log(`[GITHUB] ✅ PR closed successfully: ${prNumber}`);
    
    return {
      success: true,
      prNumber,
      closeResult: closeResult.data
    };
    
  } catch (error) {
    console.error(`[GITHUB] ❌ Error closing PR:`, error);
    throw error;
  }
}

/**
 * Extract PR number from URL
 */
function extractPRNumber(prUrl) {
  const match = prUrl.match(/\/pull\/(\d+)/);
  return match ? parseInt(match[1]) : null;
}

/**
 * Get repository status and recent AI learning updates
 */
async function getRepositoryStatus() {
  try {
    if (!octokit) {
      const { Octokit } = await import('@octokit/rest');
      octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
    }
    
    // Get recent PRs related to AI learning
    const prs = await octokit.pulls.list({
      owner: REPO.split('/')[0],
      repo: REPO.split('/')[1],
      state: 'open',
      per_page: 10
    });
    
    const aiLearningPRs = prs.data.filter(pr => 
      pr.title.includes('AI Learning') || pr.title.includes('🤖')
    );
    
    return {
      totalPRs: prs.data.length,
      aiLearningPRs: aiLearningPRs.length,
      recentPRs: aiLearningPRs.slice(0, 5).map(pr => ({
        title: pr.title,
        url: pr.html_url,
        createdAt: pr.created_at,
        state: pr.state
      }))
    };
    
  } catch (error) {
    console.error(`[GITHUB] ❌ Error getting repository status:`, error);
    return { error: error.message };
  }
}

/**
 * Create a new repository for Conquest AI apps
 */
async function createRepository(repoName, description) {
  try {
    console.log(`[GITHUB] 🚀 Creating new repository: ${repoName}`);
    
    if (!octokit) {
      const { Octokit } = await import('@octokit/rest');
      octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
    }
    
    // Create the repository
    const repo = await octokit.repos.createForAuthenticatedUser({
      name: repoName,
      description: description || 'App built by Conquest AI',
      private: false,
      auto_init: true,
      gitignore_template: 'Flutter',
      license_template: 'mit'
    });
    
    console.log(`[GITHUB] ✅ Repository created successfully: ${repo.data.html_url}`);
    
    return repo.data.html_url;
    
  } catch (error) {
    console.error(`[GITHUB] ❌ Error creating repository:`, error);
    throw error;
  }
}

/**
 * Push code to a repository
 */
async function pushToRepository(appDir, repoUrl) {
  try {
    console.log(`[GITHUB] 📤 Pushing code to repository: ${repoUrl}`);
    
    // Extract owner and repo name from URL
    const urlParts = repoUrl.split('/');
    const repoName = urlParts[urlParts.length - 1];
    const owner = urlParts[urlParts.length - 2];
    
    // Initialize git in the app directory
    const git = simpleGit(appDir);
    
    // Add all files
    await git.add('.');
    
    // Commit the changes
    await git.commit('Initial app build by Conquest AI');
    
    // Add the remote repository
    await git.addRemote('origin', repoUrl);
    
    // Push to the repository
    await git.push('origin', 'main');
    
    console.log(`[GITHUB] ✅ Code pushed successfully to: ${repoUrl}`);
    
    return {
      success: true,
      repoUrl,
      message: 'Code pushed successfully'
    };
    
  } catch (error) {
    console.error(`[GITHUB] ❌ Error pushing to repository:`, error);
    throw error;
  }
}

module.exports = { 
  applyProposalAndPR, 
  pushAICodeUpdates, 
  mergeAILearningPR, 
  getRepositoryStatus,
  closePR,
  createRepository,
  pushToRepository
};