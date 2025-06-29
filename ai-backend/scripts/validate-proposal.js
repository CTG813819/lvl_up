#!/usr/bin/env node

/**
 * Proposal Validation Script
 * Validates AI-generated proposals for compatibility and functionality
 */

const { program } = require('commander');
const fs = require('fs').promises;
const path = require('path');
const axios = require('axios');

program
  .option('--aiType <type>', 'AI Type (Imperium, Guardian, Sandbox)', 'Imperium')
  .option('--proposalId <id>', 'Proposal ID for tracking', 'test-proposal')
  .option('--approved <status>', 'Approval status (true/false)', 'false')
  .option('--filePath <path>', 'File path to validate', '')
  .option('--codeBefore <code>', 'Original code', '')
  .option('--codeAfter <code>', 'Modified code', '')
  .parse(process.argv);

const options = program.opts();

class ProposalValidator {
  constructor() {
    this.validationResults = [];
    this.errors = [];
    this.warnings = [];
  }

  log(message, type = 'INFO') {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [${type}] ${message}`);
  }

  addResult(test, passed, details = '') {
    this.validationResults.push({
      test,
      passed,
      details,
      timestamp: new Date().toISOString()
    });
  }

  addError(message) {
    this.errors.push({
      message,
      timestamp: new Date().toISOString()
    });
    this.log(message, 'ERROR');
  }

  addWarning(message) {
    this.warnings.push({
      message,
      timestamp: new Date().toISOString()
    });
    this.log(message, 'WARNING');
  }

  async validateProposalStructure() {
    this.log('🧪 Validating Proposal Structure');
    
    const requiredFields = ['aiType', 'proposalId', 'approved'];
    let structureValid = true;
    
    for (const field of requiredFields) {
      if (!options[field]) {
        this.addError(`Missing required field: ${field}`);
        structureValid = false;
      }
    }
    
    if (structureValid) {
      this.log('✅ Proposal structure validation passed');
      this.addResult('Structure Validation', true, 'All required fields present');
    } else {
      this.addResult('Structure Validation', false, 'Missing required fields');
    }
    
    return structureValid;
  }

  async validateAIType() {
    this.log('🧪 Validating AI Type');
    
    const validAITypes = ['Imperium', 'Guardian', 'Sandbox'];
    const aiType = options.aiType;
    
    if (validAITypes.includes(aiType)) {
      this.log(`✅ AI Type validation passed: ${aiType}`);
      this.addResult('AI Type Validation', true, `Valid AI type: ${aiType}`);
      return true;
    } else {
      this.addError(`Invalid AI type: ${aiType}. Valid types: ${validAITypes.join(', ')}`);
      this.addResult('AI Type Validation', false, `Invalid AI type: ${aiType}`);
      return false;
    }
  }

  async validateFilePaths() {
    this.log('🧪 Validating File Paths');
    
    if (!options.filePath) {
      this.addWarning('No file path provided for validation');
      this.addResult('File Path Validation', true, 'Skipped - no file path provided');
      return true;
    }
    
    const validExtensions = ['.dart', '.js', '.ts', '.py', '.java', '.kt', '.swift'];
    const fileExt = path.extname(options.filePath).toLowerCase();
    
    if (validExtensions.includes(fileExt)) {
      this.log(`✅ File extension validation passed: ${fileExt}`);
      this.addResult('File Extension Validation', true, `Valid extension: ${fileExt}`);
    } else {
      this.addWarning(`Unusual file extension: ${fileExt}`);
      this.addResult('File Extension Validation', false, `Unusual extension: ${fileExt}`);
    }
    
    // Check if file exists in the project structure
    try {
      const fullPath = path.join(process.cwd(), options.filePath);
      await fs.access(fullPath);
      this.log(`✅ File exists: ${options.filePath}`);
      this.addResult('File Existence', true, `File found: ${options.filePath}`);
    } catch (error) {
      this.addWarning(`File not found: ${options.filePath}`);
      this.addResult('File Existence', false, `File not found: ${options.filePath}`);
    }
    
    return true;
  }

  async validateCodeChanges() {
    this.log('🧪 Validating Code Changes');
    
    if (!options.codeBefore || !options.codeAfter) {
      this.addWarning('No code changes provided for validation');
      this.addResult('Code Changes Validation', true, 'Skipped - no code provided');
      return true;
    }
    
    let codeValid = true;
    
    // Check if code actually changed
    if (options.codeBefore === options.codeAfter) {
      this.addWarning('No code changes detected');
      this.addResult('Code Changes Detection', false, 'No changes detected');
      codeValid = false;
    } else {
      this.log('✅ Code changes detected');
      this.addResult('Code Changes Detection', true, 'Changes detected');
    }
    
    // Check code length
    const beforeLength = options.codeBefore.length;
    const afterLength = options.codeAfter.length;
    
    if (afterLength < beforeLength * 0.5) {
      this.addWarning('Significant code reduction detected - may indicate deletion');
      this.addResult('Code Length Validation', false, 'Significant reduction detected');
      codeValid = false;
    } else if (afterLength > beforeLength * 3) {
      this.addWarning('Significant code increase detected - may indicate major changes');
      this.addResult('Code Length Validation', false, 'Significant increase detected');
      codeValid = false;
    } else {
      this.log(`✅ Code length validation passed: ${beforeLength} -> ${afterLength} characters`);
      this.addResult('Code Length Validation', true, `Length change: ${beforeLength} -> ${afterLength}`);
    }
    
    // Check for common issues
    const issues = this.detectCodeIssues(options.codeAfter);
    if (issues.length > 0) {
      issues.forEach(issue => this.addWarning(issue));
      this.addResult('Code Quality Check', false, `${issues.length} issues detected`);
      codeValid = false;
    } else {
      this.log('✅ Code quality check passed');
      this.addResult('Code Quality Check', true, 'No issues detected');
    }
    
    return codeValid;
  }

  detectCodeIssues(code) {
    const issues = [];
    
    // Check for common problematic patterns
    const patterns = [
      { pattern: /TODO|FIXME|HACK/, message: 'Contains TODO/FIXME/HACK comments' },
      { pattern: /console\.log\(/, message: 'Contains console.log statements' },
      { pattern: /debugger;/, message: 'Contains debugger statements' },
      { pattern: /password.*=.*['"][^'"]+['"]/, message: 'Contains hardcoded passwords' },
      { pattern: /api.*key.*=.*['"][^'"]+['"]/, message: 'Contains hardcoded API keys' }
    ];
    
    for (const { pattern, message } of patterns) {
      if (pattern.test(code)) {
        issues.push(message);
      }
    }
    
    return issues;
  }

  async validateProposalCompatibility() {
    this.log('🧪 Validating Proposal Compatibility');
    
    const aiType = options.aiType;
    let compatibilityValid = true;
    
    // AI-specific compatibility checks
    switch (aiType) {
      case 'Imperium':
        // Imperium can modify any file
        this.log('✅ Imperium has full modification permissions');
        this.addResult('AI Permissions', true, 'Imperium has full access');
        break;
        
      case 'Guardian':
        // Guardian should focus on security and monitoring
        if (options.filePath && options.filePath.includes('security')) {
          this.log('✅ Guardian modifying security-related file');
          this.addResult('AI Permissions', true, 'Guardian modifying security file');
        } else {
          this.addWarning('Guardian should focus on security and monitoring files');
          this.addResult('AI Permissions', false, 'Guardian modifying non-security file');
          compatibilityValid = false;
        }
        break;
        
      case 'Sandbox':
        // Sandbox should focus on experimental features
        if (options.filePath && (options.filePath.includes('experiment') || options.filePath.includes('test'))) {
          this.log('✅ Sandbox modifying experimental/test file');
          this.addResult('AI Permissions', true, 'Sandbox modifying experimental file');
        } else {
          this.addWarning('Sandbox should focus on experimental and test files');
          this.addResult('AI Permissions', false, 'Sandbox modifying non-experimental file');
          compatibilityValid = false;
        }
        break;
        
      default:
        this.addError(`Unknown AI type: ${aiType}`);
        this.addResult('AI Permissions', false, `Unknown AI type: ${aiType}`);
        compatibilityValid = false;
    }
    
    return compatibilityValid;
  }

  async validateApprovalWorkflow() {
    this.log('🧪 Validating Approval Workflow');
    
    const approved = options.approved === 'true';
    let workflowValid = true;
    
    if (approved) {
      this.log('✅ Proposal is approved - proceeding with integration');
      this.addResult('Approval Status', true, 'Proposal approved');
      
      // Additional checks for approved proposals
      if (!options.filePath) {
        this.addWarning('Approved proposal without file path - may cause issues');
        this.addResult('Approved Proposal Validation', false, 'No file path for approved proposal');
        workflowValid = false;
      }
      
      if (!options.codeAfter) {
        this.addWarning('Approved proposal without code changes - may cause issues');
        this.addResult('Approved Proposal Validation', false, 'No code changes for approved proposal');
        workflowValid = false;
      }
    } else {
      this.log('ℹ️ Proposal is not approved - skipping integration');
      this.addResult('Approval Status', true, 'Proposal not approved');
    }
    
    return workflowValid;
  }

  async runValidation() {
    this.log('🚀 Starting Proposal Validation');
    this.log('================================');
    
    const validations = [
      { name: 'Proposal Structure', test: () => this.validateProposalStructure() },
      { name: 'AI Type', test: () => this.validateAIType() },
      { name: 'File Paths', test: () => this.validateFilePaths() },
      { name: 'Code Changes', test: () => this.validateCodeChanges() },
      { name: 'Proposal Compatibility', test: () => this.validateProposalCompatibility() },
      { name: 'Approval Workflow', test: () => this.validateApprovalWorkflow() }
    ];
    
    let passedValidations = 0;
    let totalValidations = validations.length;
    
    for (const validation of validations) {
      this.log(`\n📋 Running: ${validation.name}`);
      try {
        const result = await validation.test();
        if (result) {
          this.log(`✅ ${validation.name}: PASSED`);
          passedValidations++;
        } else {
          this.log(`❌ ${validation.name}: FAILED`);
        }
      } catch (error) {
        this.log(`💥 ${validation.name}: ERROR - ${error.message}`, 'ERROR');
        this.addError(`Validation error in ${validation.name}: ${error.message}`);
      }
    }
    
    this.log('\n📊 Validation Results Summary');
    this.log('=============================');
    this.log(`Total Validations: ${totalValidations}`);
    this.log(`Passed: ${passedValidations}`);
    this.log(`Failed: ${totalValidations - passedValidations}`);
    this.log(`Success Rate: ${((passedValidations / totalValidations) * 100).toFixed(1)}%`);
    
    if (this.errors.length > 0) {
      this.log(`\n❌ Errors (${this.errors.length}):`);
      this.errors.forEach(error => {
        this.log(`   - ${error.message}`);
      });
    }
    
    if (this.warnings.length > 0) {
      this.log(`\n⚠️ Warnings (${this.warnings.length}):`);
      this.warnings.forEach(warning => {
        this.log(`   - ${warning.message}`);
      });
    }
    
    this.log('\n📋 Detailed Results:');
    this.validationResults.forEach(result => {
      const status = result.passed ? '✅' : '❌';
      this.log(`   ${status} ${result.test}: ${result.details}`);
    });
    
    if (passedValidations === totalValidations && this.errors.length === 0) {
      this.log('\n🎉 All validations passed!');
      this.log('✅ Proposal is ready for integration');
      return true;
    } else if (this.errors.length === 0) {
      this.log('\n⚠️ Some validations failed, but no critical errors');
      this.log('✅ Proposal can proceed with warnings');
      return true;
    } else {
      this.log('\n❌ Critical validation errors found');
      this.log('❌ Proposal cannot proceed');
      return false;
    }
  }

  getValidationReport() {
    return {
      proposalId: options.proposalId,
      aiType: options.aiType,
      approved: options.approved === 'true',
      timestamp: new Date().toISOString(),
      results: this.validationResults,
      errors: this.errors,
      warnings: this.warnings,
      summary: {
        total: this.validationResults.length,
        passed: this.validationResults.filter(r => r.passed).length,
        failed: this.validationResults.filter(r => !r.passed).length,
        errorCount: this.errors.length,
        warningCount: this.warnings.length
      }
    };
  }
}

// Main execution
async function main() {
  const validator = new ProposalValidator();
  
  try {
    const isValid = await validator.runValidation();
    
    // Save validation report
    const report = validator.getValidationReport();
    const reportPath = path.join(process.cwd(), 'ai-backend', 'test-results', `proposal-validation-${options.proposalId}.json`);
    
    try {
      await fs.mkdir(path.dirname(reportPath), { recursive: true });
      await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
      console.log(`📄 Validation report saved to: ${reportPath}`);
    } catch (error) {
      console.warn(`⚠️ Could not save validation report: ${error.message}`);
    }
    
    if (!isValid) {
      process.exit(1);
    }
  } catch (error) {
    console.error('💥 Validation failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { ProposalValidator }; 