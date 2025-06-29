const fs = require('fs').promises;
const path = require('path');
const { exec } = require('child_process');
const util = require('util');
const execAsync = util.promisify(exec);

/**
 * Enhanced Proposal Testing Service
 * Provides comprehensive testing against current app structure
 * and advanced learning from failures
 */
class EnhancedProposalTesting {
  constructor() {
    this.testResults = [];
    this.learningPatterns = [];
    this.failureDatabase = new Map();
  }

  /**
   * Test proposal against current app structure
   */
  async testProposalAgainstAppStructure(proposal) {
    console.log(`[ENHANCED_TESTING] 🧪 Testing proposal ${proposal._id} against app structure`);
    
    const testResults = {
      proposalId: proposal._id,
      aiType: proposal.aiType,
      filePath: proposal.filePath,
      tests: [],
      overallSuccess: true,
      learningApplied: false
    };

    try {
      // Test 1: File Structure Validation
      const structureTest = await this.testFileStructure(proposal);
      testResults.tests.push(structureTest);
      
      // Test 2: Code Compilation Test
      const compilationTest = await this.testCodeCompilation(proposal);
      testResults.tests.push(compilationTest);
      
      // Test 3: Dependency Compatibility
      const dependencyTest = await this.testDependencyCompatibility(proposal);
      testResults.tests.push(dependencyTest);
      
      // Test 4: App Integration Test
      const integrationTest = await this.testAppIntegration(proposal);
      testResults.tests.push(integrationTest);
      
      // Test 5: Performance Impact Test
      const performanceTest = await this.testPerformanceImpact(proposal);
      testResults.tests.push(performanceTest);

      // Determine overall success
      testResults.overallSuccess = testResults.tests.every(test => test.passed);
      
      // Apply learning if any test failed
      if (!testResults.overallSuccess) {
        await this.learnFromTestFailures(proposal, testResults.tests);
        testResults.learningApplied = true;
      }

      console.log(`[ENHANCED_TESTING] ✅ Testing complete for ${proposal.aiType} - Success: ${testResults.overallSuccess}`);
      return testResults;

    } catch (error) {
      console.error(`[ENHANCED_TESTING] ❌ Error testing proposal: ${error.message}`);
      
      // Learn from testing error
      await this.learnFromTestingError(proposal, error);
      
      return {
        ...testResults,
        overallSuccess: false,
        error: error.message,
        learningApplied: true
      };
    }
  }

  /**
   * Test file structure compatibility
   */
  async testFileStructure(proposal) {
    const test = {
      name: 'File Structure Validation',
      passed: false,
      details: '',
      errorType: null
    };

    try {
      const filePath = proposal.filePath;
      const fullPath = path.join(process.cwd(), 'temp-repo', filePath);
      
      // Check if file exists
      const fileExists = await fs.access(fullPath).then(() => true).catch(() => false);
      
      if (!fileExists) {
        test.passed = false;
        test.details = `File not found: ${filePath}`;
        test.errorType = 'file_not_found';
        return test;
      }

      // Check file permissions
      const stats = await fs.stat(fullPath);
      if (!stats.isFile()) {
        test.passed = false;
        test.details = `Path is not a file: ${filePath}`;
        test.errorType = 'not_a_file';
        return test;
      }

      // Check if file is critical (main.dart, pubspec.yaml, etc.)
      const criticalFiles = ['main.dart', 'pubspec.yaml', 'android/app/build.gradle'];
      const isCritical = criticalFiles.some(critical => filePath.includes(critical));
      
      if (isCritical) {
        test.passed = false;
        test.details = `Critical file modification requires special validation: ${filePath}`;
        test.errorType = 'critical_file_modification';
        return test;
      }

      test.passed = true;
      test.details = `File structure validation passed for ${filePath}`;
      return test;

    } catch (error) {
      test.passed = false;
      test.details = `File structure test error: ${error.message}`;
      test.errorType = 'file_structure_error';
      return test;
    }
  }

