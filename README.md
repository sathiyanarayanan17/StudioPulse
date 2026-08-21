# 🎬 StudioPulse AI

> Autonomous AI agent that monitors, diagnoses, and self-heals media rendering pipelines using Gemini and Grafana in real-time.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Agent%20Builder-4285F4)](https://cloud.google.com)
[![Grafana](https://img.shields.io/badge/Grafana-Labs-F46800)](https://grafana.com)

---

## 🌟 Overview

StudioPulse AI is an **autonomous multi-agent system** built for media & entertainment production pipelines. It leverages **Google Cloud Agent Builder** with **Gemini Enterprise** and **Grafana Labs** observability to detect, diagnose, and auto-remediate rendering pipeline incidents — reducing mean time to resolution (MTTR) by up to 90%.

### The Problem

VFX and streaming studios run massive rendering pipelines on cloud infrastructure. When issues occur (GPU saturation, memory leaks, queue backlogs), manual diagnosis takes **30-60 minutes per incident**, causing missed deadlines and wasted compute costs.

### The Solution

StudioPulse AI deploys an autonomous agent crew that:
1. 🔍 **Monitors** — Watches Grafana dashboards for anomalies in real-time
2. 🧠 **Diagnoses** — Queries correlated metrics and uses Gemini AI for root cause analysis
3. ⚡ **Remediates** — Plans and executes corrective actions (scale nodes, restart jobs, etc.)
4. ✅ **Verifies** — Confirms resolution and generates incident reports
5. 📝 **Audits** — Creates Grafana annotations for full incident traceability

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      STUDIOPULSE AI PLATFORM                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                   AGENT ORCHESTRATOR                        │  │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────────────┐    │  │
│  │  │ MONITOR  │───▶│ DIAGNOSE │───▶│   REMEDIATE      │    │  │
│  │  │  AGENT   │    │  AGENT   │    │    AGENT         │    │  │
│  │  └──────────┘    └──────────┘    └──────────────────┘    │  │
│  └────────────────────────────────────────────────────────────┘  │
│          │                │                  │                     │
│  ┌───────▼────────────────▼──────────────────▼───────────────┐   │
│  │              INTEGRATION LAYER                             │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐ │   │
│  │  │Grafana  │  │ Gemini  │  │  Cloud  │  │ GKE/Compute │ │   │
│  │  │ API     │  │(Vertex) │  │Monitor  │  │  Operations │ │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────────┘ │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │   WEB DASHBOARD  (http://localhost:8080)                    │  │
│  │   Real-time metrics • Alert panel • Agent log • Demo ctrl  │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- (Optional) Google Cloud account for production mode
- (Optional) Grafana Cloud account for production mode

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/studiopulse-ai.git
cd studiopulse-ai

# Run setup script
# Windows:
scripts\setup.bat
# Linux/Mac:
chmod +x scripts/setup.sh && ./scripts/setup.sh
```

### 🎮 Demo Mode (No credentials needed!)

```bash
# Activate virtual environment
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Start the demo
python -m src.demo
```

Open **http://localhost:8080** to see the real-time dashboard. Click scenario buttons to trigger incidents and watch the agent pipeline respond.

### 🏭 Production Mode

```bash
# 1. Configure credentials
cp .env.example .env
# Edit .env with your Google Cloud and Grafana credentials

# 2. Set up Google Cloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable aiplatform.googleapis.com monitoring.googleapis.com

# 3. Run
python -m src.main
```

---

## 🎬 Demo Scenarios

The simulator includes 5 realistic failure scenarios:

| Scenario | Description | Auto-Fix Action |
|----------|-------------|-----------------|
| 🔥 GPU Saturation | 8K renders overwhelming GPU pool | Scale node pool |
| 💾 Memory Leak | Render workers leaking memory | Rolling restart |
| 📋 Queue Backlog | 200+ jobs pending, throughput low | Scale + reprioritize |
| 💽 Disk Full | Output volume at 95% capacity | Resize disk |
| 🖥️ Node Failure | GPU node health check failed | Drain & replace |

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| AI Engine | **Google Gemini 2.0** (via Vertex AI) | Root cause analysis, remediation planning |
| Agent Platform | **Google Cloud Agent Builder** | Agent orchestration framework |
| Observability | **Grafana Labs** (Grafana Cloud) | Alerts, metrics, dashboards |
| Infrastructure | Google Kubernetes Engine (GKE) | Render pipeline compute |
| Monitoring | Google Cloud Monitoring | Infrastructure metrics |
| API Server | aiohttp | REST API + dashboard hosting |
| Language | Python 3.11 (async) | All components |
| IaC | Terraform | Infrastructure provisioning |
| Container | Docker | Deployment packaging |

---

## 📁 Project Structure

```
studiopulse-ai/
├── src/
│   ├── main.py                    # Production entry point
│   ├── demo.py                    # Demo mode (no credentials)
│   ├── agents/
│   │   ├── orchestrator.py        # Multi-agent coordinator
│   │   ├── monitor.py             # Alert detection agent
│   │   ├── diagnose.py            # Root cause analysis agent
│   │   └── remediate.py           # Auto-fix execution agent
│   ├── grafana/
│   │   ├── client.py              # Grafana API client
│   │   ├── alerts.py              # Alert processing & categorization
│   │   └── dashboards.py          # Metric queries (PromQL)
│   ├── cloud/
│   │   ├── vertex_ai.py           # Gemini integration
│   │   ├── monitoring.py          # Cloud Monitoring client
│   │   └── compute.py             # GKE/Compute operations
│   ├── simulator/
│   │   ├── __init__.py            # Pipeline simulator
│   │   ├── grafana_sim.py         # Simulated Grafana
│   │   └── compute_sim.py         # Simulated GKE operations
│   ├── api/
│   │   └── __init__.py            # REST API server
│   ├── dashboard/
│   │   └── index.html             # Web dashboard UI
│   └── utils/
│       ├── config.py              # Configuration loader
│       └── logger.py              # Structured logging
├── config/
│   └── agents.yaml                # Agent behavior config
├── infra/
│   └── main.tf                    # Terraform IaC
├── scripts/
│   ├── setup.bat                  # Windows setup
│   ├── setup.sh                   # Linux/Mac setup
│   └── deploy.bat                 # Cloud Run deployment
├── tests/
│   ├── test_monitor.py
│   ├── test_diagnose.py
│   └── test_remediate.py
├── docs/
│   └── architecture.md            # Detailed architecture doc
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
├── LICENSE                         # MIT License
└── README.md
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_monitor.py -v
```

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web dashboard |
| GET | `/api/health` | Health check |
| GET | `/api/metrics` | Current pipeline metrics |
| GET | `/api/alerts` | Active alerts |
| GET | `/api/jobs` | Render job status |
| GET | `/api/incidents` | Incident history |
| GET | `/api/status` | Orchestrator status |
| POST | `/api/trigger` | Trigger demo scenario |

---

## 🚢 Deployment

### Docker

```bash
docker build -t studiopulse-ai .
docker run -p 8080:8080 --env-file .env studiopulse-ai
```

### Google Cloud Run

```bash
scripts\deploy.bat
```

### Terraform (Full Infrastructure)

```bash
cd infra
terraform init
terraform plan -var="project_id=YOUR_PROJECT_ID"
terraform apply -var="project_id=YOUR_PROJECT_ID"
```

---

## 🎥 Demo Video

[Watch the 3-minute demo](https://youtube.com/YOUR_VIDEO_LINK)

---

## 🏆 Built For

**Google Cloud Summer Blockbuster Hackathon 2026**
- Track: Grafana Labs
- Partner Integration: Grafana Cloud (Alerts, Metrics, Dashboards, Annotations API)
- AI: Google Gemini Enterprise via Vertex AI + Agent Builder

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Sathiyanarayanan S**

---

## 🙏 Acknowledgments

- Google Cloud Agent Builder & Gemini Enterprise
- Grafana Labs for observability platform and APIs
- Google Cloud Summer Blockbuster Hackathon 2026
