import { FailureScenario, RenderNode, BenchmarkComparison, EngineThroughput, QueueWorkload, LogEntry } from '../types';

export const INITIAL_NODES: RenderNode[] = [
  {
    id: 'node-01',
    name: 'GKE-GPU-NODE-01',
    gpuModel: 'NVIDIA H100 SXM5 80GB',
    gpuLoad: 68,
    vramUsedGB: 54.2,
    vramTotalGB: 80,
    tempC: 62,
    status: 'healthy',
    currentJob: 'Shot_104_Comp_v03 [Arnold 8K]',
    fps: 4.8
  },
  {
    id: 'node-02',
    name: 'GKE-GPU-NODE-02',
    gpuModel: 'NVIDIA H100 SXM5 80GB',
    gpuLoad: 74,
    vramUsedGB: 59.8,
    vramTotalGB: 80,
    tempC: 65,
    status: 'healthy',
    currentJob: 'Scene_Hero_Battle_04 [Unreal Engine 5]',
    fps: 12.4
  },
  {
    id: 'node-03',
    name: 'GKE-GPU-NODE-03',
    gpuModel: 'NVIDIA A100 Tensor Core 80GB',
    gpuLoad: 82,
    vramUsedGB: 66.4,
    vramTotalGB: 80,
    tempC: 71,
    status: 'healthy',
    currentJob: 'FX_Explosion_Pyro_Layer [Houdini Karma]',
    fps: 3.2
  },
  {
    id: 'node-04',
    name: 'GKE-GPU-NODE-04',
    gpuModel: 'NVIDIA A100 Tensor Core 80GB',
    gpuLoad: 45,
    vramUsedGB: 38.1,
    vramTotalGB: 80,
    tempC: 58,
    status: 'healthy',
    currentJob: 'Env_CyberCity_Denoise [Redshift]',
    fps: 8.6
  },
  {
    id: 'node-05',
    name: 'GKE-GPU-NODE-05',
    gpuModel: 'NVIDIA RTX 4090 24GB',
    gpuLoad: 63,
    vramUsedGB: 16.8,
    vramTotalGB: 24,
    tempC: 64,
    status: 'healthy',
    currentJob: 'LookDev_Character_Turn [Blender Cycles]',
    fps: 6.1
  },
  {
    id: 'node-06',
    name: 'GKE-GPU-NODE-06',
    gpuModel: 'NVIDIA RTX 4090 24GB',
    gpuLoad: 58,
    vramUsedGB: 15.2,
    vramTotalGB: 24,
    tempC: 61,
    status: 'healthy',
    currentJob: 'Background_Matte_Pass [Octane Render]',
    fps: 9.4
  },
  {
    id: 'node-07',
    name: 'GKE-GPU-NODE-07',
    gpuModel: 'NVIDIA A100 Tensor Core 80GB',
    gpuLoad: 71,
    vramUsedGB: 58.0,
    vramTotalGB: 80,
    tempC: 67,
    status: 'healthy',
    currentJob: 'Crowd_Sim_Frame_2000 [Arnold 8K]',
    fps: 5.0
  },
  {
    id: 'node-08',
    name: 'GKE-GPU-NODE-08',
    gpuModel: 'NVIDIA H100 SXM5 80GB',
    gpuLoad: 52,
    vramUsedGB: 41.5,
    vramTotalGB: 80,
    tempC: 59,
    status: 'healthy',
    currentJob: 'Lighting_Interior_Pass [Redshift]',
    fps: 11.2
  }
];

