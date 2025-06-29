const { exec } = require('child_process');
const fs = require('fs').promises;
const path = require('path');
const gitService = require('./gitService');
const Proposal = require('../models/proposal');

class APKBuildService {
  constructor() {
    this.projectPath = process.env.GIT_REPO_PATH || '.';
    this.buildPath = path.join(this.projectPath, 'build');
    this.apkOutputPath = path.join(this.buildPath, 'app', 'outputs', 'flutter-apk');
  }

  /**
   * Build APK after successful proposal
   */
  async buildAPKAfterProposal(proposalId) {
    try {
      console.log(`[APK_BUILD_SERVICE] 🏗️ Building APK after successful proposal: ${proposalId}`);
      
      const proposal = await Proposal.findById(proposalId);
      if (!proposal) {
        throw new Error(`Proposal ${proposalId} not found`);
      }

      // Check if proposal is approved and tests passed
      if (proposal.status !== 'approved' && proposal.status !== 'test-passed') {
        console.log(`[APK_BUILD_SERVICE] ⏭️ Skipping APK build - proposal status: ${proposal.status}`);
        return { success: false, reason: 'Proposal not approved' };
      }

      // Build APK
      const buildResult = await this.buildAPK();
      
      if (buildResult.success) {
        // Commit and push the built APK
        await this.commitAndPushAPK(proposal);
        
        // Update proposal with APK build info
        await this.updateProposalWithAPKInfo(proposalId, buildResult);
        
        console.log(`[APK_BUILD_SERVICE] ✅ APK built and committed successfully for proposal: ${proposalId}`);
        return buildResult;
      } else {
        console.error(`[APK_BUILD_SERVICE] ❌ APK build failed for proposal: ${proposalId}`);
        return buildResult;
      }
    } catch (error) {
      console.error(`[APK_BUILD_SERVICE] ❌ Error building APK: ${error.message}`);
      throw error;
    }
  }

  /**
   * Build APK using Flutter
   */
  async buildAPK() {
    return new Promise((resolve) => {
      console.log(`[APK_BUILD_SERVICE] 🔨 Starting APK build in ${this.projectPath}`);
      
      // Clean previous builds
      exec('flutter clean', { cwd: this.projectPath }, (cleanError) => {
        if (cleanError) {
          console.warn(`[APK_BUILD_SERVICE] ⚠️ Clean warning: ${cleanError.message}`);
        }
        
        // Get dependencies
        exec('flutter pub get', { cwd: this.projectPath }, (pubError) => {
          if (pubError) {
            console.error(`[APK_BUILD_SERVICE] ❌ Pub get failed: ${pubError.message}`);
            return resolve({ success: false, error: pubError.message });
          }
          
          // Build APK
          exec('flutter build apk --release', { cwd: this.projectPath }, (buildError, stdout, stderr) => {
            if (buildError) {
              console.error(`[APK_BUILD_SERVICE] ❌ APK build failed: ${buildError.message}`);
              console.error(`[APK_BUILD_SERVICE] Build stderr: ${stderr}`);
              return resolve({ success: false, error: buildError.message, stderr });
            }
            
            console.log(`[APK_BUILD_SERVICE] 📱 APK build output: ${stdout}`);
            
            // Check if APK was created
            this.checkAPKExists().then(apkInfo => {
              if (apkInfo.exists) {
                resolve({
                  success: true,
                  apkPath: apkInfo.path,
                  apkSize: apkInfo.size,
                  buildTime: new Date().toISOString(),
                  message: 'APK built successfully'
                });
              } else {
                resolve({ success: false, error: 'APK file not found after build' });
              }
            });
          });
        });
      });
    });
  }

