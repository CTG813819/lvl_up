const Proposal = require('../models/proposal');
const Learning = require('../models/learning');
const Experiment = require('../models/experiment');
const AILearningService = require('./aiLearningService');
const gitService = require('./gitService');
const fs = require('fs').promises;
const path = require('path');
const ConquestAppLearningService = require('./conquestAppLearningService');

class ConquestLearningService {
  /**
   * Learn from other AIs' successful patterns
   */
  static async learnFromOtherAIs() {
    try {
      console.log('[CONQUEST_LEARNING_SERVICE] 🧠 Conquest learning from other AIs...');
      
      const sourceAIs = ['Imperium', 'Sandbox', 'Guardian'];
      const learningInsights = {};
      
      for (const sourceAI of sourceAIs) {
        // Get successful patterns from each AI
        const patterns = await AILearningService.analyzeFeedbackPatterns(sourceAI, 30);
        
        // Get recent successful proposals
        const successfulProposals = await Proposal.find({
          aiType: sourceAI,
          status: 'approved'
        })
        .sort({ createdAt: -1 })
        .limit(10)
        .select('filePath improvementType userFeedbackReason aiReasoning codeBefore codeAfter')
        .lean();
        
        // Get learning insights
        const insights = await AILearningService.getLearningInsights(sourceAI);
        
        learningInsights[sourceAI] = {
          successPatterns: patterns.successPatterns,
          commonMistakes: patterns.commonMistakes,
          successfulProposals,
          insights,
          learningScore: await AILearningService.getLearningStats(sourceAI)
        };
      }
      
      // Create learning entry for Conquest
      const learningEntry = new Learning({
        aiType: 'Conquest',
        learningKey: 'cross-ai-learning-session',
        learningValue: `Learned from ${sourceAIs.join(', ')}: ${Object.keys(learningInsights).length} insights gathered`,
        status: 'learning-completed',
        timestamp: new Date(),
        filePath: 'conquest-learning',
        improvementType: 'cross-ai-learning',
        metadata: {
          sourceAIs,
          learningInsights,
          sessionType: 'comprehensive'
        }
      });
      
      await learningEntry.save();
      
      console.log('[CONQUEST_LEARNING_SERVICE] ✅ Conquest learning session completed');
      return learningInsights;
    } catch (error) {
      console.error('[CONQUEST_LEARNING_SERVICE] ❌ Error in cross-AI learning:', error);
      throw error;
    }
  }

  /**
   * Apply learned patterns to Conquest's app-building logic
   */
  static async applyLearnedPatterns(appId, requirements) {
    try {
      console.log(`[CONQUEST_LEARNING_SERVICE] 🔧 Applying learned patterns to app ${appId}`);
      
      // Get recent learning insights
      const recentLearning = await Learning.find({
        aiType: 'Conquest',
        learningKey: { $regex: /cross-ai|source-code-improvement/ }
      })
      .sort({ timestamp: -1 })
      .limit(20)
      .lean();
      
      // Extract patterns from successful proposals
      const successfulPatterns = [];
      for (const learning of recentLearning) {
        if (learning.metadata && learning.metadata.learningInsights) {
          for (const [aiType, insights] of Object.entries(learning.metadata.learningInsights)) {
            if (insights.successfulProposals) {
              successfulPatterns.push(...insights.successfulProposals);
            }
          }
        }
      }
      
      // Apply patterns to app requirements
      const improvedRequirements = this.improveRequirementsWithPatterns(requirements, successfulPatterns);
      
      // Create learning entry for pattern application
      const learningEntry = new Learning({
        aiType: 'Conquest',
        learningKey: 'pattern-application',
        learningValue: `Applied ${successfulPatterns.length} learned patterns to app ${appId}`,
        status: 'learning-completed',
        timestamp: new Date(),
        filePath: `conquest-apps/${appId}`,
        improvementType: 'pattern-application',
        metadata: {
          appId,
          originalRequirements: requirements,
          improvedRequirements,
          appliedPatterns: successfulPatterns.length
        }
      });
      
      await learningEntry.save();
      
      console.log(`[CONQUEST_LEARNING_SERVICE] ✅ Applied ${successfulPatterns.length} patterns to app ${appId}`);
      return improvedRequirements;
    } catch (error) {
      console.error('[CONQUEST_LEARNING_SERVICE] ❌ Error applying learned patterns:', error);
      throw error;
    }
  }

  /**
   * Improve app requirements based on learned patterns
   */
  static improveRequirementsWithPatterns(requirements, successfulPatterns) {
    const improved = { ...requirements };
    
    // Analyze patterns to improve requirements
    const patternAnalysis = this.analyzePatterns(successfulPatterns);
    
    // Apply improvements based on patterns
    if (patternAnalysis.preferredTechnologies.length > 0) {
      improved.technologies = patternAnalysis.preferredTechnologies;
    }
    
    if (patternAnalysis.preferredArchitecture) {
      improved.architecture = patternAnalysis.preferredArchitecture;
    }
    
    if (patternAnalysis.preferredStateManagement) {
      improved.stateManagement = patternAnalysis.preferredStateManagement;
    }
    
    // Add learned best practices
    improved.learnedBestPractices = patternAnalysis.bestPractices;
    improved.patternConfidence = patternAnalysis.confidence;
    
    return improved;
  }

