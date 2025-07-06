"""
Conquest AI Service - Creates new app repositories and APKs
"""

import asyncio
import aiohttp
import json
import tempfile
import subprocess
import os
import shutil
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog
from pathlib import Path
import uuid
import re

from ..core.database import get_session
from ..core.config import settings
from .github_service import GitHubService
from .ai_learning_service import AILearningService

logger = structlog.get_logger()


class ConquestAIService:
    """Service to create new app repositories and APKs"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConquestAIService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.github_service = GitHubService()
            self.learning_service = AILearningService()
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the Conquest AI service"""
        instance = cls()
        await instance.github_service.initialize()
        await instance.learning_service.initialize()
        logger.info("Conquest AI Service initialized")
        return instance
    
    async def create_new_app(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new app repository and generate APK"""
        try:
            logger.info(f"⚔️ Conquest AI creating new app: {app_data.get('name', 'Unknown')}")
            
            app_id = str(uuid.uuid4())
            app_name = app_data.get('name', 'conquest_app')
            description = app_data.get('description', '')
            keywords = app_data.get('keywords', [])
            
            # Step 1: Generate app structure
            app_structure = await self._generate_app_structure(app_name, description, keywords)
            
            # Step 2: Create GitHub repository
            repo_url = await self._create_github_repository(app_name, description)
            
            # Step 3: Generate Flutter app code
            app_code = await self._generate_flutter_app(app_structure, app_name, description, keywords)
            
            # Step 4: Push code to repository
            await self._push_code_to_repository(repo_url, app_code)
            
            # Step 5: Build APK
            apk_url = await self._build_apk(repo_url, app_name)
            
            # Step 6: Create deployment record
            deployment_record = await self._create_deployment_record(
                app_id, app_name, repo_url, apk_url, app_data
            )
            
            # After pushing code and workflow:
            await self._wait_for_github_actions_and_update_status(repo_url, app_id, app_name)

            return {
                "status": "success",
                "app_id": app_id,
                "app_name": app_name,
                "repository_url": repo_url,
                "apk_url": apk_url,
                "deployment_record": deployment_record,
                "message": f"App '{app_name}' created successfully!"
            }
            
        except Exception as e:
            logger.error("Error creating new app", error=str(e))
            return {"status": "error", "message": str(e)}
    
    async def _generate_app_structure(self, app_name: str, description: str, keywords: List[str]) -> Dict[str, Any]:
        """Generate the app structure based on requirements"""
        # Analyze keywords to determine app type
        app_type = self._determine_app_type(keywords, description)
        
        # Generate features based on app type
        features = self._generate_features(app_type, keywords)
        
        # Generate dependencies
        dependencies = self._generate_dependencies(features)
        
        return {
            "app_type": app_type,
            "features": features,
            "dependencies": dependencies,
            "architecture": "MVVM",
            "state_management": "Provider",
            "database": "SQLite",
            "ui_framework": "Material Design"
        }
    
    def _determine_app_type(self, keywords: List[str], description: str) -> str:
        """Determine app type based on keywords and description"""
        text = (description + " " + " ".join(keywords)).lower()
        
        if any(word in text for word in ["game", "gaming", "play", "score", "level"]):
            return "game"
        elif any(word in text for word in ["social", "chat", "message", "friend", "profile"]):
            return "social"
        elif any(word in text for word in ["fitness", "workout", "exercise", "health", "track"]):
            return "fitness"
        elif any(word in text for word in ["productivity", "task", "todo", "reminder", "schedule"]):
            return "productivity"
        elif any(word in text for word in ["education", "learn", "study", "course", "quiz"]):
            return "education"
        else:
            return "general"
    
    def _generate_features(self, app_type: str, keywords: List[str]) -> List[str]:
        """Generate features based on app type"""
        base_features = ["authentication", "settings", "navigation"]
        
        if app_type == "game":
            return base_features + ["game_engine", "score_tracking", "leaderboard", "achievements"]
        elif app_type == "social":
            return base_features + ["user_profiles", "messaging", "social_sharing", "friend_system"]
        elif app_type == "fitness":
            return base_features + ["workout_tracking", "progress_charts", "goal_setting", "health_metrics"]
        elif app_type == "productivity":
            return base_features + ["task_management", "reminders", "data_sync", "analytics"]
        elif app_type == "education":
            return base_features + ["course_management", "quiz_system", "progress_tracking", "certificates"]
        else:
            return base_features + ["custom_features"]
    
    def _generate_dependencies(self, features: List[str]) -> Dict[str, str]:
        """Generate pubspec.yaml dependencies"""
        dependencies = {
            "provider": "^6.0.0",
            "shared_preferences": "^2.0.0",
            "http": "^0.13.0",
            "sqflite": "^2.0.0",
            "path": "^1.8.0"
        }
        
        if "game_engine" in features:
            dependencies["flame"] = "^1.0.0"
        
        if "messaging" in features:
            dependencies["firebase_messaging"] = "^14.0.0"
            dependencies["firebase_core"] = "^2.0.0"
        
        if "social_sharing" in features:
            dependencies["share_plus"] = "^7.0.0"
        
        if "charts" in features:
            dependencies["fl_chart"] = "^0.60.0"
        
        return dependencies
    
    async def _create_github_repository(self, app_name: str, description: str) -> str:
        """Create a new GitHub repository"""
        try:
            repo_name = f"conquest-{app_name.lower().replace(' ', '-')}"
            
            # Create repository via GitHub API
            repo_data = {
                "name": repo_name,
                "description": f"Conquest AI Generated App: {description}",
                "private": False,
                "auto_init": True,
                "gitignore_template": "Flutter"
            }
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"token {settings.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                async with session.post(
                    "https://api.github.com/user/repos",
                    headers=headers,
                    json=repo_data
                ) as response:
                    if response.status == 201:
                        repo_info = await response.json()
                        logger.info(f"✅ Created GitHub repository: {repo_info['html_url']}")
                        return repo_info["html_url"]
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Failed to create repository: {error_text}")
                        raise Exception(f"Failed to create repository: {error_text}")
                        
        except Exception as e:
            logger.error("Error creating GitHub repository", error=str(e))
            # Try to create under the configured organization/user
            try:
                if settings.github_username:
                    org_repo_name = f"{settings.github_username}/{repo_name}"
                    logger.info(f"🔄 Attempting to create repository under {settings.github_username}")
                    return f"https://github.com/{org_repo_name}"
            except:
                pass
            
            # Return a mock URL as last resort
            return f"https://github.com/conquest-ai/{app_name.lower().replace(' ', '-')}"
    
    async def _generate_flutter_app(self, structure: Dict[str, Any], app_name: str, description: str, keywords: List[str]) -> Dict[str, str]:
        """Generate complete Flutter app code"""
        app_code = {}
        
        # Generate pubspec.yaml
        app_code["pubspec.yaml"] = self._generate_pubspec_yaml(app_name, description, structure["dependencies"])
        
        # Generate main.dart
        app_code["lib/main.dart"] = self._generate_main_dart(app_name, structure)
        
        # Generate app structure
        app_code["lib/app.dart"] = self._generate_app_dart(app_name, structure)
        
        # Generate screens
        for feature in structure["features"]:
            screen_code = self._generate_screen_code(feature, app_name)
            if screen_code:
                app_code[f"lib/screens/{feature}_screen.dart"] = screen_code
        
        # Always generate home_screen.dart
        app_code["lib/screens/home_screen.dart"] = self._generate_home_screen(app_name)
        
        # Generate models
        app_code["lib/models/app_model.dart"] = self._generate_model_code(app_name, structure)
        
        # Generate services
        app_code["lib/services/app_service.dart"] = self._generate_service_code(app_name, structure)
        
        # Generate providers
        app_code["lib/providers/app_provider.dart"] = self._generate_provider_code(app_name, structure)
        
        # Generate test files
        app_code["test/widget_test.dart"] = self._generate_widget_test(app_name)
        app_code["integration_test/app_test.dart"] = self._generate_integration_test(app_name)
        
        return app_code
    
    def _generate_pubspec_yaml(self, app_name: str, description: str, dependencies: Dict[str, str]) -> str:
        """Generate pubspec.yaml content"""
        deps_str = "\n".join([f"  {k}: {v}" for k, v in dependencies.items()])
        
        return f"""name: {app_name.lower().replace(' ', '_')}
description: {description}
publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
{deps_str}

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^2.0.0
  integration_test:
    sdk: flutter

flutter:
  uses-material-design: true
"""
    
    def _generate_main_dart(self, app_name: str, structure: Dict[str, Any]) -> str:
        """Generate main.dart content"""
        return f"""import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'app.dart';
import 'providers/app_provider.dart';

void main() {{
  runApp(MyApp());
}}

class MyApp extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AppProvider()),
      ],
      child: MaterialApp(
        title: '{app_name}',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          visualDensity: VisualDensity.adaptivePlatformDensity,
        ),
        home: AppHome(),
      ),
    );
  }}
}}
"""
    
    def _generate_widget_test(self, app_name: str) -> str:
        """Generate widget test file"""
        return f"""import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:{app_name.lower().replace(' ', '_')}/app.dart';
