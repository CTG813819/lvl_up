const simpleGit = require('simple-git');
const path = require('path');
const fs = require('fs').promises;

class GitService {
  constructor() {
    this.git = simpleGit(process.env.GIT_REPO_PATH || '.');
    this.repoPath = process.env.GIT_REPO_PATH || '.';
  }

  /**
   * Apply proposal and push to Git with learning context
   */
  async applyProposalAndPush(filePath, newCode, branch = 'ai-improvements', learningContext = {}) {
    try {
      console.log(`[GIT_SERVICE] 🔄 Applying proposal to ${filePath} on branch ${branch}`);
      
      // Check if branch exists, create if not
      const branches = await this.git.branch();
      if (!branches.all.includes(branch)) {
        console.log(`[GIT_SERVICE] 🌿 Creating new branch: ${branch}`);
        await this.git.checkoutLocalBranch(branch);
      } else {
        await this.git.checkout(branch);
      }
      
      // Write the new code to file
      const fullPath = path.join(this.repoPath, filePath);
      await fs.writeFile(fullPath, newCode, 'utf8');
      
      // Add file to staging
      await this.git.add(filePath);
      
      // Create commit message with learning context
      const commitMessage = this.generateCommitMessage(filePath, learningContext);
      await this.git.commit(commitMessage);
      
      // Push to remote
      await this.git.push('origin', branch);
      
      console.log(`[GIT_SERVICE] ✅ Successfully applied and pushed: ${filePath}`);
      return {
        success: true,
        branch,
        commitMessage,
        filePath
      };
    } catch (error) {
      console.error(`[GIT_SERVICE] ❌ Error applying proposal: ${error.message}`);
      throw error;
    }
  }

  /**
   * Generate intelligent commit message based on learning context
   */
  generateCommitMessage(filePath, learningContext = {}) {
    const { aiType, improvementType, reasoning, sourceAI } = learningContext;
    
    let message = `AI: Improve ${path.basename(filePath)}`;
    
    if (aiType) {
      message += ` (${aiType})`;
    }
    
    if (improvementType) {
      message += ` - ${improvementType}`;
    }
    
    if (sourceAI && sourceAI !== aiType) {
      message += `\n\nLearned from ${sourceAI} AI`;
    }
    
    if (reasoning) {
      message += `\n\nReasoning: ${reasoning}`;
    }
    
    return message;
  }

  /**
   * Create learning-based branch for AI improvements
   */
  async createLearningBranch(aiType, learningType = 'general') {
    const branchName = `ai-${aiType.toLowerCase()}-${learningType}-${Date.now()}`;
    
    try {
      console.log(`[GIT_SERVICE] 🌿 Creating learning branch: ${branchName}`);
      
      await this.git.checkoutLocalBranch(branchName);
      
      return {
        success: true,
        branchName,
        message: `Created learning branch: ${branchName}`
      };
    } catch (error) {
      console.error(`[GIT_SERVICE] ❌ Error creating learning branch: ${error.message}`);
      throw error;
    }
  }

  /**
   * Apply cross-AI learning improvements
   */
  async applyCrossAILearning(sourceAI, targetAI, filePath, newCode, learningData) {
    const branchName = `cross-ai-${sourceAI.toLowerCase()}-to-${targetAI.toLowerCase()}`;
    
    try {
      console.log(`[GIT_SERVICE] 🔄 Applying cross-AI learning: ${sourceAI} → ${targetAI}`);
      
      // Create or checkout branch
      const branches = await this.git.branch();
      if (!branches.all.includes(branchName)) {
        await this.git.checkoutLocalBranch(branchName);
      } else {
        await this.git.checkout(branchName);
      }
      
      // Write the improved code
      const fullPath = path.join(this.repoPath, filePath);
      await fs.writeFile(fullPath, newCode, 'utf8');
      
      // Add and commit
      await this.git.add(filePath);
      
      const commitMessage = `Cross-AI Learning: ${sourceAI} → ${targetAI}\n\n` +
        `File: ${path.basename(filePath)}\n` +
        `Learning Type: ${learningData.learningType || 'general'}\n` +
        `Insight: ${learningData.insight || 'Knowledge transfer'}`;
      
      await this.git.commit(commitMessage);
      
      // Push to remote
      await this.git.push('origin', branchName);
      
      console.log(`[GIT_SERVICE] ✅ Cross-AI learning applied: ${sourceAI} → ${targetAI}`);
      return {
        success: true,
        branchName,
        commitMessage,
        sourceAI,
        targetAI
      };
    } catch (error) {
      console.error(`[GIT_SERVICE] ❌ Error applying cross-AI learning: ${error.message}`);
      throw error;
    }
  }