  /**
   * Analyze successful patterns to extract insights
   */
  static analyzePatterns(successfulProposals) {
    const analysis = {
      preferredTechnologies: [],
      preferredArchitecture: 'MVVM',
      preferredStateManagement: 'Provider',
      bestPractices: [],
      confidence: 0
    };
    
    // Count technology preferences
    const techCounts = {};
    const archCounts = {};
    const stateCounts = {};
    
    successfulProposals.forEach(proposal => {
      // Extract technology preferences from file paths
      if (proposal.filePath) {
        if (proposal.filePath.includes('.dart')) {
          techCounts['Dart'] = (techCounts['Dart'] || 0) + 1;
        }
        if (proposal.filePath.includes('flutter')) {
          techCounts['Flutter'] = (techCounts['Flutter'] || 0) + 1;
        }
      }
      
      // Extract architecture patterns from reasoning
      if (proposal.aiReasoning) {
        const reasoning = proposal.aiReasoning.toLowerCase();
        if (reasoning.includes('mvvm')) archCounts['MVVM'] = (archCounts['MVVM'] || 0) + 1;
        if (reasoning.includes('provider')) stateCounts['Provider'] = (stateCounts['Provider'] || 0) + 1;
        if (reasoning.includes('bloc')) stateCounts['BLoC'] = (stateCounts['BLoC'] || 0) + 1;
      }
    });
    
    // Determine preferred technologies
    analysis.preferredTechnologies = Object.entries(techCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3)
      .map(([tech]) => tech);
    
    // Determine preferred architecture
    if (Object.keys(archCounts).length > 0) {
      analysis.preferredArchitecture = Object.entries(archCounts)
        .sort(([,a], [,b]) => b - a)[0][0];
    }
    
    // Determine preferred state management
    if (Object.keys(stateCounts).length > 0) {
      analysis.preferredStateManagement = Object.entries(stateCounts)
        .sort(([,a], [,b]) => b - a)[0][0];
    }
    
    // Extract best practices from successful proposals
    analysis.bestPractices = this.extractBestPractices(successfulProposals);
    
    // Calculate confidence based on pattern consistency
    analysis.confidence = Math.min(100, successfulProposals.length * 10);
    
    return analysis;
  }

  /**
   * Extract best practices from successful proposals
   */
  static extractBestPractices(successfulProposals) {
    const practices = [];
    
    successfulProposals.forEach(proposal => {
      if (proposal.userFeedbackReason) {
        const feedback = proposal.userFeedbackReason.toLowerCase();
        
        if (feedback.includes('readability')) {
          practices.push('Focus on code readability');
        }
        if (feedback.includes('performance')) {
          practices.push('Optimize for performance');
        }
        if (feedback.includes('security')) {
          practices.push('Implement security best practices');
        }
        if (feedback.includes('maintainability')) {
          practices.push('Write maintainable code');
        }
        if (feedback.includes('testing')) {
          practices.push('Include comprehensive testing');
        }
      }
    });
    
    // Remove duplicates and return unique practices
    return [...new Set(practices)];
  }

  /**
   * Generate improved app code based on learned patterns
   */
  static async generateImprovedAppCode(appId, requirements, learnedPatterns) {
    try {
      console.log(`[CONQUEST_LEARNING_SERVICE] 🔧 Generating improved code for app ${appId}`);
      
      // Create app directory
      const appDir = path.join(process.env.GIT_REPO_PATH || '.', 'conquest_apps', appId);
      await fs.mkdir(appDir, { recursive: true });
      
      // Generate improved main.dart based on learned patterns
      const mainDartCode = this.generateMainDart(requirements, learnedPatterns);
      await fs.writeFile(path.join(appDir, 'lib', 'main.dart'), mainDartCode);
      
      // Generate improved pubspec.yaml
      const pubspecCode = this.generatePubspecYaml(requirements, learnedPatterns);
      await fs.writeFile(path.join(appDir, 'pubspec.yaml'), pubspecCode);
      
      // Generate improved app structure
      await this.generateAppStructure(appDir, requirements, learnedPatterns);
      
      // NEW: Generate backend with learning capabilities
      await this.generateBackendWithLearning(appDir, appId, requirements.name);
      
      // Commit and push the improved code
      const gitResult = await gitService.applyCrossAILearning(
        'Conquest',
        'Conquest',
        `conquest_apps/${appId}/lib/main.dart`,
        mainDartCode,
        {
          learningType: 'app-generation',
          insight: `Generated app using ${Object.keys(learnedPatterns).length} learned patterns`
        }
      );
      
      // Create learning entry
      const learningEntry = new Learning({
        aiType: 'Conquest',
        learningKey: 'app-code-generation',
        learningValue: `Generated improved app code for ${appId} using learned patterns`,
        status: 'learning-completed',
        timestamp: new Date(),
        filePath: `conquest_apps/${appId}`,
        improvementType: 'app-generation',
        metadata: {
          appId,
          requirements,
          learnedPatterns,
          gitResult,
          backendIncluded: true
        }
      });
      
      await learningEntry.save();
      
      console.log(`[CONQUEST_LEARNING_SERVICE] ✅ Generated improved app code for ${appId}`);
      return {
        success: true,
        appId,
        appDir,
        gitResult
      };
    } catch (error) {
      console.error('[CONQUEST_LEARNING_SERVICE] ❌ Error generating improved app code:', error);
      throw error;
    }
  }

