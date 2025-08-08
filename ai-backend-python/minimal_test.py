#!/usr/bin/env python3
"""
Minimal test to check router inclusion
"""

import uvicorn
from fastapi import FastAPI
from app.routers.test_enhanced_router import router as test_router

# Create minimal app
app = FastAPI(title="Minimal Test")

# Include router
app.include_router(test_router)

@app.get("/")
def root():
    return {"message": "Minimal test server"}

if __name__ == "__main__":
    print("Starting minimal test server...")
    print("Available routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  - {route.path}")
    
    uvicorn.run(app, host="0.0.0.0", port=8004, reload=False) 