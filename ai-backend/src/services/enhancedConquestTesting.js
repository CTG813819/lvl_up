const fs = require('fs').promises;
const path = require('path');
const { exec } = require('child_process');
const util = require('util');
const execAsync = util.promisify(exec);

/**
 * Enhanced Conquest AI Testing Service
 * Provides comprehensive app building validation and learning from failures
 */
class EnhancedConquestTesting {
  constructor() {
    this.appTestResults = [];
    this.buildingPatterns = [];
    this.failureDatabase = new Map();
    this.successPatterns = [];
  }

  /**
   * Test Conquest app building process
   */
  async testConquestAppBuilding(app, requirements) {
    console.log(`[ENHANCED_CONQUEST_TESTING] 🧪 Testing Conquest app building: ${app.name}`);
    
    const testResults = {
      appId: app.id,
      appName: app.name,
      tests: [],
      overallSuccess: true,
      learningApplied: false,
      buildQuality: 0
    };

    try {
      // Test 1: Requirements Validation
      const requirementsTest = await this.testRequirements(requirements);
      testResults.tests.push(requirementsTest);
      
      // Test 2: Code Generation Quality
      const codeQualityTest = await this.testCodeGenerationQuality(app);
      testResults.tests.push(codeQualityTest);
      
      // Test 3: Flutter Project Structure
      const structureTest = await this.testFlutterProjectStructure(app);
      testResults.tests.push(structureTest);
      
      // Test 4: Dependency Management
      const dependencyTest = await this.testDependencyManagement(app);
      testResults.tests.push(dependencyTest);
      
      // Test 5: Compilation Test
      const compilationTest = await this.testCompilation(app);
      testResults.tests.push(compilationTest);
      
      // Test 6: App Functionality
      const functionalityTest = await this.testAppFunctionality(app, requirements);
      testResults.tests.push(functionalityTest);

      // Calculate overall success and build quality
      testResults.overallSuccess = testResults.tests.every(test => test.passed);
      testResults.buildQuality = this.calculateBuildQuality(testResults.tests);
      
      // Apply learning if any test failed
      if (!testResults.overallSuccess) {
        await this.learnFromBuildingFailures(app, testResults.tests);
        testResults.learningApplied = true;
      } else {
        await this.learnFromBuildingSuccess(app, testResults.tests);
      }

      console.log(`[ENHANCED_CONQUEST_TESTING] ✅ Testing complete for ${app.name} - Success: ${testResults.overallSuccess}, Quality: ${testResults.buildQuality}%`);
      return testResults;

    } catch (error) {
      console.error(`[ENHANCED_CONQUEST_TESTING] ❌ Error testing Conquest app: ${error.message}`);
      
      // Learn from testing error
      await this.learnFromTestingError(app, error);
      
      return {
        ...testResults,
        overallSuccess: false,
        error: error.message,
        learningApplied: true
      };
    }
  }

  /**
   * Test requirements validation
   */
  async testRequirements(requirements) {
    const test = {
      name: 'Requirements Validation',
      passed: false,
      details: '',
      errorType: null
    };

    try {
      // Check if requirements are complete
      if (!requirements.name || !requirements.description) {
        test.passed = false;
        test.details = 'Missing required fields: name and description';
        test.errorType = 'incomplete_requirements';
        return test;
      }

      // Check if keywords are provided
      if (!requirements.keywords || requirements.keywords.length === 0) {
        test.passed = false;
        test.details = 'No keywords provided for app development';
        test.errorType = 'missing_keywords';
        return test;
      }

      // Check if platform is specified
      if (!requirements.platform) {
        test.passed = false;
        test.details = 'Platform not specified for app development';
        test.errorType = 'missing_platform';
        return test;
      }

      test.passed = true;
      test.details = 'Requirements validation passed';
      return test;

    } catch (error) {
      test.passed = false;
      test.details = `Requirements test error: ${error.message}`;
      test.errorType = 'requirements_test_error';
      return test;
    }
  }

