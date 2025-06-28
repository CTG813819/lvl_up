const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const util = require('util');

const execAsync = util.promisify(exec);

/**
 * Build Service
 * Handles building deployable apps after AI improvements are approved
 */
class BuildService {
  constructor() {
    this.buildHistory = new Map();
  }

  /**
   * Build app after AI improvements are approved
   */
  async buildApp(aiType, updates) {
    console.log(`[BUILD] 🏗️ Building app for ${aiType} with ${updates.length} improvements`);
    
    const buildId = `build-${Date.now()}`;
    const buildStart = new Date();
    
    try {
      // Create build record
      const buildRecord = {
        id: buildId,
        aiType,
        updates,
        status: 'building',
        startTime: buildStart,
        steps: []
      };
      
      this.buildHistory.set(buildId, buildRecord);
      
      // Step 1: Validate code changes
      console.log(`[BUILD] 🔍 Step 1: Validating code changes`);
      await this.addBuildStep(buildId, 'validation', 'Validating code changes');
      
      const validationResult = await this.validateCodeChanges(aiType, updates);
      if (!validationResult.success) {
        throw new Error(`Code validation failed: ${validationResult.error}`);
      }
      
      // Step 2: Run tests
      console.log(`[BUILD] 🧪 Step 2: Running tests`);
      await this.addBuildStep(buildId, 'testing', 'Running automated tests');
      
      const testResult = await this.runTests(aiType);
      if (!testResult.success) {
        throw new Error(`Tests failed: ${testResult.error}`);
      }
      
      // Step 3: Build the application
      console.log(`[BUILD] 🔨 Step 3: Building application`);
      await this.addBuildStep(buildId, 'compilation', 'Building application');
      
      const buildResult = await this.compileApp(aiType);
      if (!buildResult.success) {
        throw new Error(`Build failed: ${buildResult.error}`);
      }
      
      // Step 4: Create deployment package
      console.log(`[BUILD] 📦 Step 4: Creating deployment package`);
      await this.addBuildStep(buildId, 'packaging', 'Creating deployment package');
      
      const packageResult = await this.createDeploymentPackage(aiType, buildResult);
      if (!packageResult.success) {
        throw new Error(`Packaging failed: ${packageResult.error}`);
      }
      
      // Step 5: Generate build report
      console.log(`[BUILD] 📊 Step 5: Generating build report`);
      await this.addBuildStep(buildId, 'reporting', 'Generating build report');
      
      const buildEnd = new Date();
      const buildDuration = buildEnd - buildStart;
      
      const finalBuildRecord = {
        ...buildRecord,
        status: 'completed',
        endTime: buildEnd,
        duration: buildDuration,
        result: {
          success: true,
          buildId,
          aiType,
          improvements: updates.length,
          testResults: testResult,
          buildOutput: buildResult,
          packagePath: packageResult.packagePath,
          deploymentReady: true
        }
      };
      
      this.buildHistory.set(buildId, finalBuildRecord);
      
      console.log(`[BUILD] 🎉 Build completed successfully in ${buildDuration}ms`);
      console.log(`[BUILD] 📦 Deployment package: ${packageResult.packagePath}`);
      
      return finalBuildRecord.result;
      
    } catch (error) {
      const buildEnd = new Date();
      const buildDuration = buildEnd - buildStart;
      
      const failedBuildRecord = {
        id: buildId,
        aiType,
        updates,
        status: 'failed',
        startTime: buildStart,
        endTime: buildEnd,
        duration: buildDuration,
        error: error.message
      };
      
      this.buildHistory.set(buildId, failedBuildRecord);
      
      console.error(`[BUILD] ❌ Build failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Validate code changes
   */
  async validateCodeChanges(aiType, updates) {
    try {
      // Check if AI service file exists and is valid
      const aiFilePath = path.join(process.cwd(), 'temp-repo', 'src', 'services', `${aiType.toLowerCase()}Service.js`);
      
      if (!fs.existsSync(aiFilePath)) {
        return { success: false, error: 'AI service file not found' };
      }
      
      // Basic syntax validation
      const content = fs.readFileSync(aiFilePath, 'utf8');
      
      // Check for basic JavaScript syntax
      if (!content.includes('module.exports') && !content.includes('export')) {
        return { success: false, error: 'Invalid module export' };
      }
      
      // Check for required functions
      if (!content.includes('processRequest') || !content.includes('initialize')) {
        return { success: false, error: 'Missing required functions' };
      }
      
      return { success: true, message: 'Code validation passed' };
      
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Run tests
   */
  async runTests(aiType) {
    try {
      // Check if test files exist
      const testPath = path.join(process.cwd(), 'temp-repo', 'test');
      
      if (!fs.existsSync(testPath)) {
        console.log(`[BUILD] ⚠️ No test directory found, skipping tests`);
        return { success: true, message: 'No tests to run', skipped: true };
      }
      
      // Run npm test if package.json exists
      const packagePath = path.join(process.cwd(), 'temp-repo', 'package.json');
      
      if (fs.existsSync(packagePath)) {
        console.log(`[BUILD] 🧪 Running npm test`);
        
        const { stdout, stderr } = await execAsync('npm test', {
          cwd: path.join(process.cwd(), 'temp-repo'),
          timeout: 60000 // 60 second timeout
        });
        
        return {
          success: true,
          message: 'Tests passed',
          output: stdout,
          errors: stderr
        };
      }
      
      return { success: true, message: 'No test script found, skipping tests' };
      
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Compile the application
   */
  async compileApp(aiType) {
    try {
      const repoPath = path.join(process.cwd(), 'temp-repo');
      
      // Check if it's a Flutter app
      const pubspecPath = path.join(repoPath, 'pubspec.yaml');
      if (fs.existsSync(pubspecPath)) {
        console.log(`[BUILD] 🔨 Building Flutter app`);
        
        // Run flutter build
        const { stdout, stderr } = await execAsync('flutter build apk --release', {
          cwd: repoPath,
          timeout: 300000 // 5 minute timeout
        });
        
        return {
          success: true,
          message: 'Flutter app built successfully',
          output: stdout,
          errors: stderr,
          buildType: 'flutter'
        };
      }
      
      // Check if it's a Node.js app
      const packagePath = path.join(repoPath, 'package.json');
      if (fs.existsSync(packagePath)) {
        console.log(`[BUILD] 🔨 Building Node.js app`);
        
        // Run npm build if script exists
        const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
        
        if (packageJson.scripts && packageJson.scripts.build) {
          const { stdout, stderr } = await execAsync('npm run build', {
            cwd: repoPath,
            timeout: 120000 // 2 minute timeout
          });
          
          return {
            success: true,
            message: 'Node.js app built successfully',
            output: stdout,
            errors: stderr,
            buildType: 'nodejs'
          };
        }
        
        return {
          success: true,
          message: 'No build script found, skipping build',
          buildType: 'nodejs'
        };
      }
      
      return {
        success: true,
        message: 'No build configuration found',
        buildType: 'unknown'
      };
      
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Create deployment package
   */
  async createDeploymentPackage(aiType, buildResult) {
    try {
      const repoPath = path.join(process.cwd(), 'temp-repo');
      const packageDir = path.join(process.cwd(), 'builds');
      
      // Create builds directory if it doesn't exist
      if (!fs.existsSync(packageDir)) {
        fs.mkdirSync(packageDir, { recursive: true });
      }
      
      const packageName = `${aiType}-build-${Date.now()}`;
      const packagePath = path.join(packageDir, packageName);
      
      // Copy built files to package directory
      if (buildResult.buildType === 'flutter') {
        // Copy APK file
        const apkPath = path.join(repoPath, 'build', 'app', 'outputs', 'flutter-apk', 'app-release.apk');
        if (fs.existsSync(apkPath)) {
          fs.copyFileSync(apkPath, `${packagePath}.apk`);
          return {
            success: true,
            packagePath: `${packagePath}.apk`,
            type: 'apk'
          };
        }
      }
      
      // For other types, create a zip of the build
      const { stdout } = await execAsync(`powershell Compress-Archive -Path "${repoPath}" -DestinationPath "${packagePath}.zip" -Force`);
      
      return {
        success: true,
        packagePath: `${packagePath}.zip`,
        type: 'zip'
      };
      
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Add build step
   */
  async addBuildStep(buildId, step, description) {
    const buildRecord = this.buildHistory.get(buildId);
    if (buildRecord) {
      buildRecord.steps.push({
        step,
        description,
        timestamp: new Date()
      });
    }
  }

  /**
   * Get build history
   */
  async getBuildHistory() {
    return Array.from(this.buildHistory.values());
  }

  /**
   * Get build details
   */
  async getBuildDetails(buildId) {
    return this.buildHistory.get(buildId);
  }
}

module.exports = new BuildService(); 