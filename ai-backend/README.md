# AI Backend Setup

## Prerequisites

1. **Node.js** (v16 or higher) - Download from https://nodejs.org/
2. **MongoDB Atlas** account - Create at https://www.mongodb.com/atlas
3. **OpenAI API Key** - Get from https://platform.openai.com/
4. **GitHub Personal Access Token** - Create at https://github.com/settings/tokens

## Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Create environment file**:
   Create a `.env` file in the `ai-backend` directory with:
   ```
   # MongoDB Connection
   MONGODB_URI=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/your-database
   
   # OpenAI API
   OPENAI_API_KEY=your-openai-api-key
   
   # GitHub Configuration
   GITHUB_TOKEN=your-github-personal-access-token
   GITHUB_REPO=your-username/your-repo-name
   GITHUB_USER=your-github-username
   GITHUB_EMAIL=your-github-email
   
   # Git Repository Path
   GIT_REPO_PATH=/tmp/lvlup-repo
   
   # Server Port
   PORT=4000
   ```

3. **Start the server**:
   ```bash
   node src/index.js
   ```

## Features

- **AI Code Analysis**: Imperium, Sandbox, and Guardian AIs analyze your Flutter code
- **Proposal Management**: AIs create improvement proposals for user approval
- **GitHub Integration**: Approved proposals are automatically applied to your repository
- **Real-time Updates**: Socket.IO provides real-time communication with the Flutter app
- **Test Automation**: Proposals are tested before being applied to GitHub

## API Endpoints

- `GET /health` - Health check
- `GET /api/proposals` - Get all proposals
- `POST /api/proposals/:id/approve` - Approve a proposal
- `POST /api/proposals/:id/reject` - Reject a proposal
- `GET /api/proposals/debug` - Debug proposal status

## Troubleshooting

1. **MongoDB Connection Issues**: Check your MongoDB Atlas connection string
2. **OpenAI API Errors**: Verify your API key and billing status
3. **GitHub Permission Errors**: Ensure your token has repo access
4. **Port Already in Use**: Change the PORT in .env file

## Development

The backend automatically:
- Pulls latest code from GitHub on startup
- Scans Dart files for analysis
- Runs AI experiments every minute
- Applies approved proposals to GitHub
- Sends real-time updates to the Flutter app
