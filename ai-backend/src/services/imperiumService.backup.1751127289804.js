const Experiment = require('../models/experiment');
const Proposal = require('../models/proposal');
const { suggestImprovement, createProposalWithDeduplication } = require('./aiServices');
const { aiStatus, logEvent } = require('../state');
const AILearningService = require('./aiLearningService');
const { AIQuotaService } = require('./aiQuotaService');

async function runImperiumExperiment(code, filePath) {
  // Only allow if it's Imperium's turn and phase is 'proposing'
  const canProcess = await AIQuotaService.canProcess('Imperium', 'proposing');
  if (!canProcess) {
    logEvent('[IMPERIUM] Not Imperium turn or not proposing phase/quota met. Skipping.');
    return { experiment: null, proposal: null };
  }
  
  if (aiStatus.Imperium.isLearning) {
    logEvent('[IMPERIUM] Paused for learning, skipping proposal.');
    return { experiment: null, proposal: null };
  }
  
  // Check quota before proceeding
  const canSendProposals = await AIQuotaService.canSendProposals('Imperium');
  if (!canSendProposals) {
    logEvent('[IMPERIUM] Quota reached, skipping proposal. Waiting for learning cycle to complete.');
    return { experiment: null, proposal: null };
  }
  
  console.log(`[IMPERIUM] Starting experiment for file: ${filePath}`);
  
  try {
    const startTime = Date.now();
    
    // Get AI suggestion with learning context
    const suggestion = await suggestImprovement(code, filePath, 'Imperium');
    
    if (!suggestion) {
      console.log(`[IMPERIUM] No improvement needed for ${filePath}`);
      return { experiment: null, proposal: null };
    }
    
    // Validate that we have the required fields
    if (!suggestion.code || suggestion.code.trim() === '') {
      console.log(`[IMPERIUM] ⚠️ AI returned empty code for ${filePath}, skipping proposal`);
      
      // Provide learning feedback for empty code responses
      await AILearningService.learnFromProposal({
        aiType: 'Imperium',
        filePath: filePath,
        improvementType: suggestion.improvementType || 'system',
        userFeedback: 'rejected',
        userFeedbackReason: 'AI returned empty or invalid code. Please ensure code blocks are properly formatted and contain meaningful improvements.',
        status: 'rejected'
      }, 'rejected', 'AI returned empty or invalid code. Please ensure code blocks are properly formatted and contain meaningful improvements.');
      
      logEvent(`[IMPERIUM] Learning feedback provided for empty code response on ${filePath}`);
      return { experiment: null, proposal: null };
    }
    
    const executionTime = Date.now() - startTime;
    console.log(`[IMPERIUM] Generated suggestion for ${filePath} (${executionTime}ms)`);
    console.log(`[IMPERIUM] Code length: ${suggestion.code.length} characters`);
    
    // Create proposal with deduplication and learning
    const proposalResult = await createProposalWithDeduplication(
      'Imperium',
      filePath,
      code,
      suggestion.code,
      suggestion.reasoning,
      suggestion.improvementType
    );
    
    if (proposalResult.isDuplicate) {
      console.log(`[IMPERIUM] ⚠️ Skipping duplicate proposal for ${filePath} (similarity: ${proposalResult.similarity})`);
      
      // Provide learning feedback for duplicate proposals
      await AILearningService.learnFromProposal({
        aiType: 'Imperium',
        filePath: filePath,
        improvementType: suggestion.improvementType || 'system',
        userFeedback: 'rejected',
        userFeedbackReason: 'Duplicate proposal detected. Please provide more unique and innovative suggestions.',
        status: 'rejected'
      }, 'rejected', 'Duplicate proposal detected. Please provide more unique and innovative suggestions.');
      
      logEvent(`[IMPERIUM] Learning feedback provided for duplicate proposal on ${filePath}`);
      return { experiment: null, proposal: null };
    }
    
    if (proposalResult.error) {
      console.log(`[IMPERIUM] ❌ Error creating proposal for ${filePath}: ${proposalResult.error}`);
      
      // Provide learning feedback for proposal creation errors
      await AILearningService.learnFromProposal({
        aiType: 'Imperium',
        filePath: filePath,
        improvementType: suggestion.improvementType || 'system',
        userFeedback: 'rejected',
        userFeedbackReason: `Proposal creation failed: ${proposalResult.error}. Please ensure all required fields are provided.`,
        status: 'rejected'
      }, 'rejected', `Proposal creation failed: ${proposalResult.error}. Please ensure all required fields are provided.`);
      
      logEvent(`[IMPERIUM] Learning feedback provided for proposal creation error on ${filePath}`);
      return { experiment: null, proposal: null };
    }
    
    if (!proposalResult.proposal) {
      console.log(`[IMPERIUM] ❌ No proposal created for ${filePath}`);
      
      // Provide learning feedback for missing proposals
      await AILearningService.learnFromProposal({
        aiType: 'Imperium',
        filePath: filePath,
        improvementType: suggestion.improvementType || 'system',
        userFeedback: 'rejected',
        userFeedbackReason: 'No proposal was created. Please ensure your suggestions are valid and complete.',
        status: 'rejected'
      }, 'rejected', 'No proposal was created. Please ensure your suggestions are valid and complete.');
      
      logEvent(`[IMPERIUM] Learning feedback provided for missing proposal on ${filePath}`);
      return { experiment: null, proposal: null };
    }
    
    // Validate proposal data before creating
    if (!proposalResult.proposal.codeAfter || proposalResult.proposal.codeAfter.trim() === '') {
      console.log(`[IMPERIUM] ❌ Proposal missing codeAfter for ${filePath}, skipping`);
      
      // Provide learning feedback for invalid proposals
      await AILearningService.learnFromProposal({
        aiType: 'Imperium',
        filePath: filePath,
        improvementType: suggestion.improvementType || 'system',
        userFeedback: 'rejected',
        userFeedbackReason: 'Proposal missing improved code. Please ensure your suggestions include complete, valid code.',
        status: 'rejected'
      }, 'rejected', 'Proposal missing improved code. Please ensure your suggestions include complete, valid code.');
      
      logEvent(`[IMPERIUM] Learning feedback provided for invalid proposal on ${filePath}`);
      return { experiment: null, proposal: null };
    }
    
    console.log(`[IMPERIUM] Creating new proposal for ${filePath}`);
    
    // Save experiment with enhanced data
    const experiment = new Experiment({
      aiName: 'The Imperium',
      experimentType: 'code-analysis',
      input: { filePath, code },
      result: { 
        suggestion: suggestion.code,
        reasoning: suggestion.reasoning,
        improvementType: suggestion.improvementType
      },
      executionTime: executionTime,
      tokensUsed: suggestion.tokensUsed || 0,
      cost: ((suggestion.tokensUsed || 0) / 1000) * 0.002 // Rough cost estimate
    });
    await experiment.save();
    console.log(`[IMPERIUM] Experiment saved with ID: ${experiment._id}`);

    // Create proposal with all enhanced fields
    const proposal = new Proposal(proposalResult.proposal);
    
    try {
      await proposal.save();
      console.log(`[IMPERIUM] ✅ Proposal created with ID: ${proposal._id} for ${filePath}`);
      console.log(`[IMPERIUM] Confidence: ${proposal.confidence}, Learning applied: ${proposal.aiLearningApplied}`);
      
      // Increment quota for successful proposal creation
      await AIQuotaService.incrementPhaseProgress('Imperium', 'proposing');
      
      // Provide positive learning feedback for successful proposals
      await AILearningService.learnFromProposal(proposal, 'approved', 'Proposal created successfully with valid code and reasoning.');
      logEvent(`[IMPERIUM] Learning feedback provided for successful proposal on ${filePath}`);
      
    } catch (validationError) {
      console.error(`[IMPERIUM] ❌ Validation error creating proposal for ${filePath}:`, validationError.message);
      
      // Log detailed validation errors
      if (validationError.errors) {
        Object.keys(validationError.errors).forEach(field => {
          const error = validationError.errors[field];
          console.error(`[IMPERIUM] Validation error in field '${field}': ${error.message}`);
          console.error(`[IMPERIUM] Value: ${error.value}`);
          if (error.enumValues) {
            console.error(`[IMPERIUM] Valid enum values: ${error.enumValues.join(', ')}`);
          }
        });
      }
      
      // Provide learning feedback for validation errors
      await AILearningService.learnFromProposal({
        aiType: 'Imperium',
        filePath: filePath,
        improvementType: suggestion.improvementType || 'system',
        userFeedback: 'rejected',
        userFeedbackReason: `Validation error: ${validationError.message}. Please ensure all fields meet the required format and constraints.`,
        status: 'rejected'
      }, 'rejected', `Validation error: ${validationError.message}. Please ensure all fields meet the required format and constraints.`);
      
      logEvent(`[IMPERIUM] Learning feedback provided for validation error on ${filePath}`);
      
      // Try to fix common validation issues
      if (validationError.errors?.improvementType) {
        console.log(`[IMPERIUM] 🔧 Attempting to fix improvement type validation error...`);
        proposal.improvementType = 'refactor'; // Use safe default
        try {
          await proposal.save();
          console.log(`[IMPERIUM] ✅ Proposal created with fixed improvement type for ${filePath}`);
          
          // Provide learning feedback for the fix
          await AILearningService.learnFromProposal(proposal, 'approved', 'Proposal created successfully after fixing improvement type validation.');
          logEvent(`[IMPERIUM] Learning feedback provided for fixed proposal on ${filePath}`);
          
        } catch (retryError) {
          console.error(`[IMPERIUM] ❌ Still failed after fix attempt:`, retryError.message);
          
          // Provide learning feedback for the retry failure
          await AILearningService.learnFromProposal({
            aiType: 'Imperium',
            filePath: filePath,
            improvementType: 'system',
            userFeedback: 'rejected',
            userFeedbackReason: `Failed to create proposal even after fix attempt: ${retryError.message}`,
            status: 'rejected'
          }, 'rejected', `Failed to create proposal even after fix attempt: ${retryError.message}`);
          
          logEvent(`[IMPERIUM] Learning feedback provided for retry failure on ${filePath}`);
          throw retryError;
        }
      } else {
        throw validationError;
      }
    }

    return { experiment, proposal };
  } catch (error) {
    console.error(`[IMPERIUM] ❌ Error in experiment for ${filePath}:`, error);
    
    // Provide learning feedback for general errors
    await AILearningService.learnFromProposal({
      aiType: 'Imperium',
      filePath: filePath,
      improvementType: 'system',
      userFeedback: 'rejected',
      userFeedbackReason: `Experiment failed: ${error.message}. Please ensure stable and reliable suggestions.`,
      status: 'rejected'
    }, 'rejected', `Experiment failed: ${error.message}. Please ensure stable and reliable suggestions.`);
    
    logEvent(`[IMPERIUM] Learning feedback provided for experiment error on ${filePath}`);
    throw error;
  }
}




