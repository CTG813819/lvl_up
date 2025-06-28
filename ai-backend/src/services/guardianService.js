const Experiment = require('../models/experiment');
const Proposal = require('../models/proposal');
const { suggestImprovement, createProposalWithDeduplication } = require('./aiServices');
const { aiStatus, logEvent } = require('../state');
const AILearningService = require('./aiLearningService');
const { AIQuotaService } = require('./aiQuotaService');

async function runGuardianExperiment(code, filePath) {
  // Only allow if it's Guardian's turn and phase is 'proposing'
  const canProcess = await AIQuotaService.canProcess('Guardian', 'proposing');
  if (!canProcess) {
    logEvent('[GUARDIAN] Not Guardian turn or not proposing phase/quota met. Skipping.');
    return { experiment: null, proposal: null };
  }
  
  if (aiStatus.Guardian.isLearning) {
    logEvent('[GUARDIAN] Paused for learning, skipping proposal.');
    return { experiment: null, proposal: null };
  }
  
  console.log(`[GUARDIAN] Starting experiment for file: ${filePath}`);
  
  try {
    const startTime = Date.now();
    
    // Get AI suggestion with learning context
    const suggestion = await suggestImprovement(code, filePath, 'Guardian');
    
    if (!suggestion) {
      console.log(`[GUARDIAN] No improvement needed for ${filePath}`);
      return { experiment: null, proposal: null };
    }
    
    // Validate that we have the required fields
    if (!suggestion.code || suggestion.code.trim() === '') {
      console.log(`[GUARDIAN] ⚠️ AI returned empty code for ${filePath}, skipping proposal`);
      
      // Provide learning feedback for empty code responses
      await AILearningService.learnFromProposal({
        aiType: 'Guardian',
        filePath: filePath,
        improvementType: suggestion.improvementType || 'system',
        userFeedback: 'rejected',
        userFeedbackReason: 'AI returned empty or invalid code. Please ensure code blocks are properly formatted and contain meaningful improvements.',
        status: 'rejected'
      }, 'rejected', 'AI returned empty or invalid code. Please ensure code blocks are properly formatted and contain meaningful improvements.');
      
      logEvent(`[GUARDIAN] Learning feedback provided for empty code response on ${filePath}`);
      return { experiment: null, proposal: null };
    }
    
    const executionTime = Date.now() - startTime;
    console.log(`[GUARDIAN] Generated suggestion for ${filePath} (${executionTime}ms)`);
    console.log(`[GUARDIAN] Code length: ${suggestion.code.length} characters`);
    
    // Create proposal with deduplication and learning
    const proposalResult = await createProposalWithDeduplication(
      'Guardian',
      filePath,
      code,
      suggestion.code,
      suggestion.reasoning,
      suggestion.improvementType
    );
    
    if (proposalResult.isDuplicate) {
      console.log(`[GUARDIAN] ⚠️ Skipping duplicate proposal for ${filePath} (similarity: ${proposalResult.similarity})`);
      
      // Provide learning feedback for duplicate proposals
      await AILearningService.learnFromProposal({
        aiType: 'Guardian',
        filePath: filePath,
        improvementType: suggestion.improvementType || 'system',
        userFeedback: 'rejected',
        userFeedbackReason: 'Duplicate proposal detected. Please provide more unique and innovative suggestions.',
        status: 'rejected'
      }, 'rejected', 'Duplicate proposal detected. Please provide more unique and innovative suggestions.');
      
      logEvent(`[GUARDIAN] Learning feedback provided for duplicate proposal on ${filePath}`);
      return { experiment: null, proposal: null };
    }
    
    if (proposalResult.error) {
      console.log(`[GUARDIAN] ❌ Error creating proposal for ${filePath}: ${proposalResult.error}`);
      
      // Provide learning feedback for proposal creation errors
      await AILearningService.learnFromProposal({
        aiType: 'Guardian',
        filePath: filePath,
        improvementType: suggestion.improvementType || 'system',
        userFeedback: 'rejected',
        userFeedbackReason: `Proposal creation failed: ${proposalResult.error}. Please ensure all required fields are provided.`,
        status: 'rejected'
      }, 'rejected', `Proposal creation failed: ${proposalResult.error}. Please ensure all required fields are provided.`);
      
      logEvent(`[GUARDIAN] Learning feedback provided for proposal creation error on ${filePath}`);
      return { experiment: null, proposal: null };
    }
    
    if (!proposalResult.proposal) {
      console.log(`[GUARDIAN] ❌ No proposal created for ${filePath}`);
      
      // Provide learning feedback for missing proposals
      await AILearningService.learnFromProposal({
        aiType: 'Guardian',
        filePath: filePath,
        improvementType: suggestion.improvementType || 'system',
        userFeedback: 'rejected',
        userFeedbackReason: 'No proposal was created. Please ensure your suggestions are valid and complete.',
        status: 'rejected'
      }, 'rejected', 'No proposal was created. Please ensure your suggestions are valid and complete.');
      
      logEvent(`[GUARDIAN] Learning feedback provided for missing proposal on ${filePath}`);
      return { experiment: null, proposal: null };
    }
    
    // Validate proposal data before creating
    if (!proposalResult.proposal.codeAfter || proposalResult.proposal.codeAfter.trim() === '') {
      console.log(`[GUARDIAN] ❌ Proposal missing codeAfter for ${filePath}, skipping`);
      
      // Provide learning feedback for invalid proposals
      await AILearningService.learnFromProposal({
        aiType: 'Guardian',
        filePath: filePath,
        improvementType: suggestion.improvementType || 'system',
        userFeedback: 'rejected',
        userFeedbackReason: 'Proposal missing improved code. Please ensure your suggestions include complete, valid code.',
        status: 'rejected'
      }, 'rejected', 'Proposal missing improved code. Please ensure your suggestions include complete, valid code.');
      
      logEvent(`[GUARDIAN] Learning feedback provided for invalid proposal on ${filePath}`);
      return { experiment: null, proposal: null };
    }
    
    console.log(`[GUARDIAN] Creating new proposal for ${filePath}`);
    
    // Save experiment with enhanced data
    const experiment = new Experiment({
      aiName: 'AI Guardian',
      experimentType: 'health-check',
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
    console.log(`[GUARDIAN] Experiment saved with ID: ${experiment._id}`);

    // Create proposal with all enhanced fields
    const proposal = new Proposal(proposalResult.proposal);
    
    try {
      await proposal.save();
      console.log(`[GUARDIAN] ✅ Proposal created with ID: ${proposal._id} for ${filePath}`);
      console.log(`[GUARDIAN] Confidence: ${proposal.confidence}, Learning applied: ${proposal.aiLearningApplied}`);
      
      // Increment quota for successful proposal creation
      await AIQuotaService.incrementPhaseProgress('Guardian', 'proposing');
      
      // Provide positive learning feedback for successful proposals
      await AILearningService.learnFromProposal(proposal, 'approved', 'Proposal created successfully with valid code and reasoning.');
      logEvent(`[GUARDIAN] Learning feedback provided for successful proposal on ${filePath}`);
      
    } catch (validationError) {
      console.error(`[GUARDIAN] ❌ Validation error creating proposal for ${filePath}:`, validationError.message);
      
      // Log detailed validation errors
      if (validationError.errors) {
        Object.keys(validationError.errors).forEach(field => {
          const error = validationError.errors[field];
          console.error(`[GUARDIAN] Validation error in field '${field}': ${error.message}`);
          console.error(`[GUARDIAN] Value: ${error.value}`);
          if (error.enumValues) {
            console.error(`[GUARDIAN] Valid enum values: ${error.enumValues.join(', ')}`);
          }
        });
      }
      
      // Provide learning feedback for validation errors
      await AILearningService.learnFromProposal({
        aiType: 'Guardian',
        filePath: filePath,
        improvementType: suggestion.improvementType || 'system',
        userFeedback: 'rejected',
        userFeedbackReason: `Validation error: ${validationError.message}. Please ensure all fields meet the required format and constraints.`,
        status: 'rejected'
      }, 'rejected', `Validation error: ${validationError.message}. Please ensure all fields meet the required format and constraints.`);
      
      logEvent(`[GUARDIAN] Learning feedback provided for validation error on ${filePath}`);
      
      // Try to fix common validation issues
      if (validationError.errors?.improvementType) {
        console.log(`[GUARDIAN] 🔧 Attempting to fix improvement type validation error...`);
        proposal.improvementType = 'refactor'; // Use safe default
        try {
          await proposal.save();
          console.log(`[GUARDIAN] ✅ Proposal created with fixed improvement type for ${filePath}`);
          
          // Provide learning feedback for the fix
          await AILearningService.learnFromProposal(proposal, 'approved', 'Proposal created successfully after fixing improvement type validation.');
          logEvent(`[GUARDIAN] Learning feedback provided for fixed proposal on ${filePath}`);
          
        } catch (retryError) {
          console.error(`[GUARDIAN] ❌ Still failed after fix attempt:`, retryError.message);
          
          // Provide learning feedback for the retry failure
          await AILearningService.learnFromProposal({
            aiType: 'Guardian',
            filePath: filePath,
            improvementType: 'system',
            userFeedback: 'rejected',
            userFeedbackReason: `Failed to create proposal even after fix attempt: ${retryError.message}`,
            status: 'rejected'
          }, 'rejected', `Failed to create proposal even after fix attempt: ${retryError.message}`);
          
          logEvent(`[GUARDIAN] Learning feedback provided for retry failure on ${filePath}`);
          throw retryError;
        }
      } else {
        throw validationError;
      }
    }

    return { experiment, proposal };
  } catch (error) {
    console.error(`[GUARDIAN] ❌ Error in experiment for ${filePath}:`, error);
    
    // Provide learning feedback for general errors
    await AILearningService.learnFromProposal({
      aiType: 'Guardian',
      filePath: filePath,
      improvementType: 'system',
      userFeedback: 'rejected',
      userFeedbackReason: `Experiment failed: ${error.message}. Please ensure stable and reliable suggestions.`,
      status: 'rejected'
    }, 'rejected', `Experiment failed: ${error.message}. Please ensure stable and reliable suggestions.`);
    
    logEvent(`[GUARDIAN] Learning feedback provided for experiment error on ${filePath}`);
    throw error;
  }
}

module.exports = { runGuardianExperiment };