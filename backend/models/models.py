"""
Data models for DevOps Crisis Commander
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from uuid import uuid4


class AlertType(str, Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    APPLICATION = "application"
    DATABASE = "database"


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentStatus(str, Enum):
    DETECTED = "detected"
    ANALYZING = "analyzing"
    RESOLVING = "resolving"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AlertMetrics(BaseModel):
    cpu_usage: Optional[float] = Field(None, ge=0, le=100)
    memory_usage: Optional[float] = Field(None, ge=0, le=100)
    disk_usage: Optional[float] = Field(None, ge=0, le=100)
    response_time: Optional[float] = Field(None, ge=0)
    error_rate: Optional[float] = Field(None, ge=0, le=1)


class Alert(BaseModel):
    alert_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    source_system: str
    alert_type: AlertType
    severity: SeverityLevel
    message: str
    metrics: AlertMetrics
    affected_services: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Classification(BaseModel):
    category: str
    severity: SeverityLevel
    confidence: float = Field(ge=0, le=1)
    tags: List[str] = Field(default_factory=list)


class TimelineEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    agent: str
    action: str
    result: Dict[str, Any]
    duration_ms: int


class Resolution(BaseModel):
    steps_taken: List[str] = Field(default_factory=list)
    success: bool
    resolution_time_ms: int
    manual_intervention: bool = False


class Incident(BaseModel):
    incident_id: str = Field(default_factory=lambda: str(uuid4()))
    alert_id: str
    classification: Optional[Classification] = None
    timeline: List[TimelineEntry] = Field(default_factory=list)
    status: IncidentStatus = IncidentStatus.DETECTED
    resolution: Optional[Resolution] = None
    created_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


class RunbookStep(BaseModel):
    step_number: int
    description: str
    command: Optional[str] = None
    expected_result: str
    rollback_command: Optional[str] = None
    automation_possible: bool = True


class Runbook(BaseModel):
    runbook_id: str = Field(default_factory=lambda: str(uuid4()))
    category: str
    severity_level: str
    title: str
    description: str
    steps: List[RunbookStep]
    prerequisites: List[str] = Field(default_factory=list)
    estimated_time_minutes: int
    success_rate: float = Field(ge=0, le=1)
    last_updated: datetime = Field(default_factory=datetime.now)


class PostMortemSummary(BaseModel):
    title: str
    duration: str
    impact: str
    root_cause: str


class PostMortemTimeline(BaseModel):
    time: datetime
    event: str
    details: str


class ResolutionAnalysis(BaseModel):
    effective_actions: List[str]
    ineffective_actions: List[str]
    manual_interventions: int
    total_resolution_time: int


class ActionItem(BaseModel):
    description: str
    owner: str
    due_date: datetime
    priority: SeverityLevel


class PostMortem(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid4()))
    incident_id: str
    summary: PostMortemSummary
    timeline: List[PostMortemTimeline]
    resolution_analysis: ResolutionAnalysis
    lessons_learned: List[str]
    action_items: List[ActionItem]
    generated_at: datetime = Field(default_factory=datetime.now)
    export_formats: List[str] = Field(default=["markdown", "pdf"])


# WebSocket message models
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentStatus(BaseModel):
    agent_name: str
    status: str
    current_task: Optional[str] = None
    progress: float = Field(ge=0, le=1)
    last_update: datetime = Field(default_factory=datetime.now)