  /**
   * Check if APK was created successfully
   */
  async checkAPKExists() {
    try {
      const files = await fs.readdir(this.apkOutputPath);
      const apkFile = files.find(file => file.endsWith('.apk'));
      
      if (apkFile) {
        const apkPath = path.join(this.apkOutputPath, apkFile);
        const stats = await fs.stat(apkPath);
        
        return {
          exists: true,
          path: apkPath,
          size: stats.size,
          filename: apkFile
        };
      }
      
      return { exists: false };
    } catch (error) {
      console.error(`[APK_BUILD_SERVICE] ❌ Error checking APK: ${error.message}`);
      return { exists: false, error: error.message };
    }
  }

  /**
   * Commit and push APK to Git
   */
  async commitAndPushAPK(proposal) {
    try {
      console.log(`[APK_BUILD_SERVICE] 🔄 Committing APK to Git for proposal: ${proposal._id}`);
      
      // Add APK to Git
      const apkInfo = await this.checkAPKExists();
      if (!apkInfo.exists) {
        throw new Error('APK not found for commit');
      }
      
      // Create APK branch
      const branchName = `apk-build-${proposal._id}-${Date.now()}`;
      
      // Switch to new branch
      await gitService.git.checkoutLocalBranch(branchName);
      
      // Add APK file
      await gitService.git.add(apkInfo.path);
      
      // Commit with proposal context
      const commitMessage = `APK Build: ${proposal.aiType} - ${proposal.filePath}\n\n` +
        `Proposal ID: ${proposal._id}\n` +
        `AI Type: ${proposal.aiType}\n` +
        `File: ${proposal.filePath}\n` +
        `Improvement: ${proposal.improvementType}\n` +
        `Status: ${proposal.status}\n` +
        `APK Size: ${(apkInfo.size / 1024 / 1024).toFixed(2)} MB\n` +
        `Build Time: ${new Date().toISOString()}`;
      
      await gitService.git.commit(commitMessage);
      
      // Push to remote
      await gitService.git.push('origin', branchName);
      
      // Merge to main if tests passed
      if (proposal.status === 'test-passed' || proposal.status === 'approved') {
        await this.mergeToMain(branchName, proposal);
      }
      
      console.log(`[APK_BUILD_SERVICE] ✅ APK committed to branch: ${branchName}`);
      
      return {
        success: true,
        branchName,
        commitMessage,
        apkInfo
      };
    } catch (error) {
      console.error(`[APK_BUILD_SERVICE] ❌ Error committing APK: ${error.message}`);
      throw error;
    }
  }

  /**
   * Merge APK branch to main
   */
  async mergeToMain(branchName, proposal) {
    try {
      console.log(`[APK_BUILD_SERVICE] 🔀 Merging APK branch to main: ${branchName}`);
      
      // Switch to main branch
      await gitService.git.checkout('main');
      
      // Pull latest changes
      await gitService.git.pull('origin', 'main');
      
      // Merge the APK branch
      await gitService.git.merge([branchName]);
      
      // Push to main
      await gitService.git.push('origin', 'main');
      
      // Delete the APK branch
      await gitService.git.deleteLocalBranch(branchName);
      
      console.log(`[APK_BUILD_SERVICE] ✅ APK branch merged to main: ${branchName}`);
      
      // Trigger deployment if configured
      await this.triggerDeployment(proposal);
      
    } catch (error) {
      console.error(`[APK_BUILD_SERVICE] ❌ Error merging to main: ${error.message}`);
      throw error;
    }
  }

  /**
   * Trigger deployment after successful merge
   */
  async triggerDeployment(proposal) {
    try {
      console.log(`[APK_BUILD_SERVICE] 🚀 Triggering deployment for proposal: ${proposal._id}`);
      
      // Check if deployment is configured
      if (process.env.DEPLOYMENT_ENABLED === 'true') {
        // Trigger deployment script
        exec('./deploy.sh', { cwd: this.projectPath }, (error, stdout, stderr) => {
          if (error) {
            console.error(`[APK_BUILD_SERVICE] ❌ Deployment failed: ${error.message}`);
          } else {
            console.log(`[APK_BUILD_SERVICE] ✅ Deployment triggered: ${stdout}`);
          }
        });
      } else {
        console.log(`[APK_BUILD_SERVICE] ⏭️ Deployment disabled - set DEPLOYMENT_ENABLED=true to enable`);
      }
    } catch (error) {
      console.error(`[APK_BUILD_SERVICE] ❌ Error triggering deployment: ${error.message}`);
    }
  }

