"""FastAPI server with WebSocket support for real-time alerts."""

import os
import asyncio
from typing import Set
import google.auth
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from google.adk.cli.fast_api import get_fast_api_app

from app.pipeline import ThreatDetectionPipeline

_, project_id = google.auth.default()

# Initialize FastAPI with ADK
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
session_service_uri = None

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    allow_origins=["*"],
    session_service_uri=session_service_uri,
)

app.title = "Home Threat Detection"
app.description = "Real-time home threat detection system using ADK"

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# Demo video paths (replace with actual paths)
VIDEO_PATHS = {
    1: "videos/camera1.mp4",
    2: "videos/camera2.mp4",
    3: "videos/camera3.mp4",
    4: "videos/camera4.mp4",
    5: "videos/camera5.mp4"
}

# Background task for continuous monitoring
monitoring_task = None

async def monitor_threats():
    """Background task to continuously monitor threats."""
    scenarios = ["normal", "intrusion", "fall", "fire"]
    current_scenario = 0
    
    while True:
        scenario = scenarios[current_scenario % len(scenarios)]
        pipeline = ThreatDetectionPipeline(VIDEO_PATHS, scenario)
        
        try:
            result = await pipeline.process_cycle()
            
            # Broadcast to all connected clients
            await manager.broadcast({
                "type": "threat_decision",
                "data": result
            })
            
        except Exception as e:
            print(f"Error in monitoring: {e}")
        
        # Rotate scenario every 4 cycles
        current_scenario += 1
        
        await asyncio.sleep(5)


@app.on_event("startup")
async def startup_event():
    """Start background monitoring on startup."""
    global monitoring_task
    monitoring_task = asyncio.create_task(monitor_threats())


@app.on_event("shutdown")
async def shutdown_event():
    """Cancel background monitoring on shutdown."""
    if monitoring_task:
        monitoring_task.cancel()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time threat updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "active_connections": len(manager.active_connections)
    }


@app.post("/simulate-scenario")
async def simulate_scenario(scenario: str):
    """Trigger a specific threat scenario."""
    if scenario not in ["normal", "intrusion", "fall", "fire"]:
        return {"error": "Invalid scenario"}
    
    pipeline = ThreatDetectionPipeline(VIDEO_PATHS, scenario)
    result = await pipeline.process_cycle()
    
    # Broadcast result
    await manager.broadcast({
        "type": "threat_decision",
        "data": result
    })
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)