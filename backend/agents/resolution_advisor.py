"""
Resolution Advisor Agent using Portia AI SDK
"""
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Type
from pydantic import BaseModel, Field

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.models import Classification, Runbook

# Import Portia Tool class
from portia import Tool, ToolRunContext


class ResolutionInput(BaseModel):
    """Input schema for resolution advisory"""
    classification: Dict[str, Any] = Field(description="Incident classification results")
    incident_context: Dict[str, Any] = Field(description="Additional incident context")


class ResolutionStep(BaseModel):
    """Individual resolution step"""
    step_number: int = Field(description="Step sequence number")
    description: str = Field(description="Step description")
    command: str = Field(description="Command to execute", default="")
    expected_result: str = Field(description="Expected outcome")
    automation_possible: bool = Field(description="Whether step can be automated")
    risk_level: str = Field(description="Risk level: low, medium, high")
    rollback_command: str = Field(description="Rollback command if needed", default="")


class ResolutionOutput(BaseModel):
    """Output schema for resolution advisory"""
    recommended_steps: List[ResolutionStep] = Field(description="Ordered resolution steps")
    estimated_time_minutes: int = Field(description="Estimated resolution time")
    success_probability: float = Field(description="Estimated success probability")
    human_approval_required: bool = Field(description="Whether human approval is needed")
    parallel_actions: List[str] = Field(description="Actions that can be done in parallel")
    rollback_plan: List[str] = Field(description="Complete rollback procedure")
    prerequisites: List[str] = Field(description="Required access/tools")
    reasoning: str = Field(description="Explanation of recommended approach")


