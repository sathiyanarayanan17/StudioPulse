# StudioPulse AI - Architecture

## System Overview

StudioPulse AI is a multi-agent autonomous system designed to monitor, diagnose, and self-heal media rendering pipelines in real-time.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                      STUDIOPULSE AI PLATFORM                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                   AGENT ORCHESTRATOR                        │  │
│  │                                                            │  │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────────────┐   │  │
│  │  │ MONITOR  │───▶│ DIAGNOSE │───▶│   REMEDIATE      │   │  │
│  │  │  AGENT   │    │  AGENT   │    │    AGENT         │   │  │
│  │  └──────────┘    └──────────┘    └──────────────────┘   │  │
│  │       │                │                  │               │  │
│  └───────┼────────────────┼──────────────────┼───────────────┘  │
│          │                │                  │                    │
│  ────────┼────────────────┼──────────────────┼────────────────── │
│          ▼                ▼                  ▼                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              INTEGRATION LAYER                            │   │
│  │                                                           │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │   │
│  │  │  Grafana    │  │   Gemini     │  │   GKE/GCE     │  │   │
│  │  │  Client     │  │   (Vertex)   │  │   Operations  │  │   │
│  │  └─────────────┘  └──────────────┘  └───────────────┘  │   │
│  │                                                           │   │
│  │  ┌─────────────┐  ┌──────────────┐                     │   │
│  │  │   Cloud     │  │   API        │                     │   │
│  │  │  Monitoring │  │   Server     │                     │   │
│  │  └─────────────┘  └──────────────┘                     │   │
│  │                                                           │   │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
                         │           │            │
                         ▼           ▼            ▼
              ┌──────────────┐ ┌──────────┐ ┌──────────────┐
              │   Grafana    │ │  Google  │ │     GKE      │
              │    Cloud     │ │  Cloud   │ │   Cluster    │
              │  (Alerts &   │ │  Vertex  │ │  (Render     │
              │   Metrics)   │ │    AI    │ │   Pipeline)  │
              └──────────────┘ └──────────┘ └──────────────┘
```

## Agent Descriptions

### 1. Monitor Agent
- **Role:** Sentinel - continuously watches for anomalies
- **Input:** Grafana alert API (polling)
- **Output:** Processed, categorized alerts fed to Diagnose Agent
- **Capabilities:**
  - Polls Grafana every N seconds for firing alerts
  - Categorizes alerts (GPU, memory, queue, disk, node, render)
  - Deduplicates (doesn't re-trigger on already-seen alerts)
  - Prioritizes by severity (critical → warning → info)

### 2. Diagnose Agent
- **Role:** Detective - correlates signals and finds root cause
- **Input:** Processed alert from Monitor Agent
- **Output:** Structured diagnosis with root cause and recommendations
- **Capabilities:**
  - Fetches correlated metrics from Grafana dashboards
  - Queries Google Cloud Monitoring for GKE-level metrics
  - Sends combined context to Gemini for AI-powered root cause analysis
  - Returns confidence-scored diagnosis

### 3. Remediate Agent
- **Role:** Surgeon - plans and executes fixes
- **Input:** Diagnosis from Diagnose Agent
- **Output:** Executed remediation with verification
- **Capabilities:**
  - Uses Gemini to plan remediation steps from available actions
  - Executes GKE operations (scale, restart, resize, drain)
  - Waits for stabilization period
  - Verifies resolution via post-fix metric comparison
  - Creates Grafana annotations for audit trail

## Data Flow

```
1. Grafana fires alert (GPU > 95%)
        │
2. Monitor Agent detects new alert
        │
3. Alert categorized as "gpu_saturation", severity "critical"
        │
4. Diagnose Agent activated
        │
5. Correlated metrics fetched:
   - GPU utilization: 97.5%
   - GPU memory: 92%
   - Render queue: 45 jobs
   - Frame time: 85s (normal: 12s)
        │
6. Context sent to Gemini for analysis
        │
7. Gemini returns: "Concurrent 8K renders exceeding 3-node GPU pool"
   Confidence: 0.92
   Recommendation: Scale GPU node pool to 5
        │
8. Remediate Agent plans execution:
   Step 1: scale_node_pool(target_size=5)
        │
9. GKE API called → node pool scaling initiated
        │
10. Wait 30s for stabilization
        │
11. Post-fix metrics checked:
    - GPU utilization: 62% ✓
    - Queue depth: 12 ✓
    - Frame time: 15s ✓
        │
12. Gemini verifies: "Resolved" (confidence: 0.93)
        │
13. Grafana annotation created for audit trail
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| AI Reasoning | Google Gemini 2.0 (via Vertex AI) | Root cause analysis, planning, verification |
| Agent Platform | Google Cloud Agent Builder | Agent orchestration |
| Observability | Grafana Cloud | Alerts, metrics, dashboards |
| Compute | Google Kubernetes Engine (GKE) | Render pipeline infrastructure |
| Monitoring | Google Cloud Monitoring | GKE/Compute metrics |
| API | aiohttp | REST API for dashboard |
| Language | Python 3.11 (async) | All components |
| Containerization | Docker | Deployment packaging |
| IaC | Terraform | Infrastructure provisioning |

## Deployment Options

### Local Demo (No credentials needed)
```bash
python -m src.demo
# Dashboard at http://localhost:8080
```

### Production (Google Cloud)
```bash
# Deploy to Cloud Run
gcloud run deploy studiopulse-ai \
  --source . \
  --region us-central1 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=my-project"
```

## Security Considerations

- All actions are audit-logged via Grafana annotations
- Remediation actions have a configurable allowlist
- Dangerous operations (cluster deletion) are permanently blocked
- Gemini confidence threshold must be met before auto-remediation
- Human escalation path for low-confidence diagnoses
