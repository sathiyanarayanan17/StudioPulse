export type AgentStatus = 'idle' | 'monitoring' | 'diagnosing' | 'remediating' | 'verifying' | 'resolved';

export type SeverityLevel = 'critical' | 'high' | 'medium' | 'low';

export type AgentRole = 'Monitor' | 'Diagnose' | 'Remediate' | 'Gemini' | 'Grafana' | 'System';

export interface RenderNode {
  id: string;
  name: string;
  gpuModel: string;
  gpuLoad: number; // percentage
  vramUsedGB: number;
  vramTotalGB: number;
  tempC: number;
  status: 'healthy' | 'warning' | 'critical' | 'recovering';
  currentJob: string;
  fps: number;
}

export interface MetricPoint {
  time: string;
  gpuUtil: number;
  vramUtil: number;
  queueDepth: number;
  diskIoRate: number;
  frameLatencyMs: number;
}

export interface Incident {
  id: string;
  title: string;
  scenarioId: string;
  severity: SeverityLevel;
  timestamp: string;
  resolvedAt?: string;
  durationSec: number;
  affectedResource: string;
  rootCause: string;
  geminiConfidence: number;
  contributingFactors: string[];
  remediationPlan: string[];
  executionSteps: {
    name: string;
    target: string;
    action: string;
    status: 'pending' | 'executing' | 'completed' | 'failed';
    durationMs: number;
  }[];
  beforeMetrics: {
    gpuLoad: number;
    vramGB: number;
    queueBacklog: number;
    errorRate: number;
  };
  afterMetrics: {
    gpuLoad: number;
    vramGB: number;
    queueBacklog: number;
    errorRate: number;
  };
  grafanaAnnotationId: string;
  status: 'active' | 'mitigating' | 'resolved';
}

export interface FailureScenario {
  id: string;
  name: string;
  category: 'GPU_VRAM' | 'QUEUE_STALL' | 'DISK_PRESSURE' | 'NODE_OOM' | 'STORAGE_LOCK';
  badge: string;
  description: string;
  affectedNodeId: string;
  expectedTtrSec: number;
  promptSnippet: string;
  diagnosisOutput: {
    summary: string;
    confidence: number;
    factors: string[];
    remedy: string[];
  };
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: 'INFO' | 'WARN' | 'ERROR' | 'SUCCESS' | 'AGENT';
  agent: AgentRole;
  message: string;
  details?: string;
  codeSnippet?: string;
}

export interface BenchmarkComparison {
  phase: string;
  manualTimeMin: number;
  autonomousTimeSec: number;
  manualDesc: string;
  autonomousDesc: string;
}

export interface EngineThroughput {
  engine: string;
  avgFrameSec: number;
  throughputFph: number;
  activeNodes: number;
  efficiency: number;
  color: string;
}

export interface QueueWorkload {
  layer: string;
  queued: number;
  processing: number;
  completed: number;
  priority: 'P0' | 'P1' | 'P2';
}
