#!/usr/bin/env python3
"""
Simple test server to isolate the enhanced router issue
"""

import uvicorn
from fastapi import FastAPI
from app.routers.project_horus_enhanced import router as project_horus_enhanced_router

# Create a minimal FastAPI app
app = FastAPI(title="Test Server")

# Include only the enhanced router
app.include_router(project_horus_enhanced_router)

@app.get("/")
def root():
    return {"message": "Test server running"}

@app.get("/test")
def test():
    return {"message": "Test endpoint working"}

if __name__ == "__main__":
    print("Starting test server...")
    print("Available routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  - {route.path}")
    
    print("\nStarting server on port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=False, log_level="info") 