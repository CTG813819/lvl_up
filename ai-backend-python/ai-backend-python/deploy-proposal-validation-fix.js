const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// === CONFIGURATION ===
const EC2_HOST = '34.202.215.209'; // Updated EC2 IP
const EC2_USER = 'ubuntu';
const REMOTE_PATH = '/home/ubuntu/ai-backend';
const LOCAL_PATH = '.'; // Use current directory
const SSH_KEY = '/home/ubuntu/ai-backend/New.pem'; // Updated key path

// === PATCH aiLearningService.js ===
const aiLearningServicePath = path.join(LOCAL_PATH, 'src/services/aiLearningService.js');
let aiLearningServiceCode = fs.readFileSync(aiLearningServicePath, 'utf8');

// Replace the learnFromProposal method
aiLearningServiceCode = aiLearningServiceCode.replace(
  /static async learnFromProposal\([\s\S]+?catch \(error\) \{[\s\S]+?throw error;\n\s+\}\n\s+\}/,
  `static async learnFromProposal(proposal, status, feedbackReason) {
    console.log(\`[AI_LEARNING_SERVICE] 🧠 Learning from proposal: \${status} for \${proposal.aiType}\`);

    // Always check for missing fields, even if proposal is a Mongoose doc
    const requiredFields = ['codeBefore', 'codeAfter', 'aiType', 'reasoning', 'improvementType'];
    const missingFields = requiredFields.filter(field => !proposal[field]);

    if (missingFields.length > 0) {
      console.log(\`[AI_LEARNING_SERVICE] ⚠️ Proposal missing required fields: \${missingFields.join(', ')}\`);
      console.log(\`[AI_LEARNING_SERVICE] Skipping proposal save to avoid validation errors\`);

      // Store learning entry without saving the proposal
      await Learning.create({
        aiType: proposal.aiType || 'Unknown',
        proposalId: proposal._id || null,
        status: status === 'approved' ? 'approved' : 'rejected',
        feedbackReason,
        learningKey: 'proposal_feedback',
        learningValue: \`Proposal \${status}: \${feedbackReason} (Missing fields: \${missingFields.join(', ')})\`,
        filePath: proposal.filePath || '',
        improvementType: proposal.improvementType || 'system'
      });

      console.log(\`[AI_LEARNING_SERVICE] ✅ Learning stored for incomplete proposal\`);
      return;
    }

    try {
      // Ensure proposal is a Mongoose document
      if (!(proposal instanceof ProposalModel)) {
        proposal = new ProposalModel(proposal);
      }

      // Update proposal status
      proposal.status = status;
      proposal.userFeedback = status;
      proposal.userFeedbackReason = feedbackReason;
      await proposal.save();

      // Store learning entry
      await Learning.create({
        aiType: proposal.aiType,
        proposalId: proposal._id,
        status: status === 'approved' ? 'approved' : 'rejected',
        feedbackReason,
        learningKey: 'proposal_feedback',
        learningValue: \`Proposal \${status}: \${feedbackReason}\`,
        filePath: proposal.filePath,
        improvementType: proposal.improvementType
      });

      // Trigger comprehensive AI learning cycle with internet research
      if (proposal.codeBefore && proposal.codeAfter && proposal.aiType && proposal.reasoning && proposal.improvementType) {
        await this.triggerComprehensiveLearning(proposal, status, feedbackReason);
      } else {
        console.log(\`[AI_LEARNING_SERVICE] ⚠️ Skipping comprehensive learning for incomplete proposal\`);
      }

      console.log(\`[AI_LEARNING_SERVICE] ✅ Learning from proposal completed for \${proposal.aiType}\`);

    } catch (error) {
      console.error(\`[AI_LEARNING_SERVICE] ❌ Error learning from proposal:\`, error);
      throw error;
    }
  }`
);