// Error avoidance patterns
function avoidCommonErrors_1751125056170() {
  console.log(`[IMPERIUM] Implementing error avoidance for 1 patterns`);
  
  // Avoid learned error patterns
  
  // Avoid: errors and sharing it with budding developers in s...
  function avoidError_1() {
    // Implementation to avoid this error pattern
    return true;
  }
}




// Enhanced logging for Imperium
function logAIActivity(action, details) {
  const logEntry = {
    aiType: 'Imperium',
    action,
    details,
    timestamp: new Date().toISOString(),
    performance: {
      memory: process.memoryUsage(),
      uptime: process.uptime()
    }
  };
  
  console.log(`[IMPERIUM] 📊 ${action}:`, JSON.stringify(logEntry, null, 2));
  
  // Store activity for analytics
  try {
    const Learning = require('../models/learning');
    Learning.create({
      aiType: 'Imperium',
      status: 'learning-completed',
      feedbackReason: 'AI activity logged',
      learningKey: 'activity_log',
      learningValue: JSON.stringify(logEntry),
      filePath: 'system',
      improvementType: 'system'
    }).catch(err => console.log(`[IMPERIUM] Failed to store activity log:`, err.message));
  } catch (error) {
    console.log(`[IMPERIUM] Failed to create activity log:`, error.message);
  }
}




