const crypto = require('crypto');
const Proposal = require('../models/proposal');

class DeduplicationService {
  /**
   * Generate a hash for code content
   */
  static generateCodeHash(codeBefore, codeAfter) {
    const combined = codeBefore + '|||' + codeAfter;
    return crypto.createHash('sha256').update(combined).digest('hex');
  }

  /**
   * Generate a semantic hash based on code structure and patterns
   */
  static generateSemanticHash(code) {
    // Remove comments, whitespace, and normalize
    const normalized = code
      .replace(/\/\*[\s\S]*?\*\/|\/\/.*$/gm, '') // Remove comments
      .replace(/\s+/g, ' ') // Normalize whitespace
      .replace(/[{}();,]/g, '') // Remove punctuation
      .trim();
    
    return crypto.createHash('md5').update(normalized).digest('hex');
  }

  /**
   * Calculate similarity score between two code snippets
   */
  static calculateSimilarity(code1, code2) {
    const lines1 = code1.split('\n').filter(line => line.trim().length > 0);
    const lines2 = code2.split('\n').filter(line => line.trim().length > 0);
    
    if (lines1.length === 0 || lines2.length === 0) return 0;
    
    const commonLines = lines1.filter(line => 
      lines2.some(line2 => this.normalizeLine(line) === this.normalizeLine(line2))
    );
    
    return commonLines.length / Math.max(lines1.length, lines2.length);
  }

  /**
   * Normalize a line for comparison
   */
  static normalizeLine(line) {
    return line
      .trim()
      .replace(/\s+/g, ' ')
      .replace(/[{}();,]/g, '')
      .toLowerCase();
  }

  /**
   * Check for exact duplicates
   */
  static async checkExactDuplicate(aiType, filePath, codeBefore, codeAfter) {
    const codeHash = this.generateCodeHash(codeBefore, codeAfter);
    
    const existing = await Proposal.findOne({
      aiType,
      filePath,
      codeHash
    });
    
    return existing;
  }

  /**
   * Check for semantic duplicates
   */
  static async checkSemanticDuplicate(aiType, filePath, codeBefore, codeAfter, threshold = 0.8) {
    const semanticHash = this.generateSemanticHash(codeBefore + codeAfter);
    
    // Find proposals with similar semantic hash
    const existing = await Proposal.findOne({
      aiType,
      filePath,
      semanticHash
    });
    
    if (existing) {
      const similarity = this.calculateSimilarity(
        existing.codeBefore + existing.codeAfter,
        codeBefore + codeAfter
      );
      
      if (similarity >= threshold) {
        return { proposal: existing, similarity };
      }
    }
    
    return null;
  }

  /**
   * Check for similar proposals in the same file
   */
  static async checkSimilarProposals(aiType, filePath, codeBefore, codeAfter, threshold = 0.7) {
    const recentProposals = await Proposal.find({
      aiType,
      filePath,
      createdAt: { $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) } // Last 24 hours
    }).sort({ createdAt: -1 }).limit(10);
    
    for (const proposal of recentProposals) {
      const similarity = this.calculateSimilarity(
        proposal.codeBefore + proposal.codeAfter,
        codeBefore + codeAfter
      );
      
      if (similarity >= threshold) {
        return { proposal, similarity };
      }
    }
    
    return null;
  }

  /**
   * Comprehensive duplicate check
   */
  static async checkDuplicates(aiType, filePath, codeBefore, codeAfter) {
    console.log(`[DEDUPLICATION] Checking duplicates for ${aiType} on ${filePath}`);
    
    // Check exact duplicate
    const exactDuplicate = await this.checkExactDuplicate(aiType, filePath, codeBefore, codeAfter);
    if (exactDuplicate) {
      console.log(`[DEDUPLICATION] ⚠️ Exact duplicate found: ${exactDuplicate._id}`);
      return {
        isDuplicate: true,
        type: 'exact',
        proposal: exactDuplicate,
        similarity: 1.0
      };
    }
    
    // Check semantic duplicate
    const semanticDuplicate = await this.checkSemanticDuplicate(aiType, filePath, codeBefore, codeAfter);
    if (semanticDuplicate) {
      console.log(`[DEDUPLICATION] ⚠️ Semantic duplicate found: ${semanticDuplicate.proposal._id} (similarity: ${semanticDuplicate.similarity})`);
      return {
        isDuplicate: true,
        type: 'semantic',
        proposal: semanticDuplicate.proposal,
        similarity: semanticDuplicate.similarity
      };
    }
    
    // Check similar proposals
    const similarProposal = await this.checkSimilarProposals(aiType, filePath, codeBefore, codeAfter);
    if (similarProposal) {
      console.log(`[DEDUPLICATION] ⚠️ Similar proposal found: ${similarProposal.proposal._id} (similarity: ${similarProposal.similarity})`);
      return {
        isDuplicate: true,
        type: 'similar',
        proposal: similarProposal.proposal,
        similarity: similarProposal.similarity
      };
    }
    
    console.log(`[DEDUPLICATION] ✅ No duplicates found`);
    return { isDuplicate: false };
  }

  /**
   * Get duplicate statistics
   */
  static async getDuplicateStats() {
    const stats = await Proposal.aggregate([
      {
        $group: {
          _id: '$aiType',
          total: { $sum: 1 },
          duplicates: { $sum: { $cond: [{ $ne: ['$duplicateOf', null] }, 1, 0] } },
          unique: { $sum: { $cond: [{ $eq: ['$duplicateOf', null] }, 1, 0] } }
        }
      }
    ]);
    
    return stats;
  }
}

module.exports = DeduplicationService; 