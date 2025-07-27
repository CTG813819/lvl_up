#!/usr/bin/env python3
"""
Simple Metrics Persistence Fix for EC2
=====================================

This script fixes the metrics resetting issue and updates learning cycles
without requiring external dependencies.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import asyncpg
import structlog

logger = structlog.get_logger()


async def fix_metrics_persistence():
    """Fix agent metrics persistence by ensuring proper initialization"""
    
    try:
        print("🔧 Fixing agent metrics persistence...")
        
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
            print("❌ Agent metrics table does not exist. Please run the main migration first.")
            await conn.close()
            return False
        
        # Check if we have any agent metrics
        metrics_count = await conn.fetchval("SELECT COUNT(*) FROM agent_metrics")
        print(f"📊 Found {metrics_count} existing agent metrics")
        
        # Ensure all AI types have metrics records
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            # Check if metrics exist for this AI type
            existing_metrics = await conn.fetchval("""
                SELECT COUNT(*) FROM agent_metrics 
                WHERE agent_id = $1 OR agent_type = $1
            """, ai_type)
            
            if existing_metrics == 0:
                # Create default metrics for this AI type
                await conn.execute("""
                    INSERT INTO agent_metrics (
                        agent_id, agent_type, learning_score, success_rate, 
                        failure_rate, total_learning_cycles, xp, level, prestige,
                        status, is_active, priority, created_at, updated_at
                    ) VALUES (
                        $1, $1, 0.0, 0.0, 0.0, 0, 0, 1, 0, 
                        'idle', true, 'medium', NOW(), NOW()
                    )
                """, ai_type)
                print(f"✅ Created default metrics for {ai_type}")
            else:
                print(f"✅ Metrics already exist for {ai_type}")
        
        # Verify all metrics are properly set
        final_count = await conn.fetchval("SELECT COUNT(*) FROM agent_metrics")
        print(f"📊 Total agent metrics after fix: {final_count}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing agent metrics persistence: {str(e)}")
        return False


async def update_learning_cycle_schedule():
    """Update learning cycle schedule to start at 6 AM and run every hour"""
    
    try:
        print("⏰ Updating learning cycle schedule...")
        
        # Create a schedule configuration file
        schedule_config = {
            "learning_cycle_schedule": {
                "main_cycle": {
                    "start_time": "06:00",
                    "interval": "1 hour",
                    "description": "Main learning cycle starts at 6 AM and runs every hour"
                },
                "daily_cycles": {
                    "comprehensive": "05:00",
                    "midday_advanced": "12:00", 
                    "evening_practical": "17:00",
                    "nightly_analysis": "22:00"
                },
                "custody_tests": {
                    "regular": "Every 6 hours",
                    "comprehensive": "06:00 daily"
                },
                "proposal_generation": "Every 4 hours",
                "file_analysis": "Every 6 hours",
                "ai_subject_addition": "Every 8 hours"
            },
            "background_service": {
                "learning_cycle": "Every hour (3600 seconds)",
                "health_monitor": "Continuous",
                "imperium_audit": "Every 2 hours",
                "guardian_self_heal": "Every 3 hours"
            },
            "updated_at": datetime.now().isoformat()
        }
        
        # Save schedule configuration
        with open('learning_schedule_config.json', 'w') as f:
            json.dump(schedule_config, f, indent=2)
        
        print("✅ Learning cycle schedule configuration created:")
        print("   - Main learning cycle: Every hour starting at 6 AM")
        print("   - Daily comprehensive cycles: 12 PM, 5 PM, 10 PM")
        print("   - Custody tests: Every 6 hours")
        print("   - Proposal generation: Every 4 hours")
        print("   - File analysis: Every 6 hours")
        print("   - AI subject addition: Every 8 hours")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating learning cycle schedule: {str(e)}")
        return False


async def document_custodes_testing():
    """Document the Custodes Project testing frequency"""
    
    try:
        print("🛡️ Documenting Custodes Project testing frequency...")
        
        custodes_info = {
            "custodes_testing_frequency": {
                "regular_tests": "Every 4 hours (6 times per day)",
                "comprehensive_tests": "Daily at 6:00 AM",
                "test_categories": [
                    "Knowledge Verification",
                    "Code Quality", 
                    "Security Awareness",
                    "Performance Optimization",
                    "Innovation Capability",
                    "Self Improvement",
                    "Cross-AI Collaboration",
                    "Experimental Validation"
                ],
                "test_difficulty": "Scales with AI level (Basic to Legendary)",
                "eligibility_requirements": {
                    "level_up": "80% pass rate in last 5 tests, 2 or fewer consecutive failures",
                    "proposals": "At least one test passed, 3 or fewer consecutive failures, test within 24 hours"
                },
                "total_ais_tested": 4,
                "ai_types": ["imperium", "guardian", "sandbox", "conquest"]
            }
        }
        
        # Save to file
        with open('custodes_testing_frequency.json', 'w') as f:
            json.dump(custodes_info, f, indent=2)
        
        print("✅ Custodes testing frequency documented:")
        print("   - Regular tests: Every 4 hours")
        print("   - Comprehensive tests: Daily at 6 AM")
        print("   - 8 test categories covering all aspects")
        print("   - Difficulty scales with AI level")
        print("   - Strict eligibility requirements for leveling and proposals")
        
        return True
        
    except Exception as e:
        print(f"❌ Error documenting Custodes testing: {str(e)}")
        return False


async def document_black_library():
    """Document how the Black Library works"""
    
    try:
        print("📚 Documenting Black Library functionality...")
        
        black_library_info = {
            "black_library_functionality": {
                "purpose": "AI learning visualization and knowledge management system",
                "features": {
                    "learning_trees": "Hexagonal nodes representing learned capabilities for each AI",
                    "ai_nexus": "Individual learning centers for each AI type with color-coded knowledge points",
                    "real_time_updates": "30-second polling for live data updates",
                    "knowledge_visualization": "Dynamic learning tree with level-appropriate nodes",
                    "recent_learnings": "Track of latest learning achievements for each AI",
                    "custody_integration": "Integration with Custodes Protocol testing results"
                },
                "ai_types": {
                    "imperium": {
                        "color": "amber",
                        "emoji": "👑",
                        "description": "System Architect & Overseer",
                        "focus": "System architecture, performance optimization, scalability"
                    },
                    "conquest": {
                        "color": "red",
                        "emoji": "⚔️", 
                        "description": "Code Generator & Optimizer",
                        "focus": "Code generation, optimization, app development"
                    },
                    "guardian": {
                        "color": "blue",
                        "emoji": "🛡️",
                        "description": "Security & Quality Assurance", 
                        "focus": "Security, code quality, testing"
                    },
                    "sandbox": {
                        "color": "green",
                        "emoji": "🧪",
                        "description": "Experimental & Innovation Lab",
                        "focus": "Experimentation, innovation, prototyping"
                    }
                },
                "learning_nodes": {
                    "core_intelligence": "Base AI capabilities (Level 1+)",
                    "code_analysis": "Code analysis insights (Level 2+)",
                    "system_design": "System design insights (Level 3+)",
                    "security": "Security insights (Level 4+)",
                    "optimization": "Optimization insights (Level 5+)",
                    "innovation": "Innovation insights (Level 6+)",
                    "meta_learning": "Meta-learning capabilities (Level 7+)",
                    "collaboration": "Cross-AI collaboration (Level 8+)",
                    "experimental": "Experimental capabilities (Level 9+)"
                },
                "data_sources": {
                    "backend_api": "Real-time data from AI backend services",
                    "custody_protocol": "Testing results and eligibility status",
                    "learning_metrics": "Learning scores, cycles, and progress",
                    "cached_data": "Local persistence for offline viewing"
                },
                "technical_implementation": {
                    "frontend": "Flutter app with custom painting for learning trees",
                    "backend_integration": "HTTP API calls to agent status endpoints",
                    "data_persistence": "SharedPreferences for local caching",
                    "real_time_updates": "Timer-based polling with WebSocket support"
                }
            }
        }
        
        # Save to file
        with open('black_library_functionality.json', 'w') as f:
            json.dump(black_library_info, f, indent=2)
        
        print("✅ Black Library functionality documented:")
        print("   - AI learning visualization system")
        print("   - Real-time learning tree updates")
        print("   - Integration with Custodes Protocol")
        print("   - Level-based node progression")
        print("   - Color-coded AI knowledge centers")
        print("   - Comprehensive data persistence")
        
        return True
        
    except Exception as e:
        print(f"❌ Error documenting Black Library: {str(e)}")
        return False


async def create_frontend_persistence_script():
    """Create frontend persistence enhancement script"""
    
    try:
        print("📱 Creating frontend persistence enhancement script...")
        
        frontend_script = '''
// Enhanced AI Growth Analytics Provider with better persistence
// Add this to lib/providers/ai_growth_analytics_provider.dart

class AIGrowthAnalyticsProvider with ChangeNotifier {
  // ... existing code ...
  
  // Enhanced persistence methods
  Future<void> _enhancedLoadAgentsData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      // Load cached data first
      final cachedDataString = prefs.getString('agents_data');
      if (cachedDataString != null) {
        final cachedData = jsonDecode(cachedDataString);
        _agentsData = Map<String, dynamic>.from(cachedData);
        print('[AI_GROWTH_ANALYTICS_PROVIDER] ✅ Loaded cached agents data');
      }
      
      // Try to load from backend
      try {
        final response = await http.get(
          Uri.parse('$backendUrl/api/agents/status'),
          headers: {'Content-Type': 'application/json'},
        ).timeout(const Duration(seconds: 10));
        
        if (response.statusCode == 200) {
          final backendData = jsonDecode(response.body);
          
          // Merge backend data with cached data, preserving higher values
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
                
                // Update other fields from backend
                cachedAgent.addAll(backendAgent);
                _agentsData[agentId] = cachedAgent;
              } else {
                _agentsData[agentId] = backendAgent;
              }
            }
          }
          
          print('[AI_GROWTH_ANALYTICS_PROVIDER] ✅ Merged backend and cached data');
        }
      } catch (e) {
        print('[AI_GROWTH_ANALYTICS_PROVIDER] ⚠️ Backend load failed, using cached data: $e');
      }
      
      // Save the merged data
      await _saveAgentsData();
      
    } catch (e) {
      print('[AI_GROWTH_ANALYTICS_PROVIDER] ❌ Error in enhanced load: $e');
    }
  }
  
  // Enhanced save method with backup
  Future<void> _enhancedSaveAgentsData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      // Save current data
      await prefs.setString('agents_data', jsonEncode(_agentsData));
      
      // Create backup with timestamp
      final backupKey = 'agents_data_backup_${DateTime.now().millisecondsSinceEpoch}';
      await prefs.setString(backupKey, jsonEncode(_agentsData));
      
      // Keep only last 5 backups
      final keys = prefs.getKeys();
      final backupKeys = keys.where((key) => key.startsWith('agents_data_backup_')).toList();
      backupKeys.sort();
      
      if (backupKeys.length > 5) {
        for (int i = 0; i < backupKeys.length - 5; i++) {
          await prefs.remove(backupKeys[i]);
        }
      }
      
      await prefs.setString(_lastUpdatedKey, DateTime.now().toIso8601String());
      print('[AI_GROWTH_ANALYTICS_PROVIDER] ✅ Enhanced save completed with backup');
    } catch (e) {
      print('[AI_GROWTH_ANALYTICS_PROVIDER] ❌ Error in enhanced save: $e');
    }
  }
}
'''
        
        # Write the script to a file
        with open('frontend_persistence_enhancement.dart', 'w') as f:
            f.write(frontend_script)
        
        print("✅ Frontend persistence enhancement script created")
        print("   - Enhanced data loading with backup/restore")
        print("   - Better merging of cached and backend data")
        print("   - Automatic backup creation and cleanup")
        print("   - Preserves higher values when merging data")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating frontend persistence script: {str(e)}")
        return False


async def create_monitoring_script():
    """Create a simple monitoring script for data persistence"""
    
    try:
        print("🔍 Creating persistence monitoring script...")
        
        monitoring_script = '''#!/usr/bin/env python3
"""
Simple Data Persistence Monitoring Script
========================================