  /**
   * Test code compilation
   */
  async testCodeCompilation(proposal) {
    const test = {
      name: 'Code Compilation Test',
      passed: false,
      details: '',
      errorType: null
    };

    try {
      // Create temporary file with proposed changes
      const tempDir = path.join(process.cwd(), 'temp-testing');
      await fs.mkdir(tempDir, { recursive: true });
      
      const tempFilePath = path.join(tempDir, `test_${Date.now()}.dart`);
      await fs.writeFile(tempFilePath, proposal.codeAfter);

      // Run Dart analysis
      const analysisResult = await execAsync(`dart analyze ${tempFilePath}`, {
        timeout: 30000,
        cwd: tempDir
      });

      // Clean up temp file
      await fs.unlink(tempFilePath);

      test.passed = true;
      test.details = 'Code compiles successfully';
      return test;

    } catch (error) {
      test.passed = false;
      test.details = `Compilation failed: ${error.message}`;
      
      // Categorize compilation errors
      if (error.message.includes('syntax error')) {
        test.errorType = 'syntax_error';
      } else if (error.message.includes('type error')) {
        test.errorType = 'type_error';
      } else if (error.message.includes('import error')) {
        test.errorType = 'import_error';
      } else {
        test.errorType = 'compilation_error';
      }
      
      return test;
    }
  }

  /**
   * Test dependency compatibility
   */
  async testDependencyCompatibility(proposal) {
    const test = {
      name: 'Dependency Compatibility Test',
      passed: false,
      details: '',
      errorType: null
    };

    try {
      // Extract imports from proposed code
      const imports = this.extractImports(proposal.codeAfter);
      
      // Check against current pubspec.yaml
      const pubspecPath = path.join(process.cwd(), 'temp-repo', 'pubspec.yaml');
      const pubspecExists = await fs.access(pubspecPath).then(() => true).catch(() => false);
      
      if (!pubspecExists) {
        test.passed = false;
        test.details = 'pubspec.yaml not found for dependency validation';
        test.errorType = 'pubspec_not_found';
        return test;
      }

      const pubspecContent = await fs.readFile(pubspecPath, 'utf8');
      const currentDependencies = this.parseDependencies(pubspecContent);
      
      // Check for missing dependencies
      const missingDeps = imports.filter(imp => !currentDependencies.includes(imp));
      
      if (missingDeps.length > 0) {
        test.passed = false;
        test.details = `Missing dependencies: ${missingDeps.join(', ')}`;
        test.errorType = 'missing_dependencies';
        return test;
      }

      test.passed = true;
      test.details = 'All dependencies are compatible';
      return test;

    } catch (error) {
      test.passed = false;
      test.details = `Dependency test error: ${error.message}`;
      test.errorType = 'dependency_test_error';
      return test;
    }
  }

  /**
   * Test app integration
   */
  async testAppIntegration(proposal) {
    const test = {
      name: 'App Integration Test',
      passed: false,
      details: '',
      errorType: null
    };

    try {
      // Check if proposal affects app initialization
      if (proposal.codeAfter.includes('main()') || proposal.codeAfter.includes('runApp')) {
        test.passed = false;
        test.details = 'Proposal affects app initialization - requires special validation';
        test.errorType = 'app_initialization_impact';
        return test;
      }

      // Check for breaking changes in widget structure
      if (this.detectBreakingChanges(proposal.codeBefore, proposal.codeAfter)) {
        test.passed = false;
        test.details = 'Proposal contains breaking changes to widget structure';
        test.errorType = 'breaking_changes';
        return test;
      }

      test.passed = true;
      test.details = 'App integration test passed';
      return test;

    } catch (error) {
      test.passed = false;
      test.details = `Integration test error: ${error.message}`;
      test.errorType = 'integration_test_error';
      return test;
    }
  }

  /**
   * Test performance impact
   */
  async testPerformanceImpact(proposal) {
    const test = {
      name: 'Performance Impact Test',
      passed: false,
      details: '',
      errorType: null
    };

    try {
      // Analyze code complexity
      const complexity = this.analyzeCodeComplexity(proposal.codeAfter);
      
      if (complexity.cyclomaticComplexity > 10) {
        test.passed = false;
        test.details = `High code complexity detected (${complexity.cyclomaticComplexity})`;
        test.errorType = 'high_complexity';
        return test;
      }

      // Check for performance anti-patterns
      const antiPatterns = this.detectPerformanceAntiPatterns(proposal.codeAfter);
      
      if (antiPatterns.length > 0) {
        test.passed = false;
        test.details = `Performance anti-patterns detected: ${antiPatterns.join(', ')}`;
        test.errorType = 'performance_anti_patterns';
        return test;
      }

      test.passed = true;
      test.details = 'Performance impact test passed';
      return test;

    } catch (error) {
      test.passed = false;
      test.details = `Performance test error: ${error.message}`;
      test.errorType = 'performance_test_error';
      return test;
    }
  }

