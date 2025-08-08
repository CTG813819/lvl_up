const Experiment = require('../models/experiment');
const Proposal = require('../models/proposal');
const { suggestImprovement } = require('./aiServices');

async function runImperiumExperiment(code, filePath) {
  try {
    console.log(`[Imperium] Analyzing ${filePath}...`);
    const suggestion = await suggestImprovement(code);
    console.log(`[Imperium] Suggestion for ${filePath}:`, suggestion);
    const experiment = new Experiment({
      aiName: 'The Imperium',
      experimentType: 'code-analysis',
      input: { filePath, code },
      result: { suggestion }
    });
    await experiment.save();

    const proposal = new Proposal({
      aiType: 'Imperium',
      filePath,
      codeBefore: code,
      codeAfter: suggestion,
      status: 'pending',
      summary: 'Imperium AI analysis',
      suggestion: suggestion,
      timestamp: new Date()
    });
    await proposal.save();
    console.log(`[Imperium] Proposal created for ${filePath}`);
    return { experiment, proposal };
  } catch (e) {
    console.error(`[Imperium] Error analyzing ${filePath}:`, e);
    throw e;
  }
}

module.exports = { runImperiumExperiment }; 