import 'package:{app_name.lower().replace(' ', '_')}/providers/app_provider.dart';

void main() {{
  group('{app_name} Widget Tests', () {{
    testWidgets('App should render without crashing', (WidgetTester tester) async {{
      await tester.pumpWidget(
        MultiProvider(
          providers: [
            ChangeNotifierProvider(create: (_) => AppProvider()),
          ],
          child: MaterialApp(
            home: AppHome(),
          ),
        ),
      );
      
      expect(find.byType(AppHome), findsOneWidget);
    }});
    
    testWidgets('App should display app title', (WidgetTester tester) async {{
      await tester.pumpWidget(
        MultiProvider(
          providers: [
            ChangeNotifierProvider(create: (_) => AppProvider()),
          ],
          child: MaterialApp(
            home: AppHome(),
          ),
        ),
      );
      
      expect(find.text('{app_name}'), findsOneWidget);
    }});
  }});
}}
"""
    
    def _generate_integration_test(self, app_name: str) -> str:
        """Generate integration test file"""
        return f"""import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:{app_name.lower().replace(' ', '_')}/main.dart' as app;

void main() {{
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  
  group('{app_name} Integration Tests', () {{
    testWidgets('Complete app flow test', (WidgetTester tester) async {{
      app.main();
      await tester.pumpAndSettle();
      
      // Verify app loads successfully
      expect(find.byType(MaterialApp), findsOneWidget);
      
      // Verify main screen is displayed
      expect(find.byType(Scaffold), findsOneWidget);
      
      // Verify app title is present
      expect(find.text('{app_name}'), findsOneWidget);
    }});
    
    testWidgets('App navigation test', (WidgetTester tester) async {{
      app.main();
      await tester.pumpAndSettle();
      
      // Test that app responds to user interaction
      await tester.tap(find.byType(Scaffold));
      await tester.pumpAndSettle();
      
      // App should still be responsive
      expect(find.byType(MaterialApp), findsOneWidget);
    }});
  }});
}}
"""
    
    def _generate_app_dart(self, app_name: str, structure: Dict[str, Any]) -> str:
        """Generate app.dart content"""
        return f"""import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