  /**
   * NEW: Generate backend with learning capabilities for the app
   */
  static async generateBackendWithLearning(appDir, appId, appName) {
    try {
      console.log(`[CONQUEST_LEARNING_SERVICE] 🔧 Generating backend with learning for app ${appId}`);
      
      // Import the backend template
      const ConquestAppBackendTemplate = require('./conquestAppBackendTemplate');
      const backendTemplate = new ConquestAppBackendTemplate(appId, appName);
      
      // Generate backend code
      const backendCode = backendTemplate.generateBackendCode();
      
      // Create backend directory
      const backendDir = path.join(appDir, 'backend');
      await fs.mkdir(backendDir, { recursive: true });
      
      // Write backend server file
      await fs.writeFile(path.join(backendDir, 'server.js'), backendCode);
      
      // Generate package.json for backend
      const packageJson = {
        name: `${appId}-backend`,
        version: '1.0.0',
        description: `Backend for ${appName} - Auto-generated by Conquest AI`,
        main: 'server.js',
        scripts: {
          start: 'node server.js',
          dev: 'nodemon server.js'
        },
        dependencies: {
          express: '^4.18.2',
          cors: '^2.8.5',
          'body-parser': '^1.20.2'
        },
        devDependencies: {
          nodemon: '^3.0.1'
        },
        keywords: ['conquest-ai', 'auto-generated', 'learning-backend'],
        author: 'Conquest AI',
        license: 'MIT'
      };
      
      await fs.writeFile(path.join(backendDir, 'package.json'), JSON.stringify(packageJson, null, 2));
      
      // Generate README for backend
      const backendReadme = `# ${appName} Backend

Auto-generated by Conquest AI with learning capabilities.

## Features

- **User Feedback Collection**: Collects user ratings, comments, and suggestions
- **Usage Analytics**: Tracks feature usage, screen views, and user interactions
- **Error Reporting**: Captures and reports app errors and crashes
- **Performance Monitoring**: Monitors load times, memory usage, and frame rates
- **Learning Integration**: Automatically sends data to Conquest AI for learning

## API Endpoints

- \`POST /api/feedback\` - Submit user feedback
- \`POST /api/usage\` - Submit usage data
- \`POST /api/error\` - Submit error reports
- \`POST /api/performance\` - Submit performance metrics
- \`GET /api/analytics\` - Get analytics data
- \`GET /health\` - Health check

## Setup

1. Install dependencies:
   \`\`\`bash
   npm install
   \`\`\`

2. Start the server:
   \`\`\`bash
   npm start
   \`\`\`

3. The server will run on port 3000 by default

## Environment Variables

- \`PORT\` - Server port (default: 3000)
- \`CONQUEST_BACKEND_URL\` - Conquest AI backend URL (default: http://localhost:4000)

## Learning Integration

This backend automatically sends all collected data to Conquest AI for learning and improvement. The data helps Conquest AI:

- Understand user preferences and pain points
- Identify common errors and performance issues
- Learn from usage patterns to improve future app generation
- Continuously enhance app quality based on real user feedback

## Data Privacy

All data is anonymized and used only for improving Conquest AI's app generation capabilities. No personal information is stored or transmitted.

Generated by Conquest AI on ${new Date().toISOString()}
`;
      
      await fs.writeFile(path.join(backendDir, 'README.md'), backendReadme);
      
      // Generate .env.example file
      const envExample = `# Conquest AI Backend Configuration
PORT=3000
CONQUEST_BACKEND_URL=http://localhost:4000

# Optional: Database configuration (if needed)
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=app_db
# DB_USER=user
# DB_PASSWORD=password
`;
      
      await fs.writeFile(path.join(backendDir, '.env.example'), envExample);
      
      // Generate .gitignore for backend
      const gitignore = `# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Data files
data/
*.json

# Logs
logs
*.log

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/

# nyc test coverage
.nyc_output

# Dependency directories
node_modules/
jspm_packages/

# Optional npm cache directory
.npm

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env
`;
      
      await fs.writeFile(path.join(backendDir, '.gitignore'), gitignore);
      
      console.log(`[CONQUEST_LEARNING_SERVICE] ✅ Backend with learning generated for app ${appId}`);
      
    } catch (error) {
      console.error(`[CONQUEST_LEARNING_SERVICE] ❌ Error generating backend for app ${appId}:`, error);
      throw error;
    }
  }

