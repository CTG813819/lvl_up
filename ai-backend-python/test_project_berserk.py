#!/usr/bin/env python3

print("Testing Project Berserk deployment...")

try:
    from app.models.project_berserk import ProjectBerserk
    print("✅ Project Berserk model imported successfully")
except Exception as e:
    print(f"❌ Error importing Project Berserk model: {e}")

try:
    from app.services.project_berserk_service import ProjectBerserkService
    print("✅ Project Berserk service imported successfully")
except Exception as e:
    print(f"❌ Error importing Project Berserk service: {e}")

try:
    from app.routers.project_berserk import router
    print("✅ Project Berserk router imported successfully")
except Exception as e:
    print(f"❌ Error importing Project Berserk router: {e}")

print("🎉 Project Berserk deployment test completed!")