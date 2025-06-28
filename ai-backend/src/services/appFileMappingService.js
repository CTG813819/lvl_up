const fs = require('fs');
const path = require('path');

/**
 * App File Mapping Service
 * Helps AIs understand which files they should modify based on the app structure
 */
class AppFileMappingService {
  constructor() {
    this.appStructure = {
      // Flutter app structure
      flutter: {
        lib: {
          // Core AI files
          'ai_brain.dart': {
            description: 'Main AI brain implementation',
            aiTypes: ['Imperium'],
            purpose: 'Core AI logic and decision making',
            priority: 'high'
          },
          'ai_guardian_analytics_screen.dart': {
            description: 'Guardian AI analytics and monitoring',
            aiTypes: ['Guardian'],
            purpose: 'Health checks, monitoring, and analytics',
            priority: 'high'
          },
          'ai_file_system_helper.dart': {
            description: 'File system operations for AI',
            aiTypes: ['Sandbox'],
            purpose: 'File operations and experiments',
            priority: 'medium'
          },
          // Core app structure
          'main.dart': {
            description: 'Main app entry point',
            aiTypes: ['Imperium', 'Guardian'],
            purpose: 'App initialization and routing',
            priority: 'high'
          },
          // Models
          models: {
            'ai_notification.dart': {
              description: 'AI notification model',
              aiTypes: ['Guardian'],
              purpose: 'Notification handling',
              priority: 'medium'
            },
            'ai_proposal.dart': {
              description: 'AI proposal model',
              aiTypes: ['Imperium', 'Sandbox'],
              purpose: 'Proposal management',
              priority: 'high'
            },
            'app_history.dart': {
              description: 'App history tracking',
              aiTypes: ['Guardian'],
              purpose: 'History and analytics',
              priority: 'medium'
            }
          },
          // Services
          services: {
            'ai_learning_service.dart': {
              description: 'AI learning service',
              aiTypes: ['Imperium', 'Sandbox'],
              purpose: 'Learning and improvement',
              priority: 'high'
            },
            'notification_service.dart': {
              description: 'Notification service',
              aiTypes: ['Guardian'],
              purpose: 'User notifications',
              priority: 'medium'
            }
          },
          // Screens
          screens: {
            'app_history_screen.dart': {
              description: 'App history screen',
              aiTypes: ['Guardian'],
              purpose: 'History display',
              priority: 'medium'
            },
            'notification_center_screen.dart': {
              description: 'Notification center',
              aiTypes: ['Guardian'],
              purpose: 'Notification management',
              priority: 'medium'
            },
            'proposal_approval_screen.dart': {
              description: 'Proposal approval interface',
              aiTypes: ['Imperium', 'Guardian'],
              purpose: 'User approval workflow',
              priority: 'high'
            }
          },
          // Widgets
          widgets: {
            'ai_learning_dashboard.dart': {
              description: 'AI learning dashboard',
              aiTypes: ['Imperium', 'Sandbox'],
              purpose: 'Learning progress display',
              priority: 'medium'
            },
            'approval_dashboard.dart': {
              description: 'Approval dashboard',
              aiTypes: ['Guardian'],
              purpose: 'Approval management',
              priority: 'high'
            }
          }
        },
        // Backend files (in temp-repo)
        backend: {
          'src/services/imperiumService.js': {
            description: 'Imperium AI service',
            aiTypes: ['Imperium'],
            purpose: 'Imperium AI logic',
            priority: 'high'
          },
          'src/services/guardianService.js': {
            description: 'Guardian AI service',
            aiTypes: ['Guardian'],
            purpose: 'Guardian AI logic',
            priority: 'high'
          },
          'src/services/sandboxService.js': {
            description: 'Sandbox AI service',
            aiTypes: ['Sandbox'],
            purpose: 'Sandbox AI logic',
            priority: 'high'
          }
        }
      }
    };
  }

