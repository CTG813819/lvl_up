const Experiment = require('../models/experiment');
const Proposal = require('../models/proposal');
const { suggestImprovement } = require('./aiServices');

async function runGuardianExperiment(code, filePath) {
  try {
    console.log(`[Guardian] Analyzing ${filePath}...`);
    const suggestion = await suggestImprovement(code);
    console.log(`[Guardian] Suggestion for ${filePath}:`, suggestion);
    const experiment = new Experiment({
      aiName: 'AI Guardian',
      experimentType: 'health-check',
      input: { filePath, code },
      result: { suggestion }
    });
    await experiment.save();

    const proposal = new Proposal({
      aiType: 'Guardian',
      filePath,
      codeBefore: code,
      codeAfter: suggestion,
      status: 'pending',
      summary: 'Guardian AI health check',
      suggestion: suggestion,
      timestamp: new Date()
    });
    await proposal.save();
    console.log(`[Guardian] Proposal created for ${filePath}`);
    return { experiment, proposal };
  } catch (e) {
    console.error(`[Guardian] Error analyzing ${filePath}:`, e);
    throw e;
  }
}

module.exports = { runGuardianExperiment }; 