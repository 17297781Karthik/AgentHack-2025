# Crisis Commander - Hackathon Demo Guide

## 🎯 Project Overview

**Crisis Commander** is a multi-agent AI system for intelligent DevOps incident response, built for AgentHack 2025.

### Key Features
- **Multi-Agent Architecture**: 3 specialized AI agents working together
- **Real-time Incident Detection**: Automatic classification and response
- **Intelligent Resolution**: Context-aware resolution recommendations  
- **Post-Mortem Generation**: Automated incident documentation
- **WebSocket Real-time Updates**: Live dashboard updates

## 🚀 Demo Instructions

### Option 1: Web Frontend Demo (Recommended for Presentation)

1. **Start the Backend**:
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Open the Frontend**:
   - Open `frontend/index.html` in a web browser
   - Or serve it: `python -m http.server 8080` from frontend directory
   - Navigate to: http://localhost:8080

3. **Demo Flow**:
   - Show the live dashboard with system status
   - Explain the 10 realistic incident scenarios
   - Click on scenario cards to simulate incidents
   - Watch real-time agent workflow execution
   - Show incident timeline and resolution steps

### Option 2: CLI Demo (Good for Technical Audience)

1. **Auto Demo Mode**:
   ```bash
   python demo_cli.py --auto
   ```
   - Automatically simulates 3 different incidents
   - Shows the complete multi-agent workflow
   - Displays detailed timelines and agent actions

2. **Interactive Demo Mode**:
   ```bash
   python demo_cli.py
   ```
   - Interactive menu-driven interface
   - Choose specific scenarios or random incidents
   - Real-time system monitoring

## 🎭 Available Incident Scenarios

| Scenario | Severity | Description | Services Affected |
|----------|----------|-------------|-------------------|
| CPU Spike Critical | 🔴 Critical | CPU usage exceeded 95% | api-gateway, user-service |
| Database Connection Exhausted | 🟠 High | Connection pool maxed out | user-db, order-service |
| Memory Leak Detected | 🟠 High | Memory increasing over 4 hours | payment-service |
| Service Health Check Failing | 🔴 Critical | 503 errors on health endpoint | auth-service |
| Application Error Rate | 🟠 High | 10%+ error rate threshold | checkout-service, inventory-service |
| Redis Cluster Node Down | 🟠 High | Node unresponsive, failover | cache-layer, session-service |
| Network Latency Spike | 🟡 Medium | 300% latency increase | cdn, api-gateway |
| Disk Space Warning | 🟡 Medium | 85% disk usage on logs | logging-service |
| Backup Failure | 🟡 Medium | Automated backup failed | backup-service, main-db |
| SSL Certificate Expiring | 🟢 Low | Certificate expires in 7 days | api.company.com |

## 🤖 Multi-Agent Workflow

### 1. Incident Classifier Agent 🔍
- Analyzes incoming alerts
- Categorizes incidents (infrastructure, application, database, network)
- Assigns severity levels and confidence scores
- Tags for better searchability

### 2. Resolution Advisor Agent 🛠️
- Matches incidents to proven runbooks
- Generates step-by-step resolution plans
- Estimates success probability and time required
- Provides rollback procedures and prerequisites

### 3. Post-Mortem Generator Agent 📝
- Creates comprehensive incident reports
- Documents timeline and root cause analysis
- Generates lessons learned and action items
- Exports markdown reports for documentation

## 📊 Key APIs for Demo

| Endpoint | Purpose | Demo Use |
|----------|---------|----------|
| `GET /demo/status` | System health check | Show system is operational |
| `GET /scenarios` | List available scenarios | Display incident types |
| `POST /incidents/simulate` | Trigger incident | Start the demo workflow |
| `GET /incidents/active` | Active incidents | Show current workload |
| `GET /incidents/completed` | Completed incidents | Show resolution history |
| `GET /incidents/{id}` | Incident details | Deep dive into workflow |
| `POST /admin/reset` | Reset system | Clean slate between demos |
| `WS /ws` | Real-time updates | Live dashboard updates |

## 🎪 Presentation Tips

### Opening Hook (30 seconds)
- "Imagine your production system goes down at 2 AM"
- "Instead of waking up engineers, Crisis Commander handles it automatically"
- Show the live dashboard detecting and resolving an incident

### Technical Demo (2-3 minutes)
1. **Start with System Status**: Show healthy system with 0 incidents
2. **Trigger Critical Incident**: Click "CPU Spike Critical" scenario
3. **Watch Multi-Agent Flow**: 
   - Classification → Analysis → Resolution → Documentation
   - Point out the 3 agents working together
   - Show real-time timeline updates
4. **Show Resolution**: Incident moves from active to completed
5. **Demonstrate Scale**: Trigger multiple incidents simultaneously

### Value Proposition (1 minute)
- **Reduces MTTR**: Mean Time To Resolution from hours to minutes
- **24/7 Availability**: No human required for initial response
- **Consistent Process**: Same high-quality response every time
- **Learning System**: Improves with each incident
- **Full Documentation**: Complete audit trail and post-mortems

### Technology Highlights
- **Multi-Agent Architecture**: Portia AI SDK coordination
- **Real-time Processing**: WebSocket updates
- **RESTful API**: Easy integration
- **Scalable Design**: Handle multiple simultaneous incidents
- **Extensible**: Easy to add new scenarios and agents

## 🏆 Competitive Advantages

1. **Multi-Agent Intelligence**: Not just alerts, but intelligent coordination
2. **End-to-End Workflow**: From detection to documentation
3. **Real-time Updates**: Live dashboard and notifications
4. **Proven Scenarios**: 10 realistic DevOps incident types
5. **Easy Integration**: RESTful API and WebSocket support

## 🛠️ Technical Architecture

```
Frontend (Vue.js/HTML5) ←→ WebSocket ←→ FastAPI Backend
                                            ↓
                                    Crisis Commander
                                    ↙       ↓       ↘
                        Classifier  Advisor  PostMortem
                        Agent      Agent    Agent
                                    ↓
                                Mock Data
                                & Runbooks
```

## 🚀 Future Roadmap

- **Integration with Real Monitoring**: Prometheus, Grafana, PagerDuty
- **Slack/Teams Integration**: ChatOps for team collaboration  
- **Machine Learning**: Improved classification and prediction
- **Custom Runbooks**: User-defined resolution procedures
- **Incident Analytics**: Trends and performance metrics

---

## Quick Demo Commands

```bash
# Start backend
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000

# Auto CLI demo  
python demo_cli.py --auto

# Interactive CLI demo
python demo_cli.py

# Reset system between demos
curl -X POST http://localhost:8000/admin/reset

# Simulate specific incident
curl -X POST http://localhost:8000/incidents/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario_name": "cpu_spike_critical"}'
```

**Ready to Demo! 🎉**