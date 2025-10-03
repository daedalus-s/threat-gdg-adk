"""Simple API for threat detection analysis."""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import asyncio

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("GOOGLE_API_KEY not found!")

from app.single_analysis import analyze_current_state

app = FastAPI(title="Home Threat Detection API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisRequest(BaseModel):
    """Request for threat analysis."""
    video_files: Dict[int, str]
    sensor_data: Optional[dict] = None


@app.get("/")
async def root():
    """Health check."""
    return {"status": "online", "service": "Home Threat Detection"}


@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    """
    Analyze current threat state.
    
    Returns comprehensive threat analysis.
    """
    try:
        result = await analyze_current_state(
            video_files=request.video_files,
            sensor_data=request.sensor_data
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """Get system status."""
    return {
        "cameras": {
            "total": 5,
            "online": 1,  # This would be dynamic in production
        },
        "sensors": {
            "accelerometer": "online",
            "heart_rate": "online",
            "audio": "online",
            "smoke_detector": "online"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)