  /**
   * Get files that an AI should focus on
   */
  getAIFiles(aiType) {
    const files = [];
    
    // Add backend service files
    files.push({
      path: `src/services/${aiType.toLowerCase()}Service.js`,
      description: `${aiType} AI service`,
      purpose: `${aiType} AI logic and implementation`,
      priority: 'high',
      type: 'backend'
    });

    // Add Flutter app files based on AI type
    switch (aiType.toLowerCase()) {
      case 'imperium':
        files.push(
          { path: 'lib/ai_brain.dart', description: 'Main AI brain', purpose: 'Core AI logic', priority: 'high', type: 'flutter' },
          { path: 'lib/main.dart', description: 'App entry point', purpose: 'App initialization', priority: 'high', type: 'flutter' },
          { path: 'lib/models/ai_proposal.dart', description: 'Proposal model', purpose: 'Proposal management', priority: 'high', type: 'flutter' },
          { path: 'lib/services/ai_learning_service.dart', description: 'Learning service', purpose: 'AI learning', priority: 'high', type: 'flutter' },
          { path: 'lib/screens/proposal_approval_screen.dart', description: 'Approval screen', purpose: 'User approval', priority: 'high', type: 'flutter' },
          { path: 'lib/widgets/ai_learning_dashboard.dart', description: 'Learning dashboard', purpose: 'Progress display', priority: 'medium', type: 'flutter' }
        );
        break;
        
      case 'guardian':
        files.push(
          { path: 'lib/ai_guardian_analytics_screen.dart', description: 'Guardian analytics', purpose: 'Health monitoring', priority: 'high', type: 'flutter' },
          { path: 'lib/models/ai_notification.dart', description: 'Notification model', purpose: 'Notification handling', priority: 'medium', type: 'flutter' },
          { path: 'lib/models/app_history.dart', description: 'History model', purpose: 'History tracking', priority: 'medium', type: 'flutter' },
          { path: 'lib/services/notification_service.dart', description: 'Notification service', purpose: 'User notifications', priority: 'medium', type: 'flutter' },
          { path: 'lib/screens/app_history_screen.dart', description: 'History screen', purpose: 'History display', priority: 'medium', type: 'flutter' },
          { path: 'lib/screens/notification_center_screen.dart', description: 'Notification center', purpose: 'Notification management', priority: 'medium', type: 'flutter' },
          { path: 'lib/widgets/approval_dashboard.dart', description: 'Approval dashboard', purpose: 'Approval management', priority: 'high', type: 'flutter' }
        );
        break;
        
      case 'sandbox':
        files.push(
          { path: 'lib/ai_file_system_helper.dart', description: 'File system helper', purpose: 'File operations', priority: 'medium', type: 'flutter' },
          { path: 'lib/models/ai_proposal.dart', description: 'Proposal model', purpose: 'Proposal management', priority: 'high', type: 'flutter' },
          { path: 'lib/services/ai_learning_service.dart', description: 'Learning service', purpose: 'AI learning', priority: 'high', type: 'flutter' },
          { path: 'lib/widgets/ai_learning_dashboard.dart', description: 'Learning dashboard', purpose: 'Progress display', priority: 'medium', type: 'flutter' }
        );
        break;
    }

    return files;
  }

  /**
   * Get file information for a specific file
   */
  getFileInfo(filePath) {
    const normalizedPath = filePath.replace(/\\/g, '/');
    
    // Check backend files
    if (normalizedPath.includes('src/services/')) {
      const aiType = normalizedPath.match(/src\/services\/(\w+)Service\.js/)?.[1];
      if (aiType) {
        return {
          path: normalizedPath,
          description: `${aiType} AI service`,
          purpose: `${aiType} AI logic and implementation`,
          priority: 'high',
          type: 'backend',
          aiTypes: [aiType.charAt(0).toUpperCase() + aiType.slice(1)]
        };
      }
    }

    // Check Flutter files
    const flutterFiles = this.getFlutterFileInfo(normalizedPath);
    if (flutterFiles) {
      return flutterFiles;
    }

    return {
      path: normalizedPath,
      description: 'Unknown file',
      purpose: 'General file',
      priority: 'low',
      type: 'unknown',
      aiTypes: []
    };
  }