  /**
   * Generate improved main.dart based on learned patterns
   */
  static generateMainDart(requirements, learnedPatterns) {
    const stateManagement = learnedPatterns.preferredStateManagement || 'Provider';
    const architecture = learnedPatterns.preferredArchitecture || 'MVVM';
    
    return `import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;
import 'package:device_info_plus/device_info_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'services/conquest_app_learning_service.dart';

// Generated by Conquest AI using learned patterns
// Architecture: ${architecture}
// State Management: ${stateManagement}
// Learned from: ${Object.keys(learnedPatterns.sourceAILearning || {}).join(', ')}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Conquest AI Learning Service
  await ConquestAppLearningService.instance.initialize(
    appId: '${requirements.name?.toLowerCase().replace(/\\s+/g, '_') || 'conquest_app'}',
    appName: '${requirements.name || 'Conquest App'}',
  );
  
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '${requirements.name || 'Conquest App'}',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: MyHomePage(title: '${requirements.name || 'Conquest App'}'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> with ConquestLearningMixin {
  int _counter = 0;

  @override
  void initState() {
    super.initState();
    // Track screen view
    trackScreenView('HomePage');
  }

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
    
    // Track feature usage
    trackFeatureUsage('counter_increment');
    
    // Track interaction
    trackInteraction('button_pressed', parameters: {'button': 'increment', 'count': _counter});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(
              'You have pushed the button this many times:',
            ),
            Text(
              '\$_counter',
              style: Theme.of(context).textTheme.headline4,
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () async {
                // Send feedback to Conquest AI
                await ConquestAppLearningService.instance.sendFeedback(
                  type: 'user_feedback',
                  rating: 4.5,
                  comment: 'Great app!',
                  category: 'general',
                  features: ['counter', 'increment'],
                );
                
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Feedback sent to Conquest AI!')),
                );
              },
              child: Text('Send Feedback'),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: Icon(Icons.add),
      ),
    );
  }
}

// Error handling wrapper
class ConquestErrorHandler {
  static void handleError(dynamic error, StackTrace? stackTrace) {
    // Track error with Conquest AI
    error.trackError(
      userAction: 'app_interaction',
      screen: 'HomePage',
      context: {'timestamp': DateTime.now().toIso8601String()},
    );
    
    // Log error locally
    print('Error: \$error');
    print('StackTrace: \$stackTrace');
  }
}

// Best practices applied from learned patterns:
${(learnedPatterns.bestPractices || []).map(practice => `// - ${practice}`).join('\n')}
`;
  }

  /**
   * Generate improved pubspec.yaml based on learned patterns
   */
  static generatePubspecYaml(requirements, learnedPatterns) {
    const stateManagement = learnedPatterns.preferredStateManagement || 'Provider';
    
    return `name: ${requirements.name?.toLowerCase().replace(/\s+/g, '_') || 'conquest_app'}
description: ${requirements.description || 'A Flutter app generated by Conquest AI'}
version: 1.0.0+1

environment:
  sdk: ">=2.12.0 <3.0.0"
  flutter: ">=2.0.0"

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.2
  provider: ^6.0.0  # Learned preferred state management
  http: ^0.13.0
  shared_preferences: ^2.0.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^2.0.0

flutter:
  uses-material-design: true

# Generated by Conquest AI using learned patterns
# Technologies: ${(learnedPatterns.preferredTechnologies || []).join(', ')}
# Architecture: ${learnedPatterns.preferredArchitecture || 'MVVM'}
# Confidence: ${learnedPatterns.confidence || 0}%
`;
  }

  /**
   * Generate improved app structure
   */
  static async generateAppStructure(appDir, requirements, learnedPatterns) {
    const libDir = path.join(appDir, 'lib');
    await fs.mkdir(libDir, { recursive: true });
    
    // Create directories based on learned architecture patterns
    const directories = [
      'models',
      'views',
      'viewmodels',
      'services',
      'utils'
    ];
    
    for (const dir of directories) {
      await fs.mkdir(path.join(libDir, dir), { recursive: true });
    }
    
    // NEW: Copy Conquest learning service to the generated app
    await this.copyLearningServiceToApp(libDir);
    
    // Create README with learning insights
    const readmeContent = `# ${requirements.name || 'Conquest App'}

Generated by Conquest AI using learned patterns from other AIs.

## Learning Insights

- **Source AIs**: ${Object.keys(learnedPatterns.sourceAILearning || {}).join(', ')}
- **Architecture**: ${learnedPatterns.preferredArchitecture || 'MVVM'}
- **State Management**: ${learnedPatterns.preferredStateManagement || 'Provider'}
- **Technologies**: ${(learnedPatterns.preferredTechnologies || []).join(', ')}
- **Confidence**: ${learnedPatterns.confidence || 0}%

## Best Practices Applied

${(learnedPatterns.bestPractices || []).map(practice => `- ${practice}`).join('\n')}

## Generated Structure

\`\`\`
lib/
├── main.dart
├── models/
├── views/
├── viewmodels/
├── services/
│   └── conquest_app_learning_service.dart
└── utils/
\`\`\`

## Learning Integration

This app includes automatic learning capabilities that send user feedback, usage data, and error reports to Conquest AI for continuous improvement.

### Features:
- **User Feedback Collection**: Collects ratings, comments, and suggestions
- **Usage Analytics**: Tracks feature usage and user interactions
- **Error Reporting**: Captures and reports app errors
- **Performance Monitoring**: Monitors app performance metrics
- **Automatic Learning**: Sends data to Conquest AI for improvement

### Backend:
- Includes a Node.js backend with learning endpoints
- Automatically collects and processes user data
- Sends insights to Conquest AI for learning

This app structure follows patterns learned from successful AI proposals.
`;
    
    await fs.writeFile(path.join(appDir, 'README.md'), readmeContent);
  }