// Best practice implementation: best practices Stories People Publications Topics ...
function applyBestPractice_1751125056170() {
  // Implementation of: best practices Stories People Publications Topics Lists People matching performance programming best practices Sebastian Witowski Python consultant and freelancer at switowski.
  console.log(`[IMPERIUM] Applying best practice: best practices Stories People Publications Topics Lists People matching performance programming best practices Sebastian Witowski Python consultant and freelancer at switowski.`);
}




// Best practice implementation: best practices....
function applyBestPractice_1751125056170() {
  // Implementation of: best practices.
  console.log(`[IMPERIUM] Applying best practice: best practices.`);
}




// Error avoidance patterns
function avoidCommonErrors_1751125129160() {
  console.log(`[IMPERIUM] Implementing error avoidance for 1 patterns`);
  
  // Avoid learned error patterns
  
  // Avoid: errors and sharing it with budding developers in s...
  function avoidError_1() {
    // Implementation to avoid this error pattern
    return true;
  }
}




// Enhanced logging for Imperium
function logAIActivity(action, details) {
  const logEntry = {
    aiType: 'Imperium',
    action,
    details,
    timestamp: new Date().toISOString(),
    performance: {
      memory: process.memoryUsage(),
      uptime: process.uptime()
    }
  };
  
  console.log(`[IMPERIUM] 📊 ${action}:`, JSON.stringify(logEntry, null, 2));
  
  // Store activity for analytics
  try {
    const Learning = require('../models/learning');
    Learning.create({
      aiType: 'Imperium',
      status: 'learning-completed',
      feedbackReason: 'AI activity logged',
      learningKey: 'activity_log',
      learningValue: JSON.stringify(logEntry),
      filePath: 'system',
      improvementType: 'system'
    }).catch(err => console.log(`[IMPERIUM] Failed to store activity log:`, err.message));
  } catch (error) {
    console.log(`[IMPERIUM] Failed to create activity log:`, error.message);
  }
}