  /**
   * Get Flutter file information
   */
  getFlutterFileInfo(filePath) {
    const fileMappings = {
      'lib/ai_brain.dart': {
        description: 'Main AI brain implementation',
        purpose: 'Core AI logic and decision making',
        priority: 'high',
        aiTypes: ['Imperium']
      },
      'lib/ai_guardian_analytics_screen.dart': {
        description: 'Guardian AI analytics and monitoring',
        purpose: 'Health checks, monitoring, and analytics',
        priority: 'high',
        aiTypes: ['Guardian']
      },
      'lib/ai_file_system_helper.dart': {
        description: 'File system operations for AI',
        purpose: 'File operations and experiments',
        priority: 'medium',
        aiTypes: ['Sandbox']
      },
      'lib/main.dart': {
        description: 'Main app entry point',
        purpose: 'App initialization and routing',
        priority: 'high',
        aiTypes: ['Imperium', 'Guardian']
      },
      'lib/models/ai_notification.dart': {
        description: 'AI notification model',
        purpose: 'Notification handling',
        priority: 'medium',
        aiTypes: ['Guardian']
      },
      'lib/models/ai_proposal.dart': {
        description: 'AI proposal model',
        purpose: 'Proposal management',
        priority: 'high',
        aiTypes: ['Imperium', 'Sandbox']
      },
      'lib/models/app_history.dart': {
        description: 'App history tracking',
        purpose: 'History and analytics',
        priority: 'medium',
        aiTypes: ['Guardian']
      },
      'lib/services/ai_learning_service.dart': {
        description: 'AI learning service',
        purpose: 'Learning and improvement',
        priority: 'high',
        aiTypes: ['Imperium', 'Sandbox']
      },
      'lib/services/notification_service.dart': {
        description: 'Notification service',
        purpose: 'User notifications',
        priority: 'medium',
        aiTypes: ['Guardian']
      },
      'lib/screens/app_history_screen.dart': {
        description: 'App history screen',
        purpose: 'History display',
        priority: 'medium',
        aiTypes: ['Guardian']
      },
      'lib/screens/notification_center_screen.dart': {
        description: 'Notification center',
        purpose: 'Notification management',
        priority: 'medium',
        aiTypes: ['Guardian']
      },
      'lib/screens/proposal_approval_screen.dart': {
        description: 'Proposal approval interface',
        purpose: 'User approval workflow',
        priority: 'high',
        aiTypes: ['Imperium', 'Guardian']
      },
      'lib/widgets/ai_learning_dashboard.dart': {
        description: 'AI learning dashboard',
        purpose: 'Learning progress display',
        priority: 'medium',
        aiTypes: ['Imperium', 'Sandbox']
      },
      'lib/widgets/approval_dashboard.dart': {
        description: 'Approval dashboard',
        purpose: 'Approval management',
        priority: 'high',
        aiTypes: ['Guardian']
      }
    };

    return fileMappings[filePath] ? {
      path: filePath,
      type: 'flutter',
      ...fileMappings[filePath]
    } : null;
  }

  /**
   * Get app structure overview
   */
  getAppStructure() {
    return {
      description: 'Flutter AI Learning App with Backend Services',
      structure: {
        flutter: {
          description: 'Flutter mobile application',
          directories: {
            'lib/': 'Main Dart source code',
            'lib/models/': 'Data models',
            'lib/services/': 'Business logic services',
            'lib/screens/': 'UI screens',
            'lib/widgets/': 'Reusable UI components'
          }
        },
        backend: {
          description: 'Node.js backend services',
          directories: {
            'src/services/': 'AI service implementations',
            'src/models/': 'Database models',
            'src/routes/': 'API endpoints'
          }
        }
      },
      aiTypes: {
        'Imperium': 'Main AI for code generation and learning',
        'Guardian': 'AI for monitoring, health checks, and approvals',
        'Sandbox': 'AI for experiments and file operations'
      }
    };
  }

  /**
   * Validate if a file path is appropriate for an AI type
   */
  isFileAppropriateForAI(filePath, aiType) {
    const fileInfo = this.getFileInfo(filePath);
    return fileInfo.aiTypes.includes(aiType);
  }

  /**
   * Get suggested improvements for an AI type
   */
  getSuggestedImprovements(aiType) {
    const files = this.getAIFiles(aiType);
    const suggestions = [];

    files.forEach(file => {
      if (file.priority === 'high') {
        suggestions.push({
          file: file.path,
          suggestion: `Focus on improving ${file.description} for better ${file.purpose}`,
          priority: 'high'
        });
      }
    });

    return suggestions;
  }
}

module.exports = new AppFileMappingService(); 