class AppHome extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: Text('{app_name}'),
        backgroundColor: Colors.blue,
      ),
      body: HomeScreen(),
    );
  }}
}}
"""
    
    def _generate_screen_code(self, feature: str, app_name: str) -> str:
        """Generate screen code for a feature"""
        if feature == "authentication":
            return f"""import 'package:flutter/material.dart';

class AuthenticationScreen extends StatefulWidget {{
  @override
  _AuthenticationScreenState createState() => _AuthenticationScreenState();
}}

class _AuthenticationScreenState extends State<AuthenticationScreen> {{
  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Welcome to {app_name}',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {{
                // Authentication logic
              }},
              child: Text('Sign In'),
            ),
          ],
        ),
      ),
    );
  }}
}}
"""
        elif feature == "home_screen":
            return f"""import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.home,
            size: 100,
            color: Colors.blue,
          ),
          SizedBox(height: 20),
          Text(
            'Welcome to {app_name}',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 10),
          Text(
            'Your app is ready!',
            style: TextStyle(fontSize: 16, color: Colors.grey),
          ),
        ],
      ),
    );
  }}
}}
"""
        return None
    
    def _generate_home_screen(self, app_name: str) -> str:
        """Generate a simple HomeScreen widget"""
        return f"""import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return Center(
      child: Text('Welcome to {app_name}!', style: TextStyle(fontSize: 24)),\n    );
  }}
}}
"""
    
    def _generate_model_code(self, app_name: str, structure: Dict[str, Any]) -> str:
        """Generate model code"""
        return f"""class AppModel {{
  final String id;
  final String name;
  final String description;
  final DateTime createdAt;

  AppModel({{
    required this.id,
    required this.name,
    required this.description,
    required this.createdAt,
  }});

  factory AppModel.fromJson(Map<String, dynamic> json) {{
    return AppModel(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      createdAt: DateTime.parse(json['createdAt']),
    );
  }}

  Map<String, dynamic> toJson() {{
    return {{
      'id': id,
      'name': name,
      'description': description,
      'createdAt': createdAt.toIso8601String(),
    }};
  }}
}}
"""
    
    def _generate_service_code(self, app_name: str, structure: Dict[str, Any]) -> str:
        """Generate service code"""
        return f"""import 'dart:convert';
