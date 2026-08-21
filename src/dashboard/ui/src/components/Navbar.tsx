import React from 'react';
import { Activity, ShieldCheck, Cpu, RefreshCw, Play, Pause, Sparkles } from 'lucide-react';

interface NavbarProps {
  isAutoSimulating: boolean;
  setIsAutoSimulating: (val: boolean) => void;
  resetSimulation: () => void;
  clusterHealth: number;
  resolvedCount: number;
  onOpenDiagnosticModal: () => void;
  hasDiagnostic: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  isAutoSimulating,
  setIsAutoSimulating,
  resetSimulation,
  clusterHealth,
  resolvedCount,
  onOpenDiagnosticModal,
  hasDiagnostic
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#182236] bg-[#030508]/90 backdrop-blur-xl px-4 lg:px-8 py-3.5 transition-all">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Brand identity */}
        <div className="flex items-center gap-3.5">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 via-violet-500/20 to-transparent border border-cyan-500/40 glow-cyan">
            <Activity className="w-5 h-5 text-cyan-400 animate-pulse" />
            <div className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping opacity-75" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white font-sans">
                StudioPulse <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-violet-400">AI</span>
              </h1>
              <span className="px-2 py-0.5 text-[10px] font-mono font-semibold tracking-wider uppercase bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 rounded">
                v2.4 Autonomous
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono flex items-center gap-1.5 mt-0.5">
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Autonomous Multi-Agent Incident Response for Media Rendering Pipelines
            </p>
          </div>
        </div>

        {/* Integration Status Badges */}
        <div className="hidden xl:flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#0b101b] border border-[#1b273d]">
            <div className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />
            <span className="text-xs font-mono text-slate-300">Google Gemini 2.0 Flash</span>
            <span className="text-[10px] px-1.5 py-0.2 rounded bg-violet-500/20 text-violet-300 font-mono">Vertex AI</span>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#0b101b] border border-[#1b273d]">
            <div className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
            <span className="text-xs font-mono text-slate-300">Grafana Cloud APIs</span>
            <span className="text-[10px] px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 font-mono">Telemetry</span>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#0b101b] border border-[#1b273d]">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-mono text-slate-300">GKE GPU Farm</span>
            <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 font-mono">8 Nodes</span>
          </div>
        </div>

        {/* Global Controls */}
        <div className="flex items-center gap-2.5">
          {hasDiagnostic && (
            <button
              onClick={onOpenDiagnosticModal}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-violet-500/40 bg-violet-500/10 text-violet-300 hover:bg-violet-500/20 transition-all glow-purple cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-violet-400" />
              <span>Inspect Gemini AI</span>
            </button>
          )}

          <button
            onClick={() => setIsAutoSimulating(!isAutoSimulating)}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border transition-all cursor-pointer ${
              isAutoSimulating
                ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/20'
                : 'bg-slate-800/60 border-slate-700 text-slate-300 hover:bg-slate-800'
            }`}
            title="Toggle live telemetry stream"
          >
            {isAutoSimulating ? (
              <>
                <Pause className="w-3.5 h-3.5" />
                <span>Live Stream</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 text-amber-400" />
                <span>Stream Paused</span>
              </>
            )}
          </button>

          <button
            onClick={resetSimulation}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-[#23324f] bg-[#0c1322] text-slate-300 hover:text-white hover:border-cyan-500/40 hover:bg-[#121c32] transition-all cursor-pointer"
            title="Reset pipeline simulation to baseline"
          >
            <RefreshCw className="w-3.5 h-3.5 text-slate-400" />
            <span>Reset</span>
          </button>
        </div>

      </div>
    </header>
  );
};
