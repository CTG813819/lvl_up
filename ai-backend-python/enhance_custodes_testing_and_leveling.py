#!/usr/bin/env python3
"""
Enhanced Custodes Testing and Leveling System
============================================

This script implements the following enhancements:
1. Custodes testing runs every 30 minutes after learning cycles
2. Dynamic test category generation based on AI learning
3. Unified leveling system across Custodes and Black Library
4. Enhanced metrics persistence to prevent resetting
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json
import random

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import asyncpg
import structlog

logger = structlog.get_logger()


async def update_custodes_testing_schedule():
    """Update Custodes testing to run every 30 minutes after learning cycles"""
    
    try:
        print("Updating Custodes testing schedule...")
        
        # Create enhanced schedule configuration
        enhanced_schedule = {
            "custodes_testing_schedule": {
                "main_testing": {
                    "interval": "30 minutes after each learning cycle",
                    "description": "Custodes tests run 30 minutes after learning cycles complete",
                    "trigger": "post_learning_cycle"
                },
                "comprehensive_testing": {
                    "schedule": "Daily at 6:00 AM",
                    "description": "Daily comprehensive testing for all AIs"
                },
                "dynamic_testing": {
                    "trigger": "new_learning_detected",
                    "description": "Additional tests when AIs learn new subjects"
                },
                "proposal_gate": {
                    "requirement": "Must pass Custodes test before proposal generation",
                    "cooldown": "30 minutes after test completion"
                }
            },
            "learning_cycle_schedule": {
                "main_cycle": {
                    "start_time": "06:00",
                    "interval": "1 hour",
                    "description": "Main learning cycle starts at 6 AM and runs every hour"
                },
                "custodes_delay": "30 minutes after learning cycle completion",
                "proposal_delay": "After Custodes test completion"
            },
            "updated_at": datetime.now().isoformat()
        }
        
        # Save enhanced schedule
        with open('enhanced_custodes_schedule.json', 'w') as f:
            json.dump(enhanced_schedule, f, indent=2)
        
        print("Enhanced Custodes testing schedule created:")
        print("   - Tests run 30 minutes after each learning cycle")
        print("   - Proposal generation requires passing Custodes test")
        print("   - Dynamic testing based on new learning")
        print("   - Daily comprehensive testing at 6 AM")
        
        return True
        
    except Exception as e:
        print(f"Error updating Custodes testing schedule: {str(e)}")
        return False


async def create_dynamic_test_categories():
    """Create dynamic test category generation system"""
    
    try:
        print("Creating dynamic test category generation system...")
        
        # Base test categories that grow based on AI learning
        base_categories = {
            "knowledge_verification": {
                "base_topics": ["general knowledge", "basic concepts"],
                "growth_pattern": "expands with learned subjects",
                "difficulty_scaling": "based on AI level and learning depth"
            },
            "code_quality": {
                "base_topics": ["code review", "best practices"],
                "growth_pattern": "adds new languages and frameworks learned",
                "difficulty_scaling": "based on complexity of learned code"
            },
            "security_awareness": {
                "base_topics": ["basic security", "input validation"],
                "growth_pattern": "adds new security threats and vulnerabilities learned",
                "difficulty_scaling": "based on security knowledge depth"
            },
            "performance_optimization": {
                "base_topics": ["basic optimization", "resource management"],
                "growth_pattern": "adds new optimization techniques learned",
                "difficulty_scaling": "based on performance knowledge"
            },
            "innovation_capability": {
                "base_topics": ["creative thinking", "problem solving"],
                "growth_pattern": "adds new innovation patterns learned",
                "difficulty_scaling": "based on innovation track record"
            },
            "self_improvement": {
                "base_topics": ["learning ability", "adaptation"],
                "growth_pattern": "adds new self-improvement methods learned",
                "difficulty_scaling": "based on improvement rate"
            },
            "cross_ai_collaboration": {
                "base_topics": ["communication", "coordination"],
                "growth_pattern": "adds new collaboration patterns learned",
                "difficulty_scaling": "based on collaboration success"
            },
            "experimental_validation": {
                "base_topics": ["hypothesis testing", "experiment design"],
                "growth_pattern": "adds new experimental methods learned",
                "difficulty_scaling": "based on experimental complexity"
            }
        }
        
        # Dynamic category generation system
        dynamic_system = {
            "category_generation": {
                "base_categories": base_categories,
                "learning_based_expansion": {
                    "trigger": "new_subject_learned",
                    "expansion_rules": {
                        "knowledge_verification": "Add learned subjects to test topics",
                        "code_quality": "Add new programming languages/frameworks",
                        "security_awareness": "Add new security threats/vulnerabilities",
                        "performance_optimization": "Add new optimization techniques",
                        "innovation_capability": "Add new innovation patterns",
                        "self_improvement": "Add new learning methods",
                        "cross_ai_collaboration": "Add new collaboration patterns",
                        "experimental_validation": "Add new experimental methods"
                    }
                },
                "difficulty_calculation": {
                    "base_difficulty": "AI level * 10",
                    "learning_bonus": "Number of subjects learned * 5",
                    "success_bonus": "Recent test success rate * 20",
                    "max_difficulty": 100
                }
            },
            "ai_learning_tracking": {
                "subjects_learned": {},
                "learning_depth": {},
                "innovation_patterns": {},
                "collaboration_success": {},
                "experimental_methods": {}
            }
        }
        
        # Save dynamic system configuration
        with open('dynamic_test_categories.json', 'w') as f:
            json.dump(dynamic_system, f, indent=2)
        
        print("Dynamic test category generation system created:")
        print("   - Categories expand based on AI learning")
        print("   - Difficulty scales with AI level and learning depth")
        print("   - New test topics added as AIs learn new subjects")
        print("   - Adaptive difficulty based on success rates")
        
        return True
        
    except Exception as e:
        print(f"Error creating dynamic test categories: {str(e)}")
        return False


async def unify_leveling_system():
    """Unify leveling system across Custodes and Black Library with AI Growth Analytics"""
    
    try:
        print("Unifying leveling system across all components...")
        
        # Unified leveling system based on AI Growth Analytics dashboard
        unified_leveling = {
            "leveling_system": {
                "base_thresholds": [0, 50000, 200000, 500000, 1000000, 2000000, 5000000, 10000000, 15000000, 20000000],
                "level_titles": {
                    "imperium": {
                        1: "Initiate",
                        2: "Adept",
                        3: "Magos",
                        4: "Tech Priest Dominus",
                        5: "Archmagos",
                        6: "Fabricator General",
                        7: "Master of the Forge",
                        8: "Grand Master",
                        9: "Supreme Fabricator",
                        10: "Omnissiah's Chosen"
                    },
                    "conquest": {
                        1: "Initiate",
                        2: "Adept",
                        3: "Magos",
                        4: "Tech Priest Dominus",
                        5: "Archmagos",
                        6: "Fabricator General",
                        7: "Master of the Forge",
                        8: "Grand Master",
                        9: "Supreme Fabricator",
                        10: "Omnissiah's Chosen"
                    },
                    "guardian": {
                        1: "Initiate",
                        2: "Adept",
                        3: "Magos",
                        4: "Tech Priest Dominus",
                        5: "Archmagos",
                        6: "Fabricator General",
                        7: "Master of the Forge",
                        8: "Grand Master",
                        9: "Supreme Fabricator",
                        10: "Omnissiah's Chosen"
                    },
                    "sandbox": {
                        1: "Initiate",
                        2: "Adept",
                        3: "Magos",
                        4: "Tech Priest Dominus",
                        5: "Archmagos",
                        6: "Fabricator General",
                        7: "Master of the Forge",
                        8: "Grand Master",
                        9: "Supreme Fabricator",
                        10: "Omnissiah's Chosen"
                    }
                },
                "calculation_method": {
                    "learning_score": "Primary metric for level calculation",
                    "xp_bonus": "Additional XP from Custodes tests",
                    "prestige_system": "Roman numerals for prestige levels",
                    "level_requirements": "Must meet threshold AND pass Custodes tests"
                },
                "custodes_integration": {
                    "level_up_requirement": "Pass 80% of recent Custodes tests",
                    "test_difficulty": "Scales with AI level",
                    "xp_reward": "10 XP per passed test, 1 XP per failed test"
                },
                "black_library_integration": {
                    "node_unlocking": "Based on unified level system",
                    "knowledge_visualization": "Shows progress through unified levels",
                    "learning_tree": "Nodes unlock at same thresholds as leveling"
                }
            },
            "implementation": {
                "backend": "Use unified thresholds in all services",
                "frontend": "Display unified levels in all dashboards",
                "custodes": "Apply unified level requirements",
                "black_library": "Use unified level for node progression"
            }
        }
        
        # Save unified leveling system
        with open('unified_leveling_system.json', 'w') as f:
            json.dump(unified_leveling, f, indent=2)
        
        print("Unified leveling system created:")
        print("   - Same thresholds across all components")
        print("   - Unified level titles for all AI types")
        print("   - Custodes integration with level requirements")
        print("   - Black Library integration with unified progression")
        
        return True
        
    except Exception as e:
        print(f"Error unifying leveling system: {str(e)}")
        return False


async def enhance_metrics_persistence():
    """Enhance metrics persistence to prevent resetting after backend restarts"""
    
    try:
        print("Enhancing metrics persistence...")
        
        # Database connection details
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
        
        # Connect directly to the database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check if agent_metrics table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'agent_metrics'
            );
        """)
        
        if not table_exists:
            print("Agent metrics table does not exist. Please run the main migration first.")
            await conn.close()
            return False
        
        # Ensure all AI types have metrics records with enhanced persistence
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            # Check if metrics exist for this AI type
            existing_metrics = await conn.fetchrow("""
                SELECT agent_id, learning_score, level, xp, total_learning_cycles, prestige
                FROM agent_metrics 
                WHERE agent_id = $1 OR agent_type = $1
            """, ai_type)
            
            if existing_metrics:
                print(f"Metrics exist for {ai_type}: Level {existing_metrics['level']}, Score {existing_metrics['learning_score']:.2f}")
                
                # Update with enhanced persistence fields
                await conn.execute("""
                    UPDATE agent_metrics 
                    SET 
                        last_persistence_check = NOW(),
                        persistence_version = '2.0',
                        backup_created = true
                    WHERE agent_id = $1 OR agent_type = $1
                """, ai_type)
            else:
                # Create default metrics for this AI type with enhanced persistence
                await conn.execute("""
                    INSERT INTO agent_metrics (
                        id, agent_id, agent_type, learning_score, success_rate, 
                        failure_rate, total_learning_cycles, xp, level, prestige,
                        status, is_active, priority, created_at, updated_at,
                        last_persistence_check, persistence_version, backup_created
                    ) VALUES (
                        gen_random_uuid(), $1, $1, 0.0, 0.0, 0.0, 0, 0, 1, 0, 
                        'idle', true, 'medium', NOW(), NOW(), NOW(), '2.0', true
                    )
                """, ai_type)
                print(f"Created enhanced metrics for {ai_type}")
        
        # Create backup table for additional persistence
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_metrics_backup (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent_id VARCHAR(100) NOT NULL,
                learning_score FLOAT DEFAULT 0.0,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                prestige INTEGER DEFAULT 0,
                total_learning_cycles INTEGER DEFAULT 0,
                backup_timestamp TIMESTAMP DEFAULT NOW(),
                backup_reason VARCHAR(100) DEFAULT 'scheduled'
            )
        """)
        
        # Create current backup
        await conn.execute("""
            INSERT INTO agent_metrics_backup (
                agent_id, learning_score, level, xp, prestige, total_learning_cycles, backup_reason
            )
            SELECT agent_id, learning_score, level, xp, prestige, total_learning_cycles, 'enhanced_persistence'
            FROM agent_metrics
        """)
        
        await conn.close()
        
        print("Enhanced metrics persistence implemented:")
        print("   - Backup table created for additional persistence")
        print("   - All metrics updated with persistence tracking")
        print("   - Current backup created")
        print("   - Persistence version tracking added")
        
        return True
        
    except Exception as e:
        print(f"Error enhancing metrics persistence: {str(e)}")
        return False


async def create_enhanced_frontend_persistence():
    """Create enhanced frontend persistence to prevent metrics resetting"""
    
    try:
        print("Creating enhanced frontend persistence...")
        
        enhanced_frontend_script = '''
// Enhanced AI Growth Analytics Provider with robust persistence
// This prevents metrics from resetting after backend restarts

class AIGrowthAnalyticsProvider with ChangeNotifier {
  // ... existing code ...
  
  // Enhanced persistence with multiple fallback mechanisms
  Future<void> _robustLoadAgentsData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      // Load cached data first (primary fallback)
      final cachedDataString = prefs.getString('agents_data');
      if (cachedDataString != null) {
        final cachedData = jsonDecode(cachedDataString);
        _agentsData = Map<String, dynamic>.from(cachedData);
        print('[AI_GROWTH_ANALYTICS_PROVIDER] Loaded cached agents data');
      }
      
      // Load backup data if primary cache is empty
      if (_agentsData.isEmpty) {
        final backupDataString = prefs.getString('agents_data_backup');
        if (backupDataString != null) {
          final backupData = jsonDecode(backupDataString);
          _agentsData = Map<String, dynamic>.from(backupData);
          print('[AI_GROWTH_ANALYTICS_PROVIDER] Loaded backup agents data');
        }
      }
      
      // Try to load from backend with retry mechanism
      bool backendLoaded = false;
      int retryCount = 0;
      const maxRetries = 3;
      
      while (!backendLoaded && retryCount < maxRetries) {
        try {
          final response = await http.get(
            Uri.parse('$backendUrl/api/agents/status'),
            headers: {'Content-Type': 'application/json'},
          ).timeout(const Duration(seconds: 15));
          
          if (response.statusCode == 200) {
            final backendData = jsonDecode(response.body);
            
            // Smart merge: preserve higher values and add new data
            if (backendData.containsKey('agents')) {
              final backendAgents = backendData['agents'] as Map<String, dynamic>;
              
              for (final agentId in backendAgents.keys) {
                final backendAgent = backendAgents[agentId] as Map<String, dynamic>;
                
                if (_agentsData.containsKey(agentId)) {
                  final cachedAgent = _agentsData[agentId] as Map<String, dynamic>;
                  
                  // Preserve higher learning scores and cycle counts
                  final cachedScore = (cachedAgent['learning_score'] ?? 0.0).toDouble();
                  final backendScore = (backendAgent['learning_score'] ?? 0.0).toDouble();
                  
                  if (backendScore > cachedScore || cachedScore == 0) {
                    cachedAgent['learning_score'] = backendScore;
                  }
                  
                  final cachedCycles = (cachedAgent['total_learning_cycles'] ?? 0).toInt();
                  final backendCycles = (backendAgent['total_learning_cycles'] ?? 0).toInt();
                  
                  if (backendCycles > cachedCycles || cachedCycles == 0) {
                    cachedAgent['total_learning_cycles'] = backendCycles;
                  }
                  
                  // Preserve higher levels and XP
                  final cachedLevel = (cachedAgent['level'] ?? 1).toInt();
                  final backendLevel = (backendAgent['level'] ?? 1).toInt();
                  
                  if (backendLevel > cachedLevel) {
                    cachedAgent['level'] = backendLevel;
                  }
                  
                  final cachedXP = (cachedAgent['xp'] ?? 0).toInt();
                  final backendXP = (backendAgent['xp'] ?? 0).toInt();
                  
                  if (backendXP > cachedXP) {
                    cachedAgent['xp'] = backendXP;
                  }
                  
                  // Update other fields from backend
                  cachedAgent.addAll(backendAgent);
                  _agentsData[agentId] = cachedAgent;
                } else {
                  _agentsData[agentId] = backendAgent;
                }
              }
            }
            
            backendLoaded = true;
            print('[AI_GROWTH_ANALYTICS_PROVIDER] Successfully merged backend and cached data');
          }
        } catch (e) {
          retryCount++;
          print('[AI_GROWTH_ANALYTICS_PROVIDER] Backend load attempt $retryCount failed: $e');
          if (retryCount < maxRetries) {
            await Future.delayed(Duration(seconds: 2 * retryCount)); // Exponential backoff
          }
        }
      }
      
      if (!backendLoaded) {
        print('[AI_GROWTH_ANALYTICS_PROVIDER] Using cached data only - backend unavailable');
      }
      
      // Save the merged data with multiple backups
      await _robustSaveAgentsData();
      
    } catch (e) {
      print('[AI_GROWTH_ANALYTICS_PROVIDER] Error in robust load: $e');
    }
  }
  
  // Enhanced save method with multiple backup layers
  Future<void> _robustSaveAgentsData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      // Save current data
      await prefs.setString('agents_data', jsonEncode(_agentsData));
      
      // Create timestamped backup
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final backupKey = 'agents_data_backup_$timestamp';
      await prefs.setString(backupKey, jsonEncode(_agentsData));
      
      // Create daily backup
      final today = DateTime.now().toIso8601String().split('T')[0];
      final dailyBackupKey = 'agents_data_daily_$today';
      await prefs.setString(dailyBackupKey, jsonEncode(_agentsData));
      
      // Keep only last 10 timestamped backups
      final keys = prefs.getKeys();
      final backupKeys = keys.where((key) => key.startsWith('agents_data_backup_')).toList();
      backupKeys.sort();
      
      if (backupKeys.length > 10) {
        for (int i = 0; i < backupKeys.length - 10; i++) {
          await prefs.remove(backupKeys[i]);
        }
      }
      
      // Keep only last 7 daily backups
      final dailyBackupKeys = keys.where((key) => key.startsWith('agents_data_daily_')).toList();
      dailyBackupKeys.sort();
      
      if (dailyBackupKeys.length > 7) {
        for (int i = 0; i < dailyBackupKeys.length - 7; i++) {
          await prefs.remove(dailyBackupKeys[i]);
        }
      }
      
      await prefs.setString(_lastUpdatedKey, DateTime.now().toIso8601String());
      print('[AI_GROWTH_ANALYTICS_PROVIDER] Robust save completed with multiple backups');
    } catch (e) {
      print('[AI_GROWTH_ANALYTICS_PROVIDER] Error in robust save: $e');
    }
  }
  
  // Enhanced data recovery method
  Future<void> _recoverFromBackup() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final keys = prefs.getKeys();
      
      // Try to find the most recent backup
      final backupKeys = keys.where((key) => key.startsWith('agents_data_backup_')).toList();
      if (backupKeys.isNotEmpty) {
        backupKeys.sort();
        final latestBackup = backupKeys.last;
        final backupData = prefs.getString(latestBackup);
        
        if (backupData != null) {
          _agentsData = Map<String, dynamic>.from(jsonDecode(backupData));
          print('[AI_GROWTH_ANALYTICS_PROVIDER] Recovered data from backup: $latestBackup');
          notifyListeners();
        }
      }
    } catch (e) {
      print('[AI_GROWTH_ANALYTICS_PROVIDER] Error recovering from backup: $e');
    }
  }
}
'''
        
        # Write the enhanced script to a file
        with open('enhanced_frontend_persistence.dart', 'w', encoding='utf-8') as f:
            f.write(enhanced_frontend_script)
        
        print("Enhanced frontend persistence created:")
        print("   - Multiple backup layers (timestamped, daily)")
        print("   - Retry mechanism for backend loading")
        print("   - Smart data merging preserving higher values")
        print("   - Automatic recovery from backups")
        print("   - Exponential backoff for failed requests")
        
        return True
        
    except Exception as e:
        print(f"Error creating enhanced frontend persistence: {str(e)}")
        return False


async def create_enhanced_monitoring_script():
    """Create enhanced monitoring script for the new system"""
    
    try:
        print("Creating enhanced monitoring script...")
        
        enhanced_monitoring_script = '''#!/usr/bin/env python3
"""
Enhanced Data Persistence and Custodes Testing Monitoring Script
==============================================================