export const FAILURE_SCENARIOS: FailureScenario[] = [
  {
    id: 'scenario-gpu-leak',
    name: 'GPU VRAM Leak & Thermal Saturation',
    category: 'GPU_VRAM',
    badge: 'GPU CLUSTER CRITICAL',
    description: 'Unbounded Arnold 8K texture buffer allocation on GKE-GPU-NODE-03 causes 99.2% VRAM pressure and thermal throttling at 88C.',
    affectedNodeId: 'node-03',
    expectedTtrSec: 85,
    promptSnippet: 'Analyze firing Grafana Alert: GPU_MEMORY_EXHAUSTION_CRITICAL on node GKE-GPU-NODE-03. Correlate with temperature metrics (88C) and frame drop velocity.',
    diagnosisOutput: {
      summary: 'Texture buffer heap leak in Arnold 8K worker process causing severe VRAM fragmentation and GPU hardware throttling.',
      confidence: 98.8,
      factors: [
        'Texture cache pool size exceeded hard limit of 64GB',
        'Frame render time surged from 3.2s to 48.6s (1418% increase)',
        'Thermal junction reached 88C trigger point on Node-03'
      ],
      remedy: [
        'Drain active render pod on GKE-GPU-NODE-03 safely',
        'Trigger graceful rolling restart of Arnold worker daemonset',
        'Auto-scale temporary overflow worker on GKE node pool to avoid queue drop'
      ]
    }
  },
  {
    id: 'scenario-queue-jam',
    name: '4K EXR Compositing Queue Jam',
    category: 'QUEUE_STALL',
    badge: 'PIPELINE BACKLOG',
    description: 'Cryptomatte extraction passes accumulating in Redis queue faster than worker consumption rate. Queue depth reaches 1,420 items.',
    affectedNodeId: 'node-01',
    expectedTtrSec: 62,
    promptSnippet: 'Grafana Alert: QUEUE_CONSUMPTION_RATE_DEFICIT on pipeline /vfx/shots/blockbuster/seq04. Queue depth increased 340% over 5 minutes.',
    diagnosisOutput: {
      summary: 'Worker pool starvation: Ingest throughput exceeds single-node processing throughput due to uncompressed multi-layer EXR stream.',
      confidence: 97.4,
      factors: [
        'Queue ingress rate: 84 frames/min vs egress rate: 22 frames/min',
        'Memory bandwidth saturation on compositing worker group',
        'Worker thread locking during Cryptomatte manifest parsing'
      ],
      remedy: [
        'Auto-scale GKE Horizontal Pod Autoscaler (HPA) replicas from 4 to 12',
        'Switch batch ingestion policy to parallel chunked decompression',
        'Verify queue drain rate reaches >110 frames/min'
      ]
    }
  },
  {
    id: 'scenario-nvme-saturation',
    name: 'NVMe Scratch Cache Capacity Breach',
    category: 'DISK_PRESSURE',
    badge: 'STORAGE SATURATION',
    description: 'Local NVMe scratch disk on GKE-GPU-NODE-04 reached 97.8% utilization due to unpruned Houdini pyro simulation caches.',
    affectedNodeId: 'node-04',
    expectedTtrSec: 45,
    promptSnippet: 'Grafana Alert: DISK_VOLUME_EXHAUSTION_PREDICTED. Local scratch mount /mnt/scratch at 97.8% capacity with write freeze imminent.',
    diagnosisOutput: {
      summary: 'Pyro VDB cache volume leak: Houdini temporary voxel buffers not purged after frame handoff to compositing stage.',
      confidence: 99.2,
      factors: [
        'Available scratch disk space dropped below 8.2 GB safety threshold',
        'Write I/O latency surged to 420ms causing pipeline lockup',
        'Zero disk space head-room detected for next frame simulation'
      ],
      remedy: [
        'Execute automated disk cleanup utility for orphaned .vdb scratch buffers',
        'Trigger Google Cloud Persistent Disk dynamic volume expansion (+200GB)',
        'Verify write throughput stabilizes under 12ms latency'
      ]
    }
  },
  {
    id: 'scenario-node-oom',
    name: 'Unreal Engine 5 Worker Kernel Panic & OOM',
    category: 'NODE_OOM',
    badge: 'NODE CRASH',
    description: 'Niagara particle simulation memory spike triggers Linux kernel OOM killer on GKE-GPU-NODE-02, crashing worker pod.',
    affectedNodeId: 'node-02',
    expectedTtrSec: 92,
    promptSnippet: 'Grafana Alert: KUBERNETES_POD_CRASH_LOOP_BACKOFF and OOMKILLED event on namespace render-farm / pod ue5-worker-8f9a.',
    diagnosisOutput: {
      summary: 'Kernel OOM Killer invoked on Niagara simulation engine when particle buffer exceeded 128GB node memory ceiling.',
      confidence: 96.5,
      factors: [
        'Memory consumption spiked to 100% in 12 seconds',
        'Render worker process terminated with SIGKILL (Exit Code 137)',
        'Unfinished frame 1042 state orphaned in memory'
      ],
      remedy: [
        'Isolate corrupted frame 1042 parameters and re-queue with sub-sampling',
        'Cordon and drain unhealthy node GKE-GPU-NODE-02',
        'Provision replacement GKE node instance and restart worker container'
      ]
    }
  },
  {
    id: 'scenario-storage-lock',
    name: 'Distributed Asset Storage NFS Deadlock',
    category: 'STORAGE_LOCK',
    badge: 'ASSET IO DEADLOCK',
    description: 'Shared NFS asset storage client connection pool saturated, causing frame render locks across multiple cluster nodes.',
    affectedNodeId: 'node-07',
    expectedTtrSec: 78,
    promptSnippet: 'Grafana Alert: STORAGE_IOPS_THROTTLED and NFS_RPC_TIMEOUT_BURST on filestore-vfx-assets cluster mount.',
    diagnosisOutput: {
      summary: 'NFS RPC connection table deadlock caused by simultaneous asset texture fetches across 64 parallel threads.',
      confidence: 95.8,
      factors: [
        'NFS client pending RPC calls exceeded 2048 queue capacity',
        'Asset fetch latency increased from 4ms to 3,800ms',
        'Multiple GPU nodes idling while awaiting raw geometry buffers'
      ],
      remedy: [
        'Reset and flush stale NFS client lock tables on affected nodes',
        'Activate distributed local SSD caching proxy layer (Cloud Filestore High-Scale)',
        'Confirm IOPS recovery to >45,000 read IOPS'
      ]
    }
  }
];