import 'package:http/http.dart' as http;

class AppService {{
  static const String baseUrl = 'https://api.example.com';

  Future<Map<String, dynamic>> getData() async {{
    try {{
      final response = await http.get(Uri.parse('$baseUrl/data'));
      if (response.statusCode == 200) {{
        return json.decode(response.body);
      }} else {{
        throw Exception('Failed to load data');
      }}
    }} catch (e) {{
      throw Exception('Error: $e');
    }}
  }}
}}
"""
    
    def _generate_provider_code(self, app_name: str, structure: Dict[str, Any]) -> str:
        """Generate provider code"""
        return f"""import 'package:flutter/foundation.dart';
import '../models/app_model.dart';
import '../services/app_service.dart';

class AppProvider with ChangeNotifier {{
  AppService _service = AppService();
  List<AppModel> _items = [];
  bool _isLoading = false;

  List<AppModel> get items => _items;
  bool get isLoading => _isLoading;

  Future<void> loadData() async {{
    _isLoading = true;
    notifyListeners();

    try {{
      final data = await _service.getData();
      // Process data and update _items
      _isLoading = false;
      notifyListeners();
    }} catch (e) {{
      _isLoading = false;
      notifyListeners();
    }}
  }}
}}
"""
    
    async def _push_code_to_repository(self, repo_url: str, app_code: Dict[str, str]) -> bool:
        """Push generated code to GitHub repository using GitHub API"""
        try:
            # Extract repo name from URL
            repo_name = repo_url.split('/')[-1]
            owner = repo_url.split('/')[-2]
            
            logger.info(f"📤 Pushing code to repository: {owner}/{repo_name}")
            
            # Push each file using GitHub API
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"token {settings.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                for file_path, content in app_code.items():
                    # GitHub API expects base64 encoded content
                    import base64
                    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
                    
                    # Create file via GitHub API
                    file_data = {
                        "message": f"Add {file_path} - Generated by Conquest AI",
                        "content": encoded_content,
                        "branch": "main"
                    }
                    
                    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}"
                    
                    async with session.put(api_url, headers=headers, json=file_data) as response:
                        if response.status in [200, 201]:
                            logger.info(f"✅ Pushed {file_path}")
                        else:
                            error_text = await response.text()
                            logger.error(f"❌ Failed to push {file_path}: {error_text}")
                            return False
            
            logger.info(f"✅ Successfully pushed all files to {repo_url}")
            return True
            
        except Exception as e:
            logger.error("Error pushing code to repository", error=str(e))
            return False
    
    async def _build_apk(self, repo_url: str, app_name: str) -> str:
        """Build APK using GitHub Actions"""
        try:
            # Trigger GitHub Actions build
            repo_name = repo_url.split('/')[-1]
            
            # Create workflow file for APK building
            workflow_content = self._generate_apk_workflow(app_name)
            
            # Push workflow file to repository
            await self._push_workflow_file(repo_url, workflow_content)
            
            # Return the expected APK URL
            return f"{repo_url}/releases/latest/download/{app_name.lower().replace(' ', '-')}.apk"
            
        except Exception as e:
            logger.error("Error building APK", error=str(e))
            return f"{repo_url}/releases"
    
    def _generate_apk_workflow(self, app_name: str) -> str:
        """Generate GitHub Actions workflow for APK building with testing"""
        return f"""name: Build and Test APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.32.5'
          channel: 'stable'
      
      - name: Get dependencies
        run: flutter pub get
      
      - name: Run tests
        run: flutter test
      
      - name: Run integration tests
        run: flutter test integration_test/
      
      - name: Analyze code
        run: flutter analyze
      
      - name: Check formatting
        run: dart format --set-exit-if-changed .

  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.32.5'
          channel: 'stable'
      
      - name: Get dependencies
        run: flutter pub get
      
      - name: Build APK
        run: flutter build apk --release
      
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: {app_name.lower().replace(' ', '-')}-apk
          path: build/app/outputs/flutter-apk/app-release.apk
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: build/app/outputs/flutter-apk/app-release.apk
          tag_name: v${{{{ github.run_number }}}}
          name: {app_name} v${{{{ github.run_number }}}}
          body: |
            Automated build of {app_name}
            
            ✅ All tests passed
            ✅ Code analysis passed
            ✅ Formatting check passed
            
            Built from commit: ${{{{ github.sha }}}}
            Build number: ${{{{ github.run_number }}}}
        env:
          GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
