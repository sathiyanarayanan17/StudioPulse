import React from 'react';
import { Server, Thermometer, Cpu, HardDrive, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import { RenderNode } from '../types';

interface ClusterNodeGridProps {
  nodes: RenderNode[];
  selectedNodeId: string | null;
  onSelectNode: (id: string) => void;
}

export const ClusterNodeGrid: React.FC<ClusterNodeGridProps> = ({
  nodes,
  selectedNodeId,
  onSelectNode
}) => {
  return (
    <div className="glass-panel rounded-2xl p-5 border border-[#1b273d]">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-[#182236]">
        <div>
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-cyan-400" />
            <h3 className="text-base font-bold font-sans text-white tracking-tight uppercase tracking-wider">
              GKE GPU Server Rack: 8 Active Node Blades
            </h3>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Live blade telemetry, thermal sensors, and worker process health
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono text-slate-400">
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> Healthy</span>
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-amber-400" /> Warning</span>
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-rose-400 animate-ping" /> Critical</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4">
        {nodes.map((node) => {
          const isSelected = selectedNodeId === node.id;
          const isCrit = node.status === 'critical';
          const isWarn = node.status === 'warning';
          const isRecov = node.status === 'recovering';

          return (
            <div
              key={node.id}
              onClick={() => onSelectNode(node.id)}
              className={`p-3.5 rounded-xl border transition-all cursor-pointer relative overflow-hidden ${
                isCrit
                  ? 'bg-rose-950/20 border-rose-500/60 glow-rose animate-pulse'
                  : isWarn
                  ? 'bg-amber-950/20 border-amber-500/50 glow-amber'
                  : isRecov
                  ? 'bg-cyan-950/20 border-cyan-500/50 glow-cyan'
                  : isSelected
                  ? 'bg-[#0e1626] border-cyan-500/60 ring-1 ring-cyan-500/30'
                  : 'bg-[#090d16] border-[#182338] hover:border-slate-700 hover:bg-[#0c1220]'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1.5">
                  <div className={`w-2 h-2 rounded-full ${
                    isCrit ? 'bg-rose-400 animate-ping' : isWarn ? 'bg-amber-400' : isRecov ? 'bg-cyan-400 animate-spin' : 'bg-emerald-400 animate-pulse'
                  }`} />
                  <span className="text-xs font-mono font-bold text-white">{node.name.replace('GKE-GPU-', '')}</span>
                </div>
                <span className={`text-[10px] font-mono font-semibold px-1.5 py-0.2 rounded uppercase ${
                  isCrit ? 'bg-rose-500/20 text-rose-300' : isWarn ? 'bg-amber-500/20 text-amber-300' : isRecov ? 'bg-cyan-500/20 text-cyan-300' : 'bg-emerald-500/10 text-emerald-400'
                }`}>
                  {node.status}
                </span>
              </div>

              <div className="text-[11px] font-mono text-slate-400 truncate mb-2.5" title={node.currentJob}>
                {node.currentJob}
              </div>

              {/* Mini compute & memory bars */}
              <div className="space-y-2 text-[10px] font-mono">
                <div>
                  <div className="flex justify-between text-slate-400 mb-1">
                    <span>GPU Load</span>
                    <span className={isCrit ? 'text-rose-400 font-bold' : 'text-slate-200'}>{node.gpuLoad}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-[#060a12] rounded overflow-hidden">
                    <div
                      style={{ width: `${node.gpuLoad}%` }}
                      className={`h-full rounded ${
                        isCrit ? 'bg-rose-500' : isWarn ? 'bg-amber-500' : 'bg-cyan-400'
                      }`}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-slate-400 mb-1">
                    <span>VRAM ({node.vramUsedGB.toFixed(0)}/{node.vramTotalGB}G)</span>
                    <span className="text-slate-200">{Math.round((node.vramUsedGB / node.vramTotalGB) * 100)}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-[#060a12] rounded overflow-hidden">
                    <div
                      style={{ width: `${(node.vramUsedGB / node.vramTotalGB) * 100}%` }}
                      className="h-full rounded bg-violet-400"
                    />
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between mt-3 pt-2 border-t border-[#162033] text-[10px] font-mono text-slate-400">
                <span className="flex items-center gap-1"><Thermometer className="w-3 h-3 text-amber-400" /> {node.tempC} C</span>
                <span className="text-slate-300">{node.fps} fps</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