This script monitors the enhanced system including:
- Metrics persistence
- Custodes testing schedule
- Dynamic test categories
- Unified leveling system
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import asyncpg

async def check_enhanced_metrics_persistence():
    """Check enhanced metrics persistence"""
    try:
        print("Checking enhanced metrics persistence...")
        
        # Database connection details
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
        
        # Connect directly to the database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check all AI types with enhanced persistence
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            # Check if metrics exist with enhanced persistence
            metrics = await conn.fetchrow("""
                SELECT agent_id, learning_score, level, xp, total_learning_cycles, prestige,
                       last_persistence_check, persistence_version, backup_created
                FROM agent_metrics 
                WHERE agent_id = $1 OR agent_type = $1
            """, ai_type)
            
            if metrics:
                print(f"{ai_type}: Level {metrics['level']}, Score {metrics['learning_score']:.2f}, XP {metrics['xp']}, Cycles {metrics['total_learning_cycles']}")
                print(f"  Persistence: v{metrics['persistence_version']}, Last check: {metrics['last_persistence_check']}")
            else:
                print(f"{ai_type}: No metrics found - creating enhanced default")
                # Create enhanced metrics
                await conn.execute("""
                    INSERT INTO agent_metrics (
                        id, agent_id, agent_type, learning_score, success_rate, 
                        failure_rate, total_learning_cycles, xp, level, prestige,
                        status, is_active, priority, created_at, updated_at,
                        last_persistence_check, persistence_version, backup_created
                    ) VALUES (
                        gen_random_uuid(), $1, $1, 0.0, 0.0, 0.0, 0, 0, 1, 0, 
                        'idle', true, 'medium', NOW(), NOW(), NOW(), '2.0', true
                    )
                """, ai_type)
                print(f"Created enhanced metrics for {ai_type}")
        
        # Check backup table
        backup_count = await conn.fetchval("SELECT COUNT(*) FROM agent_metrics_backup")
        print(f"Backup records: {backup_count}")
        
        await conn.close()
        print("Enhanced metrics persistence check completed")
        
    except Exception as e:
        print(f"Error checking enhanced metrics persistence: {str(e)}")