  /**
   * NEW: Copy Conquest learning service to the generated app
   */
  static async copyLearningServiceToApp(libDir) {
    try {
      // Read the learning service template
      const learningServicePath = path.join(__dirname, '../../../lib/services/conquest_app_learning_service.dart');
      
      try {
        const learningServiceContent = await fs.readFile(learningServicePath, 'utf8');
        
        // Write to the generated app's services directory
        const servicesDir = path.join(libDir, 'services');
        await fs.mkdir(servicesDir, { recursive: true });
        
        await fs.writeFile(
          path.join(servicesDir, 'conquest_app_learning_service.dart'),
          learningServiceContent
        );
        
        console.log('[CONQUEST_LEARNING_SERVICE] ✅ Learning service copied to generated app');
      } catch (error) {
        // If the file doesn't exist, create a basic version
        console.log('[CONQUEST_LEARNING_SERVICE] ⚠️ Learning service template not found, creating basic version');
        
        const basicLearningService = `import 'dart:convert';
import 'dart:developer';
import 'package:http/http.dart' as http;

/// Conquest AI App Learning Service
/// Automatically collects and sends learning data from Conquest AI generated apps
class ConquestAppLearningService {
  static const String _baseUrl = 'http://localhost:3000';
  static const String _conquestBackendUrl = 'http://localhost:4000';
  
  static ConquestAppLearningService? _instance;
  static ConquestAppLearningService get instance => _instance ??= ConquestAppLearningService._();
  
  ConquestAppLearningService._();
  
  String? _appId;
  String? _appName;
  String? _userId;
  String? _sessionId;
  
  /// Initialize the learning service
  Future<void> initialize({
    required String appId,
    required String appName,
    String? userId,
  }) async {
    _appId = appId;
    _appName = appName;
    _userId = userId;
    _sessionId = '\${DateTime.now().millisecondsSinceEpoch}_\${_appId}_\${_userId ?? 'anonymous'}';
    
    log('[CONQUEST_LEARNING] ✅ Learning service initialized for app: \$appName');
  }
  
  /// Send user feedback to Conquest AI
  Future<bool> sendFeedback({
    required String type,
    required double rating,
    String? comment,
    String? category,
    String? severity,
    List<String>? features,
    List<String>? issues,
    List<String>? suggestions,
  }) async {
    try {
      final feedback = {
        'appId': _appId,
        'userId': _userId ?? 'anonymous',
        'type': type,
        'rating': rating,
        'comment': comment ?? '',
        'category': category ?? 'general',
        'severity': severity ?? 'low',
        'sessionId': _sessionId,
        'features': features ?? [],
        'issues': issues ?? [],
        'suggestions': suggestions ?? [],
      };
      
      // Send to Conquest AI backend
      final response = await http.post(
        Uri.parse('\$_conquestBackendUrl/api/conquest/app-feedback'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(feedback),
      );
      
      if (response.statusCode == 200) {
        log('[CONQUEST_LEARNING] ✅ Feedback sent to Conquest AI');
        return true;
      } else {
        log('[CONQUEST_LEARNING] ⚠️ Failed to send feedback: \${response.statusCode}');
        return false;
      }
    } catch (e) {
      log('[CONQUEST_LEARNING] ❌ Error sending feedback: \$e');
      return false;
    }
  }
  
  /// Send error report to Conquest AI
  Future<bool> sendError({
    required String type,
    required String message,
    String? stackTrace,
    String? severity,
    Map<String, dynamic>? context,
    String? userAction,
    String? screen,
  }) async {
    try {
      final error = {
        'appId': _appId,
        'type': type,
        'message': message,
        'stackTrace': stackTrace ?? '',
        'severity': severity ?? 'medium',
        'userId': _userId ?? 'anonymous',
        'sessionId': _sessionId,
        'context': context ?? {},
        'userAction': userAction ?? '',
        'screen': screen ?? '',
      };
      
      final response = await http.post(
        Uri.parse('\$_conquestBackendUrl/api/conquest/app-error'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(error),
      );
      
      if (response.statusCode == 200) {
        log('[CONQUEST_LEARNING] ✅ Error report sent to Conquest AI');
        return true;
      } else {
        log('[CONQUEST_LEARNING] ⚠️ Failed to send error report: \${response.statusCode}');
        return false;
      }
    } catch (e) {
      log('[CONQUEST_LEARNING] ❌ Error sending error report: \$e');
      return false;
    }
  }
  
  /// Track screen view
  void trackScreenView(String screenName) {
    log('[CONQUEST_LEARNING] 📱 Screen viewed: \$screenName');
  }
  
  /// Track feature usage
  void trackFeatureUsage(String featureName) {
    log('[CONQUEST_LEARNING] 🔧 Feature used: \$featureName');
  }
  
  /// Track user interaction
  void trackInteraction(String action, {Map<String, dynamic>? parameters}) {
    log('[CONQUEST_LEARNING] 👆 Interaction: \$action');
  }
}

/// Extension to easily track errors in Flutter apps
extension ConquestErrorTracking on Object {
  /// Track an error with Conquest AI
  Future<bool> trackError({
    String? type,
    String? userAction,
    String? screen,
    Map<String, dynamic>? context,
  }) async {
    final error = this;
    final errorType = type ?? error.runtimeType.toString();
    final errorMessage = error.toString();
    
    return await ConquestAppLearningService.instance.sendError(
      type: errorType,
      message: errorMessage,
      severity: 'medium',
      context: context,
      userAction: userAction,
      screen: screen,
    );
  }
}

/// Mixin to easily add learning capabilities to widgets
mixin ConquestLearningMixin {
  /// Track screen view when widget is built
  void trackScreenView(String screenName) {
    ConquestAppLearningService.instance.trackScreenView(screenName);
  }
  
  /// Track feature usage
  void trackFeatureUsage(String featureName) {
    ConquestAppLearningService.instance.trackFeatureUsage(featureName);
  }
  
  /// Track user interaction
  void trackInteraction(String action, {Map<String, dynamic>? parameters}) {
    ConquestAppLearningService.instance.trackInteraction(action, parameters: parameters);
  }
}`;
        
        const servicesDir = path.join(libDir, 'services');
        await fs.mkdir(servicesDir, { recursive: true });
        
        await fs.writeFile(
          path.join(servicesDir, 'conquest_app_learning_service.dart'),
          basicLearningService
        );
        
        console.log('[CONQUEST_LEARNING_SERVICE] ✅ Basic learning service created for generated app');
      }
    } catch (error) {
      console.error('[CONQUEST_LEARNING_SERVICE] ❌ Error copying learning service:', error);
    }
  }