  /**
   * Test code generation quality
   */
  async testCodeGenerationQuality(app) {
    const test = {
      name: 'Code Generation Quality',
      passed: false,
      details: '',
      errorType: null
    };

    try {
      const appPath = path.join(process.cwd(), 'conquest_apps', app.id);
      
      // Check if app directory exists
      const appExists = await fs.access(appPath).then(() => true).catch(() => false);
      
      if (!appExists) {
        test.passed = false;
        test.details = 'App directory not found';
        test.errorType = 'app_directory_not_found';
        return test;
      }

      // Check for main.dart file
      const mainDartPath = path.join(appPath, 'lib', 'main.dart');
      const mainDartExists = await fs.access(mainDartPath).then(() => true).catch(() => false);
      
      if (!mainDartExists) {
        test.passed = false;
        test.details = 'main.dart file not found';
        test.errorType = 'main_dart_missing';
        return test;
      }

      // Check for pubspec.yaml
      const pubspecPath = path.join(appPath, 'pubspec.yaml');
      const pubspecExists = await fs.access(pubspecPath).then(() => true).catch(() => false);
      
      if (!pubspecExists) {
        test.passed = false;
        test.details = 'pubspec.yaml file not found';
        test.errorType = 'pubspec_missing';
        return test;
      }

      // Analyze code quality
      const mainDartContent = await fs.readFile(mainDartPath, 'utf8');
      const codeQuality = this.analyzeCodeQuality(mainDartContent);
      
      if (codeQuality.score < 0.7) {
        test.passed = false;
        test.details = `Low code quality score: ${(codeQuality.score * 100).toFixed(1)}%`;
        test.errorType = 'low_code_quality';
        return test;
      }

      test.passed = true;
      test.details = `Code quality score: ${(codeQuality.score * 100).toFixed(1)}%`;
      return test;

    } catch (error) {
      test.passed = false;
      test.details = `Code quality test error: ${error.message}`;
      test.errorType = 'code_quality_test_error';
      return test;
    }
  }

  /**
   * Test Flutter project structure
   */
  async testFlutterProjectStructure(app) {
    const test = {
      name: 'Flutter Project Structure',
      passed: false,
      details: '',
      errorType: null
    };

    try {
      const appPath = path.join(process.cwd(), 'conquest_apps', app.id);
      
      // Check required directories
      const requiredDirs = ['lib', 'android', 'ios', 'web'];
      const missingDirs = [];
      
      for (const dir of requiredDirs) {
        const dirPath = path.join(appPath, dir);
        const exists = await fs.access(dirPath).then(() => true).catch(() => false);
        if (!exists) {
          missingDirs.push(dir);
        }
      }
      
      if (missingDirs.length > 0) {
        test.passed = false;
        test.details = `Missing required directories: ${missingDirs.join(', ')}`;
        test.errorType = 'missing_directories';
        return test;
      }

      // Check for essential files
      const essentialFiles = [
        'lib/main.dart',
        'pubspec.yaml',
        'android/app/build.gradle',
        'ios/Runner/Info.plist'
      ];
      
      const missingFiles = [];
      for (const file of essentialFiles) {
        const filePath = path.join(appPath, file);
        const exists = await fs.access(filePath).then(() => true).catch(() => false);
        if (!exists) {
          missingFiles.push(file);
        }
      }
      
      if (missingFiles.length > 0) {
        test.passed = false;
        test.details = `Missing essential files: ${missingFiles.join(', ')}`;
        test.errorType = 'missing_essential_files';
        return test;
      }

      test.passed = true;
      test.details = 'Flutter project structure is valid';
      return test;

    } catch (error) {
      test.passed = false;
      test.details = `Project structure test error: ${error.message}`;
      test.errorType = 'project_structure_test_error';
      return test;
    }
  }

  /**
   * Test dependency management
   */
  async testDependencyManagement(app) {
    const test = {
      name: 'Dependency Management',
      passed: false,
      details: '',
      errorType: null
    };

    try {
      const appPath = path.join(process.cwd(), 'conquest_apps', app.id);
      const pubspecPath = path.join(appPath, 'pubspec.yaml');
      
      const pubspecContent = await fs.readFile(pubspecPath, 'utf8');
      const dependencies = this.parsePubspecDependencies(pubspecContent);
      
      // Check for required Flutter dependencies
      const requiredDeps = ['flutter'];
      const missingDeps = requiredDeps.filter(dep => !dependencies.includes(dep));
      
      if (missingDeps.length > 0) {
        test.passed = false;
        test.details = `Missing required dependencies: ${missingDeps.join(', ')}`;
        test.errorType = 'missing_required_dependencies';
        return test;
      }

      // Check for dependency conflicts
      const conflicts = this.checkDependencyConflicts(dependencies);
      
      if (conflicts.length > 0) {
        test.passed = false;
        test.details = `Dependency conflicts detected: ${conflicts.join(', ')}`;
        test.errorType = 'dependency_conflicts';
        return test;
      }

      test.passed = true;
      test.details = `Dependencies valid (${dependencies.length} packages)`;
      return test;

    } catch (error) {
      test.passed = false;
      test.details = `Dependency test error: ${error.message}`;
      test.errorType = 'dependency_test_error';
      return test;
    }
  }