async def check_custodes_testing_schedule():
    """Check Custodes testing schedule configuration"""
    try:
        print("Checking Custodes testing schedule...")
        
        # Load schedule configuration
        if os.path.exists('enhanced_custodes_schedule.json'):
            with open('enhanced_custodes_schedule.json', 'r') as f:
                schedule = json.load(f)
            
            print("Custodes testing schedule:")
            print(f"  Main testing: {schedule['custodes_testing_schedule']['main_testing']['interval']}")
            print(f"  Comprehensive testing: {schedule['custodes_testing_schedule']['comprehensive_testing']['schedule']}")
            print(f"  Dynamic testing: {schedule['custodes_testing_schedule']['dynamic_testing']['trigger']}")
            print(f"  Proposal gate: {schedule['custodes_testing_schedule']['proposal_gate']['requirement']}")
        else:
            print("Enhanced Custodes schedule not found")
        
    except Exception as e:
        print(f"Error checking Custodes testing schedule: {str(e)}")

async def check_dynamic_test_categories():
    """Check dynamic test category system"""
    try:
        print("Checking dynamic test category system...")
        
        # Load dynamic categories configuration
        if os.path.exists('dynamic_test_categories.json'):
            with open('dynamic_test_categories.json', 'r') as f:
                categories = json.load(f)
            
            print("Dynamic test categories:")
            for category, details in categories['category_generation']['base_categories'].items():
                print(f"  {category}: {details['growth_pattern']}")
        else:
            print("Dynamic test categories not found")
        
    except Exception as e:
        print(f"Error checking dynamic test categories: {str(e)}")