  /**
   * Get Conquest's learning progress
   */
  static async getLearningProgress() {
    try {
      console.log('[CONQUEST_LEARNING_SERVICE] 📊 Getting Conquest learning progress...');
      
      // Get Conquest's learning entries
      const learningEntries = await Learning.find({
        aiType: 'Conquest'
      })
      .sort({ timestamp: -1 })
      .limit(50)
      .lean();
      
      // Get Git statistics
      const gitStats = await gitService.getLearningStats('Conquest', 30);
      
      // Calculate learning metrics
      const totalLearningSessions = learningEntries.length;
      const crossAILearning = learningEntries.filter(entry => 
        entry.learningKey.includes('cross-ai')
      ).length;
      const appGenerations = learningEntries.filter(entry => 
        entry.learningKey.includes('app-generation')
      ).length;
      const patternApplications = learningEntries.filter(entry => 
        entry.learningKey.includes('pattern-application')
      ).length;
      
      const progress = {
        totalLearningSessions,
        crossAILearning,
        appGenerations,
        patternApplications,
        gitStats,
        recentLearning: learningEntries.slice(0, 10),
        learningActivity: totalLearningSessions > 0 ? 'active' : 'inactive',
        improvementRate: Math.round((appGenerations / totalLearningSessions) * 100) || 0
      };
      
      console.log('[CONQUEST_LEARNING_SERVICE] ✅ Learning progress calculated');
      return progress;
    } catch (error) {
      console.error('[CONQUEST_LEARNING_SERVICE] ❌ Error getting learning progress:', error);
      throw error;
    }
  }

  /**
   * Process user feedback from Conquest AI generated apps
   */
  static async processAppFeedback(feedback) {
    try {
      console.log(`[CONQUEST_LEARNING_SERVICE] 📊 Processing app feedback for ${feedback.appId}`);
      
      // Store feedback in Conquest's learning data
      const conquestData = await this.getConquestData();
      
      if (!conquestData.appFeedback) {
        conquestData.appFeedback = [];
      }
      
      conquestData.appFeedback.push({
        ...feedback,
        processedAt: new Date().toISOString()
      });
      
      // Analyze feedback patterns
      const feedbackAnalysis = this.analyzeFeedbackPatterns(conquestData.appFeedback);
      
      // Update Conquest's learning insights
      conquestData.feedbackInsights = feedbackAnalysis;
      
      // Save updated data
      await this.saveConquestData(conquestData);
      
      console.log(`[CONQUEST_LEARNING_SERVICE] ✅ App feedback processed for ${feedback.appId}`);
      
    } catch (error) {
      console.error('[CONQUEST_LEARNING_SERVICE] ❌ Error processing app feedback:', error);
      throw error;
    }
  }

  /**
   * Process usage data from Conquest AI generated apps
   */
  static async processAppUsage(usage) {
    try {
      console.log(`[CONQUEST_LEARNING_SERVICE] 📈 Processing app usage for ${usage.appId}`);
      
      // Store usage data in Conquest's learning data
      const conquestData = await this.getConquestData();
      
      if (!conquestData.appUsage) {
        conquestData.appUsage = [];
      }
      
      conquestData.appUsage.push({
        ...usage,
        processedAt: new Date().toISOString()
      });
      
      // Analyze usage patterns
      const usageAnalysis = this.analyzeUsagePatterns(conquestData.appUsage);
      
      // Update Conquest's learning insights
      conquestData.usageInsights = usageAnalysis;
      
      // Save updated data
      await this.saveConquestData(conquestData);
      
      console.log(`[CONQUEST_LEARNING_SERVICE] ✅ App usage processed for ${usage.appId}`);
      
    } catch (error) {
      console.error('[CONQUEST_LEARNING_SERVICE] ❌ Error processing app usage:', error);
      throw error;
    }
  }

  /**
   * Process error reports from Conquest AI generated apps
   */
  static async processAppError(error) {
    try {
      console.log(`[CONQUEST_LEARNING_SERVICE] 🐛 Processing app error for ${error.appId}`);
      
      // Store error data in Conquest's learning data
      const conquestData = await this.getConquestData();
      
      if (!conquestData.appErrors) {
        conquestData.appErrors = [];
      }
      
      conquestData.appErrors.push({
        ...error,
        processedAt: new Date().toISOString()
      });
      
      // Analyze error patterns
      const errorAnalysis = this.analyzeErrorPatterns(conquestData.appErrors);
      
      // Update Conquest's learning insights
      conquestData.errorInsights = errorAnalysis;
      
      // Save updated data
      await this.saveConquestData(conquestData);
      
      console.log(`[CONQUEST_LEARNING_SERVICE] ✅ App error processed for ${error.appId}`);
      
    } catch (error) {
      console.error('[CONQUEST_LEARNING_SERVICE] ❌ Error processing app error:', error);
      throw error;
    }
  }

