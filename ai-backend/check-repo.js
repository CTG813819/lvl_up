require('dotenv').config();

async function checkRepository() {
  console.log('🔍 Checking GitHub Repository...\n');
  
  const repoName = process.env.GITHUB_REPO;
  console.log(`Repository: ${repoName}`);
  console.log(`Token: ${process.env.GITHUB_TOKEN ? '✅ Set' : '❌ Missing'}\n`);
  
  if (!repoName) {
    console.log('❌ No repository name found in environment variables');
    return;
  }
  
  try {
    // Initialize Octokit
    const { Octokit } = await import('@octokit/rest');
    const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
    
    // Parse repository name
    const [owner, repo] = repoName.split('/');
    console.log(`Owner: ${owner}`);
    console.log(`Repo: ${repo}\n`);
    
    // Check if repository exists
    console.log('📡 Checking repository existence...');
    const response = await octokit.repos.get({
      owner: owner,
      repo: repo
    });
    
    console.log('✅ Repository found!');
    console.log(`   - Name: ${response.data.full_name}`);
    console.log(`   - Description: ${response.data.description || 'No description'}`);
    console.log(`   - Visibility: ${response.data.private ? 'Private' : 'Public'}`);
    console.log(`   - Default branch: ${response.data.default_branch}`);
    console.log(`   - Created: ${response.data.created_at}`);
    console.log(`   - URL: ${response.data.html_url}`);
    console.log(`   - Clone URL: ${response.data.clone_url}\n`);
    
    // Check repository permissions
    console.log('🔐 Checking permissions...');
    const permissions = response.data.permissions;
    if (permissions) {
      console.log(`   - Admin: ${permissions.admin ? '✅' : '❌'}`);
      console.log(`   - Push: ${permissions.push ? '✅' : '❌'}`);
      console.log(`   - Pull: ${permissions.pull ? '✅' : '❌'}`);
    }
    
    // Check if repository has content
    console.log('\n📁 Checking repository content...');
    try {
      const contents = await octokit.repos.getContent({
        owner: owner,
        repo: repo,
        path: ''
      });
      
      if (Array.isArray(contents.data)) {
        console.log(`   - Files/folders: ${contents.data.length}`);
        contents.data.forEach(item => {
          console.log(`     - ${item.name} (${item.type})`);
        });
      } else {
        console.log('   - Single file repository');
      }
    } catch (contentError) {
      console.log('   - Repository appears to be empty');
    }
    
    console.log('\n🎉 Repository is accessible and ready for AI learning system!');
    
  } catch (error) {
    if (error.status === 404) {
      console.log('❌ Repository not found');
      console.log(`   The repository "${repoName}" does not exist on GitHub.`);
      console.log('\n🔧 To fix this:');
      console.log('   1. Go to https://github.com/new');
      console.log(`   2. Create a repository named "${repo}"`);
      console.log('   3. Make it public or private');
      console.log('   4. Run this check again');
    } else {
      console.log('❌ Error checking repository:');
      console.log(`   Status: ${error.status}`);
      console.log(`   Message: ${error.message}`);
    }
  }
}

// Run the check
checkRepository().catch(console.error); 