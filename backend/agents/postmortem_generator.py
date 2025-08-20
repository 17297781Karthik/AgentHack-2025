"""
Post-Mortem Generator Agent using Portia AI SDK
"""
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Type
from pydantic import BaseModel, Field

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Portia Tool class
from portia import Tool, ToolRunContext


class PostMortemInput(BaseModel):
    """Input schema for post-mortem generation"""
    incident_data: Dict[str, Any] = Field(description="Complete incident data and timeline")
    resolution_data: Dict[str, Any] = Field(description="Resolution steps and outcomes")


class PostMortemTimelineEntry(BaseModel):
    """Timeline entry for post-mortem"""
    time: str = Field(description="Timestamp of event")
    event: str = Field(description="Event description")
    details: str = Field(description="Detailed information")
    agent_action: bool = Field(description="Whether this was an automated agent action")


class ActionItem(BaseModel):
    """Action item from post-mortem analysis"""
    description: str = Field(description="Action item description")
    owner: str = Field(description="Responsible party")
    priority: str = Field(description="Priority level")
    due_date: str = Field(description="Target completion date")
    category: str = Field(description="Category of action item")


class PostMortemOutput(BaseModel):
    """Output schema for post-mortem generation"""
    summary: Dict[str, str] = Field(description="Executive summary of incident")
    timeline: List[PostMortemTimelineEntry] = Field(description="Chronological timeline")
    root_cause_analysis: str = Field(description="Root cause analysis")
    resolution_effectiveness: Dict[str, Any] = Field(description="Analysis of resolution steps")
    lessons_learned: List[str] = Field(description="Key lessons from incident")
    action_items: List[ActionItem] = Field(description="Follow-up action items")
    metrics: Dict[str, Any] = Field(description="Incident metrics and KPIs")
    recommendations: List[str] = Field(description="Process improvement recommendations")
    markdown_report: str = Field(description="Complete markdown formatted report")