  /**
   * Test compilation
   */
  async testCompilation(app) {
    const test = {
      name: 'Compilation Test',
      passed: false,
      details: '',
      errorType: null
    };

    try {
      const appPath = path.join(process.cwd(), 'conquest_apps', app.id);
      
      // Run flutter pub get
      try {
        await execAsync('flutter pub get', { cwd: appPath, timeout: 60000 });
      } catch (error) {
        test.passed = false;
        test.details = `Dependency resolution failed: ${error.message}`;
        test.errorType = 'dependency_resolution_failed';
        return test;
      }

      // Run flutter analyze
      try {
        await execAsync('flutter analyze', { cwd: appPath, timeout: 60000 });
      } catch (error) {
        test.passed = false;
        test.details = `Code analysis failed: ${error.message}`;
        test.errorType = 'code_analysis_failed';
        return test;
      }

      // Run flutter build (dry run)
      try {
        await execAsync('flutter build apk --debug', { cwd: appPath, timeout: 120000 });
      } catch (error) {
        test.passed = false;
        test.details = `Build failed: ${error.message}`;
        test.errorType = 'build_failed';
        return test;
      }

      test.passed = true;
      test.details = 'App compiles and builds successfully';
      return test;

    } catch (error) {
      test.passed = false;
      test.details = `Compilation test error: ${error.message}`;
      test.errorType = 'compilation_test_error';
      return test;
    }
  }

  /**
   * Test app functionality
   */
  async testAppFunctionality(app, requirements) {
    const test = {
      name: 'App Functionality',
      passed: false,
      details: '',
      errorType: null
    };

    try {
      const appPath = path.join(process.cwd(), 'conquest_apps', app.id);
      const mainDartPath = path.join(appPath, 'lib', 'main.dart');
      
      const mainDartContent = await fs.readFile(mainDartPath, 'utf8');
      
      // Check if app implements required features
      const requiredFeatures = requirements.keywords || [];
      const implementedFeatures = this.checkImplementedFeatures(mainDartContent, requiredFeatures);
      
      if (implementedFeatures.missing.length > 0) {
        test.passed = false;
        test.details = `Missing required features: ${implementedFeatures.missing.join(', ')}`;
        test.errorType = 'missing_features';
        return test;
      }

      // Check for basic app structure
      if (!mainDartContent.includes('runApp') || !mainDartContent.includes('MaterialApp')) {
        test.passed = false;
        test.details = 'App does not have proper Flutter app structure';
        test.errorType = 'invalid_app_structure';
        return test;
      }

      test.passed = true;
      test.details = `App implements ${implementedFeatures.implemented.length}/${requiredFeatures.length} required features`;
      return test;

    } catch (error) {
      test.passed = false;
      test.details = `Functionality test error: ${error.message}`;
      test.errorType = 'functionality_test_error';
      return test;
    }
  }

  /**
   * Learn from building failures
   */
  async learnFromBuildingFailures(app, failedTests) {
    console.log(`[ENHANCED_CONQUEST_TESTING] 📚 Learning from ${failedTests.length} building failures`);
    
    for (const test of failedTests) {
      if (!test.passed) {
        const learningPattern = {
          appId: app.id,
          appName: app.name,
          errorType: test.errorType,
          errorDetails: test.details,
          timestamp: new Date(),
          testName: test.name
        };

        // Store learning pattern
        this.buildingPatterns.push(learningPattern);
        
        // Update failure database
        const key = `conquest_${test.errorType}`;
        if (!this.failureDatabase.has(key)) {
          this.failureDatabase.set(key, []);
        }
        this.failureDatabase.get(key).push(learningPattern);
        
        console.log(`[ENHANCED_CONQUEST_TESTING] 📚 Learned building pattern: ${test.errorType}`);
      }
    }
  }

  /**
   * Learn from building success
   */
  async learnFromBuildingSuccess(app, successfulTests) {
    console.log(`[ENHANCED_CONQUEST_TESTING] 📚 Learning from building success`);
    
    const successPattern = {
      appId: app.id,
      appName: app.name,
      successType: 'building_success',
      timestamp: new Date(),
      qualityScore: this.calculateBuildQuality(successfulTests),
      implementedFeatures: successfulTests.find(t => t.name === 'App Functionality')?.details || 'Unknown'
    };

    this.successPatterns.push(successPattern);
    console.log(`[ENHANCED_CONQUEST_TESTING] 📚 Learned success pattern for ${app.name}`);
  }

