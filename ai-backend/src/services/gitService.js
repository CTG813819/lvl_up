const simpleGit = require('simple-git');
const git = simpleGit(process.env.GIT_REPO_PATH);

async function applyProposalAndPush(filePath, newCode, branch = 'ai-improvements') {
  await git.checkout(branch);
  require('fs').writeFileSync(filePath, newCode);
  await git.add(filePath);
  await git.commit('AI: Applied code improvement');
  await git.push('origin', branch);
}
module.exports = { applyProposalAndPush };