class PostMortemGeneratorTool(Tool):
    """Tool for generating comprehensive post-incident reports"""
    
    id: str = "postmortem_generator"
    name: str = "PostMortem Generator"
    description: str = """
    Generates comprehensive post-incident reports including timeline reconstruction,
    root cause analysis, lessons learned, and action items. Analyzes the effectiveness
    of agent responses and provides recommendations for improvement.
    """
    
    output_schema: tuple = ("dict", "dict: postmortem report with timeline, root cause, lessons learned, and action items")
    
    def run(self, context: ToolRunContext = None) -> Dict[str, Any]:
        """
        Generate comprehensive post-mortem report
        """
        try:
            # Get data from context parameters
            incident_data = {}
            resolution_data = {}
            
            if context is not None:
                incident_data = getattr(context, 'incident_data', {})
                if not incident_data and hasattr(context, 'kwargs') and isinstance(context.kwargs, dict):
                    incident_data = context.kwargs.get('incident_data', {})
                
                resolution_data = getattr(context, 'resolution_data', {})
                if not resolution_data and hasattr(context, 'kwargs') and isinstance(context.kwargs, dict):
                    resolution_data = context.kwargs.get('resolution_data', {})
            
            # Parse incident data
            if isinstance(incident_data, str):
                try:
                    incident = json.loads(incident_data)
                except json.JSONDecodeError:
                    incident = {"incident_id": "unknown", "timeline": []}
            else:
                incident = incident_data
            
            # Extract key information
            incident_id = incident.get("incident_id", "unknown")
            alert_data = incident.get("alert", {})
            classification = incident.get("classification", {})
            timeline_data = incident.get("timeline", [])
            
            # Create dummy resolution data for now
            resolution_data = incident.get("resolution_data", {})
            
            # Generate timeline
            timeline = self._reconstruct_timeline(timeline_data, alert_data)
            
            # Convert timeline objects to dictionaries
            timeline_dict = [entry.dict() for entry in timeline]
            
            # Create summary
            summary = self._generate_summary(incident, resolution_data, timeline)
            
            # Analyze root cause
            root_cause = self._analyze_root_cause(alert_data, classification, timeline)
            
            # Evaluate resolution effectiveness
            resolution_effectiveness = self._analyze_resolution_effectiveness(
                resolution_data, timeline
            )
            
            # Extract lessons learned
            lessons_learned = self._extract_lessons_learned(
                incident, resolution_data, resolution_effectiveness
            )
            
            # Generate action items
            action_items = self._generate_action_items(
                lessons_learned, resolution_effectiveness, classification
            )
            
            # Convert action items to dictionaries
            action_items_dict = [item.dict() for item in action_items]
            
            # Calculate metrics
            metrics = self._calculate_incident_metrics(timeline, resolution_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                resolution_effectiveness, lessons_learned, metrics
            )
            
            # Create markdown report
            markdown_report = self._generate_markdown_report(
                incident_id, summary, timeline, root_cause, resolution_effectiveness,
                lessons_learned, action_items, metrics, recommendations
            )
            
            return {
                "incident_id": incident_id,
                "summary": summary,
                "timeline": timeline_dict,
                "root_cause_analysis": root_cause,
                "resolution_effectiveness": resolution_effectiveness,
                "lessons_learned": lessons_learned,
                "action_items": action_items_dict,
                "metrics": metrics,
                "recommendations": recommendations,
                "markdown_report": markdown_report,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._generate_fallback_postmortem(str(e))
    
    def _reconstruct_timeline(self, timeline_data: List[Dict], alert_data: Dict) -> List[PostMortemTimelineEntry]:
        """Reconstruct chronological timeline of incident"""
        timeline = []
        
        # Add initial alert
        alert_time = alert_data.get("timestamp", datetime.now().isoformat())
        timeline.append(PostMortemTimelineEntry(
            time=alert_time,
            event="Incident Detected",
            details=f"Alert: {alert_data.get('message', 'Unknown alert')}",
            agent_action=False
        ))
        
        # Add timeline entries from incident data
        for entry in timeline_data:
            timeline.append(PostMortemTimelineEntry(
                time=entry.get("timestamp", datetime.now().isoformat()),
                event=entry.get("action", "Unknown action"),
                details=self._format_timeline_details(entry),
                agent_action=entry.get("agent", "").startswith("AI") or "Agent" in entry.get("agent", "")
            ))
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x.time)
        
        return timeline
    
    def _format_timeline_details(self, entry: Dict) -> str:
        """Format timeline entry details"""
        agent = entry.get("agent", "Unknown")
        result = entry.get("result", {})
        duration = entry.get("duration_ms", 0)
        
        details = f"Agent: {agent}"
        if duration:
            details += f" (Duration: {duration}ms)"
        
        if isinstance(result, dict) and result:
            if "success" in result:
                details += f" - Success: {result['success']}"
            if "message" in result:
                details += f" - {result['message']}"
        
        return details
    
    def _generate_summary(self, incident_data: Dict, resolution_data: Dict, timeline: List) -> Dict[str, str]:
        """Generate executive summary"""
        alert = incident_data.get("alert", {})
        classification = incident_data.get("classification", {})
        
        # Calculate duration
        start_time = datetime.fromisoformat(timeline[0].time.replace('Z', '+00:00')) if timeline else datetime.now()
        end_time = datetime.fromisoformat(timeline[-1].time.replace('Z', '+00:00')) if timeline else start_time
        duration = end_time - start_time
        
        # Determine impact
        severity = classification.get("severity", "unknown")
        affected_services = alert.get("affected_services", [])
        impact = self._assess_impact(severity, affected_services)
        
        return {
            "title": f"{classification.get('category', 'Unknown')} Incident - {alert.get('source_system', 'Unknown System')}",
            "duration": str(duration).split('.')[0],  # Remove microseconds
            "impact": impact,
            "root_cause": self._extract_primary_cause(alert, classification),
            "status": "Resolved" if resolution_data.get("success", False) else "Ongoing"
        }
    
    def _assess_impact(self, severity: str, affected_services: List[str]) -> str:
        """Assess business impact based on severity and affected services"""
        service_count = len(affected_services)
        
        if severity == "critical":
            if service_count > 3:
                return "High - Multiple critical services affected, significant user impact"
            else:
                return "Medium-High - Critical severity but limited service scope"
        elif severity == "high":
            if service_count > 2:
                return "Medium - Multiple services affected"
            else:
                return "Medium-Low - Limited service impact"
        elif severity == "medium":
            return "Low-Medium - Minor service disruption"
        else:
            return "Low - Minimal impact"
    
    def _extract_primary_cause(self, alert: Dict, classification: Dict) -> str:
        """Extract primary root cause from alert and classification"""
        message = alert.get("message", "").lower()
        category = classification.get("category", "unknown")
        
        if "cpu" in message or "memory" in message:
            return "Resource exhaustion"
        elif "connection" in message:
            return "Connection pool exhaustion"
        elif "timeout" in message or "latency" in message:
            return "Performance degradation"
        elif "error rate" in message:
            return "Application errors"
        elif "disk" in message or "storage" in message:
            return "Storage capacity issue"
        else:
            return f"Unknown - requires investigation ({category} related)"
    
    def _analyze_root_cause(self, alert: Dict, classification: Dict, timeline: List) -> str:
        """Perform detailed root cause analysis"""
        primary_cause = self._extract_primary_cause(alert, classification)
        message = alert.get("message", "")
        metrics = alert.get("metrics", {})
        
        analysis = f"**Primary Cause:** {primary_cause}\n\n"
        analysis += f"**Alert Details:** {message}\n\n"
        
        # Analyze metrics
        if metrics:
            analysis += "**Contributing Factors:**\n"
            if metrics.get("cpu_usage", 0) > 90:
                analysis += f"- High CPU usage: {metrics['cpu_usage']}%\n"
            if metrics.get("memory_usage", 0) > 85:
                analysis += f"- High memory usage: {metrics['memory_usage']}%\n"
            if metrics.get("error_rate", 0) > 0.05:
                analysis += f"- Elevated error rate: {metrics['error_rate']*100:.1f}%\n"
            if metrics.get("response_time", 0) > 3000:
                analysis += f"- Slow response time: {metrics['response_time']}ms\n"
        
        # Analyze timeline for patterns
        agent_actions = [entry for entry in timeline if entry.agent_action]
        if agent_actions:
            analysis += f"\n**Agent Response:** {len(agent_actions)} automated actions taken\n"
        
        analysis += "\n**Recommendation:** Implement monitoring thresholds and automated scaling to prevent recurrence."
        
        return analysis
    
    def _analyze_resolution_effectiveness(self, resolution_data: Dict, timeline: List) -> Dict[str, Any]:
        """Analyze how effective the resolution was"""
        steps = resolution_data.get("recommended_steps", [])
        success = resolution_data.get("success", False)
        
        # Count automated vs manual actions
        automated_actions = sum(1 for entry in timeline if entry.agent_action)
        manual_actions = len(timeline) - automated_actions - 1  # Subtract initial alert
        
        # Calculate time to resolution
        if len(timeline) >= 2:
            start_time = datetime.fromisoformat(timeline[0].time.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(timeline[-1].time.replace('Z', '+00:00'))
            resolution_time = int((end_time - start_time).total_seconds() / 60)
        else:
            resolution_time = 0
        
        effective_steps = []
        ineffective_steps = []
        
        # Analyze individual steps (simplified analysis)
        for i, step in enumerate(steps):
            if i < len(timeline) - 1:  # Has corresponding timeline entry
                if "success" in str(step).lower() or step.get("automation_possible", False):
                    effective_steps.append(step.get("description", f"Step {i+1}"))
                else:
                    ineffective_steps.append(step.get("description", f"Step {i+1}"))
        
        return {
            "overall_success": success,
            "resolution_time_minutes": resolution_time,
            "automated_actions": automated_actions,
            "manual_interventions": manual_actions,
            "effective_steps": effective_steps,
            "ineffective_steps": ineffective_steps,
            "automation_rate": automated_actions / max(len(timeline) - 1, 1)
        }
    
    def _extract_lessons_learned(self, incident_data: Dict, resolution_data: Dict, effectiveness: Dict) -> List[str]:
        """Extract key lessons from the incident"""
        lessons = []
        
        classification = incident_data.get("classification", {})
        confidence = classification.get("confidence", 0)
        
        # Classification accuracy lessons
        if confidence < 0.7:
            lessons.append("Improve alert classification accuracy through better data collection")
        
        # Resolution effectiveness lessons
        if effectiveness["automation_rate"] < 0.5:
            lessons.append("Increase automation for common resolution steps")
        
        if effectiveness["resolution_time_minutes"] > 30:
            lessons.append("Optimize response time through better automation and runbook improvements")
        
        if effectiveness["manual_interventions"] > 2:
            lessons.append("Reduce manual intervention requirements through improved automation")
        
        # Category-specific lessons
        category = classification.get("category", "")
        if category == "database":
            lessons.append("Consider implementing connection pool monitoring and auto-scaling")
        elif category == "infrastructure":
            lessons.append("Implement predictive monitoring to catch resource issues earlier")
        elif category == "application":
            lessons.append("Improve application health checks and circuit breaker patterns")
        
        # Severity-based lessons
        severity = classification.get("severity", "")
        if severity == "critical":
            lessons.append("Critical incidents require immediate escalation protocols")
        
        if not lessons:
            lessons.append("Incident handled effectively - maintain current processes")
        
        return lessons
    
    def _generate_action_items(self, lessons: List[str], effectiveness: Dict, classification: Dict) -> List[ActionItem]:
        """Generate actionable follow-up items"""
        action_items = []
        
        # Based on lessons learned
        for lesson in lessons:
            if "automation" in lesson.lower():
                action_items.append(ActionItem(
                    description="Implement additional automation for identified manual steps",
                    owner="DevOps Team",
                    priority="high",
                    due_date=(datetime.now() + timedelta(days=14)).isoformat(),
                    category="automation"
                ))
            elif "monitoring" in lesson.lower():
                action_items.append(ActionItem(
                    description="Enhance monitoring thresholds and alert accuracy",
                    owner="SRE Team",
                    priority="medium",
                    due_date=(datetime.now() + timedelta(days=21)).isoformat(),
                    category="monitoring"
                ))
        
        # Based on effectiveness analysis
        if effectiveness["resolution_time_minutes"] > 20:
            action_items.append(ActionItem(
                description="Review and optimize incident response runbooks",
                owner="On-call Team",
                priority="medium",
                due_date=(datetime.now() + timedelta(days=10)).isoformat(),
                category="process"
            ))
        
        # Category-specific actions
        category = classification.get("category", "")
        if category == "database":
            action_items.append(ActionItem(
                description="Implement database connection pool monitoring dashboard",
                owner="Database Team",
                priority="high",
                due_date=(datetime.now() + timedelta(days=7)).isoformat(),
                category="infrastructure"
            ))
        
        # Always add documentation action
        action_items.append(ActionItem(
            description="Update incident response documentation with lessons learned",
            owner="Documentation Team",
            priority="low",
            due_date=(datetime.now() + timedelta(days=30)).isoformat(),
            category="documentation"
        ))
        
        return action_items
    
    def _calculate_incident_metrics(self, timeline: List, resolution_data: Dict) -> Dict[str, Any]:
        """Calculate key incident metrics"""
        if not timeline:
            return {}
        
        # Time metrics
        start_time = datetime.fromisoformat(timeline[0].time.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(timeline[-1].time.replace('Z', '+00:00'))
        
        total_duration = (end_time - start_time).total_seconds() / 60  # minutes
        
        # Count different types of actions
        agent_actions = sum(1 for entry in timeline if entry.agent_action)
        human_actions = len(timeline) - agent_actions - 1  # Exclude initial alert
        
        return {
            "total_duration_minutes": round(total_duration, 1),
            "mean_time_to_recovery": round(total_duration, 1),
            "agent_actions_count": agent_actions,
            "human_actions_count": human_actions,
            "automation_percentage": round((agent_actions / max(len(timeline) - 1, 1)) * 100, 1),
            "timeline_entries": len(timeline),
            "resolution_success": resolution_data.get("success", False)
        }
    
    def _generate_recommendations(self, effectiveness: Dict, lessons: List[str], metrics: Dict) -> List[str]:
        """Generate process improvement recommendations"""
        recommendations = []
        
        # Based on automation rate
        automation_rate = effectiveness.get("automation_rate", 0)
        if automation_rate < 0.7:
            recommendations.append("Increase automation coverage for incident response procedures")
        
        # Based on resolution time
        resolution_time = metrics.get("total_duration_minutes", 0)
        if resolution_time > 15:
            recommendations.append("Implement faster detection and response mechanisms")
        
        # Based on manual interventions
        manual_interventions = effectiveness.get("manual_interventions", 0)
        if manual_interventions > 3:
            recommendations.append("Reduce manual intervention requirements through better tooling")
        
        # General recommendations
        recommendations.extend([
            "Conduct regular incident response drills to improve team readiness",
            "Review and update monitoring thresholds based on incident patterns",
            "Implement chaos engineering practices to proactively identify weaknesses"
        ])
        
        return recommendations
    
    def _generate_markdown_report(self, incident_id: str, summary: Dict, timeline: List,
                                 root_cause: str, effectiveness: Dict, lessons: List[str],
                                 action_items: List, metrics: Dict, recommendations: List[str]) -> str:
        """Generate complete markdown formatted report"""
        
        report = f"""# Post-Incident Report: {summary['title']}

**Incident ID:** {incident_id}  
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** {summary['status']}  

## Executive Summary

- **Duration:** {summary['duration']}
- **Impact:** {summary['impact']}
- **Root Cause:** {summary['root_cause']}

## Timeline

| Time | Event | Details |
|------|-------|---------|
"""
        
        for entry in timeline:
            agent_indicator = "🤖" if entry.agent_action else "👤"
            report += f"| {entry.time} | {agent_indicator} {entry.event} | {entry.details} |\n"
        
        report += f"""
## Root Cause Analysis

{root_cause}

## Resolution Effectiveness

- **Overall Success:** {effectiveness['overall_success']}
- **Resolution Time:** {effectiveness['resolution_time_minutes']} minutes
- **Automated Actions:** {effectiveness['automated_actions']}
- **Manual Interventions:** {effectiveness['manual_interventions']}
- **Automation Rate:** {effectiveness['automation_rate']:.1%}

### Effective Steps
"""
        for step in effectiveness.get('effective_steps', []):
            report += f"- {step}\n"
        
        if effectiveness.get('ineffective_steps'):
            report += "\n### Ineffective Steps\n"
            for step in effectiveness['ineffective_steps']:
                report += f"- {step}\n"
        
        report += "\n## Lessons Learned\n\n"
        for lesson in lessons:
            report += f"- {lesson}\n"
        
        report += "\n## Action Items\n\n"
        for item in action_items:
            report += f"- **{item.description}** (Owner: {item.owner}, Priority: {item.priority}, Due: {item.due_date[:10]})\n"
        
        report += "\n## Metrics\n\n"
        for key, value in metrics.items():
            formatted_key = key.replace('_', ' ').title()
            report += f"- **{formatted_key}:** {value}\n"
        
        report += "\n## Recommendations\n\n"
        for rec in recommendations:
            report += f"- {rec}\n"
        
        report += f"""
## Appendix

This report was automatically generated by the DevOps Crisis Commander Post-Mortem Agent.  
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return report
    
    def _generate_fallback_postmortem(self, error: str) -> Dict[str, Any]:
        """Generate fallback post-mortem when main logic fails"""
        return {
            "incident_id": "unknown",
            "summary": {
                "title": "Post-Mortem Generation Failed",
                "duration": "Unknown",
                "impact": "Unknown",
                "root_cause": f"Report generation error: {error}",
                "status": "Manual review required"
            },
            "timeline": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "event": "Post-mortem generation failed",
                    "actor": "postmortem_generator",
                    "description": f"Error occurred: {error}"
                }
            ],
            "root_cause_analysis": f"Unable to generate analysis due to error: {error}",
            "resolution_effectiveness": "Unknown",
            "lessons_learned": ["Post-mortem generation process needs improvement"],
            "action_items": ["Fix post-mortem generation error", "Manual post-mortem review required"],
            "metrics": {},
            "recommendations": ["Investigate post-mortem generation failure"],
            "markdown_report": f"# Post-Mortem Generation Error\\n\\nError: {error}\\n\\nManual review required.",
            "generated_at": datetime.now().isoformat()
        }


# Create the tool instance
postmortem_generator_tool = PostMortemGeneratorTool()
