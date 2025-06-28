const { spawn } = require('child_process');
const path = require('path');

/**
 * Runs 'dart test' in the specified directory and returns the results.
 * @param {string} repoPath - The path to the Dart project (where pubspec.yaml is located).
 * @returns {Promise<{ success: boolean, output: string }>} Test results.
 */
async function runDartTests(repoPath) {
  return new Promise((resolve) => {
    const testProcess = spawn('dart', ['test'], { cwd: repoPath });
    let output = '';
    testProcess.stdout.on('data', (data) => {
      output += data.toString();
    });
    testProcess.stderr.on('data', (data) => {
      output += data.toString();
    });
    testProcess.on('close', (code) => {
      resolve({
        success: code === 0,
        output,
      });
    });
  });
}

module.exports = { runDartTests }; 