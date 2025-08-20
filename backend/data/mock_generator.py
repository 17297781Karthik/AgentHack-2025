"""
Mock data generators for DevOps Crisis Commander
"""
import random
import sys
import os
from datetime import datetime, timedelta
from typing import List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.models import Alert, AlertType, SeverityLevel, AlertMetrics, Runbook, RunbookStep


class MockDataGenerator:
    """Generates realistic mock alerts and scenarios for demo purposes"""
    
    MOCK_SCENARIOS = {
        "cpu_spike_critical": {
            "alert_type": AlertType.CPU,
            "severity": SeverityLevel.CRITICAL,
            "message": "CPU usage exceeded 95% threshold on production server",
            "metrics": {"cpu_usage": 98.5, "memory_usage": 82.3},
            "affected_services": ["api-gateway", "user-service"],
            "source_system": "prometheus-monitoring"
        },
        
        "database_connection_exhausted": {
            "alert_type": AlertType.DATABASE,
            "severity": SeverityLevel.HIGH,
            "message": "Database connection pool exhausted - max connections reached",
            "metrics": {"response_time": 5000, "error_rate": 0.25},
            "affected_services": ["user-db", "order-service"],
            "source_system": "database-monitor"
        },
        
        "memory_leak_detected": {
            "alert_type": AlertType.MEMORY,
            "severity": SeverityLevel.HIGH,
            "message": "Memory usage steadily increasing over 4 hours",
            "metrics": {"memory_usage": 89.7, "cpu_usage": 45.2},
            "affected_services": ["payment-service"],
            "source_system": "application-insights"
        },
        
        "disk_space_warning": {
            "alert_type": AlertType.DISK,
            "severity": SeverityLevel.MEDIUM,
            "message": "Disk usage approaching 85% on log partition",
            "metrics": {"disk_usage": 84.3},
            "affected_services": ["logging-service"],
            "source_system": "infrastructure-monitor"
        },
        
        "network_latency_spike": {
            "alert_type": AlertType.NETWORK,
            "severity": SeverityLevel.MEDIUM,
            "message": "Network latency increased 300% between regions",
            "metrics": {"response_time": 1200, "error_rate": 0.08},
            "affected_services": ["cdn", "api-gateway"],
            "source_system": "network-monitor"
        },
        
        "application_error_rate": {
            "alert_type": AlertType.APPLICATION,
            "severity": SeverityLevel.HIGH,
            "message": "Application error rate exceeding 10% threshold",
            "metrics": {"error_rate": 0.15, "response_time": 3500},
            "affected_services": ["checkout-service", "inventory-service"],
            "source_system": "application-monitor"
        },
        
        "service_health_check_failing": {
            "alert_type": AlertType.APPLICATION,
            "severity": SeverityLevel.CRITICAL,
            "message": "Health check endpoint returning 503 for critical service",
            "metrics": {"error_rate": 1.0, "response_time": 0},
            "affected_services": ["auth-service"],
            "source_system": "kubernetes-monitor"
        },
        
        "ssl_certificate_expiring": {
            "alert_type": AlertType.NETWORK,
            "severity": SeverityLevel.LOW,
            "message": "SSL certificate expires in 7 days",
            "metrics": {},
            "affected_services": ["api.company.com"],
            "source_system": "certificate-monitor"
        },
        
        "backup_failure": {
            "alert_type": AlertType.DATABASE,
            "severity": SeverityLevel.MEDIUM,
            "message": "Automated backup failed for production database",
            "metrics": {},
            "affected_services": ["backup-service", "main-db"],
            "source_system": "backup-monitor"
        },
        
        "redis_cluster_node_down": {
            "alert_type": AlertType.DATABASE,
            "severity": SeverityLevel.HIGH,
            "message": "Redis cluster node unresponsive - failover initiated",
            "metrics": {"response_time": 2000, "error_rate": 0.12},
            "affected_services": ["cache-layer", "session-service"],
            "source_system": "redis-monitor"
        }
    }
    
    @classmethod
    def generate_alert(cls, scenario_name: str = None) -> Alert:
        """Generate a mock alert based on scenario or random"""
        if scenario_name and scenario_name in cls.MOCK_SCENARIOS:
            scenario = cls.MOCK_SCENARIOS[scenario_name]
        else:
            scenario = random.choice(list(cls.MOCK_SCENARIOS.values()))
        
        # Add some randomness to metrics
        metrics = AlertMetrics(**scenario["metrics"])
        if metrics.cpu_usage:
            metrics.cpu_usage += random.uniform(-5, 5)
        if metrics.memory_usage:
            metrics.memory_usage += random.uniform(-3, 3)
        if metrics.response_time:
            metrics.response_time += random.uniform(-500, 500)
        
        return Alert(
            timestamp=datetime.now() - timedelta(seconds=random.randint(0, 300)),
            source_system=scenario["source_system"],
            alert_type=scenario["alert_type"],
            severity=scenario["severity"],
            message=scenario["message"],
            metrics=metrics,
            affected_services=scenario["affected_services"],
            metadata={
                "environment": "production",
                "region": random.choice(["us-east-1", "eu-west-1", "ap-southeast-1"]),
                "cluster": f"cluster-{random.randint(1, 5)}"
            }
        )
    
    @classmethod
    def get_scenario_names(cls) -> List[str]:
        """Get list of available scenario names"""
        return list(cls.MOCK_SCENARIOS.keys())
    
    @classmethod
    def generate_runbooks(cls) -> List[Runbook]:
        """Generate mock runbooks for different incident types"""
        runbooks = [
            Runbook(
                category="cpu",
                severity_level="critical",
                title="High CPU Usage Resolution",
                description="Steps to diagnose and resolve high CPU usage incidents",
                steps=[
                    RunbookStep(
                        step_number=1,
                        description="Check top CPU consuming processes",
                        command="top -o %CPU | head -10",
                        expected_result="List of processes sorted by CPU usage",
                        automation_possible=True
                    ),
                    RunbookStep(
                        step_number=2,
                        description="Analyze process details and resource allocation",
                        command="ps aux | grep [high-cpu-process]",
                        expected_result="Detailed process information",
                        automation_possible=True
                    ),
                    RunbookStep(
                        step_number=3,
                        description="Scale horizontally if possible",
                        command="kubectl scale deployment [service-name] --replicas=5",
                        expected_result="Additional pods created",
                        rollback_command="kubectl scale deployment [service-name] --replicas=3",
                        automation_possible=True
                    ),
                    RunbookStep(
                        step_number=4,
                        description="Monitor CPU usage trends",
                        command="Monitor dashboard for 10 minutes",
                        expected_result="CPU usage stabilizes below 80%",
                        automation_possible=False
                    )
                ],
                prerequisites=["kubectl access", "monitoring dashboard access"],
                estimated_time_minutes=15,
                success_rate=0.85
            ),
            
            Runbook(
                category="database",
                severity_level="high",
                title="Database Connection Pool Exhaustion",
                description="Resolve database connection pool exhaustion issues",
                steps=[
                    RunbookStep(
                        step_number=1,
                        description="Check current connection count",
                        command="SELECT count(*) FROM pg_stat_activity;",
                        expected_result="Current active connections",
                        automation_possible=True
                    ),
                    RunbookStep(
                        step_number=2,
                        description="Identify long-running queries",
                        command="SELECT query, state, query_start FROM pg_stat_activity WHERE state != 'idle' ORDER BY query_start;",
                        expected_result="List of active queries",
                        automation_possible=True
                    ),
                    RunbookStep(
                        step_number=3,
                        description="Kill problematic long-running queries",
                        command="SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE query_start < now() - interval '1 hour';",
                        expected_result="Terminated long-running connections",
                        automation_possible=False
                    ),
                    RunbookStep(
                        step_number=4,
                        description="Restart application connection pools",
                        command="kubectl rollout restart deployment [app-name]",
                        expected_result="Fresh connection pools established",
                        automation_possible=True
                    )
                ],
                prerequisites=["database admin access", "kubectl access"],
                estimated_time_minutes=10,
                success_rate=0.92
            ),
            
            Runbook(
                category="memory",
                severity_level="high",
                title="Memory Leak Investigation",
                description="Diagnose and resolve memory leak issues",
                steps=[
                    RunbookStep(
                        step_number=1,
                        description="Generate heap dump",
                        command="jcmd [pid] GC.run_finalization; jcmd [pid] VM.gc",
                        expected_result="Forced garbage collection completed",
                        automation_possible=True
                    ),
                    RunbookStep(
                        step_number=2,
                        description="Analyze memory usage patterns",
                        command="Monitor memory metrics for 5 minutes",
                        expected_result="Memory usage trend analysis",
                        automation_possible=False
                    ),
                    RunbookStep(
                        step_number=3,
                        description="Restart affected service",
                        command="kubectl rollout restart deployment [service-name]",
                        expected_result="Service restarted with fresh memory allocation",
                        automation_possible=True
                    )
                ],
                prerequisites=["JVM monitoring access", "kubectl access"],
                estimated_time_minutes=12,
                success_rate=0.78
            ),
            
            Runbook(
                category="network",
                severity_level="medium",
                title="Network Latency Resolution",
                description="Diagnose and resolve network latency issues",
                steps=[
                    RunbookStep(
                        step_number=1,
                        description="Test network connectivity",
                        command="ping -c 10 [target-host]",
                        expected_result="Network connectivity confirmed",
                        automation_possible=True
                    ),
                    RunbookStep(
                        step_number=2,
                        description="Check network path and routing",
                        command="traceroute [target-host]",
                        expected_result="Network path analysis",
                        automation_possible=True
                    ),
                    RunbookStep(
                        step_number=3,
                        description="Enable CDN or edge caching",
                        command="Update DNS to point to CDN endpoint",
                        expected_result="Traffic routed through CDN",
                        automation_possible=False
                    )
                ],
                prerequisites=["network admin access", "DNS admin access"],
                estimated_time_minutes=8,
                success_rate=0.88
            )
        ]
        
        return runbooks
    
    @classmethod
    def generate_scenario_alert(cls, scenario_name: str) -> dict:
        """Generate alert data for a specific scenario"""
        if scenario_name not in cls.MOCK_SCENARIOS:
            # Return random alert if scenario not found
            return cls.generate_random_alert()
        
        scenario = cls.MOCK_SCENARIOS[scenario_name]
        
        return {
            "id": f"alert-{random.randint(1000, 9999)}",
            "alert_type": scenario["alert_type"],
            "severity": scenario["severity"],
            "message": scenario["message"],
            "metrics": scenario["metrics"],
            "affected_services": scenario["affected_services"],
            "source_system": scenario["source_system"],
            "timestamp": datetime.now().isoformat(),
            "scenario_name": scenario_name
        }
    
    @classmethod
    def generate_random_alert(cls) -> dict:
        """Generate a random alert from available scenarios"""
        scenario_name = random.choice(list(cls.MOCK_SCENARIOS.keys()))
        return cls.generate_scenario_alert(scenario_name)
