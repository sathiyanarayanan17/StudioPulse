import React, { useState } from 'react';
import { Cpu, HardDrive, Thermometer, Zap, Layers } from 'lucide-react';
import { RenderNode } from '../../types';

interface GpuNodeBarChartProps {
  nodes: RenderNode[];
  selectedNodeId: string | null;
  onSelectNode: (id: string) => void;
}

export const GpuNodeBarChart: React.FC<GpuNodeBarChartProps> = ({
  nodes,
  selectedNodeId,
  onSelectNode
}) => {
  const [activeMetric, setActiveMetric] = useState<'gpu' | 'vram'>('gpu');
  const selectedNode = nodes.find(n => n.id === selectedNodeId) || nodes[0];

  return (
    <div className="glass-panel rounded-2xl p-5 border border-[#1b273d] flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-[#182236]">
          <div>
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <h3 className="text-base font-bold font-sans text-white tracking-tight uppercase tracking-wider">
                GPU Node Farm Telemetry: 8 Active Nodes
              </h3>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Real-time compute load and VRAM allocation across NVIDIA H100, A100, and RTX 4090 clusters
            </p>
          </div>

          {/* Metric Selector Tabs */}
          <div className="flex items-center gap-1 bg-[#090d16] p-1 rounded-lg border border-[#1a263c]">
            <button
              onClick={() => setActiveMetric('gpu')}
              className={`px-2.5 py-1 text-xs font-mono rounded transition-all cursor-pointer ${
                activeMetric === 'gpu'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              GPU Compute %
            </button>
            <button
              onClick={() => setActiveMetric('vram')}
              className={`px-2.5 py-1 text-xs font-mono rounded transition-all cursor-pointer ${
                activeMetric === 'vram'
                  ? 'bg-violet-500/20 text-violet-300 border border-violet-500/40 font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              VRAM (GB) Used
            </button>
          </div>
        </div>

        {/* Bar Graph Grid */}
        <div className="grid grid-cols-4 sm:grid-cols-8 gap-3 mt-6 items-end min-h-[190px] pt-4 px-2">
          {nodes.map((node) => {
            const isSelected = selectedNodeId === node.id;
            const valuePercent = activeMetric === 'gpu'
              ? node.gpuLoad
              : Math.round((node.vramUsedGB / node.vramTotalGB) * 100);

            const displayVal = activeMetric === 'gpu'
              ? `${node.gpuLoad}%`
              : `${node.vramUsedGB.toFixed(0)}G`;

            // Color threshold
            let barColor = 'bg-gradient-to-t from-cyan-600 to-cyan-400 border-cyan-400';
            let glowClass = 'shadow-[0_0_12px_rgba(0,240,255,0.3)]';
            if (valuePercent > 90 || node.status === 'critical') {
              barColor = 'bg-gradient-to-t from-rose-600 to-rose-400 border-rose-400 animate-pulse';
              glowClass = 'shadow-[0_0_15px_rgba(239,68,68,0.5)]';
            } else if (valuePercent > 78 || node.status === 'warning') {
              barColor = 'bg-gradient-to-t from-amber-600 to-amber-400 border-amber-400';
              glowClass = 'shadow-[0_0_12px_rgba(245,158,11,0.4)]';
            } else if (activeMetric === 'vram') {
              barColor = 'bg-gradient-to-t from-violet-600 to-violet-400 border-violet-400';
              glowClass = 'shadow-[0_0_12px_rgba(168,85,247,0.3)]';
            }

            return (
              <div
                key={node.id}
                onClick={() => onSelectNode(node.id)}
                className={`group flex flex-col items-center cursor-pointer transition-all ${
                  isSelected ? 'scale-105' : 'hover:scale-102'
                }`}
              >
                {/* Value Label on Top */}
                <span className={`text-[11px] font-mono font-bold mb-1.5 transition-colors ${
                  isSelected ? 'text-white' : 'text-slate-400 group-hover:text-cyan-300'
                }`}>
                  {displayVal}
                </span>

                {/* Vertical Bar Container */}
                <div className={`w-full max-w-[36px] h-36 bg-[#070b14] rounded-t-lg border flex flex-col justify-end p-1 relative overflow-hidden transition-all ${
                  isSelected
                    ? 'border-cyan-400 ring-2 ring-cyan-500/30'
                    : 'border-[#1b263b] group-hover:border-slate-500'
                }`}>
                  {/* Grid lines inside bar container */}
                  <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-20">
                    <div className="border-b border-white w-full" />
                    <div className="border-b border-white w-full" />
                    <div className="border-b border-white w-full" />
                  </div>

                  {/* Filled Animated Bar */}
                  <div
                    style={{ height: `${Math.max(8, valuePercent)}%` }}
                    className={`w-full rounded-t-md transition-all duration-500 border-t ${barColor} ${glowClass}`}
                  />
                </div>

                {/* Node Name Label */}
                <span className={`text-[10px] font-mono mt-2 font-medium tracking-tight ${
                  isSelected ? 'text-cyan-400 font-bold' : 'text-slate-400'
                }`}>
                  {node.name.replace('GKE-GPU-', '')}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Selected Node Details Footer */}
      <div className="mt-4 pt-3.5 border-t border-[#182236] bg-[#070c16]/70 rounded-xl p-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs font-mono">
        <div className="flex items-center gap-2.5">
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <span className="font-bold text-white">{selectedNode.name}</span>
          <span className="text-slate-400">|</span>
          <span className="text-slate-300">{selectedNode.gpuModel}</span>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-slate-300">
          <div className="flex items-center gap-1.5">
            <Thermometer className="w-3.5 h-3.5 text-amber-400" />
            <span>{selectedNode.tempC} C</span>
          </div>
          <div className="flex items-center gap-1.5">
            <HardDrive className="w-3.5 h-3.5 text-violet-400" />
            <span>VRAM: {selectedNode.vramUsedGB.toFixed(1)} / {selectedNode.vramTotalGB} GB</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-emerald-400" />
            <span>FPS: {selectedNode.fps}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
