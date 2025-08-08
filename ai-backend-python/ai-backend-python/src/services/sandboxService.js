const Experiment = require('../models/experiment');
const Proposal = require('../models/proposal');
const { suggestImprovement } = require('./aiServices');

async function runSandboxExperiment(code, filePath) {
  try {
    console.log(`[Sandbox] Analyzing ${filePath}...`);
    const suggestion = await suggestImprovement(code);
    console.log(`[Sandbox] Suggestion for ${filePath}:`, suggestion);
    const experiment = new Experiment({
      aiName: 'AI Sandbox',
      experimentType: 'sandbox-analysis',
      input: { filePath, code },
      result: { suggestion }
    });
    await experiment.save();

    const proposal = new Proposal({
      aiType: 'Sandbox',
      filePath,
      codeBefore: code,
      codeAfter: suggestion,
      status: 'pending',
      summary: 'Sandbox AI analysis',
      suggestion: suggestion,
      timestamp: new Date()
    });
    await proposal.save();
    console.log(`[Sandbox] Proposal created for ${filePath}`);
    return { experiment, proposal };
  } catch (e) {
    console.error(`[Sandbox] Error analyzing ${filePath}:`, e);
    throw e;
  }
}

module.exports = { runSandboxExperiment }; 