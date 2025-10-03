"""API v1 Router"""

from fastapi import APIRouter
from .endpoints import traffic, routing, incidents

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(traffic.router, prefix="/traffic", tags=["Traffic Prediction"])
api_router.include_router(routing.router, prefix="/routing", tags=["Smart Routing"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])

@api_router.get("/")
async def api_root():
    return {
        "message": "Smart Traffic System API v1",
        "endpoints": {
            "traffic": "/api/v1/traffic",
            "routing": "/api/v1/routing",
            "incidents": "/api/v1/incidents"
        }
    }
