# DevOps Crisis Commander

**AgentHack 2025 Winner Project**

A multi-agent system for intelligent DevOps incident response using Portia AI SDK and Vue.js.

## 🎯 Project Overview

DevOps Crisis Commander automates incident detection, classification, resolution advisory, and post-mortem generation using coordinated AI agents.

### Architecture
- **Backend**: Python + Portia AI SDK + FastAPI
- **Frontend**: Vue.js + Pinia + WebSocket
- **Agents**: Incident Classifier, Resolution Advisor, Post-Mortem Generator

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 📊 Features

- ✅ Real-time incident detection & classification
- ✅ Intelligent resolution recommendations  
- ✅ Multi-agent workflow orchestration
- ✅ Post-incident documentation generation
- ✅ Interactive Vue.js dashboard
- ✅ WebSocket real-time updates

## 🏗️ Project Structure

```
devops-crisis-commander/
├── backend/                 # Python + Portia AI
│   ├── agents/             # Agent implementations
│   ├── models/             # Data models
│   ├── api/               # FastAPI routes
│   └── main.py           # Application entry
├── frontend/               # Vue.js dashboard
│   ├── src/
│   │   ├── components/    # Vue components
│   │   ├── stores/       # Pinia stores
│   │   └── views/        # Page views
│   └── package.json
└── docs/                   # Documentation
```

## 🔧 Development

This project demonstrates advanced multi-agent orchestration patterns using Portia AI's three-agent architecture:
1. **Planning Agent**: Creates incident response plans
2. **Execution Agent**: Executes resolution steps  
3. **Introspection Agent**: Monitors and validates progress

Built for AgentHack 2025 - showcasing the future of autonomous DevOps operations.