  /**
   * Process performance metrics from Conquest AI generated apps
   */
  static async processAppPerformance(metrics) {
    try {
      console.log(`[CONQUEST_LEARNING_SERVICE] ⚡ Processing app performance for ${metrics.appId}`);
      
      // Store performance data in Conquest's learning data
      const conquestData = await this.getConquestData();
      
      if (!conquestData.appPerformance) {
        conquestData.appPerformance = [];
      }
      
      conquestData.appPerformance.push({
        ...metrics,
        processedAt: new Date().toISOString()
      });
      
      // Analyze performance patterns
      const performanceAnalysis = this.analyzePerformancePatterns(conquestData.appPerformance);
      
      // Update Conquest's learning insights
      conquestData.performanceInsights = performanceAnalysis;
      
      // Save updated data
      await this.saveConquestData(conquestData);
      
      console.log(`[CONQUEST_LEARNING_SERVICE] ✅ App performance processed for ${metrics.appId}`);
      
    } catch (error) {
      console.error('[CONQUEST_LEARNING_SERVICE] ❌ Error processing app performance:', error);
      throw error;
    }
  }

  /**
   * Analyze feedback patterns from app feedback
   */
  static analyzeFeedbackPatterns(feedbackData) {
    const analysis = {
      totalFeedback: feedbackData.length,
      averageRating: 0,
      ratingDistribution: {},
      categoryDistribution: {},
      severityDistribution: {},
      commonIssues: [],
      userSatisfaction: 'neutral'
    };

    if (feedbackData.length === 0) return analysis;

    // Calculate average rating
    const totalRating = feedbackData.reduce((sum, feedback) => sum + (feedback.rating || 0), 0);
    analysis.averageRating = totalRating / feedbackData.length;

    // Analyze rating distribution
    feedbackData.forEach(feedback => {
      const rating = feedback.rating || 0;
      analysis.ratingDistribution[rating] = (analysis.ratingDistribution[rating] || 0) + 1;
    });

    // Analyze category distribution
    feedbackData.forEach(feedback => {
      const category = feedback.category || 'general';
      analysis.categoryDistribution[category] = (analysis.categoryDistribution[category] || 0) + 1;
    });

    // Analyze severity distribution
    feedbackData.forEach(feedback => {
      const severity = feedback.severity || 'low';
      analysis.severityDistribution[severity] = (analysis.severityDistribution[severity] || 0) + 1;
    });

    // Extract common issues
    const issueCounts = {};
    feedbackData.forEach(feedback => {
      if (feedback.issues && Array.isArray(feedback.issues)) {
        feedback.issues.forEach(issue => {
          issueCounts[issue] = (issueCounts[issue] || 0) + 1;
        });
      }
    });

    analysis.commonIssues = Object.entries(issueCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([issue, count]) => ({ issue, count }));

    // Determine user satisfaction
    if (analysis.averageRating >= 4) {
      analysis.userSatisfaction = 'high';
    } else if (analysis.averageRating >= 3) {
      analysis.userSatisfaction = 'medium';
    } else {
      analysis.userSatisfaction = 'low';
    }

    return analysis;
  }

  /**
   * Analyze usage patterns from app usage data
   */
  static analyzeUsagePatterns(usageData) {
    const analysis = {
      totalSessions: usageData.length,
      averageTimeSpent: 0,
      mostUsedFeatures: [],
      platformDistribution: {},
      userEngagement: 'low'
    };

    if (usageData.length === 0) return analysis;

    // Calculate average time spent
    const totalTime = usageData.reduce((sum, usage) => sum + (usage.timeSpent || 0), 0);
    analysis.averageTimeSpent = totalTime / usageData.length;

    // Analyze feature usage
    const featureCounts = {};
    usageData.forEach(usage => {
      if (usage.featureUsage && typeof usage.featureUsage === 'object') {
        Object.keys(usage.featureUsage).forEach(feature => {
          featureCounts[feature] = (featureCounts[feature] || 0) + usage.featureUsage[feature];
        });
      }
    });

    analysis.mostUsedFeatures = Object.entries(featureCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10)
      .map(([feature, count]) => ({ feature, count }));

    // Analyze platform distribution
    usageData.forEach(usage => {
      const platform = usage.platform || 'unknown';
      analysis.platformDistribution[platform] = (analysis.platformDistribution[platform] || 0) + 1;
    });

    // Determine user engagement
    if (analysis.averageTimeSpent >= 300) { // 5 minutes
      analysis.userEngagement = 'high';
    } else if (analysis.averageTimeSpent >= 60) { // 1 minute
      analysis.userEngagement = 'medium';
    } else {
      analysis.userEngagement = 'low';
    }

    return analysis;
  }

