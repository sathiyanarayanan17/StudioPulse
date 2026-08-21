import React from 'react';
import { Eye, Sparkles, ShieldCheck, AlertTriangle, Terminal } from 'lucide-react';
import { Incident, FailureScenario } from '../types';

interface AgentPipelineVisualizerProps {
  agentStep: 'IDLE' | 'MONITOR' | 'DIAGNOSE' | 'REMEDIATE' | 'VERIFY' | 'RESOLVED';
  monitorState: 'monitoring' | 'alert_fired' | 'idle';
  diagnoseState: 'idle' | 'correlating' | 'analyzing' | 'completed';
  remediateState: 'idle' | 'planning' | 'executing' | 'verifying' | 'completed';
  activeIncident: Incident | null;
  activeScenario: FailureScenario | null;
  onOpenDiagnosticModal: () => void;
}

export const AgentPipelineVisualizer: React.FC<AgentPipelineVisualizerProps> = ({
  agentStep,
  monitorState,
  diagnoseState,
  remediateState,
  activeIncident,
  activeScenario,
  onOpenDiagnosticModal
}) => {
  const isIncidentActive = activeIncident && activeIncident.status !== 'resolved';

  return (
    <div className="glass-panel rounded-2xl p-5 border border-[#1b273d] relative overflow-hidden">
      
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#182236]">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <h2 className="text-base font-bold font-sans text-white tracking-tight uppercase tracking-wider">
              Autonomous Multi-Agent Crew Orchestration
            </h2>
            <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
              3 Specialized Agents
            </span>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Clean separation of concerns: Monitor, Diagnose, and Remediate with Google Gemini 2.0 and Grafana Labs
          </p>
        </div>

        {isIncidentActive && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-rose-500/10 border border-rose-500/30 glow-rose animate-pulse">
            <AlertTriangle className="w-4 h-4 text-rose-400" />
            <span className="text-xs font-mono font-semibold text-rose-300">ACTIVE INCIDENT RESPONSE</span>
          </div>
        )}
      </div>

      {/* Agent Workflow Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 my-5">
        
        {/* AGENT 1: Sentinel Monitor Agent */}
        <div className={`p-4 rounded-xl border transition-all relative ${
          agentStep === 'MONITOR'
            ? 'bg-cyan-950/30 border-cyan-500/60 glow-cyan ring-1 ring-cyan-500/40'
            : 'bg-[#090d16] border-[#182338] hover:border-slate-700'
        }`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                <Eye className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white font-sans">Monitor Agent</h3>
                <span className="text-[10px] font-mono text-cyan-400">Sentinel Observer</span>
              </div>
            </div>
            <span className={`px-2 py-0.5 text-[10px] font-mono font-medium rounded ${
              monitorState === 'alert_fired'
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 animate-pulse'
                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
            }`}>
              {monitorState === 'alert_fired' ? 'ALERT FIRED' : 'POLLING GRAFANA'}
            </span>
          </div>

          <p className="text-xs text-slate-300 font-sans leading-relaxed mb-3">
            Continuously polls Grafana Cloud alert channels every 2.5s. Triages alerts by severity and categorizes GPU, VRAM, queue, disk, and node anomalies.
          </p>

          <div className="space-y-1.5 text-[11px] font-mono border-t border-[#162033] pt-2.5 text-slate-400">
            <div className="flex justify-between">
              <span>Poll Cadence:</span>
              <span className="text-slate-200">2,500 ms</span>
            </div>
            <div className="flex justify-between">
              <span>Grafana Endpoints:</span>
              <span className="text-cyan-400">/api/v1/alerts</span>
            </div>
            <div className="flex justify-between">
              <span>Noise Filter Rate:</span>
              <span className="text-emerald-400">100% Zero Noise</span>
            </div>
          </div>
        </div>

        {/* AGENT 2: Detective Diagnose Agent */}
        <div className={`p-4 rounded-xl border transition-all relative ${
          agentStep === 'DIAGNOSE'
            ? 'bg-violet-950/30 border-violet-500/60 glow-purple ring-1 ring-violet-500/40'
            : 'bg-[#090d16] border-[#182338] hover:border-slate-700'
        }`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-violet-500/10 border border-violet-500/30 flex items-center justify-center text-violet-400">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white font-sans">Diagnose Agent</h3>
                <span className="text-[10px] font-mono text-violet-400">Gemini 2.0 Detective</span>
              </div>
            </div>
            <span className={`px-2 py-0.5 text-[10px] font-mono font-medium rounded ${
              diagnoseState === 'analyzing'
                ? 'bg-violet-500/20 text-violet-300 border border-violet-500/40 animate-pulse'
                : diagnoseState === 'completed'
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : 'bg-slate-800 text-slate-400 border border-slate-700'
            }`}>
              {diagnoseState === 'analyzing' ? 'REASONING...' : diagnoseState === 'completed' ? 'DIAGNOSED 98.8%' : 'STANDBY'}
            </span>
          </div>

          <p className="text-xs text-slate-300 font-sans leading-relaxed mb-3">
            Aggregates cross-metric timeseries from Grafana dashboards, queries Google Gemini 2.0 on Vertex AI with structured prompt, and computes confidence scores.
          </p>

          <div className="space-y-1.5 text-[11px] font-mono border-t border-[#162033] pt-2.5 text-slate-400">
            <div className="flex justify-between">
              <span>Foundation Model:</span>
              <span className="text-violet-300">Gemini 2.0 Flash</span>
            </div>
            <div className="flex justify-between">
              <span>Confidence Scoring:</span>
              <span className="text-emerald-400">Active (90%+ threshold)</span>
            </div>
            <div className="flex justify-between">
              <span>Context Window:</span>
              <span className="text-slate-200">14 Metric Streams</span>
            </div>
          </div>
        </div>

        {/* AGENT 3: Surgeon Remediate Agent */}
        <div className={`p-4 rounded-xl border transition-all relative ${
          agentStep === 'REMEDIATE' || agentStep === 'VERIFY'
            ? 'bg-emerald-950/30 border-emerald-500/60 glow-emerald ring-1 ring-emerald-500/40'
            : 'bg-[#090d16] border-[#182338] hover:border-slate-700'
        }`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white font-sans">Remediate Agent</h3>
                <span className="text-[10px] font-mono text-emerald-400">Cloud Surgeon</span>
              </div>
            </div>
            <span className={`px-2 py-0.5 text-[10px] font-mono font-medium rounded ${
              remediateState === 'executing'
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 animate-pulse'
                : remediateState === 'completed'
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : 'bg-slate-800 text-slate-400 border border-slate-700'
            }`}>
              {remediateState === 'executing' ? 'EXECUTING FIX' : remediateState === 'completed' ? 'VERIFIED HEALTHY' : 'STANDBY'}
            </span>
          </div>

          <p className="text-xs text-slate-300 font-sans leading-relaxed mb-3">
            Executes safe allowlisted actions via GKE and Cloud APIs, validates stabilization with Gemini before-after metric verification, and logs Grafana audit annotations.
          </p>

          <div className="space-y-1.5 text-[11px] font-mono border-t border-[#162033] pt-2.5 text-slate-400">
            <div className="flex justify-between">
              <span>Allowlist Policy:</span>
              <span className="text-emerald-400">Enforced & Safe</span>
            </div>
            <div className="flex justify-between">
              <span>Target API:</span>
              <span className="text-slate-200">GKE / Cloud Compute</span>
            </div>
            <div className="flex justify-between">
              <span>Audit Trail:</span>
              <span className="text-amber-300">Grafana Annotations</span>
            </div>
          </div>
        </div>

      </div>

      {/* Stepper Progress Bar for Active Incident */}
      {isIncidentActive && (
        <div className="mt-4 pt-4 border-t border-[#182236] bg-[#070b13]/60 rounded-xl p-3.5 border border-[#162134]">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-white font-mono uppercase tracking-wider">
                Live Incident Flow:
              </span>
              <span className="text-xs font-mono text-cyan-300 font-semibold">
                {activeIncident.title}
              </span>
            </div>
            
            <button
              onClick={onOpenDiagnosticModal}
              className="inline-flex items-center gap-1 text-xs font-mono text-violet-300 hover:text-white bg-violet-500/10 hover:bg-violet-500/20 border border-violet-500/30 px-2.5 py-1 rounded transition-all cursor-pointer"
            >
              <Terminal className="w-3.5 h-3.5" />
              <span>View Structured Gemini Diagnostic Payload</span>
            </button>
          </div>

          {/* 5-step horizontal progression */}
          <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 text-center text-xs font-mono">
            <div className={`p-2 rounded border transition-all ${
              agentStep === 'MONITOR' || agentStep === 'DIAGNOSE' || agentStep === 'REMEDIATE' || agentStep === 'VERIFY' || agentStep === 'RESOLVED'
                ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-300'
                : 'bg-[#090d16] border-[#182338] text-slate-500'
            }`}>
              <div className="font-bold">1. Alert Fired</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Grafana Polled</div>
            </div>

            <div className={`p-2 rounded border transition-all ${
              agentStep === 'DIAGNOSE' || agentStep === 'REMEDIATE' || agentStep === 'VERIFY' || agentStep === 'RESOLVED'
                ? 'bg-violet-500/15 border-violet-500/40 text-violet-300'
                : 'bg-[#090d16] border-[#182338] text-slate-500'
            }`}>
              <div className="font-bold">2. Timeseries Pulled</div>
              <div className="text-[10px] text-slate-400 mt-0.5">14 Metrics Bound</div>
            </div>

            <div className={`p-2 rounded border transition-all ${
              agentStep === 'REMEDIATE' || agentStep === 'VERIFY' || agentStep === 'RESOLVED'
                ? 'bg-violet-500/20 border-violet-500/50 text-violet-200'
                : 'bg-[#090d16] border-[#182338] text-slate-500'
            }`}>
              <div className="font-bold">3. Gemini 2.0 Analysis</div>
              <div className="text-[10px] text-slate-400 mt-0.5">98.8% Confidence</div>
            </div>

            <div className={`p-2 rounded border transition-all ${
              agentStep === 'VERIFY' || agentStep === 'RESOLVED'
                ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300'
                : agentStep === 'REMEDIATE'
                ? 'bg-amber-500/15 border-amber-500/40 text-amber-300 animate-pulse'
                : 'bg-[#090d16] border-[#182338] text-slate-500'
            }`}>
              <div className="font-bold">4. Cloud Action</div>
              <div className="text-[10px] text-slate-400 mt-0.5">GKE Safe Rollout</div>
            </div>

            <div className={`p-2 rounded border transition-all ${
              agentStep === 'RESOLVED'
                ? 'bg-emerald-500/20 border-emerald-500/60 text-emerald-200 glow-emerald'
                : 'bg-[#090d16] border-[#182338] text-slate-500'
            }`}>
              <div className="font-bold">5. Audit Verified</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Annotation Logged</div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