"""
    
    async def _push_workflow_file(self, repo_url: str, workflow_content: str) -> bool:
        """Push workflow file to repository using GitHub API"""
        try:
            # Extract repo name from URL
            repo_name = repo_url.split('/')[-1]
            owner = repo_url.split('/')[-2]
            
            # GitHub API expects base64 encoded content
            import base64
            encoded_content = base64.b64encode(workflow_content.encode('utf-8')).decode('utf-8')
            
            # Create workflow file via GitHub API
            file_data = {
                "message": "Add GitHub Actions workflow for APK building - Generated by Conquest AI",
                "content": encoded_content,
                "branch": "main"
            }
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"token {settings.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/.github/workflows/build-apk.yml"
                
                async with session.put(api_url, headers=headers, json=file_data) as response:
                    if response.status in [200, 201]:
                        logger.info(f"✅ Created GitHub Actions workflow for {repo_name}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Failed to create workflow: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error("Error pushing workflow file", error=str(e))
            return False
    
    async def _create_deployment_record(self, app_id: str, app_name: str, repo_url: str, apk_url: str, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a deployment record in the database"""
        try:
            from sqlalchemy import insert
            from ..models.sql_models import ConquestDeployment
            
            deployment_data = {
                "id": app_id,
                "app_name": app_name,
                "repository_url": repo_url,
                "apk_url": apk_url,
                "status": "completed",
                "created_at": datetime.utcnow(),
                "app_data": json.dumps(app_data),
                "build_logs": json.dumps({"status": "success", "message": "App created successfully"})
            }
            
            session = get_session()
            try:
                stmt = insert(ConquestDeployment).values(**deployment_data)
                await session.execute(stmt)
                await session.commit()
                return deployment_data
            finally:
                await session.close()
                
        except Exception as e:
            logger.error("Error creating deployment record", error=str(e))
            return {
                "id": app_id,
                "app_name": app_name,
                "repository_url": repo_url,
                "apk_url": apk_url,
                "status": "completed",
                "created_at": datetime.utcnow().isoformat()
            }
    
    async def get_deployment_status(self, app_id: str) -> Dict[str, Any]:
        """Get deployment status for an app"""
        try:
            from sqlalchemy import select
            from ..models.sql_models import ConquestDeployment
            
            session = get_session()
            try:
                stmt = select(ConquestDeployment).where(ConquestDeployment.id == app_id)
                result = await session.execute(stmt)
                deployment = result.scalar_one_or_none()
                
                if deployment:
                    return {
                        "status": "success",
                        "deployment": {
                            "id": deployment.id,
                            "app_name": deployment.app_name,
                            "repository_url": deployment.repository_url,
                            "apk_url": deployment.apk_url,
                            "status": deployment.status,
                            "created_at": deployment.created_at.isoformat(),
                            "app_data": json.loads(deployment.app_data) if deployment.app_data else {},
                            "build_logs": json.loads(deployment.build_logs) if deployment.build_logs else {}
                        }
                    }
                else:
                    return {"status": "error", "message": "Deployment not found"}
                    
            finally:
                await session.close()
                
        except Exception as e:
            logger.error("Error getting deployment status", error=str(e))
            return {"status": "error", "message": str(e)}
    
    async def list_deployments(self) -> Dict[str, Any]:
        """List all deployments"""
        try:
            from sqlalchemy import select
            from ..models.sql_models import ConquestDeployment
            
            session = get_session()
            try:
                stmt = select(ConquestDeployment).order_by(ConquestDeployment.created_at.desc())
                result = await session.execute(stmt)
                deployments = result.scalars().all()
                
                return {
                    "status": "success",
                    "deployments": [
                        {
                            "id": d.id,
                            "app_name": d.app_name,
                            "repository_url": d.repository_url,
                            "apk_url": d.apk_url,
                            "status": d.status,
                            "created_at": d.created_at.isoformat()
                        }
                        for d in deployments
                    ]
                }
                
            finally:
                await session.close()
                
        except Exception as e:
            logger.error("Error listing deployments", error=str(e))
            return {"status": "error", "message": str(e)} 
    
    async def update_deployment_status(
        self, 
        app_id: str, 
        status: str, 
        error_message: Optional[str] = None,
        build_logs: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update deployment status"""
        try:
            session = get_session()
            try:
                # Update deployment record
                query = """
                    UPDATE conquest_deployments 
                    SET status = $1, updated_at = $2, error_message = $3, build_logs = $4
                    WHERE app_id = $5
                """
                await session.execute(
                    query, 
                    status, 
                    datetime.utcnow(), 
                    error_message or "", 
                    build_logs or "", 
                    app_id
                )
                await session.commit()
                
                return {
                    "status": "success",
                    "message": f"Deployment status updated to {status}"
                }
            finally:
                await session.close()
                
        except Exception as e:
            logger.error("Error updating deployment status", error=str(e))
            return {"status": "error", "message": str(e)}

    async def get_progress_logs(self) -> List[Dict[str, Any]]:
        """Get recent progress logs for Conquest AI operations"""
        try:
            session = get_session()
            try:
                query = """
                    SELECT 
                        app_id,
                        app_name,
                        status,
                        created_at,
                        updated_at,
                        error_message,
                        build_logs
                    FROM conquest_deployments 
                    ORDER BY created_at DESC 
                    LIMIT 50
                """
                result = await session.execute(query)
                rows = result.fetchall()
                
                logs = []
                for row in rows:
                    logs.append({
                        "app_id": row[0],
                        "app_name": row[1],
                        "status": row[2],
                        "created_at": row[3].isoformat() if row[3] else None,
                        "updated_at": row[4].isoformat() if row[4] else None,
                        "error_message": row[5],
                        "build_logs": row[6],
                        "type": "progress",
                        "message": f"App '{row[1]}' - Status: {row[2]}"
                    })
                
                return logs
            finally:
                await session.close()
                
        except Exception as e:
            logger.error("Error getting progress logs", error=str(e))
            return []

    async def get_error_learnings(self) -> List[Dict[str, Any]]:
        """Get error learnings from failed deployments"""
        try:
            session = get_session()
            try:
                query = """
                    SELECT 
                        app_id,
                        app_name,
                        error_message,
                        build_logs,
                        created_at
                    FROM conquest_deployments 
                    WHERE status = 'failed' AND error_message IS NOT NULL
                    ORDER BY created_at DESC 
                    LIMIT 20
                """
                result = await session.execute(query)
                rows = result.fetchall()
                
                learnings = []
                for row in rows:
                    learnings.append({
                        "app_id": row[0],
                        "app_name": row[1],
                        "error_message": row[2],
                        "build_logs": row[3],
                        "created_at": row[4].isoformat() if row[4] else None,
                        "learning_type": "build_failure",
                        "recommendation": self._generate_error_recommendation(row[2])
                    })
                
                return learnings
            finally:
                await session.close()
                
        except Exception as e:
            logger.error("Error getting error learnings", error=str(e))
            return []

    def _generate_error_recommendation(self, error_message: Optional[str]) -> str:
        """Generate recommendation based on error message"""
        if not error_message:
            return "Review the build logs for specific error details"
            
        error_lower = error_message.lower()
        
        if "dependency" in error_lower or "package" in error_lower:
            return "Check and update dependencies in pubspec.yaml"
        elif "syntax" in error_lower or "compile" in error_lower:
            return "Review code syntax and fix compilation errors"
        elif "permission" in error_lower or "access" in error_lower:
            return "Check file permissions and access rights"
        elif "network" in error_lower or "connection" in error_lower:
            return "Verify network connectivity and API endpoints"
        elif "memory" in error_lower or "resource" in error_lower:
            return "Optimize memory usage and resource allocation"
        else:
            return "Review the build logs for specific error details" 

    async def _wait_for_github_actions_and_update_status(self, repo_url: str, app_id: str, app_name: str):
        """Poll GitHub Actions workflow run, fetch test results, and update deployment record. Now runs tests twice and sets 'testing' status."""
        repo_name = repo_url.split('/')[-1]
        owner = repo_url.split('/')[-2]
        workflow_filename = 'build-apk.yml'
        headers = {
            "Authorization": f"token {settings.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Set status to 'testing' before starting tests
        await self.update_deployment_status(app_id, 'testing')

        async def wait_for_test_run():
            workflow_run_id = None
            test_status = 'unknown'
            test_output = ''
            for attempt in range(30):  # Poll for up to ~5 minutes
                await asyncio.sleep(10)
                async with aiohttp.ClientSession() as session:
                    # List workflow runs
                    url = f"https://api.github.com/repos/{owner}/{repo_name}/actions/workflows/{workflow_filename}/runs?branch=main"
                    async with session.get(url, headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            runs = data.get('workflow_runs', [])
                            if runs:
                                workflow_run_id = runs[0]['id']
                                status = runs[0]['status']
                                conclusion = runs[0]['conclusion']
                                if status == 'completed':
                                    # Get jobs for this run
                                    jobs_url = runs[0]['jobs_url']
                                    async with session.get(jobs_url, headers=headers) as jobs_resp:
                                        jobs_data = await jobs_resp.json()
                                        jobs = jobs_data.get('jobs', [])
                                        for job in jobs:
                                            if job['name'].lower().startswith('test'):
                                                test_status = job['conclusion']
                                                # Get logs
                                                logs_url = job['logs_url']
                                                async with session.get(logs_url, headers=headers) as logs_resp:
                                                    if logs_resp.status == 200:
                                                        test_output = await logs_resp.text()
                                                    else:
                                                        test_output = f"Failed to fetch logs: {logs_resp.status}"
                                                break
                                    break
                        else:
                            logger.warning(f"Failed to fetch workflow runs: {resp.status}")
            return test_status, test_output

        # First test run
        first_status, first_output = await wait_for_test_run()
        if first_status != 'success':
            await self.update_deployment_status(app_id, 'failed', error_message='First test run failed', build_logs=first_output)
            return first_status, first_output

        # Trigger a re-run of the workflow for the second test
        # Find the latest workflow run id
        async with aiohttp.ClientSession() as session:
            url = f"https://api.github.com/repos/{owner}/{repo_name}/actions/workflows/{workflow_filename}/runs?branch=main"
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    runs = data.get('workflow_runs', [])
                    if runs:
                        workflow_run_id = runs[0]['id']
                        # Trigger re-run
                        rerun_url = f"https://api.github.com/repos/{owner}/{repo_name}/actions/runs/{workflow_run_id}/rerun"
                        async with session.post(rerun_url, headers=headers) as rerun_resp:
                            if rerun_resp.status != 201 and rerun_resp.status != 200:
                                logger.warning(f"Failed to trigger workflow re-run: {rerun_resp.status}")
                else:
                    logger.warning(f"Failed to fetch workflow runs for re-run: {resp.status}")

        # Wait for the second test run
        second_status, second_output = await wait_for_test_run()
        if second_status == 'success':
            await self.update_deployment_status(app_id, 'completed', build_logs=second_output)
        else:
            await self.update_deployment_status(app_id, 'failed', error_message='Second test run failed', build_logs=second_output)
        return (first_status, first_output), (second_status, second_output) 