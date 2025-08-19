"""
Incident Classifier Agent using Portia AI SDK
"""
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Type
from pydantic import BaseModel, Field

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Import Portia Tool class
from portia import Tool, ToolRunContext


class ClassificationInput(BaseModel):
    """Input schema for incident classification"""
    alert_data: Dict[str, Any] = Field(description="Raw alert data to classify")


class ClassificationOutput(BaseModel):
    """Output schema for incident classification"""
    category: str = Field(description="Classified incident category")
    severity: str = Field(description="Assessed severity level")
    confidence: float = Field(description="Classification confidence score")
    tags: list[str] = Field(description="Relevant tags for this incident")
    estimated_impact: str = Field(description="Estimated business impact")
    reasoning: str = Field(description="Explanation of classification logic")


class IncidentClassifierTool(Tool):
    """Tool for classifying incidents based on alert data"""
    
    id: str = "incident_classifier"
    name: str = "Incident Classifier"
    description: str = """
    Classifies incoming alerts by analyzing their type, severity, metrics, and context.
    Uses rule-based logic combined with pattern matching to determine:
    - Incident category (infrastructure, application, database, network)
    - Severity level (critical, high, medium, low)
    - Confidence score for the classification
    - Relevant tags and estimated business impact
    """
    
    output_schema: tuple = ("dict", "dict: classification results with category, severity, confidence, and reasoning")
    
    def run(self, context: ToolRunContext, alert_data: str) -> Dict[str, Any]:
        """
        Classify an alert using rule-based logic
        """
        try:
            # Parse alert data if it's a JSON string
            if isinstance(alert_data, str):
                try:
                    alert_info = json.loads(alert_data)
                except json.JSONDecodeError:
                    alert_info = {"raw_data": alert_data}
            else:
                alert_info = alert_data
            
            # Parse alert data
            alert_type = alert_info.get("alert_type", "").lower()
            severity = alert_info.get("severity", "").lower()
            metrics = alert_info.get("metrics", {})
            message = alert_info.get("message", "").lower()
            affected_services = alert_info.get("affected_services", [])
            
            # Determine category
            category = self._determine_category(alert_type, message, affected_services)
            
            # Assess severity with context
            assessed_severity = self._assess_severity(severity, metrics, message, category)
            
            # Calculate confidence
            confidence = self._calculate_confidence(alert_info, category, assessed_severity)
            
            # Generate tags
            tags = self._generate_tags(alert_type, message, affected_services, metrics)
            
            # Estimate impact
            impact = self._estimate_impact(assessed_severity, affected_services, category)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(category, assessed_severity, confidence, metrics)
            
            return {
                "incident_id": alert_info.get("id", "unknown"),
                "category": category,
                "severity": assessed_severity,
                "confidence": confidence,
                "tags": tags,
                "estimated_impact": impact,
                "reasoning": reasoning,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            # Fallback classification
            return {
                "incident_id": "unknown",
                "category": "unknown",
                "severity": "medium",
                "confidence": 0.3,
                "tags": ["unclassified", "needs-review"],
                "estimated_impact": "unknown",
                "reasoning": f"Classification failed: {str(e)}. Manual review required.",
                "generated_at": datetime.now().isoformat()
            }
    
    def _determine_category(self, alert_type: str, message: str, services: list) -> str:
        """Determine incident category based on alert characteristics"""
        
        # Database-related keywords
        if any(word in message for word in ["database", "connection", "query", "sql", "redis", "mongo"]):
            return "database"
        if any(word in alert_type for word in ["database", "db"]):
            return "database"
        if any("db" in service for service in services):
            return "database"
            
        # Network-related keywords  
        if any(word in message for word in ["network", "latency", "timeout", "ssl", "certificate", "dns"]):
            return "network"
        if alert_type in ["network"]:
            return "network"
        if any(word in message for word in ["cdn", "proxy", "gateway"]):
            return "network"
            
        # Application-related keywords
        if any(word in message for word in ["application", "service", "endpoint", "api", "error rate"]):
            return "application"
        if alert_type in ["application"]:
            return "application"
        if any("service" in service for service in services):
            return "application"
            
        # Infrastructure-related (CPU, memory, disk)
        if alert_type in ["cpu", "memory", "disk"]:
            return "infrastructure"
        if any(word in message for word in ["cpu", "memory", "disk", "storage", "filesystem"]):
            return "infrastructure"
            
        return "infrastructure"  # Default fallback
    
    def _assess_severity(self, original_severity: str, metrics: Dict, message: str, category: str) -> str:
        """Assess and potentially adjust severity based on context"""
        
        severity_score = 0
        
        # Base severity mapping
        severity_map = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        base_score = severity_map.get(original_severity, 2)
        severity_score += base_score
        
        # Metric-based adjustments
        if metrics.get("cpu_usage", 0) > 95:
            severity_score += 1
        if metrics.get("memory_usage", 0) > 90:
            severity_score += 1
        if metrics.get("error_rate", 0) > 0.1:
            severity_score += 1
        if metrics.get("response_time", 0) > 5000:
            severity_score += 1
            
        # Message-based severity indicators
        critical_keywords = ["down", "failed", "critical", "emergency", "outage"]
        if any(word in message for word in critical_keywords):
            severity_score += 1
            
        # Category-specific adjustments
        if category == "database" and "connection" in message:
            severity_score += 1  # DB connection issues are typically severe
        if category == "application" and "health check" in message:
            severity_score += 1  # Health check failures are critical
            
        # Convert score back to severity level
        if severity_score >= 5:
            return "critical"
        elif severity_score >= 4:
            return "high"
        elif severity_score >= 3:
            return "medium"
        else:
            return "low"
    
    def _calculate_confidence(self, alert_data: Dict, category: str, severity: str) -> float:
        """Calculate confidence score for the classification"""
        
        confidence = 0.5  # Base confidence
        
        # Data completeness boosts confidence
        if alert_data.get("alert_type"):
            confidence += 0.1
        if alert_data.get("metrics"):
            confidence += 0.1
        if alert_data.get("affected_services"):
            confidence += 0.1
        if alert_data.get("source_system"):
            confidence += 0.1
            
        # Clear categorization patterns boost confidence
        message = alert_data.get("message", "").lower()
        category_keywords = {
            "database": ["database", "connection", "query", "sql"],
            "network": ["network", "latency", "ssl", "dns"],
            "application": ["application", "service", "api", "error"],
            "infrastructure": ["cpu", "memory", "disk", "storage"]
        }
        
        if category in category_keywords:
            keyword_matches = sum(1 for keyword in category_keywords[category] if keyword in message)
            confidence += min(keyword_matches * 0.05, 0.2)
            
        # Severity alignment with metrics
        metrics = alert_data.get("metrics", {})
        if severity == "critical" and (
            metrics.get("cpu_usage", 0) > 95 or 
            metrics.get("error_rate", 0) > 0.2
        ):
            confidence += 0.1
            
        return min(confidence, 1.0)
    
    def _generate_tags(self, alert_type: str, message: str, services: list, metrics: Dict) -> list[str]:
        """Generate relevant tags for the incident"""
        tags = []
        
        # Alert type tag
        if alert_type:
            tags.append(alert_type)
            
        # Service tags
        for service in services[:3]:  # Limit to first 3 services
            tags.append(f"service:{service}")
            
        # Metric-based tags
        if metrics.get("cpu_usage", 0) > 90:
            tags.append("high-cpu")
        if metrics.get("memory_usage", 0) > 85:
            tags.append("high-memory")
        if metrics.get("error_rate", 0) > 0.05:
            tags.append("high-error-rate")
        if metrics.get("response_time", 0) > 3000:
            tags.append("slow-response")
            
        # Message-based tags
        if "backup" in message:
            tags.append("backup")
        if "ssl" in message or "certificate" in message:
            tags.append("security")
        if "cluster" in message:
            tags.append("clustering")
            
        return tags
    
    def _estimate_impact(self, severity: str, services: list, category: str) -> str:
        """Estimate business impact of the incident"""
        
        # Critical services that affect user experience
        critical_services = ["auth", "api-gateway", "payment", "checkout", "user"]
        
        service_criticality = any(
            any(critical in service.lower() for critical in critical_services)
            for service in services
        )
        
        if severity == "critical":
            if service_criticality:
                return "High - Critical user-facing services affected"
            else:
                return "Medium-High - System stability compromised"
        elif severity == "high":
            if service_criticality:
                return "Medium-High - User experience degraded"
            else:
                return "Medium - Internal systems affected"
        elif severity == "medium":
            if category == "database":
                return "Medium - Data integrity or availability concerns"
            else:
                return "Low-Medium - Limited service impact"
        else:
            return "Low - Minimal business impact"
    
    def _generate_reasoning(self, category: str, severity: str, confidence: float, metrics: Dict) -> str:
        """Generate human-readable reasoning for the classification"""
        
        reasoning_parts = []
        
        # Category reasoning
        reasoning_parts.append(f"Classified as '{category}' incident based on alert characteristics.")
        
        # Severity reasoning
        if severity == "critical":
            reasoning_parts.append("Severity elevated to CRITICAL due to:")
            if metrics.get("cpu_usage", 0) > 95:
                reasoning_parts.append("- CPU usage exceeding 95%")
            if metrics.get("error_rate", 0) > 0.2:
                reasoning_parts.append("- Error rate above 20%")
        elif severity == "high":
            reasoning_parts.append("Assessed as HIGH severity due to significant system impact.")
        
        # Confidence reasoning
        if confidence > 0.8:
            reasoning_parts.append("High confidence classification based on clear indicators.")
        elif confidence < 0.6:
            reasoning_parts.append("Moderate confidence - may require manual review.")
            
        return " ".join(reasoning_parts)


# Create the tool instance
incident_classifier_tool = IncidentClassifierTool()