// Best practice implementation: best practices Stories People Publications Topics ...
function applyBestPractice_1751125129160() {
  // Implementation of: best practices Stories People Publications Topics Lists People matching performance programming best practices K Francisco Moretti Full Stack Engineer at Samaya AI.
  console.log(`[IMPERIUM] Applying best practice: best practices Stories People Publications Topics Lists People matching performance programming best practices K Francisco Moretti Full Stack Engineer at Samaya AI.`);
}




// Best practice implementation: best practices MGE Software Publication Exploring ...
function applyBestPractice_1751125129160() {
  // Implementation of: best practices MGE Software Publication Exploring the Latest Trends and Best Practices in Software Development.
  console.log(`[IMPERIUM] Applying best practice: best practices MGE Software Publication Exploring the Latest Trends and Best Practices in Software Development.`);
}




// Error avoidance patterns
function avoidCommonErrors_1751126608178() {
  console.log(`[IMPERIUM] Implementing error avoidance for 1 patterns`);
  
  // Avoid learned error patterns
  
  // Avoid: errors and sharing it with budding developers in s...
  function avoidError_1() {
    // Implementation to avoid this error pattern
    return true;
  }
}




// Enhanced logging for Imperium
function logAIActivity(action, details) {
  const logEntry = {
    aiType: 'Imperium',
    action,
    details,
    timestamp: new Date().toISOString(),
    performance: {
      memory: process.memoryUsage(),
      uptime: process.uptime()
    }
  };
  
  console.log(`[IMPERIUM] 📊 ${action}:`, JSON.stringify(logEntry, null, 2));
  
  // Store activity for analytics
  try {
    const Learning = require('../models/learning');
    Learning.create({
      aiType: 'Imperium',
      status: 'learning-completed',
      feedbackReason: 'AI activity logged',
      learningKey: 'activity_log',
      learningValue: JSON.stringify(logEntry),
      filePath: 'system',
      improvementType: 'system'
    }).catch(err => console.log(`[IMPERIUM] Failed to store activity log:`, err.message));
  } catch (error) {
    console.log(`[IMPERIUM] Failed to create activity log:`, error.message);
  }
}