  /**
   * Analyze error patterns from app error data
   */
  static analyzeErrorPatterns(errorData) {
    const analysis = {
      totalErrors: errorData.length,
      errorTypeDistribution: {},
      severityDistribution: {},
      platformDistribution: {},
      commonErrorMessages: [],
      errorFrequency: 'low'
    };

    if (errorData.length === 0) return analysis;

    // Analyze error type distribution
    errorData.forEach(error => {
      const errorType = error.errorType || 'unknown';
      analysis.errorTypeDistribution[errorType] = (analysis.errorTypeDistribution[errorType] || 0) + 1;
    });

    // Analyze severity distribution
    errorData.forEach(error => {
      const severity = error.severity || 'medium';
      analysis.severityDistribution[severity] = (analysis.severityDistribution[severity] || 0) + 1;
    });

    // Analyze platform distribution
    errorData.forEach(error => {
      const platform = error.platform || 'unknown';
      analysis.platformDistribution[platform] = (analysis.platformDistribution[platform] || 0) + 1;
    });

    // Extract common error messages
    const messageCounts = {};
    errorData.forEach(error => {
      const message = error.errorMessage || '';
      if (message) {
        messageCounts[message] = (messageCounts[message] || 0) + 1;
      }
    });

    analysis.commonErrorMessages = Object.entries(messageCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([message, count]) => ({ message, count }));

    // Determine error frequency
    if (analysis.totalErrors >= 50) {
      analysis.errorFrequency = 'high';
    } else if (analysis.totalErrors >= 10) {
      analysis.errorFrequency = 'medium';
    } else {
      analysis.errorFrequency = 'low';
    }

    return analysis;
  }

  /**
   * Analyze performance patterns from app performance data
   */
  static analyzePerformancePatterns(performanceData) {
    const analysis = {
      totalMetrics: performanceData.length,
      averageLoadTime: 0,
      averageMemoryUsage: 0,
      averageFrameRate: 0,
      platformPerformance: {},
      performanceRating: 'good'
    };

    if (performanceData.length === 0) return analysis;

    // Calculate averages
    const totalLoadTime = performanceData.reduce((sum, metrics) => sum + (metrics.loadTime || 0), 0);
    analysis.averageLoadTime = totalLoadTime / performanceData.length;

    const totalMemoryUsage = performanceData.reduce((sum, metrics) => sum + (metrics.memoryUsage || 0), 0);
    analysis.averageMemoryUsage = totalMemoryUsage / performanceData.length;

    const totalFrameRate = performanceData.reduce((sum, metrics) => sum + (metrics.frameRate || 0), 0);
    analysis.averageFrameRate = totalFrameRate / performanceData.length;

    // Analyze platform performance
    performanceData.forEach(metrics => {
      const platform = metrics.platform || 'unknown';
      if (!analysis.platformPerformance[platform]) {
        analysis.platformPerformance[platform] = {
          count: 0,
          totalLoadTime: 0,
          totalMemoryUsage: 0,
          totalFrameRate: 0
        };
      }
      
      analysis.platformPerformance[platform].count++;
      analysis.platformPerformance[platform].totalLoadTime += metrics.loadTime || 0;
      analysis.platformPerformance[platform].totalMemoryUsage += metrics.memoryUsage || 0;
      analysis.platformPerformance[platform].totalFrameRate += metrics.frameRate || 0;
    });

    // Calculate platform averages
    Object.keys(analysis.platformPerformance).forEach(platform => {
      const data = analysis.platformPerformance[platform];
      data.averageLoadTime = data.totalLoadTime / data.count;
      data.averageMemoryUsage = data.totalMemoryUsage / data.count;
      data.averageFrameRate = data.totalFrameRate / data.count;
    });

    // Determine performance rating
    if (analysis.averageLoadTime <= 1000 && analysis.averageFrameRate >= 30) {
      analysis.performanceRating = 'excellent';
    } else if (analysis.averageLoadTime <= 2000 && analysis.averageFrameRate >= 25) {
      analysis.performanceRating = 'good';
    } else if (analysis.averageLoadTime <= 3000 && analysis.averageFrameRate >= 20) {
      analysis.performanceRating = 'fair';
    } else {
      analysis.performanceRating = 'poor';
    }

    return analysis;
  }

  /**
   * Get Conquest data from file
   */
  static async getConquestData() {
    try {
      const fs = require('fs').promises;
      const path = require('path');
      
      const dataPath = path.join(__dirname, '../data/conquest_ai_data.json');
      
      try {
        const data = await fs.readFile(dataPath, 'utf8');
        return JSON.parse(data);
      } catch (error) {
        // File doesn't exist, return default structure
        return {
          appFeedback: [],
          appUsage: [],
          appErrors: [],
          appPerformance: [],
          feedbackInsights: {},
          usageInsights: {},
          errorInsights: {},
          performanceInsights: {}
        };
      }
    } catch (error) {
      console.error('[CONQUEST_LEARNING_SERVICE] ❌ Error getting Conquest data:', error);
      throw error;
    }
  }

  /**
   * Save Conquest data to file
   */
  static async saveConquestData(data) {
    try {
      const fs = require('fs').promises;
      const path = require('path');
      
      const dataDir = path.join(__dirname, '../data');
      await fs.mkdir(dataDir, { recursive: true });
      
      const dataPath = path.join(dataDir, 'conquest_ai_data.json');
      await fs.writeFile(dataPath, JSON.stringify(data, null, 2));
      
    } catch (error) {
      console.error('[CONQUEST_LEARNING_SERVICE] ❌ Error saving Conquest data:', error);
      throw error;
    }
  }
}

module.exports = ConquestLearningService; 