  /**
   * Update proposal with APK build information
   */
  async updateProposalWithAPKInfo(proposalId, buildResult) {
    try {
      const apkInfo = await this.checkAPKExists();
      
      await Proposal.findByIdAndUpdate(proposalId, {
        apkBuildInfo: {
          success: buildResult.success,
          apkPath: apkInfo.path,
          apkSize: apkInfo.size,
          buildTime: buildResult.buildTime,
          branchName: buildResult.branchName,
          mergedToMain: buildResult.success
        },
        status: buildResult.success ? 'apk-built' : 'apk-build-failed'
      });
      
      console.log(`[APK_BUILD_SERVICE] ✅ Proposal updated with APK info: ${proposalId}`);
    } catch (error) {
      console.error(`[APK_BUILD_SERVICE] ❌ Error updating proposal: ${error.message}`);
    }
  }

  /**
   * Get APK build history
   */
  async getAPKBuildHistory(days = 7) {
    try {
      const cutoffDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
      
      const proposals = await Proposal.find({
        'apkBuildInfo.success': true,
        'apkBuildInfo.buildTime': { $gte: cutoffDate }
      })
      .sort({ 'apkBuildInfo.buildTime': -1 })
      .select('aiType filePath improvementType apkBuildInfo status createdAt')
      .lean();
      
      return {
        totalBuilds: proposals.length,
        successfulBuilds: proposals.filter(p => p.apkBuildInfo.success).length,
        failedBuilds: proposals.filter(p => !p.apkBuildInfo.success).length,
        recentBuilds: proposals.slice(0, 10),
        averageAPKSize: proposals.length > 0 ? 
          proposals.reduce((sum, p) => sum + (p.apkBuildInfo.apkSize || 0), 0) / proposals.length : 0
      };
    } catch (error) {
      console.error(`[APK_BUILD_SERVICE] ❌ Error getting build history: ${error.message}`);
      return { totalBuilds: 0, successfulBuilds: 0, failedBuilds: 0, recentBuilds: [], averageAPKSize: 0 };
    }
  }

  /**
   * Clean old APK builds
   */
  async cleanOldAPKBuilds() {
    try {
      console.log(`[APK_BUILD_SERVICE] 🧹 Cleaning old APK builds`);
      
      // Remove build directory
      await fs.rm(this.buildPath, { recursive: true, force: true });
      
      // Clean Flutter
      exec('flutter clean', { cwd: this.projectPath }, (error) => {
        if (error) {
          console.warn(`[APK_BUILD_SERVICE] ⚠️ Clean warning: ${error.message}`);
        } else {
          console.log(`[APK_BUILD_SERVICE] ✅ Old builds cleaned`);
        }
      });
    } catch (error) {
      console.error(`[APK_BUILD_SERVICE] ❌ Error cleaning builds: ${error.message}`);
    }
  }

  /**
   * Get current APK status
   */
  async getCurrentAPKStatus() {
    try {
      const apkInfo = await this.checkAPKExists();
      
      if (apkInfo.exists) {
        const stats = await fs.stat(apkInfo.path);
        return {
          exists: true,
          path: apkInfo.path,
          size: apkInfo.size,
          filename: apkInfo.filename,
          lastModified: stats.mtime,
          ageInHours: Math.round((Date.now() - stats.mtime.getTime()) / (1000 * 60 * 60))
        };
      }
      
      return { exists: false };
    } catch (error) {
      console.error(`[APK_BUILD_SERVICE] ❌ Error getting APK status: ${error.message}`);
      return { exists: false, error: error.message };
    }
  }
}

module.exports = new APKBuildService(); 