  /**
   * Learn from testing errors
   */
  async learnFromTestingError(app, error) {
    const learningPattern = {
      appId: app.id,
      appName: app.name,
      errorType: 'testing_system_error',
      errorDetails: error.message,
      timestamp: new Date()
    };

    this.buildingPatterns.push(learningPattern);
    console.log(`[ENHANCED_CONQUEST_TESTING] 📚 Learned from testing error: ${error.message}`);
  }

  /**
   * Get building patterns for Conquest AI
   */
  getBuildingPatterns(errorType = null) {
    if (errorType) {
      return this.buildingPatterns.filter(pattern => pattern.errorType === errorType);
    }
    return this.buildingPatterns;
  }

  /**
   * Get success patterns for Conquest AI
   */
  getSuccessPatterns() {
    return this.successPatterns;
  }

  /**
   * Get failure frequency for Conquest AI
   */
  getFailureFrequency() {
    const frequency = {};
    
    this.buildingPatterns.forEach(pattern => {
      frequency[pattern.errorType] = (frequency[pattern.errorType] || 0) + 1;
    });
    
    return frequency;
  }

  /**
   * Helper methods
   */
  calculateBuildQuality(tests) {
    const passedTests = tests.filter(test => test.passed).length;
    const totalTests = tests.length;
    return totalTests > 0 ? (passedTests / totalTests) * 100 : 0;
  }

  analyzeCodeQuality(code) {
    const quality = {
      score: 0,
      issues: []
    };

    // Check for proper imports
    if (code.includes('import \'package:flutter/material.dart\';')) {
      quality.score += 0.2;
    } else {
      quality.issues.push('missing_flutter_import');
    }

    // Check for proper app structure
    if (code.includes('runApp') && code.includes('MaterialApp')) {
      quality.score += 0.3;
    } else {
      quality.issues.push('invalid_app_structure');
    }

    // Check for proper widget structure
    if (code.includes('class') && code.includes('extends StatelessWidget')) {
      quality.score += 0.2;
    } else if (code.includes('class') && code.includes('extends StatefulWidget')) {
      quality.score += 0.2;
    } else {
      quality.issues.push('missing_widget_structure');
    }

    // Check for proper build method
    if (code.includes('Widget build(BuildContext context)')) {
      quality.score += 0.2;
    } else {
      quality.issues.push('missing_build_method');
    }

    // Check for proper return statement
    if (code.includes('return') && code.includes('Scaffold')) {
      quality.score += 0.1;
    } else {
      quality.issues.push('missing_scaffold');
    }

    return quality;
  }

  parsePubspecDependencies(pubspecContent) {
    const dependencies = [];
    const lines = pubspecContent.split('\n');
    let inDependencies = false;
    
    for (const line of lines) {
      if (line.trim() === 'dependencies:') {
        inDependencies = true;
        continue;
      }
      
      if (inDependencies && line.trim().startsWith('  ')) {
        const dep = line.trim().split(':')[0];
        dependencies.push(dep);
      } else if (inDependencies && line.trim() !== '' && !line.trim().startsWith('  ')) {
        break;
      }
    }
    
    return dependencies;
  }

  checkDependencyConflicts(dependencies) {
    const conflicts = [];
    
    // Check for known conflicting packages
    const knownConflicts = [
      ['provider', 'riverpod'],
      ['bloc', 'riverpod'],
      ['get_it', 'riverpod']
    ];
    
    for (const [dep1, dep2] of knownConflicts) {
      if (dependencies.includes(dep1) && dependencies.includes(dep2)) {
        conflicts.push(`${dep1} vs ${dep2}`);
      }
    }
    
    return conflicts;
  }

  checkImplementedFeatures(code, requiredFeatures) {
    const implemented = [];
    const missing = [];
    
    const featurePatterns = {
      'ui': ['Scaffold', 'AppBar', 'Container', 'Column', 'Row'],
      'widgets': ['StatelessWidget', 'StatefulWidget', 'CustomWidget'],
      'state-management': ['Provider', 'Bloc', 'Riverpod', 'setState'],
      'navigation': ['Navigator', 'push', 'pop', 'routes'],
      'authentication': ['auth', 'login', 'signup', 'firebase_auth'],
      'database': ['database', 'sqlite', 'firebase_firestore', 'shared_preferences'],
      'network': ['http', 'dio', 'api', 'network'],
      'storage': ['storage', 'file', 'cache', 'shared_preferences']
    };
    
    for (const feature of requiredFeatures) {
      const patterns = featurePatterns[feature.toLowerCase()] || [];
      const isImplemented = patterns.some(pattern => 
        code.includes(pattern)
      );
      
      if (isImplemented) {
        implemented.push(feature);
      } else {
        missing.push(feature);
      }
    }
    
    return { implemented, missing };
  }
}

module.exports = { EnhancedConquestTesting }; 