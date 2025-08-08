from app.routers import proposals, growth, monitoring, issues

app.include_router(proposals.router, prefix="/api/proposals", tags=["Proposals"])
app.include_router(growth.router, prefix="/api/growth", tags=["Growth"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Monitoring"])
app.include_router(issues.router, prefix="/api/issues", tags=["Issues"]) 