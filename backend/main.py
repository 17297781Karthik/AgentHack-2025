"""
FastAPI Backend for DevOps Crisis Commander
"""
import json
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from models.models import Alert, Incident, WebSocketMessage
from simple_orchestrator import crisis_commander
from data.mock_generator import MockDataGenerator


app = FastAPI(
    title="DevOps Crisis Commander API",
    description="Multi-agent system for intelligent DevOps incident response",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vue.js dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Register with crisis commander for updates
        crisis_commander.register_websocket_callback(self.broadcast_to_websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message, default=str))

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message, default=str))
            except Exception:
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_to_websocket(self, message: WebSocketMessage):
        """Callback for crisis commander updates"""
        await self.broadcast(message.dict())

manager = ConnectionManager()


# Request/Response models
class SimulationRequest(BaseModel):
    scenario_name: str = None


class AlertRequest(BaseModel):
    alert: Alert


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle any client messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Echo back for testing
            await manager.send_personal_message({
                "type": "echo",
                "data": message,
                "timestamp": datetime.now().isoformat()
            }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# API Routes
@app.get("/")
async def root():
    return {
        "message": "DevOps Crisis Commander API",
        "version": "1.0.0",
        "status": "operational",
        "agents": ["IncidentClassifier", "ResolutionAdvisor", "PostMortemGenerator"]
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_incidents": len(crisis_commander.get_active_incidents()),
        "completed_incidents": len(crisis_commander.get_completed_incidents())
    }


@app.post("/incidents/simulate")
async def simulate_incident(request: SimulationRequest):
    """Simulate an incident for demo purposes"""
    try:
        incident = await crisis_commander.simulate_incident(request.scenario_name)
        return {
            "success": True,
            "incident_id": incident.incident_id,
            "status": incident.status,
            "message": f"Incident simulation started: {incident.incident_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/incidents/process")
async def process_alert(request: AlertRequest):
    """Process a real alert through the incident response workflow"""
    try:
        incident = await crisis_commander.process_alert(request.alert)
        return {
            "success": True,
            "incident_id": incident.incident_id,
            "status": incident.status,
            "classification": incident.classification.dict() if incident.classification else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/incidents/active")
async def get_active_incidents():
    """Get all active incidents"""
    incidents = crisis_commander.get_active_incidents()
    return [incident.dict() for incident in incidents]


@app.get("/incidents/completed")
async def get_completed_incidents():
    """Get all completed incidents"""
    incidents = crisis_commander.get_completed_incidents()
    return [incident.dict() for incident in incidents]


@app.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get specific incident by ID"""
    incident = crisis_commander.get_incident_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return incident.dict()


@app.get("/incidents/{incident_id}/timeline")
async def get_incident_timeline(incident_id: str):
    """Get incident timeline"""
    incident = crisis_commander.get_incident_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return {
        "incident_id": incident_id,
        "timeline": incident.timeline,
        "status": incident.status
    }


@app.get("/scenarios")
async def get_available_scenarios():
    """Get available simulation scenarios"""
    scenarios = crisis_commander.get_available_scenarios()
    scenario_details = {}
    
    for scenario_name in scenarios:
        # Get scenario details from mock generator
        scenario_data = MockDataGenerator.MOCK_SCENARIOS.get(scenario_name, {})
        scenario_details[scenario_name] = {
            "name": scenario_name.replace('_', ' ').title(),
            "description": scenario_data.get("message", ""),
            "severity": scenario_data.get("severity", "medium"),
            "type": scenario_data.get("alert_type", "unknown"),
            "affected_services": scenario_data.get("affected_services", [])
        }
    
    return scenario_details


@app.get("/scenarios/{scenario_name}")
async def get_scenario_details(scenario_name: str):
    """Get details for a specific scenario"""
    if scenario_name not in MockDataGenerator.MOCK_SCENARIOS:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    scenario_data = MockDataGenerator.MOCK_SCENARIOS[scenario_name]
    return {
        "name": scenario_name,
        "details": scenario_data
    }


@app.get("/runbooks")
async def get_runbooks():
    """Get available runbooks"""
    runbooks = MockDataGenerator.generate_runbooks()
    return [runbook.dict() for runbook in runbooks]


@app.get("/metrics/dashboard")
async def get_dashboard_metrics():
    """Get metrics for dashboard display"""
    active_incidents = crisis_commander.get_active_incidents()
    completed_incidents = crisis_commander.get_completed_incidents()
    
    # Calculate basic metrics
    total_incidents = len(active_incidents) + len(completed_incidents)
    
    # Severity breakdown
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    for incident in active_incidents + completed_incidents:
        if incident.classification:
            severity = incident.classification.severity
            if severity in severity_counts:
                severity_counts[severity] += 1
    
    # Resolution time (mock data for demo)
    avg_resolution_time = 15.5  # minutes
    
    return {
        "total_incidents": total_incidents,
        "active_incidents": len(active_incidents),
        "completed_incidents": len(completed_incidents),
        "severity_breakdown": severity_counts,
        "avg_resolution_time_minutes": avg_resolution_time,
        "automation_rate": 0.78,  # 78% automated
        "agent_status": {
            "incident_classifier": "ready",
            "resolution_advisor": "ready", 
            "postmortem_generator": "ready"
        }
    }


@app.post("/admin/reset")
async def reset_system():
    """Reset the system (clear all incidents) - for demo purposes"""
    crisis_commander.active_incidents.clear()
    crisis_commander.completed_incidents.clear()
    
    await manager.broadcast({
        "type": "system_reset",
        "data": {"message": "System reset completed"},
        "timestamp": datetime.now().isoformat()
    })
    
    return {"success": True, "message": "System reset completed"}


@app.get("/demo/status")
async def demo_status():
    """Get demo system status"""
    return {
        "system": "DevOps Crisis Commander",
        "mode": "demo",
        "portia_ai": "integrated",
        "agents_available": 3,
        "scenarios_available": len(MockDataGenerator.get_scenario_names()),
        "websocket_connections": len(manager.active_connections),
        "uptime": "demo mode"
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    print("🚀 DevOps Crisis Commander API starting up...")
    print("📡 WebSocket endpoint available at: /ws")
    print("📊 Dashboard metrics available at: /metrics/dashboard")
    print("🎭 Demo scenarios available at: /scenarios")
    print("✅ System ready for incident simulation!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