  /**
   * Apply self-improvement changes
   */
  async applySelfImprovement(aiType, filePath, newCode, improvementData) {
    const branchName = `self-improvement-${aiType.toLowerCase()}-${Date.now()}`;
    
    try {
      console.log(`[GIT_SERVICE] 🚀 Applying self-improvement for ${aiType}`);
      
      await this.git.checkoutLocalBranch(branchName);
      
      // Write the improved code
      const fullPath = path.join(this.repoPath, filePath);
      await fs.writeFile(fullPath, newCode, 'utf8');
      
      // Add and commit
      await this.git.add(filePath);
      
      const commitMessage = `Self-Improvement: ${aiType} AI\n\n` +
        `File: ${path.basename(filePath)}\n` +
        `Improvement Type: ${improvementData.improvementType || 'general'}\n` +
        `Learning Context: ${improvementData.learningContext ? 'Applied' : 'None'}`;
      
      await this.git.commit(commitMessage);
      
      // Push to remote
      await this.git.push('origin', branchName);
      
      console.log(`[GIT_SERVICE] ✅ Self-improvement applied for ${aiType}`);
      return {
        success: true,
        branchName,
        commitMessage,
        aiType
      };
    } catch (error) {
      console.error(`[GIT_SERVICE] ❌ Error applying self-improvement: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get recent AI improvements from Git history
   */
  async getRecentAIImprovements(aiType, days = 7) {
    try {
      console.log(`[GIT_SERVICE] 📊 Getting recent improvements for ${aiType}`);
      
      const since = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
      const log = await this.git.log({
        from: since.toISOString(),
        to: new Date().toISOString()
      });
      
      // Filter commits by AI type
      const aiCommits = log.all.filter(commit => 
        commit.message.includes(`(${aiType})`) || 
        commit.message.includes(`${aiType} AI`) ||
        commit.message.includes(`ai-${aiType.toLowerCase()}`)
      );
      
      return aiCommits.map(commit => ({
        hash: commit.hash,
        message: commit.message,
        date: commit.date,
        author: commit.author_name
      }));
    } catch (error) {
      console.error(`[GIT_SERVICE] ❌ Error getting recent improvements: ${error.message}`);
      return [];
    }
  }

  /**
   * Get learning statistics from Git
   */
  async getLearningStats(aiType, days = 30) {
    try {
      console.log(`[GIT_SERVICE] 📈 Getting learning stats for ${aiType}`);
      
      const since = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
      const log = await this.git.log({
        from: since.toISOString(),
        to: new Date().toISOString()
      });
      
      const aiCommits = log.all.filter(commit => 
        commit.message.includes(`(${aiType})`) || 
        commit.message.includes(`${aiType} AI`)
      );
      
      const crossAILearning = log.all.filter(commit => 
        commit.message.includes('Cross-AI Learning') &&
        (commit.message.includes(aiType) || commit.message.includes(`→ ${aiType}`))
      );
      
      const selfImprovements = log.all.filter(commit => 
        commit.message.includes('Self-Improvement') &&
        commit.message.includes(aiType)
      );
      
      return {
        totalCommits: aiCommits.length,
        crossAILearning: crossAILearning.length,
        selfImprovements: selfImprovements.length,
        averageCommitsPerDay: Math.round(aiCommits.length / days * 10) / 10,
        learningActivity: aiCommits.length > 0 ? 'active' : 'inactive'
      };
    } catch (error) {
      console.error(`[GIT_SERVICE] ❌ Error getting learning stats: ${error.message}`);
      return {
        totalCommits: 0,
        crossAILearning: 0,
        selfImprovements: 0,
        averageCommitsPerDay: 0,
        learningActivity: 'unknown'
      };
    }
  }

  /**
   * Merge learning branch to main
   */
  async mergeLearningBranch(branchName, aiType) {
    try {
      console.log(`[GIT_SERVICE] 🔀 Merging learning branch: ${branchName}`);
      
      // Switch to main branch
      await this.git.checkout('main');
      
      // Merge the learning branch
      await this.git.merge([branchName]);
      
      // Push the merge
      await this.git.push('origin', 'main');
      
      // Delete the learning branch
      await this.git.deleteLocalBranch(branchName);
      
      console.log(`[GIT_SERVICE] ✅ Successfully merged: ${branchName}`);
      return {
        success: true,
        message: `Merged ${branchName} to main`,
        aiType
      };
    } catch (error) {
      console.error(`[GIT_SERVICE] ❌ Error merging branch: ${error.message}`);
      throw error;
    }
  }

  /**
   * Get current branch status
   */
  async getBranchStatus() {
    try {
      const status = await this.git.status();
      const currentBranch = await this.git.branch();
      
      return {
        currentBranch: currentBranch.current,
        isClean: status.isClean(),
        modifiedFiles: status.modified,
        untrackedFiles: status.not_added,
        ahead: status.ahead,
        behind: status.behind
      };
    } catch (error) {
      console.error(`[GIT_SERVICE] ❌ Error getting branch status: ${error.message}`);
      return {
        currentBranch: 'unknown',
        isClean: false,
        modifiedFiles: [],
        untrackedFiles: [],
        ahead: 0,
        behind: 0
      };
    }
  }
}

// Create singleton instance
const gitService = new GitService();

// Export both the class and the singleton instance
module.exports = gitService;
module.exports.GitService = GitService;