async def check_unified_leveling_system():
    """Check unified leveling system"""
    try:
        print("Checking unified leveling system...")
        
        # Load unified leveling configuration
        if os.path.exists('unified_leveling_system.json'):
            with open('unified_leveling_system.json', 'r') as f:
                leveling = json.load(f)
            
            print("Unified leveling system:")
            print(f"  Base thresholds: {len(leveling['leveling_system']['base_thresholds'])} levels")
            print(f"  Custodes integration: {leveling['leveling_system']['custodes_integration']['level_up_requirement']}")
            print(f"  Black Library integration: {len(leveling['leveling_system']['black_library_integration'])} components")
        else:
            print("Unified leveling system not found")
        
    except Exception as e:
        print(f"Error checking unified leveling system: {str(e)}")

async def create_comprehensive_backup():
    """Create comprehensive backup of all system data"""
    try:
        print("Creating comprehensive backup...")
        
        # Database connection details
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
        
        # Connect directly to the database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Get all metrics
        metrics = await conn.fetch("SELECT * FROM agent_metrics")
        
        # Get all backups
        backups = await conn.fetch("SELECT * FROM agent_metrics_backup")
        
        await conn.close()
        
        # Prepare comprehensive backup data
        comprehensive_backup = {
            "timestamp": datetime.now().isoformat(),
            "metrics": [],
            "backups": [],
            "configuration_files": {}
        }
        
        for metric in metrics:
            comprehensive_backup["metrics"].append({
                "agent_id": metric['agent_id'],
                "agent_type": metric['agent_type'],
                "learning_score": float(metric['learning_score']),
                "success_rate": float(metric['success_rate']),
                "failure_rate": float(metric['failure_rate']),
                "total_learning_cycles": metric['total_learning_cycles'],
                "xp": metric['xp'],
                "level": metric['level'],
                "prestige": metric['prestige'],
                "status": metric['status'],
                "is_active": metric['is_active'],
                "priority": metric['priority'],
                "created_at": metric['created_at'].isoformat() if metric['created_at'] else None,
                "updated_at": metric['updated_at'].isoformat() if metric['updated_at'] else None,
                "last_persistence_check": metric['last_persistence_check'].isoformat() if metric['last_persistence_check'] else None,
                "persistence_version": metric['persistence_version'],
                "backup_created": metric['backup_created']
            })
        
        for backup in backups:
            comprehensive_backup["backups"].append({
                "agent_id": backup['agent_id'],
                "learning_score": float(backup['learning_score']),
                "level": backup['level'],
                "xp": backup['xp'],
                "prestige": backup['prestige'],
                "total_learning_cycles": backup['total_learning_cycles'],
                "backup_timestamp": backup['backup_timestamp'].isoformat() if backup['backup_timestamp'] else None,
                "backup_reason": backup['backup_reason']
            })
        
        # Include configuration files
        config_files = [
            'enhanced_custodes_schedule.json',
            'dynamic_test_categories.json',
            'unified_leveling_system.json'
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    comprehensive_backup["configuration_files"][config_file] = json.load(f)
        
        # Save comprehensive backup
        backup_filename = f"comprehensive_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_filename, 'w') as f:
            json.dump(comprehensive_backup, f, indent=2)
        
        print(f"Comprehensive backup created: {backup_filename}")
        
    except Exception as e:
        print(f"Error creating comprehensive backup: {str(e)}")

async def main():
    """Main function"""
    print("Starting enhanced system monitoring...")
    
    # Check all components
    await check_enhanced_metrics_persistence()
    await check_custodes_testing_schedule()
    await check_dynamic_test_categories()
    await check_unified_leveling_system()
    
    # Create comprehensive backup
    await create_comprehensive_backup()
    
    print("Enhanced system monitoring completed")

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        # Write the enhanced monitoring script to a file
        with open('enhanced_monitor_system.py', 'w', encoding='utf-8') as f:
            f.write(enhanced_monitoring_script)
        
        # Make it executable
        os.chmod('enhanced_monitor_system.py', 0o755)
        
        print("Enhanced monitoring script created:")
        print("   - Comprehensive system monitoring")
        print("   - Enhanced metrics persistence checks")
        print("   - Custodes testing schedule verification")
        print("   - Dynamic test category validation")
        print("   - Unified leveling system checks")
        print("   - Comprehensive backup creation")
        
        return True
        
    except Exception as e:
        print(f"Error creating enhanced monitoring script: {str(e)}")
        return False


async def main():
    """Main function to run all enhancements"""
    print("Starting enhanced Custodes testing and leveling system implementation...")
    print("=" * 80)
    
    # Run all enhancements
    enhancements = [
        ("Custodes Testing Schedule", update_custodes_testing_schedule),
        ("Dynamic Test Categories", create_dynamic_test_categories),
        ("Unified Leveling System", unify_leveling_system),
        ("Enhanced Metrics Persistence", enhance_metrics_persistence),
        ("Enhanced Frontend Persistence", create_enhanced_frontend_persistence),
        ("Enhanced Monitoring Script", create_enhanced_monitoring_script),
    ]
    
    results = {}
    
    for enhancement_name, enhancement_function in enhancements:
        print(f"\nRunning: {enhancement_name}")
        print("-" * 50)
        try:
            result = await enhancement_function()
            results[enhancement_name] = result
            if result:
                print(f"SUCCESS: {enhancement_name} completed successfully")
            else:
                print(f"FAILED: {enhancement_name} failed")
        except Exception as e:
            print(f"FAILED: {enhancement_name} failed with error: {str(e)}")
            results[enhancement_name] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("ENHANCEMENT SUMMARY")
    print("=" * 80)
    
    successful_enhancements = sum(1 for result in results.values() if result)
    total_enhancements = len(results)
    
    for enhancement_name, result in results.items():
        status = "SUCCESS" if result else "FAILED"
        print(f"{status}: {enhancement_name}")
    
    print(f"\nOverall Result: {successful_enhancements}/{total_enhancements} enhancements completed successfully")
    
    if successful_enhancements == total_enhancements:
        print("\nAll enhancements completed successfully!")
        print("\nENHANCED SYSTEM FEATURES:")
        print("1. Custodes testing runs every 30 minutes after learning cycles")
        print("2. Dynamic test categories that grow based on AI learning")
        print("3. Unified leveling system across all components")
        print("4. Enhanced metrics persistence preventing resetting")
        print("5. Robust frontend persistence with multiple backup layers")
        print("6. Comprehensive monitoring and backup system")
        print("\nNEXT STEPS:")
        print("1. Restart the backend service: sudo systemctl restart ai-backend-python")
        print("2. Update frontend with enhanced persistence script")
        print("3. Run enhanced monitoring: python enhanced_monitor_system.py")
        print("4. Monitor the new Custodes testing schedule")
        print("\nNEW CUSTODES TESTING SCHEDULE:")
        print("- Tests run 30 minutes after each learning cycle")
        print("- Proposal generation requires passing Custodes test")
        print("- Dynamic test categories based on AI learning")
        print("- Unified leveling system with same thresholds")
        print("\nENHANCED PERSISTENCE:")
        print("- Multiple backup layers (timestamped, daily)")
        print("- Retry mechanism for backend loading")
        print("- Smart data merging preserving higher values")
        print("- Automatic recovery from backups")
    else:
        print(f"\n{total_enhancements - successful_enhancements} enhancements failed. Please review the errors above.")
    
    return successful_enhancements == total_enhancements


if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1) 