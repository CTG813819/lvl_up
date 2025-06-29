const OpenAI = require('openai');
const DeduplicationService = require('./deduplicationService');
const AILearningService = require('./aiLearningService');
const Proposal = require('../models/proposal');

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const MAX_CODE_LENGTH = 8000; // Safe limit to avoid context window issues

async function suggestImprovement(code, filePath, aiType) {
  console.log(`[AI_SERVICES] ${aiType} analyzing ${filePath} (code length: ${code.length})`);
  
  try {
    // Check if code is too long and truncate if necessary
    const maxCodeLength = 6000; // Safe limit for user prompt
    if (code.length > maxCodeLength) {
      console.log(`[AI_SERVICES] ⚠️ Code too long (${code.length} chars), truncating to ${maxCodeLength} chars`);
      code = code.substring(0, maxCodeLength) + '\n// ... (code truncated for token limit)';
    }
    
    // Get learning context
    const AILearningService = require('./aiLearningService');
    const learningContext = await AILearningService.getLearningContext(aiType);
    console.log(`[AI_SERVICES] Generated learning context for ${aiType} (length: ${learningContext.length})`);

    const systemPrompt = await getSystemPrompt(aiType, code, filePath);
    console.log(`[AI_SERVICES] Generated system prompt for ${aiType} with learning integration`);

    let userPrompt = `Analyze this code and suggest improvements if needed:

\`\`\`dart
${code}
\`\`\`

If you find meaningful improvements, respond with:
IMPROVEMENT_TYPE: [type]
IMPROVED_CODE:
\`\`\`dart
[improved code here]
\`\`\`
REASONING: [explanation]

If no meaningful improvement is needed, respond with: NO_IMPROVEMENT_NEEDED`;

    // Check total prompt length to avoid token limit
    const totalPromptLength = systemPrompt.length + userPrompt.length;
    console.log(`[AI_SERVICES] Total prompt length: ${totalPromptLength} characters`);
    
    if (totalPromptLength > 12000) {
      console.log(`[AI_SERVICES] ⚠️ Prompt too long (${totalPromptLength} chars), truncating code further`);
      const maxUserPromptLength = 12000 - systemPrompt.length - 500; // Leave room for safety
      userPrompt = `Analyze this code and suggest improvements if needed:

\`\`\`dart
${code.substring(0, maxUserPromptLength)}...
\`\`\`

If you find meaningful improvements, respond with:
IMPROVEMENT_TYPE: [type]
IMPROVED_CODE:
\`\`\`dart
[improved code here]
\`\`\`
REASONING: [explanation]

If no meaningful improvement is needed, respond with: NO_IMPROVEMENT_NEEDED`;
    }

    const response = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      max_tokens: 2000,
      temperature: 0.3
    });

    const aiResponse = response.choices[0].message.content;
    console.log(`[AI_SERVICES] ${aiType} response: ${aiResponse.substring(0, 200)}...`);
    
    return parseAIResponse(aiResponse);
  } catch (error) {
    console.error(`[AI_SERVICES] Error in ${aiType} suggestion:`, error);
    return { type: 'ERROR', error: error.message };
  }
}

