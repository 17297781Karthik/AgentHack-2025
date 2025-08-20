# Crisis Commander - Hackathon Demo Package

## ✅ What's Ready for Demo

### 🎯 Complete Demo System
- **✅ Backend API**: Fully functional FastAPI with 10+ endpoints
- **✅ Multi-Agent Workflow**: 3 AI agents working together (Classifier, Advisor, PostMortem)
- **✅ Real-time Updates**: WebSocket support for live dashboard
- **✅ Web Frontend**: Beautiful HTML5 dashboard with real-time updates
- **✅ CLI Interface**: Professional command-line demo tool
- **✅ 10 Realistic Scenarios**: CPU spikes, DB issues, network problems, etc.

### 🚀 Demo Options

#### Option 1: Web Dashboard (Best for Presentation)
```bash
# Start backend
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000

# Serve frontend  
cd frontend && python -m http.server 8080
# Open http://localhost:8080 in browser
```

**Features:**
- 🎨 Beautiful gradient UI with glassmorphism design
- 📊 Real-time system status dashboard
- 🎭 Interactive scenario cards (click to simulate)
- ⚡ Live incident timeline with agent actions
- 🔔 Toast notifications for real-time updates
- 📱 Responsive design for any screen size

#### Option 2: CLI Demo (Technical Audience)
```bash
# Auto demo - simulates 3 incidents automatically
python demo_cli.py --auto

# Interactive demo - menu-driven interface
python demo_cli.py
```

**Features:**
- 🎪 Professional banner and status display
- 🎯 Menu-driven scenario selection
- 📋 Detailed incident timelines
- 🔍 Real-time multi-agent workflow visualization
- 📊 System statistics and summaries

### 🤖 Multi-Agent Architecture

**1. Incident Classifier Agent 🔍**
- Analyzes alert data and context
- Categorizes incidents (infrastructure/application/database/network)
- Assigns severity and confidence scores
- Generates classification reasoning

**2. Resolution Advisor Agent 🛠️**
- Matches incidents to proven runbooks
- Creates step-by-step resolution plans
- Estimates success probability and time
- Provides rollback procedures

**3. Post-Mortem Generator Agent 📝**
- Documents complete incident timeline
- Performs root cause analysis
- Generates lessons learned
- Creates markdown reports

### 🎭 Incident Scenarios Available

| Scenario | Severity | Services | Use Case |
|----------|----------|----------|----------|
| CPU Spike Critical | 🔴 Critical | api-gateway, user-service | Resource exhaustion |
| Database Connection Exhausted | 🟠 High | user-db, order-service | Connection pool issues |
| Memory Leak Detected | 🟠 High | payment-service | Memory management |
| Service Health Check Failing | 🔴 Critical | auth-service | Service downtime |
| Application Error Rate | 🟠 High | checkout-service | Application stability |
| Redis Cluster Node Down | 🟠 High | cache-layer | Infrastructure failure |
| Network Latency Spike | 🟡 Medium | cdn, api-gateway | Performance degradation |
| Disk Space Warning | 🟡 Medium | logging-service | Storage management |
| Backup Failure | 🟡 Medium | backup-service | Data protection |
| SSL Certificate Expiring | 🟢 Low | api.company.com | Security maintenance |

## 🏆 Demo Script for Hackathon

### Opening (30 seconds)
> "Traditional DevOps incident response is reactive, manual, and inconsistent. Crisis Commander changes that with multi-agent AI automation."

**Show:** Live dashboard with system status

### Problem Statement (30 seconds)
> "When production goes down at 2 AM, you need instant, intelligent response - not sleepy engineers fumbling through runbooks."

### Solution Demo (2-3 minutes)

1. **Trigger Critical Incident**: Click "CPU Spike Critical"
   - *"Watch as our AI agents spring into action..."*

2. **Multi-Agent Workflow**: Point out real-time updates
   - 🔍 "Classifier agent analyzes the alert data"
   - 🛠️ "Resolution advisor matches to proven runbooks"  
   - 📝 "PostMortem generator documents everything"

3. **Show Results**: Incident timeline and resolution
   - *"From detection to resolution in seconds, with full documentation"*

4. **Scale Demo**: Trigger multiple incidents
   - *"Handles multiple simultaneous incidents effortlessly"*

### Value Proposition (1 minute)
- **⚡ Instant Response**: Seconds vs hours
- **🎯 Consistent Quality**: Same expertise every time
- **📊 Complete Documentation**: Full audit trail
- **🔄 Continuous Learning**: Improves with each incident

### Technology Stack (30 seconds)
- **🤖 Multi-Agent AI**: Portia AI SDK coordination
- **⚡ Real-time**: WebSocket updates
- **🔗 RESTful API**: Easy integration
- **🎨 Modern UI**: Responsive dashboard

## 🛠️ Quick Setup for Judges

```bash
# 1. Start the backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# 2. Quick CLI demo
python demo_cli.py --auto

# 3. Or web demo
cd frontend && python -m http.server 8080
# Open http://localhost:8080
```

## 📊 Key APIs for Integration

- `POST /incidents/simulate` - Trigger incidents
- `GET /incidents/active` - Monitor active incidents  
- `GET /incidents/completed` - View resolution history
- `WS /ws` - Real-time updates
- `POST /admin/reset` - Clean slate between demos

## 🎯 Competitive Advantages

1. **End-to-End Automation**: Not just alerting, complete resolution
2. **Multi-Agent Intelligence**: Coordinated AI agents
3. **Real-time Dashboard**: Live updates and visualizations
4. **Proven Scenarios**: 10 realistic DevOps incidents
5. **Easy Integration**: RESTful API + WebSocket

---

## 🚀 Ready to Present!

**Files Created:**
- ✅ `demo_cli.py` - Professional CLI demo tool
- ✅ `frontend/index.html` - Beautiful web dashboard
- ✅ `DEMO_GUIDE.md` - Complete presentation guide
- ✅ `frontend_screenshot.png` - UI preview
- ✅ Backend API fully functional with mock Portia SDK

**Everything is ready for an impressive hackathon demo! 🏆**