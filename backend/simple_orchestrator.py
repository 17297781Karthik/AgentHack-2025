"""
Simplified Crisis Commander for testing without complex Portia setup
"""
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import the agent tools
from agents.incident_classifier import IncidentClassifierTool
from agents.resolution_advisor import ResolutionAdvisorTool
from agents.postmortem_generator import PostMortemGeneratorTool
from models.models import Incident, Alert, Classification, IncidentStatus, WebSocketMessage
from data.mock_generator import MockDataGenerator


class SimpleCrisisCommander:
    """
    Simplified version for testing without complex Portia orchestration
    """
    
    def __init__(self):
        # Create tool instances
        self.incident_classifier = IncidentClassifierTool()
        self.resolution_advisor = ResolutionAdvisorTool()
        self.postmortem_generator = PostMortemGeneratorTool()
        
        # In-memory storage for demo
        self.active_incidents: Dict[str, Incident] = {}
        self.completed_incidents: Dict[str, Incident] = {}
        self.websocket_callbacks: List[callable] = []
        
        # Load mock data
        self.runbooks = MockDataGenerator.generate_runbooks()
    
    def register_websocket_callback(self, callback):
        """Register a callback for WebSocket notifications"""
        self.websocket_callbacks.append(callback)
    
    def get_active_incidents(self) -> List[Incident]:
        """Get list of active incidents"""
        return list(self.active_incidents.values())
    
    def get_completed_incidents(self) -> List[Incident]:
        """Get list of completed incidents"""
        return list(self.completed_incidents.values())
    
    async def broadcast_update(self, message: Dict[str, Any]):
        """Broadcast update to all registered WebSocket callbacks"""
        for callback in self.websocket_callbacks:
            try:
                await callback(message)
            except Exception as e:
                print(f"Error broadcasting to WebSocket: {e}")
    
    async def process_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an alert through the crisis response pipeline
        """
        try:
            # Generate incident ID
            incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Step 1: Classify the incident
            print(f"Classifying incident {incident_id}...")
            classification = self.incident_classifier.run(alert_data)
            
            # Step 2: Get resolution recommendations
            print(f"Getting resolution recommendations...")
            incident_context = {
                "incident_id": incident_id,
                "duration_minutes": 0,
                "user_impact": "unknown"
            }
            resolution = self.resolution_advisor.run(classification, incident_context)
            
            # Create incident record
            incident = {
                "incident_id": incident_id,
                "alert": alert_data,
                "classification": classification,
                "resolution": resolution,
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "timeline": [
                    {
                        "timestamp": datetime.now().isoformat(),
                        "event": "Alert received and classified",
                        "details": classification
                    },
                    {
                        "timestamp": datetime.now().isoformat(),
                        "event": "Resolution plan generated",
                        "details": f"{len(resolution['recommended_steps'])} steps identified"
                    }
                ]
            }
            
            # Store incident
            self.active_incidents[incident_id] = incident
            
            print(f"✓ Incident {incident_id} processed successfully")
            return incident
            
        except Exception as e:
            print(f"Error processing alert: {e}")
            raise
    
    async def resolve_incident(self, incident_id: str) -> Dict[str, Any]:
        """
        Mark incident as resolved and generate postmortem
        """
        try:
            if incident_id not in self.active_incidents:
                raise ValueError(f"Incident {incident_id} not found")
            
            incident = self.active_incidents[incident_id]
            
            # Generate postmortem
            print(f"Generating postmortem for {incident_id}...")
            incident_data = {
                "incident_id": incident_id,
                "alert": incident["alert"],
                "classification": incident["classification"],
                "timeline": incident["timeline"]
            }
            resolution_data = {
                "status": "resolved",
                "resolution": incident["resolution"]
            }
            
            postmortem = self.postmortem_generator.run(incident_data, resolution_data)
            
            # Update incident
            incident["status"] = "resolved"
            incident["postmortem"] = postmortem
            incident["resolved_at"] = datetime.now().isoformat()
            incident["timeline"].append({
                "timestamp": datetime.now().isoformat(),
                "event": "Incident resolved",
                "details": "Postmortem generated"
            })
            
            # Move to completed
            self.completed_incidents[incident_id] = incident
            del self.active_incidents[incident_id]
            
            print(f"✓ Incident {incident_id} resolved and postmortem generated")
            return incident
            
        except Exception as e:
            print(f"Error resolving incident: {e}")
            raise
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data for the dashboard
        """
        return {
            "active_incidents": len(self.active_incidents),
            "resolved_incidents": len(self.completed_incidents),
            "total_incidents": len(self.active_incidents) + len(self.completed_incidents),
            "recent_incidents": list(self.active_incidents.values())[:10]
        }
    
    def get_available_scenarios(self) -> List[str]:
        """Get available simulation scenarios"""
        return MockDataGenerator.get_scenario_names()
    
    async def simulate_incident(self, scenario_name: str = None) -> Incident:
        """Simulate an incident for demo purposes"""
        alert = MockDataGenerator.generate_alert(scenario_name)
        return await self.process_alert(alert)
    
    async def process_alert(self, alert: Alert) -> Incident:
        """Process an alert and create an incident with full workflow"""
        try:
            # Create incident
            incident = Incident(
                incident_id=str(uuid.uuid4()),
                alert_id=alert.alert_id,
                status=IncidentStatus.DETECTED,
                created_at=datetime.now(),
                timeline=[]
            )
            
            # Store in active incidents
            self.active_incidents[incident.incident_id] = incident
            
            # Broadcast incident creation
            await self.broadcast_update({
                "type": "incident_created",
                "data": {
                    "incident_id": incident.incident_id,
                    "alert": alert.model_dump() if hasattr(alert, 'model_dump') else alert.__dict__,
                    "status": incident.status
                },
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 1: Classify the incident
            await self._update_incident_status(incident, IncidentStatus.ANALYZING)
            classification_result = self.incident_classifier.run(alert.__dict__ if hasattr(alert, '__dict__') else alert)
            
            # Update incident with classification
            incident.classification = Classification(**classification_result)
            incident.timeline.append({
                "timestamp": datetime.now(),
                "agent": "IncidentClassifier",
                "action": "classify_incident", 
                "result": classification_result,
                "duration_ms": 2000
            })
            
            # Step 2: Get resolution advisory
            await self._update_incident_status(incident, IncidentStatus.RESOLVING)
            resolution_result = self.resolution_advisor.run(
                classification=classification_result,
                incident_context=alert.__dict__ if hasattr(alert, '__dict__') else alert
            )
            
            # Add resolution to timeline
            incident.timeline.append({
                "timestamp": datetime.now(),
                "agent": "ResolutionAdvisor",
                "action": "suggest_resolution",
                "result": resolution_result,
                "duration_ms": 3500
            })
            
            # Step 3: Auto-resolve for demo
            await self._simulate_resolution(incident, resolution_result)
            
            return incident
            
        except Exception as e:
            print(f"Error processing alert: {e}")
            raise
    
    async def _update_incident_status(self, incident: Incident, status: IncidentStatus):
        """Update incident status and broadcast"""
        incident.status = status
        
        await self.broadcast_update({
            "type": "incident_updated",
            "data": {
                "incident_id": incident.incident_id,
                "status": status,
                "timestamp": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat()
        })
    
    async def _simulate_resolution(self, incident: Incident, resolution_result: Dict[str, Any]):
        """Simulate incident resolution for demo"""
        try:
            # Simulate some resolution time
            import asyncio
            await asyncio.sleep(2)
            
            # Mark as resolved
            await self._update_incident_status(incident, IncidentStatus.RESOLVED)
            
            # Generate postmortem
            postmortem_result = self.postmortem_generator.run(
                incident_data=incident.__dict__ if hasattr(incident, '__dict__') else incident,
                resolution_data=resolution_result
            )
            
            # Add postmortem to timeline
            incident.timeline.append({
                "timestamp": datetime.now(),
                "agent": "PostMortemGenerator", 
                "action": "generate_postmortem",
                "result": postmortem_result,
                "duration_ms": 1500
            })
            
            # Move to completed
            self.completed_incidents[incident.incident_id] = incident
            del self.active_incidents[incident.incident_id]
            
            # Broadcast completion
            await self.broadcast_update({
                "type": "incident_resolved",
                "data": {
                    "incident_id": incident.incident_id,
                    "postmortem": postmortem_result
                },
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"✓ Incident {incident.incident_id} resolved with full workflow")
            
        except Exception as e:
            print(f"Error resolving incident: {e}")
            raise
    
    def get_incident_by_id(self, incident_id: str) -> Optional[Incident]:
        """Get specific incident by ID"""
        return (self.active_incidents.get(incident_id) or 
                self.completed_incidents.get(incident_id))

# Create global instance
crisis_commander = SimpleCrisisCommander()
