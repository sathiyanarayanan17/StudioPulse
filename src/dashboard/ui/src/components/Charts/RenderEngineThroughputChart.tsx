import React from 'react';
import { Layers, Activity, Play } from 'lucide-react';
import { ENGINE_THROUGHPUTS } from '../../mock/simulationData';

export const RenderEngineThroughputChart: React.FC = () => {
  const maxThroughput = Math.max(...ENGINE_THROUGHPUTS.map(e => e.throughputFph));

  return (
    <div className="glass-panel rounded-2xl p-5 border border-[#1b273d]">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-[#182236]">
        <div>
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-violet-400" />
            <h3 className="text-base font-bold font-sans text-white tracking-tight uppercase tracking-wider">
              Render Engine Throughput & Frame Latency
            </h3>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Throughput (Frames/Hour) and average render time per frame across 5 active VFX engines
          </p>
        </div>
        <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-[#090e18] border border-[#1c2940] text-violet-300">
          5 Engine Groups Active
        </span>
      </div>

      <div className="space-y-3.5 mt-4">
        {ENGINE_THROUGHPUTS.map((eng, idx) => {
          const percent = (eng.throughputFph / maxThroughput) * 100;
          return (
            <div key={idx} className="space-y-1.5">
              <div className="flex justify-between items-center text-xs font-mono">
                <span className="font-bold text-slate-200">{eng.engine}</span>
                <div className="flex items-center gap-3 text-[11px]">
                  <span className="text-cyan-400 font-semibold">{eng.throughputFph} fph</span>
                  <span className="text-slate-400">({eng.avgFrameSec}s/frame)</span>
                  <span className="text-emerald-400">{eng.efficiency}% Eff</span>
                </div>
              </div>

              <div className="w-full h-4 bg-[#070c16] rounded-md p-0.5 border border-[#18243a] overflow-hidden">
                <div
                  style={{ width: `${percent}%`, backgroundColor: eng.color }}
                  className="h-full rounded-sm opacity-90 transition-all duration-500 shadow-[0_0_8px_currentColor]"
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