class ResolutionAdvisorTool(Tool):
    """Tool for providing contextual resolution guidance"""
    
    id: str = "resolution_advisor"
    name: str = "Resolution Advisor"
    description: str = """
    Provides intelligent resolution guidance based on incident classification.
    Matches incidents to proven runbooks, generates step-by-step plans,
    estimates success probability, and provides rollback procedures.
    Considers automation possibilities and human approval requirements.
    """
    
    output_schema: tuple = ("dict", "dict: resolution guidance with steps, runbooks, and rollback plans")
    
    def __init__(self):
        super().__init__()
        # Initialize runbooks - storing as instance data
        self._runbooks = self._load_runbooks()
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'runbook_db', self._runbooks)
    
    def run(self, context: ToolRunContext = None) -> Dict[str, Any]:
        """
        Generate resolution plan based on classification and context
        """
        try:
            # Extract inputs from context
            classification_data = None
            incident_context = {}
            
            if context is not None:
                # Try various ways to extract classification data
                for key in ('classification_data', 'classification', 'input', 'inputs'):
                    value = getattr(context, key, None)
                    if value is None and hasattr(context, 'kwargs') and isinstance(context.kwargs, dict):
                        value = context.kwargs.get(key)
                    if value is not None:
                        classification_data = value
                        break
                
                # Try to get incident context
                incident_context = getattr(context, 'incident_context', {})
                if not incident_context and hasattr(context, 'kwargs') and isinstance(context.kwargs, dict):
                    incident_context = context.kwargs.get('incident_context', {})
            
            # Parse classification data
            if isinstance(classification_data, str):
                try:
                    classification = json.loads(classification_data)
                except json.JSONDecodeError:
                    classification = {"category": "unknown", "severity": "medium"}
            elif isinstance(classification_data, dict):
                classification = classification_data
            elif hasattr(classification_data, 'dict'):
                classification = classification_data.dict()
            else:
                classification = {"category": "unknown", "severity": "medium"}
            
            category = classification.get("category", "unknown")
            severity = classification.get("severity", "medium")
            confidence = classification.get("confidence", 0.5)
            
            # Create empty incident context for now
            incident_context = {}
            
            # Find matching runbooks
            matched_runbooks = self._find_matching_runbooks(category, severity)
            
            # Generate resolution steps
            resolution_steps = self._generate_resolution_steps(
                matched_runbooks, classification, incident_context
            )
            
            # Convert ResolutionStep objects to dictionaries
            resolution_steps_dict = [step.dict() for step in resolution_steps]
            
            # Calculate estimates
            estimated_time = self._estimate_resolution_time(resolution_steps, severity)
            success_probability = self._calculate_success_probability(
                matched_runbooks, confidence, severity
            )
            
            # Determine approval requirements
            human_approval = self._requires_human_approval(resolution_steps, severity)
            
            # Generate parallel actions
            parallel_actions = self._identify_parallel_actions(resolution_steps)
            
            # Create rollback plan
            rollback_plan = self._generate_rollback_plan(resolution_steps)
            
            # Gather prerequisites
            prerequisites = self._gather_prerequisites(matched_runbooks, category)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                category, severity, len(matched_runbooks), success_probability
            )
            
            return {
                "incident_id": classification.get("incident_id", "unknown"),
                "recommended_steps": resolution_steps_dict,
                "estimated_time_minutes": estimated_time,
                "success_probability": success_probability,
                "human_approval_required": human_approval,
                "parallel_actions": parallel_actions,
                "rollback_plan": rollback_plan,
                "prerequisites": prerequisites,
                "reasoning": reasoning,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            # Fallback resolution
            return self._generate_fallback_resolution(str(e))
    
    def _load_runbooks(self) -> List[Dict[str, Any]]:
        """Load runbook database (in production this would be from a database)"""
        return [
            {
                "category": "infrastructure",
                "severity_levels": ["critical", "high"],
                "title": "High CPU Usage Resolution",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Identify top CPU consuming processes",
                        "command": "top -o %CPU | head -10",
                        "expected_result": "List of processes sorted by CPU usage",
                        "automation_possible": True,
                        "risk_level": "low"
                    },
                    {
                        "step_number": 2,
                        "description": "Check system load and resource allocation",
                        "command": "uptime && free -h && df -h",
                        "expected_result": "System resource overview",
                        "automation_possible": True,
                        "risk_level": "low"
                    },
                    {
                        "step_number": 3,
                        "description": "Scale horizontally if using container orchestration",
                        "command": "kubectl scale deployment [service-name] --replicas=5",
                        "expected_result": "Additional instances created",
                        "automation_possible": True,
                        "risk_level": "medium",
                        "rollback_command": "kubectl scale deployment [service-name] --replicas=3"
                    },
                    {
                        "step_number": 4,
                        "description": "Monitor CPU usage stabilization",
                        "command": "Monitor for 5 minutes",
                        "expected_result": "CPU usage below 80%",
                        "automation_possible": False,
                        "risk_level": "low"
                    }
                ],
                "prerequisites": ["kubectl access", "monitoring access"],
                "estimated_time": 15,
                "success_rate": 0.85
            },
            {
                "category": "database",
                "severity_levels": ["critical", "high"],
                "title": "Database Connection Pool Exhaustion",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Check current connection count",
                        "command": "SELECT count(*) FROM pg_stat_activity;",
                        "expected_result": "Current active connections",
                        "automation_possible": True,
                        "risk_level": "low"
                    },
                    {
                        "step_number": 2,
                        "description": "Identify long-running queries",
                        "command": "SELECT query, state, query_start FROM pg_stat_activity WHERE state != 'idle' ORDER BY query_start;",
                        "expected_result": "List of active queries",
                        "automation_possible": True,
                        "risk_level": "low"
                    },
                    {
                        "step_number": 3,
                        "description": "Terminate problematic connections",
                        "command": "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE query_start < now() - interval '30 minutes';",
                        "expected_result": "Long-running connections terminated",
                        "automation_possible": False,
                        "risk_level": "high"
                    },
                    {
                        "step_number": 4,
                        "description": "Restart application connection pools",
                        "command": "kubectl rollout restart deployment [app-name]",
                        "expected_result": "Fresh connection pools",
                        "automation_possible": True,
                        "risk_level": "medium"
                    }
                ],
                "prerequisites": ["database admin access", "kubectl access"],
                "estimated_time": 10,
                "success_rate": 0.92
            },
            {
                "category": "application",
                "severity_levels": ["critical", "high"],
                "title": "Application Error Rate Resolution",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Check application logs for error patterns",
                        "command": "kubectl logs -l app=[service-name] --tail=100 | grep ERROR",
                        "expected_result": "Recent error log entries",
                        "automation_possible": True,
                        "risk_level": "low"
                    },
                    {
                        "step_number": 2,
                        "description": "Verify service health endpoints",
                        "command": "curl -f http://[service]/health",
                        "expected_result": "Health check returns 200 OK",
                        "automation_possible": True,
                        "risk_level": "low"
                    },
                    {
                        "step_number": 3,
                        "description": "Restart affected service pods",
                        "command": "kubectl rollout restart deployment [service-name]",
                        "expected_result": "Service pods restarted successfully",
                        "automation_possible": True,
                        "risk_level": "medium"
                    },
                    {
                        "step_number": 4,
                        "description": "Monitor error rate recovery",
                        "command": "Monitor error metrics for 10 minutes",
                        "expected_result": "Error rate returns to baseline",
                        "automation_possible": False,
                        "risk_level": "low"
                    }
                ],
                "prerequisites": ["kubectl access", "service logs access"],
                "estimated_time": 12,
                "success_rate": 0.78
            },
            {
                "category": "network",
                "severity_levels": ["high", "medium"],
                "title": "Network Latency Resolution",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Test network connectivity and latency",
                        "command": "ping -c 10 [target-host] && traceroute [target-host]",
                        "expected_result": "Network path analysis",
                        "automation_possible": True,
                        "risk_level": "low"
                    },
                    {
                        "step_number": 2,
                        "description": "Check load balancer health",
                        "command": "Check load balancer status and backend health",
                        "expected_result": "All backends healthy",
                        "automation_possible": False,
                        "risk_level": "low"
                    },
                    {
                        "step_number": 3,
                        "description": "Enable CDN or adjust routing",
                        "command": "Update CDN configuration or DNS routing",
                        "expected_result": "Traffic optimized through best path",
                        "automation_possible": False,
                        "risk_level": "medium"
                    }
                ],
                "prerequisites": ["network admin access", "CDN access"],
                "estimated_time": 8,
                "success_rate": 0.88
            }
        ]
    
    def _find_matching_runbooks(self, category: str, severity: str) -> List[Dict[str, Any]]:
        """Find runbooks that match the incident category and severity"""
        matched = []
        
        for runbook in self.runbook_db:
            if (runbook["category"] == category or 
                category == "infrastructure" and runbook["category"] in ["cpu", "memory", "disk"]):
                if severity in runbook["severity_levels"]:
                    matched.append(runbook)
        
        # If no exact match, find similar categories
        if not matched:
            for runbook in self.runbook_db:
                if severity in runbook["severity_levels"]:
                    matched.append(runbook)
        
        return matched[:2]  # Limit to top 2 matches
    
    def _generate_resolution_steps(self, runbooks: List[Dict], classification: Dict, context: Dict) -> List[ResolutionStep]:
        """Generate detailed resolution steps based on matched runbooks"""
        if not runbooks:
            return self._generate_generic_steps(classification)
        
        # Use the best matching runbook
        primary_runbook = runbooks[0]
        steps = []
        
        for step_data in primary_runbook["steps"]:
            step = ResolutionStep(
                step_number=step_data["step_number"],
                description=step_data["description"],
                command=step_data.get("command", ""),
                expected_result=step_data["expected_result"],
                automation_possible=step_data.get("automation_possible", False),
                risk_level=step_data.get("risk_level", "medium"),
                rollback_command=step_data.get("rollback_command", "")
            )
            steps.append(step)
        
        return steps
    
    def _generate_generic_steps(self, classification: Dict) -> List[ResolutionStep]:
        """Generate generic resolution steps when no specific runbook matches"""
        severity = classification.get("severity", "medium")
        category = classification.get("category", "unknown")
        
        steps = [
            ResolutionStep(
                step_number=1,
                description=f"Investigate {category} incident details",
                command="Review monitoring dashboards and logs",
                expected_result="Root cause identified",
                automation_possible=False,
                risk_level="low"
            ),
            ResolutionStep(
                step_number=2,
                description="Apply immediate mitigation if available",
                command="Execute appropriate mitigation steps",
                expected_result="Incident impact reduced",
                automation_possible=False,
                risk_level="medium"
            )
        ]
        
        if severity in ["critical", "high"]:
            steps.append(ResolutionStep(
                step_number=3,
                description="Escalate to on-call engineer",
                command="Page on-call engineer with incident details",
                expected_result="Expert engaged for resolution",
                automation_possible=True,
                risk_level="low"
            ))
        
        return steps
    
    def _estimate_resolution_time(self, steps: List[ResolutionStep], severity: str) -> int:
        """Estimate total resolution time in minutes"""
        base_time = len(steps) * 3  # 3 minutes per step base
        
        # Adjust based on severity
        if severity == "critical":
            base_time *= 1.5  # More urgency, potentially more resources
        elif severity == "low":
            base_time *= 0.8
        
        # Add time for manual steps
        manual_steps = sum(1 for step in steps if not step.automation_possible)
        base_time += manual_steps * 2
        
        return max(int(base_time), 5)  # Minimum 5 minutes
    
    def _calculate_success_probability(self, runbooks: List[Dict], confidence: float, severity: str) -> float:
        """Calculate probability of successful resolution"""
        if not runbooks:
            return 0.6  # Default probability for generic approach
        
        # Average success rate from matched runbooks
        avg_success_rate = sum(rb.get("success_rate", 0.7) for rb in runbooks) / len(runbooks)
        
        # Adjust based on classification confidence
        probability = avg_success_rate * (0.7 + 0.3 * confidence)
        
        # Adjust based on severity (critical incidents may be harder to resolve)
        if severity == "critical":
            probability *= 0.9
        elif severity == "low":
            probability *= 1.1
        
        return min(probability, 0.95)  # Cap at 95%
    
    def _requires_human_approval(self, steps: List[ResolutionStep], severity: str) -> bool:
        """Determine if human approval is required"""
        # Always require approval for critical incidents
        if severity == "critical":
            return True
        
        # Require approval for high-risk steps
        high_risk_steps = [step for step in steps if step.risk_level == "high"]
        if high_risk_steps:
            return True
        
        # Require approval for database operations
        db_operations = [step for step in steps if "database" in step.command.lower() or "pg_" in step.command]
        if db_operations:
            return True
        
        return False
    
    def _identify_parallel_actions(self, steps: List[ResolutionStep]) -> List[str]:
        """Identify actions that can be performed in parallel"""
        parallel_actions = []
        
        # Monitoring and investigation can often be done in parallel
        monitoring_steps = [step for step in steps if "monitor" in step.description.lower()]
        if len(monitoring_steps) > 1:
            parallel_actions.append("Multiple monitoring tasks can be executed simultaneously")
        
        # Log analysis and health checks can be parallel
        investigation_steps = [step for step in steps if any(keyword in step.description.lower() 
                                                           for keyword in ["check", "analyze", "review"])]
        if len(investigation_steps) > 1:
            parallel_actions.append("Investigation and analysis steps can run concurrently")
        
        return parallel_actions
    
    def _generate_rollback_plan(self, steps: List[ResolutionStep]) -> List[str]:
        """Generate complete rollback procedure"""
        rollback_plan = []
        
        # Collect rollback commands in reverse order
        for step in reversed(steps):
            if step.rollback_command:
                rollback_plan.append(f"Step {step.step_number} rollback: {step.rollback_command}")
        
        # Add general rollback guidance
        if not rollback_plan:
            rollback_plan = [
                "No specific rollback commands available",
                "Monitor system state and manually revert changes if needed",
                "Restore from backup if system state is compromised"
            ]
        else:
            rollback_plan.insert(0, "Execute rollback commands in the following order:")
        
        return rollback_plan
    
    def _gather_prerequisites(self, runbooks: List[Dict], category: str) -> List[str]:
        """Gather all prerequisites from matched runbooks"""
        prerequisites = set()
        
        for runbook in runbooks:
            prerequisites.update(runbook.get("prerequisites", []))
        
        # Add category-specific prerequisites
        if category == "database":
            prerequisites.add("database admin access")
        if category == "infrastructure":
            prerequisites.add("system admin access")
        if category == "application":
            prerequisites.add("kubectl access")
        
        return list(prerequisites)
    
    def _generate_reasoning(self, category: str, severity: str, runbook_count: int, success_prob: float) -> str:
        """Generate reasoning for the recommended approach"""
        reasoning_parts = []
        
        reasoning_parts.append(f"Resolution approach selected for {category} incident with {severity} severity.")
        
        if runbook_count > 0:
            reasoning_parts.append(f"Matched {runbook_count} proven runbook(s) for this incident type.")
        else:
            reasoning_parts.append("No specific runbooks matched - using generic resolution approach.")
        
        if success_prob > 0.8:
            reasoning_parts.append("High probability of successful resolution based on historical data.")
        elif success_prob < 0.6:
            reasoning_parts.append("Moderate success probability - consider escalation if initial steps fail.")
        
        if severity == "critical":
            reasoning_parts.append("Critical severity requires immediate action and human oversight.")
        
        return " ".join(reasoning_parts)
    
    def _generate_fallback_resolution(self, error: str) -> Dict[str, Any]:
        """Generate fallback resolution when main logic fails"""
        return {
            "incident_id": "unknown",
            "recommended_steps": [
                {
                    "step_number": 1,
                    "description": "Manual investigation required",
                    "command": "Review all available data sources",
                    "expected_result": "Understanding of incident scope",
                    "automation_possible": False,
                    "risk_level": "low"
                },
                {
                    "step_number": 2,
                    "description": "Escalate to senior engineer",
                    "command": "Contact on-call senior engineer",
                    "expected_result": "Expert assistance engaged",
                    "automation_possible": False,
                    "risk_level": "low"
                }
            ],
            "estimated_time_minutes": 60,
            "success_probability": 0.8,
            "human_approval_required": True,
            "parallel_actions": [],
            "rollback_plan": "No automated rollback available - manual intervention required",
            "prerequisites": ["Access to monitoring systems", "Contact information for senior engineer"],
            "reasoning": f"Fallback resolution due to error: {error}. Manual investigation and escalation required.",
            "generated_at": datetime.now().isoformat()
        }


# Create the tool instance
resolution_advisor_tool = ResolutionAdvisorTool()