  /**
   * Learn from test failures
   */
  async learnFromTestFailures(proposal, failedTests) {
    console.log(`[ENHANCED_TESTING] 📚 Learning from ${failedTests.length} test failures`);
    
    for (const test of failedTests) {
      if (!test.passed) {
        const learningPattern = {
          aiType: proposal.aiType,
          filePath: proposal.filePath,
          errorType: test.errorType,
          errorDetails: test.details,
          timestamp: new Date(),
          proposalId: proposal._id,
          improvementType: proposal.improvementType
        };

        // Store learning pattern
        this.learningPatterns.push(learningPattern);
        
        // Update failure database
        const key = `${proposal.aiType}_${test.errorType}`;
        if (!this.failureDatabase.has(key)) {
          this.failureDatabase.set(key, []);
        }
        this.failureDatabase.get(key).push(learningPattern);
        
        console.log(`[ENHANCED_TESTING] 📚 Learned pattern: ${test.errorType} for ${proposal.aiType}`);
      }
    }
  }

  /**
   * Learn from testing errors
   */
  async learnFromTestingError(proposal, error) {
    const learningPattern = {
      aiType: proposal.aiType,
      filePath: proposal.filePath,
      errorType: 'testing_system_error',
      errorDetails: error.message,
      timestamp: new Date(),
      proposalId: proposal._id,
      improvementType: proposal.improvementType
    };

    this.learningPatterns.push(learningPattern);
    console.log(`[ENHANCED_TESTING] 📚 Learned from testing error: ${error.message}`);
  }

  /**
   * Get learning patterns for an AI
   */
  getLearningPatterns(aiType, errorType = null) {
    if (errorType) {
      return this.learningPatterns.filter(
        pattern => pattern.aiType === aiType && pattern.errorType === errorType
      );
    }
    return this.learningPatterns.filter(pattern => pattern.aiType === aiType);
  }

  /**
   * Get failure frequency for an AI
   */
  getFailureFrequency(aiType) {
    const patterns = this.getLearningPatterns(aiType);
    const frequency = {};
    
    patterns.forEach(pattern => {
      frequency[pattern.errorType] = (frequency[pattern.errorType] || 0) + 1;
    });
    
    return frequency;
  }

  /**
   * Helper methods
   */
  extractImports(code) {
    const importRegex = /import\s+['"]([^'"]+)['"]/g;
    const imports = [];
    let match;
    
    while ((match = importRegex.exec(code)) !== null) {
      imports.push(match[1]);
    }
    
    return imports;
  }

  parseDependencies(pubspecContent) {
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

  detectBreakingChanges(codeBefore, codeAfter) {
    // Simple heuristic for detecting breaking changes
    const beforeWidgets = (codeBefore.match(/class\s+\w+Widget/g) || []).length;
    const afterWidgets = (codeAfter.match(/class\s+\w+Widget/g) || []).length;
    
    return Math.abs(beforeWidgets - afterWidgets) > 1;
  }

  analyzeCodeComplexity(code) {
    // Simple cyclomatic complexity calculation
    const complexity = {
      cyclomaticComplexity: 1, // Base complexity
      linesOfCode: code.split('\n').length,
      nestingDepth: 0
    };
    
    // Count control flow statements
    const controlFlowKeywords = ['if', 'else', 'for', 'while', 'switch', 'case', 'catch'];
    controlFlowKeywords.forEach(keyword => {
      const regex = new RegExp(`\\b${keyword}\\b`, 'g');
      const matches = code.match(regex);
      if (matches) {
        complexity.cyclomaticComplexity += matches.length;
      }
    });
    
    return complexity;
  }

  detectPerformanceAntiPatterns(code) {
    const antiPatterns = [];
    
    // Check for common performance issues
    if (code.includes('setState(() {});')) {
      antiPatterns.push('empty_setState');
    }
    
    if (code.includes('Widget build(BuildContext context)') && code.includes('Future.delayed')) {
      antiPatterns.push('build_with_future_delayed');
    }
    
    if (code.includes('ListView.builder') && !code.includes('itemCount')) {
      antiPatterns.push('listview_without_itemcount');
    }
    
    return antiPatterns;
  }
}

module.exports = { EnhancedProposalTesting }; 