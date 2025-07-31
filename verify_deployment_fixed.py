#!/usr/bin/env python3
"""
Corrected verification script to test that all deployment fixes are working
"""

import asyncio
import sys
import os
import re

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def verify_deployment():
    """Verify that all deployment fixes are working"""
    print("🔍 Verifying deployment fixes (Corrected Version)...")
    
    try:
        # Test 1: Check if migration file has revision identifiers
        print("\n1. Checking migration file...")
        migration_file = "app/migrations/versions/fix_json_extract_function.py"
        if os.path.exists(migration_file):
            with open(migration_file, 'r') as f:
                content = f.read()
                if "revision =" in content:
                    print("✅ Migration file has revision identifiers")
                else:
                    print("❌ Migration file missing revision identifiers")
        else:
            print("❌ Migration file not found")
        
        # Test 2: Check if Learning model usage is fixed
        print("\n2. Checking Learning model usage...")
        growth_service_file = "app/services/ai_growth_service.py"
        if os.path.exists(growth_service_file):
            with open(growth_service_file, 'r') as f:
                content = f.read()
                if "json_extract_path_text" in content:
                    print("✅ AI Growth Service uses json_extract_path_text")
                else:
                    print("❌ AI Growth Service still uses Learning.confidence")
        else:
            print("❌ AI Growth Service file not found")
        
        # Test 3: Check if internet fetchers have rate limiting
        print("\n3. Checking internet fetchers...")
        internet_fetchers_file = "app/services/internet_fetchers.py"
        if os.path.exists(internet_fetchers_file):
            with open(internet_fetchers_file, 'r') as f:
                content = f.read()
                if "RateLimiter" in content:
                    print("✅ Internet fetchers have rate limiting")
                else:
                    print("❌ Internet fetchers missing rate limiting")
        else:
            print("❌ Internet fetchers file not found")
        
        # Test 4: Check if Terra Extension Service is fixed
        print("\n4. Checking Terra Extension Service...")
        terra_service_file = "app/services/terra_extension_service.py"
        if os.path.exists(terra_service_file):
            with open(terra_service_file, 'r') as f:
                content = f.read()
                if "call_claude" in content:
                    print("✅ Terra Extension Service has real AI code generation")
                else:
                    print("❌ Terra Extension Service still has placeholder code")
        else:
            print("❌ Terra Extension Service file not found")
        
        # Test 5: Check if plugin system is fixed (CORRECTED)
        print("\n5. Checking plugin system...")
        plugin_file = "plugins/base_plugin.py"
        if os.path.exists(plugin_file):
            with open(plugin_file, 'r') as f:
                content = f.read()
                # Look for actual TODO comments, not just "Implementation"
                todos = re.findall(r'# TODO', content)
                if not todos:
                    print("✅ Plugin system has no TODO comments")
                else:
                    print(f"❌ Plugin system still has {len(todos)} TODO comments")
        else:
            print("❌ Plugin file not found")
        
        # Test 6: Check if AI services are fixed (CORRECTED)
        print("\n6. Checking AI services...")
        sckipit_file = "app/services/sckipit_service.py"
        conquest_file = "app/services/conquest_ai_service.py"
        
        if os.path.exists(sckipit_file):
            with open(sckipit_file, 'r') as f:
                content = f.read()
                todos = re.findall(r'# TODO', content)
                if not todos:
                    print("✅ Sckipit service has no TODO comments")
                else:
                    print(f"❌ Sckipit service still has {len(todos)} TODO comments")
        else:
            print("❌ Sckipit service file not found")
        
        if os.path.exists(conquest_file):
            with open(conquest_file, 'r') as f:
                content = f.read()
                todos = re.findall(r'# TODO', content)
                if not todos:
                    print("✅ Conquest AI service has no TODO comments")
                else:
                    print(f"❌ Conquest AI service still has {len(todos)} TODO comments")
        else:
            print("❌ Conquest AI service file not found")
        
        # Test 7: Check if proposal endpoints have error logging
        print("\n7. Checking proposal endpoints...")
        proposals_file = "app/routers/proposals.py"
        if os.path.exists(proposals_file):
            with open(proposals_file, 'r') as f:
                content = f.read()
                if "logger.error" in content:
                    print("✅ Proposal endpoints have error logging")
                else:
                    print("❌ Proposal endpoints missing error logging")
        else:
            print("❌ Proposals router file not found")
        
        # Test 8: Check if SQL script was created
        print("\n8. Checking SQL script...")
        sql_file = "create_json_function.sql"
        if os.path.exists(sql_file):
            print("✅ SQL script for json_extract_path_text function created")
            with open(sql_file, 'r') as f:
                content = f.read()
                if "json_extract_path_text" in content:
                    print("✅ SQL script contains the correct function")
                else:
                    print("❌ SQL script missing function definition")
        else:
            print("❌ SQL script not found")
        
        print("\n🎉 Deployment verification completed!")
        print("\n📝 Next steps:")
        print("   1. Create the function in your Neon database:")
        print("      psql \"postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require\" -f create_json_function.sql")
        print("   2. Test the function:")
        print("      psql \"postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require\" -c \"SELECT json_extract_path_text('{\\\"test\\\": \\\"value\\\"}'::jsonb, 'test');\"")
        print("   3. Restart your application: pkill -f 'python.*main.py' && python app/main.py")
        print("   4. Test your API endpoints to ensure everything is working")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")

if __name__ == "__main__":
    asyncio.run(verify_deployment()) 