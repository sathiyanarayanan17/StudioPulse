import React from 'react';
import { Cpu, Zap, Layers, ShieldCheck, TrendingDown } from 'lucide-react';
import { RenderNode } from '../types';

interface MetricsOverviewProps {
  nodes: RenderNode[];
  resolvedCount: number;
  framesProcessed: number;
  clusterHealth: number;
  avgTtrSeconds: number;
}

export const MetricsOverview: React.FC<MetricsOverviewProps> = ({
  nodes,
  resolvedCount,
  framesProcessed,
  clusterHealth,
  avgTtrSeconds
}) => {
  const totalVramUsed = nodes.reduce((acc, n) => acc + n.vramUsedGB, 0).toFixed(1);
  const totalVramCap = nodes.reduce((acc, n) => acc + n.vramTotalGB, 0);
  const avgGpuLoad = Math.round(nodes.reduce((acc, n) => acc + n.gpuLoad, 0) / nodes.length);
  const healthyNodeCount = nodes.filter(n => n.status === 'healthy').length;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      
      {/* Metric 1: GPU Farm Cluster */}
      <div className="glass-card p-4 rounded-xl relative overflow-hidden transition-all hover:border-cyan-500/40 group">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono font-medium text-slate-400 uppercase tracking-wider">GPU Cluster Load</span>
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 group-hover:scale-110 transition-transform">
            <Cpu className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-white tracking-tight">{avgGpuLoad}%</span>
          <span className="text-xs font-mono text-cyan-400 font-medium">8 Active GPUs</span>
        </div>
        <div className="mt-3 flex items-center justify-between text-[11px] font-mono text-slate-400 border-t border-[#1a2538] pt-2">
          <span>VRAM: {totalVramUsed} / {totalVramCap} GB</span>
          <span className="text-emerald-400">{healthyNodeCount}/{nodes.length} Nodes OK</span>
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-cyan-500/60 to-transparent" />
      </div>

      {/* Metric 2: MTTR Autonomous vs Manual */}
      <div className="glass-card p-4 rounded-xl relative overflow-hidden transition-all hover:border-violet-500/40 group">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono font-medium text-slate-400 uppercase tracking-wider">Autonomous MTTR</span>
          <div className="p-2 rounded-lg bg-violet-500/10 border border-violet-500/30 text-violet-400 group-hover:scale-110 transition-transform">
            <Zap className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-white tracking-tight">{(avgTtrSeconds / 60).toFixed(2)} min</span>
          <span className="inline-flex items-center text-xs font-mono text-emerald-400 font-medium bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/30">
            <TrendingDown className="w-3 h-3 mr-0.5" /> -96.5% vs Ops
          </span>
        </div>
        <div className="mt-3 flex items-center justify-between text-[11px] font-mono text-slate-400 border-t border-[#1a2538] pt-2">
          <span>Traditional Ops: 45.0 min</span>
          <span className="text-violet-400">Zero Human Triage</span>
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-violet-500/60 to-transparent" />
      </div>

      {/* Metric 3: Total Frames Processed */}
      <div className="glass-card p-4 rounded-xl relative overflow-hidden transition-all hover:border-emerald-500/40 group">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono font-medium text-slate-400 uppercase tracking-wider">Render Throughput</span>
          <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 group-hover:scale-110 transition-transform">
            <Layers className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-white tracking-tight">{framesProcessed.toLocaleString()}</span>
          <span className="text-xs font-mono text-emerald-400 font-medium">+1,420 fph</span>
        </div>
        <div className="mt-3 flex items-center justify-between text-[11px] font-mono text-slate-400 border-t border-[#1a2538] pt-2">
          <span>Frame Drop Rate: 0.0%</span>
          <span className="text-emerald-400">Cluster Uptime {clusterHealth}%</span>
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-emerald-500/60 to-transparent" />
      </div>

      {/* Metric 4: Autonomous Resolutions */}
      <div className="glass-card p-4 rounded-xl relative overflow-hidden transition-all hover:border-amber-500/40 group">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono font-medium text-slate-400 uppercase tracking-wider">Self-Healed Incidents</span>
          <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400 group-hover:scale-110 transition-transform">
            <ShieldCheck className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-white tracking-tight">{resolvedCount}</span>
          <span className="text-xs font-mono text-amber-300 font-medium">100% Success</span>
        </div>
        <div className="mt-3 flex items-center justify-between text-[11px] font-mono text-slate-400 border-t border-[#1a2538] pt-2">
          <span>Allowlist Guard: Active</span>
          <span className="text-amber-400">Audit Trail Logged</span>
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-amber-500/60 to-transparent" />
      </div>

    </div>
  );
};
