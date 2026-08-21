import { useState, useEffect, useCallback, useRef } from 'react';
import { RenderNode, Incident, FailureScenario, LogEntry, AgentStatus } from '../types';
import { INITIAL_NODES, FAILURE_SCENARIOS, INITIAL_LOGS } from '../mock/simulationData';

export function useSimulationEngine() {
  const [nodes, setNodes] = useState<RenderNode[]>(INITIAL_NODES);
  const [activeIncident, setActiveIncident] = useState<Incident | null>(null);
  const [incidentHistory, setIncidentHistory] = useState<Incident[]>([]);
  const [activeScenario, setActiveScenario] = useState<FailureScenario | null>(null);

  const [agentStep, setAgentStep] = useState<'IDLE' | 'MONITOR' | 'DIAGNOSE' | 'REMEDIATE' | 'VERIFY' | 'RESOLVED'>('IDLE');
  const [monitorState, setMonitorState] = useState<'monitoring' | 'alert_fired' | 'idle'>('monitoring');
  const [diagnoseState, setDiagnoseState] = useState<'idle' | 'correlating' | 'analyzing' | 'completed'>('idle');
  const [remediateState, setRemediateState] = useState<'idle' | 'planning' | 'executing' | 'verifying' | 'completed'>('idle');

  const [geminiPrompt, setGeminiPrompt] = useState<string>('');
  const [geminiResponse, setGeminiResponse] = useState<any>(null);
  const [logs, setLogs] = useState<LogEntry[]>(INITIAL_LOGS);
  const [isAutoSimulating, setIsAutoSimulating] = useState<boolean>(true);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>('node-03');
  const [metricsCount, setMetricsCount] = useState({
    resolvedCount: 38,
    framesProcessed: 14820,
    avgTtrSeconds: 84.2,
    clusterHealth: 99.8
  });

  const timeoutsRef = useRef<number[]>([]);

  const addLog = useCallback((agent: LogEntry['agent'], level: LogEntry['level'], message: string, details?: string, codeSnippet?: string) => {
    const newEntry: LogEntry = {
      id: 'log-' + Date.now() + '-' + Math.random().toString(36).substr(2, 4),
      timestamp: new Date().toTimeString().split(' ')[0],
      agent,
      level,
      message,
      details,
      codeSnippet
    };
    setLogs(prev => [newEntry, ...prev.slice(0, 150)]);
  }, []);

  const clearAllTimeouts = useCallback(() => {
    timeoutsRef.current.forEach(t => clearTimeout(t));
    timeoutsRef.current = [];
  }, []);

  // Background subtle telemetry jitter for realism
  useEffect(() => {
    if (!isAutoSimulating) return;

    const interval = setInterval(() => {
      setNodes(prev => prev.map(node => {
        if (activeIncident && node.id === activeIncident.affectedResource && activeIncident.status !== 'resolved') {
          return node;
        }
        const deltaLoad = (Math.random() * 4 - 2);
        const newLoad = Math.min(92, Math.max(35, Math.round(node.gpuLoad + deltaLoad)));
        const deltaTemp = (Math.random() * 1.5 - 0.75);
        const newTemp = Math.min(78, Math.max(52, Math.round(node.tempC + deltaTemp)));
        const deltaFps = (Math.random() * 0.4 - 0.2);
        const newFps = Math.max(1.5, Number((node.fps + deltaFps).toFixed(1)));

        return {
          ...node,
          gpuLoad: newLoad,
          tempC: newTemp,
          fps: newFps
        };
      }));

      setMetricsCount(prev => ({
        ...prev,
        framesProcessed: prev.framesProcessed + Math.floor(Math.random() * 4 + 2)
      }));
    }, 2800);

    return () => clearInterval(interval);
  }, [isAutoSimulating, activeIncident]);

  // Trigger a Failure Scenario
  const triggerScenario = useCallback((scenarioId: string) => {
    clearAllTimeouts();
    const scenario = FAILURE_SCENARIOS.find(s => s.id === scenarioId) || FAILURE_SCENARIOS[0];
    setActiveScenario(scenario);

    // 1. Immediately inject fault into affected node
    setNodes(prev => prev.map(n => {
      if (n.id === scenario.affectedNodeId) {
        return {
          ...n,
          gpuLoad: 99,
          vramUsedGB: n.vramTotalGB * 0.98,
          tempC: 88,
          status: 'critical',
          fps: 0.2
        };
      }
      return n;
    }));

    const incidentId = 'INC-' + Math.floor(1000 + Math.random() * 9000);
    const newIncident: Incident = {
      id: incidentId,
      title: scenario.name,
      scenarioId: scenario.id,
      severity: 'critical',
      timestamp: new Date().toTimeString().split(' ')[0],
      durationSec: 0,
      affectedResource: scenario.affectedNodeId,
      rootCause: scenario.diagnosisOutput.summary,
      geminiConfidence: scenario.diagnosisOutput.confidence,
      contributingFactors: scenario.diagnosisOutput.factors,
      remediationPlan: scenario.diagnosisOutput.remedy,
      executionSteps: scenario.diagnosisOutput.remedy.map((step, idx) => ({
        name: 'Step ' + (idx + 1) + ': ' + step.split(' ')[0] + ' ' + (step.split(' ')[1] || ''),
        target: scenario.affectedNodeId,
        action: step,
        status: 'pending',
        durationMs: 800 + idx * 400
      })),
      beforeMetrics: {
        gpuLoad: 99,
        vramGB: 78.8,
        queueBacklog: 1420,
        errorRate: 34.2
      },
      afterMetrics: {
        gpuLoad: 64,
        vramGB: 42.0,
        queueBacklog: 45,
        errorRate: 0.0
      },
      grafanaAnnotationId: 'grafana-ann-' + Date.now(),
      status: 'active'
    };

    setActiveIncident(newIncident);
    setAgentStep('MONITOR');
    setMonitorState('alert_fired');
    setDiagnoseState('idle');
    setRemediateState('idle');

    addLog('System', 'WARN', 'SIMULATION FAULT INJECTED: ' + scenario.name + ' on ' + scenario.affectedNodeId, scenario.description);

    // STEP 1: Monitor Agent detects alert (1.2s)
    const t1 = window.setTimeout(() => {
      addLog('Monitor', 'ERROR', 'Grafana Cloud Alert Fired: ' + scenario.badge + ' on ' + scenario.affectedNodeId, 'Alert Rule: Alerting on metric threshold > 95% for 3 consecutive poll cycles.');
      setAgentStep('DIAGNOSE');
      setDiagnoseState('correlating');
    }, 1200);

    // STEP 2: Diagnose Agent pulls metrics & formats Gemini 2.0 prompt (2.8s)
    const t2 = window.setTimeout(() => {
      const constructedPrompt = `System: You are StudioPulse AI Root Cause Diagnostic Agent.
Analyze firing Grafana Alert on VFX Render Cluster.

Context Metrics:
- Target Node: ${scenario.affectedNodeId}
- GPU Model: NVIDIA H100 SXM5
- GPU Compute Load: 99.4%
- VRAM Saturation: 98.6% (78.8 GB / 80 GB)
- Node Thermal Junction: 88.0 C
- Frame Rate Degradation: 0.2 fps (down from 8.6 fps)
- Queue Backlog: 1,420 pending EXR layers

Analyze the anomaly, determine root cause, compute confidence score, and output ranked safe remediation commands.`;

      setGeminiPrompt(constructedPrompt);
      setDiagnoseState('analyzing');
      addLog('Diagnose', 'AGENT', 'Aggregated 14 correlated timeseries metrics from Grafana. Prompt dispatched to Google Gemini 2.0 on Vertex AI.');
    }, 2800);

    // STEP 3: Gemini 2.0 returns structured diagnosis (5.2s)
    const t3 = window.setTimeout(() => {
      const structuredGeminiJson = {
        model: 'vertex-ai/gemini-2.0-flash',
        confidenceScore: scenario.diagnosisOutput.confidence,
        rootCauseSummary: scenario.diagnosisOutput.summary,
        contributingFactors: scenario.diagnosisOutput.factors,
        recommendedActionPlan: scenario.diagnosisOutput.remedy,
        safetyValidation: 'Passed: 100% allowlist compliant, zero destructive operations.'
      };

      setGeminiResponse(structuredGeminiJson);
      setDiagnoseState('completed');
      addLog('Gemini', 'SUCCESS', 'Gemini 2.0 Root Cause Analysis Completed with ' + scenario.diagnosisOutput.confidence + '% confidence score.', scenario.diagnosisOutput.summary);
      setAgentStep('REMEDIATE');
      setRemediateState('planning');
    }, 5200);

    // STEP 4: Remediate Agent begins execution (7.2s)
    const t4 = window.setTimeout(() => {
      setRemediateState('executing');
      addLog('Remediate', 'AGENT', 'Executing Step 1/3: ' + scenario.diagnosisOutput.remedy[0]);

      setActiveIncident(prev => {
        if (!prev) return prev;
        const updatedSteps = [...prev.executionSteps];
        if (updatedSteps[0]) updatedSteps[0].status = 'completed';
        if (updatedSteps[1]) updatedSteps[1].status = 'executing';
        return { ...prev, executionSteps: updatedSteps };
      });

      setNodes(prev => prev.map(n => {
        if (n.id === scenario.affectedNodeId) {
          return { ...n, status: 'recovering', tempC: 76, gpuLoad: 84 };
        }
        return n;
      }));
    }, 7200);

    // STEP 5: Execution Step 2 & 3 (9.2s)
    const t5 = window.setTimeout(() => {
      addLog('Remediate', 'AGENT', 'Executing Step 2/3 and 3/3: ' + scenario.diagnosisOutput.remedy[1]);

      setActiveIncident(prev => {
        if (!prev) return prev;
        const updatedSteps = prev.executionSteps.map(s => ({ ...s, status: 'completed' as const }));
        return { ...prev, executionSteps: updatedSteps };
      });

      setNodes(prev => prev.map(n => {
        if (n.id === scenario.affectedNodeId) {
          return { ...n, status: 'healthy', tempC: 63, gpuLoad: 65, vramUsedGB: 48.0, fps: 7.8 };
        }
        return n;
      }));
      setAgentStep('VERIFY');
      setRemediateState('verifying');
    }, 9200);

    // STEP 6: Gemini verification & Grafana Annotation creation (11.0s)
    const t6 = window.setTimeout(() => {
      addLog('Gemini', 'SUCCESS', 'Verification Pass: Before vs After metric comparison confirms healthy stabilization. Cluster IOPS and VRAM normal.');
      addLog('Grafana', 'SUCCESS', 'Audit Trail Created: Grafana Cloud Annotation #ann-' + Date.now().toString().slice(-6) + ' tagged with incident resolution metadata.');

      setActiveIncident(prev => {
        if (!prev) return prev;
        const resolved: Incident = {
          ...prev,
          status: 'resolved',
          resolvedAt: new Date().toTimeString().split(' ')[0],
          durationSec: scenario.expectedTtrSec
        };
        setIncidentHistory(h => [resolved, ...h]);
        return resolved;
      });

      setMetricsCount(prev => ({
        ...prev,
        resolvedCount: prev.resolvedCount + 1,
        clusterHealth: 99.9
      }));

      setAgentStep('RESOLVED');
      setMonitorState('monitoring');
      setDiagnoseState('idle');
      setRemediateState('completed');
    }, 11000);

    timeoutsRef.current = [t1, t2, t3, t4, t5, t6];
  }, [clearAllTimeouts, addLog]);

  const resetSimulation = useCallback(() => {
    clearAllTimeouts();
    setNodes(INITIAL_NODES);
    setActiveIncident(null);
    setActiveScenario(null);
    setAgentStep('IDLE');
    setMonitorState('monitoring');
    setDiagnoseState('idle');
    setRemediateState('idle');
    setGeminiPrompt('');
    setGeminiResponse(null);
    addLog('System', 'INFO', 'Render cluster simulation reset to default baseline.');
  }, [clearAllTimeouts, addLog]);

  return {
    nodes,
    activeIncident,
    incidentHistory,
    activeScenario,
    agentStep,
    monitorState,
    diagnoseState,
    remediateState,
    geminiPrompt,
    geminiResponse,
    logs,
    isAutoSimulating,
    setIsAutoSimulating,
    selectedNodeId,
    setSelectedNodeId,
    metricsCount,
    triggerScenario,
    resetSimulation,
    addLog
  };
}