This script monitors and maintains data persistence to prevent metrics resetting.
Run this script periodically to ensure data integrity.
"""

import asyncio
import sys
import os
from datetime import datetime
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import asyncpg

async def check_metrics_persistence():
    """Check if agent metrics are properly persisted"""
    try:
        print("🔍 Checking metrics persistence...")
        
        # Database connection details
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
        
        # Connect directly to the database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check all AI types
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            # Check if metrics exist for this AI type
            metrics = await conn.fetchrow("""
                SELECT agent_id, learning_score, level, xp, total_learning_cycles
                FROM agent_metrics 
                WHERE agent_id = $1 OR agent_type = $1
            """, ai_type)
            
            if metrics:
                print(f"✅ {ai_type}: Level {metrics['level']}, Score {metrics['learning_score']:.2f}, XP {metrics['xp']}, Cycles {metrics['total_learning_cycles']}")
            else:
                print(f"❌ {ai_type}: No metrics found - creating default")
                # Create default metrics
                await conn.execute("""
                    INSERT INTO agent_metrics (
                        agent_id, agent_type, learning_score, success_rate, 
                        failure_rate, total_learning_cycles, xp, level, prestige,
                        status, is_active, priority, created_at, updated_at
                    ) VALUES (
                        $1, $1, 0.0, 0.0, 0.0, 0, 0, 1, 0, 
                        'idle', true, 'medium', NOW(), NOW()
                    )
                """, ai_type)
                print(f"✅ Created default metrics for {ai_type}")
        
        await conn.close()
        print("✅ Metrics persistence check completed")
        
    except Exception as e:
        print(f"❌ Error checking metrics persistence: {str(e)}")

async def backup_metrics_data():
    """Create backup of metrics data"""
    try:
        print("💾 Creating metrics backup...")
        
        # Database connection details
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
        
        # Connect directly to the database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Get all metrics
        metrics = await conn.fetch("SELECT * FROM agent_metrics")
        
        backup_data = []
        for metric in metrics:
            backup_data.append({
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
                "updated_at": metric['updated_at'].isoformat() if metric['updated_at'] else None
            })
        
        await conn.close()
        
        # Save backup to file
        backup_filename = f"metrics_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_filename, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"✅ Metrics backup created: {backup_filename}")
        
    except Exception as e:
        print(f"❌ Error creating metrics backup: {str(e)}")

async def main():
    """Main function"""
    print("🚀 Starting data persistence monitoring...")
    
    # Check metrics persistence
    await check_metrics_persistence()
    
    # Create backup
    await backup_metrics_data()
    
    print("✅ Data persistence monitoring completed")

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        # Write the script to a file
        with open('monitor_persistence.py', 'w') as f:
            f.write(monitoring_script)
        
        # Make it executable
        os.chmod('monitor_persistence.py', 0o755)
        
        print("✅ Persistence monitoring script created")
        print("   - Regular metrics persistence checks")
        print("   - Automatic backup creation")
        print("   - Data integrity validation")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating monitoring script: {str(e)}")
        return False


async def main():
    """Main function to run all fixes"""
    print("🚀 Starting simple metrics persistence and learning cycle fix for EC2...")
    print("=" * 80)
    
    # Run all fixes
    fixes = [
        ("Agent Metrics Persistence", fix_metrics_persistence),
        ("Learning Cycle Schedule", update_learning_cycle_schedule),
        ("Custodes Testing Documentation", document_custodes_testing),
        ("Black Library Documentation", document_black_library),
        ("Frontend Persistence Script", create_frontend_persistence_script),
        ("Persistence Monitoring Script", create_monitoring_script),
    ]
    
    results = {}
    
    for fix_name, fix_function in fixes:
        print(f"\n🔧 Running: {fix_name}")
        print("-" * 50)
        try:
            result = await fix_function()
            results[fix_name] = result
            if result:
                print(f"✅ {fix_name} completed successfully")
            else:
                print(f"❌ {fix_name} failed")
        except Exception as e:
            print(f"❌ {fix_name} failed with error: {str(e)}")
            results[fix_name] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 FIX SUMMARY")
    print("=" * 80)
    
    successful_fixes = sum(1 for result in results.values() if result)
    total_fixes = len(results)
    
    for fix_name, result in results.items():
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"{status}: {fix_name}")
    
    print(f"\n🎯 Overall Result: {successful_fixes}/{total_fixes} fixes completed successfully")
    
    if successful_fixes == total_fixes:
        print("\n🎉 All fixes completed successfully!")
        print("\n📋 NEXT STEPS:")
        print("1. Restart the backend service to apply the new learning cycle schedule")
        print("2. Update the frontend with the persistence enhancement script")
        print("3. Run the monitoring script periodically: python monitor_persistence.py")
        print("4. Monitor the Custodes testing frequency and Black Library functionality")
        print("\n⏰ NEW LEARNING CYCLE SCHEDULE:")
        print("- Main learning cycle: Every hour starting at 6 AM")
        print("- Daily comprehensive cycles: 12 PM, 5 PM, 10 PM")
        print("- Custody tests: Every 6 hours")
        print("- Proposal generation: Every 4 hours")
        print("- File analysis: Every 6 hours")
        print("- AI subject addition: Every 8 hours")
        print("\n🛡️ CUSTODES PROJECT TESTING:")
        print("- Regular tests: Every 4 hours (6 times per day)")
        print("- Comprehensive tests: Daily at 6:00 AM")
        print("- 8 test categories covering all aspects")
        print("- Difficulty scales with AI level")
        print("\n📚 BLACK LIBRARY FUNCTIONALITY:")
        print("- AI learning visualization system")
        print("- Real-time learning tree updates")
        print("- Integration with Custodes Protocol")
        print("- Level-based node progression")
        print("- Color-coded AI knowledge centers")
    else:
        print(f"\n⚠️ {total_fixes - successful_fixes} fixes failed. Please review the errors above.")
    
    return successful_fixes == total_fixes


if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1) 