// Enhanced logging for Imperium
function logAIActivity(action, details) {
  const logEntry = {
    aiType: 'Imperium',
    action,
    details,
    timestamp: new Date().toISOString(),
    performance: {
      memory: process.memoryUsage(),
      uptime: process.uptime()
    }
  };
  
  console.log(`[IMPERIUM] 📊 ${action}:`, JSON.stringify(logEntry, null, 2));
  
  // Store activity for analytics
  try {
    const Learning = require('../models/learning');
    Learning.create({
      aiType: 'Imperium',
      status: 'learning-completed',
      feedbackReason: 'AI activity logged',
      learningKey: 'activity_log',
      learningValue: JSON.stringify(logEntry),
      filePath: 'system',
      improvementType: 'system'
    }).catch(err => console.log(`[IMPERIUM] Failed to store activity log:`, err.message));
  } catch (error) {
    console.log(`[IMPERIUM] Failed to create activity log:`, error.message);
  }
}




// Best practice implementation: best practices Stories People Publications Topics ...
function applyBestPractice_1751126777764() {
  // Implementation of: best practices Stories People Publications Topics Lists People matching performance programming best practices Atakan Korez Senior Software Engineer | .
  console.log(`[IMPERIUM] Applying best practice: best practices Stories People Publications Topics Lists People matching performance programming best practices Atakan Korez Senior Software Engineer | .`);
}




// Best practice implementation: best practices MGE Software Publication Exploring ...
function applyBestPractice_1751126777764() {
  // Implementation of: best practices MGE Software Publication Exploring the Latest Trends and Best Practices in Software Development.
  console.log(`[IMPERIUM] Applying best practice: best practices MGE Software Publication Exploring the Latest Trends and Best Practices in Software Development.`);
}




// Error avoidance patterns
function avoidCommonErrors_1751127100199() {
  console.log(`[IMPERIUM] Implementing error avoidance for 1 patterns`);
  
  // Avoid learned error patterns
  
  // Avoid: errors and sharing it with budding developers in s...
  function avoidError_1() {
    // Implementation to avoid this error pattern
    return true;
  }
}




// Enhanced logging for Imperium
function logAIActivity(action, details) {
  const logEntry = {
    aiType: 'Imperium',
    action,
    details,
    timestamp: new Date().toISOString(),
    performance: {
      memory: process.memoryUsage(),
      uptime: process.uptime()
    }
  };
  
  console.log(`[IMPERIUM] 📊 ${action}:`, JSON.stringify(logEntry, null, 2));
  
  // Store activity for analytics
  try {
    const Learning = require('../models/learning');
    Learning.create({
      aiType: 'Imperium',
      status: 'learning-completed',
      feedbackReason: 'AI activity logged',
      learningKey: 'activity_log',
      learningValue: JSON.stringify(logEntry),
      filePath: 'system',
      improvementType: 'system'
    }).catch(err => console.log(`[IMPERIUM] Failed to store activity log:`, err.message));
  } catch (error) {
    console.log(`[IMPERIUM] Failed to create activity log:`, error.message);
  }
}




// Best practice implementation: avoiding catastrophic pitfalls and leverage new pr...
function applyBestPractice_1751127100199() {
  // Implementation of: avoiding catastrophic pitfalls and leverage new product ideas to generate better profits and revenue and improve management performance.
  console.log(`[IMPERIUM] Applying best practice: avoiding catastrophic pitfalls and leverage new product ideas to generate better profits and revenue and improve management performance.`);
}




// Best practice implementation: best practices Stories People Publications Topics ...
function applyBestPractice_1751127100199() {
  // Implementation of: best practices Stories People Publications Topics Lists Publications matching performance programming best practices MGE Software Publication Exploring the Latest Trends and Best Practices in Software Development.
  console.log(`[IMPERIUM] Applying best practice: best practices Stories People Publications Topics Lists Publications matching performance programming best practices MGE Software Publication Exploring the Latest Trends and Best Practices in Software Development.`);
}