export const BENCHMARK_COMPARISONS: BenchmarkComparison[] = [
  {
    phase: 'Alert Triage & Detection',
    manualTimeMin: 8.5,
    autonomousTimeSec: 4.2,
    manualDesc: 'Human on-call engineer notices Slack alert, logs into Grafana dashboard, filters noise',
    autonomousDesc: 'Monitor Agent polls Grafana Cloud API continuously (2.5s cadence) with zero latency'
  },
  {
    phase: 'Multi-Metric Correlation',
    manualTimeMin: 14.0,
    autonomousTimeSec: 18.5,
    manualDesc: 'Manual inspection across GPU, VRAM, I/O, and Kubernetes logs to connect symptoms',
    autonomousDesc: 'Diagnose Agent aggregates correlated timeseries metrics into structured contextual payload'
  },
  {
    phase: 'Root Cause Reasoning',
    manualTimeMin: 16.5,
    autonomousTimeSec: 24.0,
    manualDesc: 'Engineers debate cause in incident bridge, test hypotheses, search runbooks',
    autonomousDesc: 'Google Gemini 2.0 generates structured root cause, confidence score, and remediation plan'
  },
  {
    phase: 'Remediation & Verification',
    manualTimeMin: 13.0,
    autonomousTimeSec: 42.0,
    manualDesc: 'Manual kubectl commands, cloud console scaling, waiting and watching dashboards',
    autonomousDesc: 'Remediate Agent runs safe allowlisted GKE/Cloud APIs and verifies before vs after metrics'
  }
];

export const ENGINE_THROUGHPUTS: EngineThroughput[] = [
  {
    engine: 'Unreal Engine 5 (Lumen/Nanite)',
    avgFrameSec: 2.4,
    throughputFph: 1500,
    activeNodes: 14,
    efficiency: 98.2,
    color: '#00f0ff'
  },
  {
    engine: 'Arnold 8K Raytracing',
    avgFrameSec: 18.6,
    throughputFph: 194,
    activeNodes: 28,
    efficiency: 94.6,
    color: '#a855f7'
  },
  {
    engine: 'Redshift GPU Photoreal',
    avgFrameSec: 6.2,
    throughputFph: 580,
    activeNodes: 18,
    efficiency: 96.8,
    color: '#00e676'
  },
  {
    engine: 'Octane Render 2026',
    avgFrameSec: 4.8,
    throughputFph: 750,
    activeNodes: 12,
    efficiency: 97.4,
    color: '#ffb703'
  },
  {
    engine: 'Blender Cycles X',
    avgFrameSec: 7.9,
    throughputFph: 456,
    activeNodes: 8,
    efficiency: 95.1,
    color: '#38bdf8'
  }
];

export const QUEUE_WORKLOADS: QueueWorkload[] = [
  { layer: '4K EXR Beauty Pass', queued: 340, processing: 96, completed: 1840, priority: 'P0' },
  { layer: 'Cryptomatte Manifests', queued: 180, processing: 48, completed: 1420, priority: 'P1' },
  { layer: 'Deep Volumetric FX', queued: 290, processing: 64, completed: 890, priority: 'P0' },
  { layer: 'Z-Depth & Motion Vectors', queued: 110, processing: 32, completed: 1980, priority: 'P2' },
  { layer: 'AI Denoising Passes', queued: 145, processing: 40, completed: 1650, priority: 'P1' }
];

export const INITIAL_LOGS: LogEntry[] = [
  {
    id: 'log-1',
    timestamp: '11:04:12',
    level: 'INFO',
    agent: 'System',
    message: 'StudioPulse AI autonomous cluster engine initialized. Connected to Grafana Cloud & Vertex AI.'
  },
  {
    id: 'log-2',
    timestamp: '11:05:30',
    level: 'AGENT',
    agent: 'Monitor',
    message: 'Sentinel poll cycle completed: 8 GKE GPU nodes active. 0 firing alerts across render clusters.'
  },
  {
    id: 'log-3',
    timestamp: '11:06:45',
    level: 'INFO',
    agent: 'Grafana',
    message: 'Dashboard timeseries stream healthy: GPU Load 64.2% | VRAM Usage 71.4% | Queue Backlog normal.'
  },
  {
    id: 'log-4',
    timestamp: '11:08:00',
    level: 'AGENT',
    agent: 'Diagnose',
    message: 'Gemini 2.0 telemetry model standby: Model vertex-ai/gemini-2.0-flash ready (p99 latency 420ms).'
  },
  {
    id: 'log-5',
    timestamp: '11:09:15',
    level: 'SUCCESS',
    agent: 'Remediate',
    message: 'Safe execution policy active: Allowlist verified. Destructive cluster commands permanently blocked.'
  }
];