function parseAIResponse(response) {
  console.log(`[AI_SERVICES] Parsing AI response: ${response.substring(0, 200)}...`);
  
  // Check if no improvement is needed
  if (response.includes('NO_IMPROVEMENT_NEEDED')) {
    console.log('[AI_SERVICES] No improvement needed detected');
    return { type: 'NO_IMPROVEMENT' };
  }
  
  // Parse structured response - handle both IMPROVED_CODE and CODE formats
  const improvementTypeMatch = response.match(/IMPROVEMENT_TYPE:\s*(.+)/i);
  const reasoningMatch = response.match(/REASONING:\s*(.+)/i);
  
  // Try multiple code block patterns
  let codeMatch = response.match(/IMPROVED_CODE:\s*```(?:\w+)?\s*\n([\s\S]*?)\n```/i);
  if (!codeMatch) {
    codeMatch = response.match(/CODE:\s*```(?:\w+)?\s*\n([\s\S]*?)\n```/i);
  }
  if (!codeMatch) {
    codeMatch = response.match(/```(?:\w+)?\s*\n([\s\S]*?)\n```/i);
  }
  
  console.log(`[AI_SERVICES] Parsed values:`);
  console.log(`[AI_SERVICES] - Raw improvement type: ${improvementTypeMatch?.[1]?.trim() || 'not found'}`);
  console.log(`[AI_SERVICES] - Reasoning: ${reasoningMatch?.[1]?.trim() || 'not found'}`);
  console.log(`[AI_SERVICES] - Code found: ${codeMatch ? 'yes' : 'no'}`);
  
  // If no code block found, try alternative parsing
  if (!codeMatch) {
    console.log('[AI_SERVICES] No code block found, trying alternative parsing...');
    
    // Try to find code after IMPROVED_CODE: without backticks
    const improvedCodeMatch = response.match(/IMPROVED_CODE:\s*\n([\s\S]*?)(?=\n(?:REASONING|$))/i);
    if (improvedCodeMatch) {
      console.log('[AI_SERVICES] Found code after IMPROVED_CODE: without backticks');
      const code = improvedCodeMatch[1].trim();
      
      // Check if the code is meaningful (not just whitespace or comments)
      if (code.length > 10 && !code.match(/^\s*(?:\/\/|\/\*|\*|\#)/)) {
        return {
          type: 'IMPROVEMENT',
          improvementType: normalizeImprovementType(improvementTypeMatch?.[1]?.trim() || 'refactor'),
          reasoning: reasoningMatch?.[1]?.trim() || 'Code improvement suggested',
          code: code
        };
      }
    }
    
    // If still no valid code found, check if the entire response might be code
    const trimmedResponse = response.trim();
    if (trimmedResponse.length > 20 && !trimmedResponse.includes('IMPROVEMENT_TYPE') && !trimmedResponse.includes('REASONING')) {
      console.log('[AI_SERVICES] Treating entire response as code');
      return {
        type: 'IMPROVEMENT',
        improvementType: 'refactor',
        reasoning: 'Code improvement suggested',
        code: trimmedResponse
      };
    }
    
    console.log('[AI_SERVICES] No valid code found in response, treating as no improvement needed');
    return { type: 'NO_IMPROVEMENT' };
  }
  
  // Normalize improvement type to match enum values
  const rawImprovementType = improvementTypeMatch?.[1]?.trim() || 'refactor';
  const normalizedImprovementType = normalizeImprovementType(rawImprovementType);
  
  console.log(`[AI_SERVICES] Normalized improvement type: ${rawImprovementType} -> ${normalizedImprovementType}`);
  
  const code = codeMatch[1].trim();
  
  // Validate that the code is meaningful
  if (code.length < 10) {
    console.log('[AI_SERVICES] Code too short, treating as no improvement needed');
    return { type: 'NO_IMPROVEMENT' };
  }
  
  return {
    type: 'IMPROVEMENT',
    improvementType: normalizedImprovementType,
    reasoning: reasoningMatch?.[1]?.trim() || 'Code improvement suggested',
    code: code
  };
}

function normalizeImprovementType(type) {
  const typeMap = {
    'performance': 'performance',
    'Performance': 'performance',
    'PERFORMANCE': 'performance',
    'readability': 'readability',
    'Readability': 'readability',
    'READABILITY': 'readability',
    'security': 'security',
    'Security': 'security',
    'SECURITY': 'security',
    'bug-fix': 'bug-fix',
    'Bug-fix': 'bug-fix',
    'Bug Fix': 'bug-fix',
    'BUG-FIX': 'bug-fix',
    'bugfix': 'bug-fix',
    'Bugfix': 'bug-fix',
    'refactor': 'refactor',
    'Refactor': 'refactor',
    'REFACTOR': 'refactor',
    'feature': 'feature',
    'Feature': 'feature',
    'FEATURE': 'feature'
  };
  
  return typeMap[type] || 'refactor'; // Default to refactor if unknown
}

async function createProposalWithDeduplication(aiType, filePath, codeBefore, codeAfter, reasoning, improvementType) {
  if (aiType === 'Conquest') {
    // Skip deduplication/throttling for Conquest (handled elsewhere)
    // ... existing code ...
  }

  // Throttling: limit to 15 pending proposals per AI
  const pendingCount = await Proposal.countDocuments({ aiType, status: 'pending' });
  if (pendingCount >= 15) {
    console.log(`[AI_SERVICES] Throttling: ${aiType} has ${pendingCount} pending proposals, skipping new proposal.`);
    return {
      isDuplicate: true,
      error: 'Throttling: too many pending proposals',
      proposal: null
    };
  }

  // Deduplication: check for duplicates (already implemented)
  const duplicateCheck = await DeduplicationService.checkDuplicates(aiType, filePath, codeBefore, codeAfter);
  if (duplicateCheck.isDuplicate && duplicateCheck.similarity >= 0.9) {
    return {
      isDuplicate: true,
      originalProposal: duplicateCheck.proposal,
      similarity: duplicateCheck.similarity
    };
  }

  // Quality control: keep only the best proposal per file/type/AI
  const best = await Proposal.findOne({
    aiType,
    filePath,
    improvementType,
    status: 'pending'
  }).sort({ confidence: -1, diffScore: -1 });
  // If a better or equal proposal exists, skip
  if (best && best.confidence >= 0.99) {
    return {
      isDuplicate: true,
      originalProposal: best,
      similarity: 1.0
    };
  }
  // If this is better, remove the old one
  if (best && best.confidence < 0.99) {
    await Proposal.deleteOne({ _id: best._id });
  }

  // Generate hashes for the proposal
  const codeHash = DeduplicationService.generateCodeHash(codeBefore, codeAfter);
  const semanticHash = DeduplicationService.generateSemanticHash(codeBefore + codeAfter);

  // Create proposal object with all required fields
  const proposal = {
    aiType,
    filePath,
    codeBefore: codeBefore.trim(),
    codeAfter: codeAfter.trim(),
    aiReasoning: reasoning || `${aiType} AI analysis`,
    improvementType: improvementType || 'refactor',
    codeHash,
    semanticHash,
    diffScore: duplicateCheck.isDuplicate ? duplicateCheck.similarity : 0,
    duplicateOf: duplicateCheck.isDuplicate ? duplicateCheck.proposal._id : null
  };

  // Apply AI learning
  const enhancedProposal = await AILearningService.applyLearning(proposal, aiType);

  // Save proposal
  const savedProposal = await Proposal.create(enhancedProposal);

  // Update Codex and learning dashboard (asynchronously)
  setImmediate(() => {
    try {
      AILearningService.updateCodexAndDashboard(aiType);
    } catch (e) {
      console.error('[AI_SERVICES] Error updating Codex/dashboard:', e);
    }
  });

  return {
    isDuplicate: false,
    proposal: savedProposal
  };
}

async function getSystemPrompt(aiType, code, filePath) {
  // Get learning insights with a limit to avoid token overflow
  const AILearningService = require('./aiLearningService');
  const allInsights = await AILearningService.getLearningInsights(aiType);
  
  // Limit to top 5 most important insights to avoid token limit
  const insights = allInsights.slice(0, 5);
  
  console.log(`[AI_SERVICES] 📚 Retrieved ${insights.length} learning insights for ${aiType} (limited from ${allInsights.length} total)`);
  
  // Log specific learnings
  insights.forEach((insight, index) => {
    console.log(`[AI_SERVICES] 📖 Learning ${index + 1} for ${aiType}: ${insight.lesson}`);
  });
  
  // Truncate code if it's too long to avoid token limit
  const maxCodeLength = 4000; // Safe limit for code in system prompt
  const truncatedCode = code.length > maxCodeLength 
    ? code.substring(0, maxCodeLength) + '\n// ... (code truncated for token limit)'
    : code;
  
  const basePrompt = `You are ${aiType}, an AI specialized in Flutter/Dart code analysis and improvement. 
  
CRITICAL LEARNING FROM PREVIOUS FAILURES:
${insights.map(insight => `- ${insight.lesson}`).join('\n')}

KEY RULES:
- Use 'flutter pub' not 'dart pub'
- Ensure Flutter SDK is available
- Follow Flutter/Dart best practices
- Consider null safety
- Avoid breaking existing functionality
- Test that code compiles before suggesting

TASK: Analyze the Dart code and suggest improvements if needed.

RESPONSE FORMAT:
IMPROVEMENT_TYPE: [readability|performance|bugfix|feature|refactor]
IMPROVED_CODE:
\`\`\`dart
[improved code]
\`\`\`
REASONING: [explanation]

If no improvement needed, respond: NO_IMPROVEMENT_NEEDED

CODE TO ANALYZE:
File: ${filePath}
\`\`\`dart
${truncatedCode}
\`\`\``;

  console.log(`[AI_SERVICES] 🧠 ${aiType} system prompt includes ${insights.length} learned lessons (${basePrompt.length} chars)`);
  
  return basePrompt;
}

module.exports = { 
  suggestImprovement, 
  createProposalWithDeduplication,
  parseAIResponse,
  getSystemPrompt
};