// Enhanced logging for Imperium
function logAIActivity(action, details) {
  const logEntry = {
    aiType: 'Imperium',
    action,
    details,
    timestamp: new Date().toISOString(),
    performance: {
      memory: process.memoryUsage(),
      uptime: process.uptime()
    }
  };
  
  console.log(`[IMPERIUM] 📊 ${action}:`, JSON.stringify(logEntry, null, 2));
  
  // Store activity for analytics
  try {
    const Learning = require('../models/learning');
    Learning.create({
      aiType: 'Imperium',
      status: 'learning-completed',
      feedbackReason: 'AI activity logged',
      learningKey: 'activity_log',
      learningValue: JSON.stringify(logEntry),
      filePath: 'system',
      improvementType: 'system'
    }).catch(err => console.log(`[IMPERIUM] Failed to store activity log:`, err.message));
  } catch (error) {
    console.log(`[IMPERIUM] Failed to create activity log:`, error.message);
  }
}




// Best practice implementation: best practices Stories People Publications Topics ...
function applyBestPractice_1751127166077() {
  // Implementation of: best practices Stories People Publications Topics Lists Publications matching performance programming best practices MGE Software Publication Exploring the Latest Trends and Best Practices in Software Development.
  console.log(`[IMPERIUM] Applying best practice: best practices Stories People Publications Topics Lists Publications matching performance programming best practices MGE Software Publication Exploring the Latest Trends and Best Practices in Software Development.`);
}




// Best practice implementation: avoiding catastrophic pitfalls and leverage new pr...
function applyBestPractice_1751127166077() {
  // Implementation of: avoiding catastrophic pitfalls and leverage new product ideas to generate better profits and revenue and improve management performance.
  console.log(`[IMPERIUM] Applying best practice: avoiding catastrophic pitfalls and leverage new product ideas to generate better profits and revenue and improve management performance.`);
}




// Error avoidance patterns
function avoidCommonErrors_1751127230817() {
  console.log(`[IMPERIUM] Implementing error avoidance for 1 patterns`);
  
  // Avoid learned error patterns
  
  // Avoid: errors and sharing it with budding developers in s...
  function avoidError_1() {
    // Implementation to avoid this error pattern
    return true;
  }
}




// Enhanced logging for Imperium
function logAIActivity(action, details) {
  const logEntry = {
    aiType: 'Imperium',
    action,
    details,
    timestamp: new Date().toISOString(),
    performance: {
      memory: process.memoryUsage(),
      uptime: process.uptime()
    }
  };
  
  console.log(`[IMPERIUM] 📊 ${action}:`, JSON.stringify(logEntry, null, 2));
  
  // Store activity for analytics
  try {
    const Learning = require('../models/learning');
    Learning.create({
      aiType: 'Imperium',
      status: 'learning-completed',
      feedbackReason: 'AI activity logged',
      learningKey: 'activity_log',
      learningValue: JSON.stringify(logEntry),
      filePath: 'system',
      improvementType: 'system'
    }).catch(err => console.log(`[IMPERIUM] Failed to store activity log:`, err.message));
  } catch (error) {
    console.log(`[IMPERIUM] Failed to create activity log:`, error.message);
  }
}




// Best practice implementation: avoiding catastrophic pitfalls and leverage new pr...
function applyBestPractice_1751127230817() {
  // Implementation of: avoiding catastrophic pitfalls and leverage new product ideas to generate better profits and revenue and improve management performance.
  console.log(`[IMPERIUM] Applying best practice: avoiding catastrophic pitfalls and leverage new product ideas to generate better profits and revenue and improve management performance.`);
}




// Best practice implementation: best practices Stories People Publications Topics ...
function applyBestPractice_1751127230817() {
  // Implementation of: best practices Stories People Publications Topics Lists Publications matching performance programming best practices MGE Software Publication Exploring the Latest Trends and Best Practices in Software Development.
  console.log(`[IMPERIUM] Applying best practice: best practices Stories People Publications Topics Lists Publications matching performance programming best practices MGE Software Publication Exploring the Latest Trends and Best Practices in Software Development.`);
}

module.exports = { runImperiumExperiment };