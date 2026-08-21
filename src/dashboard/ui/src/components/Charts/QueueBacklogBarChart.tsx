import React from 'react';
import { Layers, CheckCircle2, Clock } from 'lucide-react';
import { QUEUE_WORKLOADS } from '../../mock/simulationData';

export const QueueBacklogBarChart: React.FC = () => {
  return (
    <div className="glass-panel rounded-2xl p-5 border border-[#1b273d]">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-[#182236]">
        <div>
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            <h3 className="text-base font-bold font-sans text-white tracking-tight uppercase tracking-wider">
              VFX Shot Layer Queue Distribution
            </h3>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Active 4K/8K frame passes: Queued vs In-Process vs Completed
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono text-slate-300">
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-cyan-400" /> Queued</span>
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-violet-400" /> Processing</span>
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-emerald-400" /> Done</span>
        </div>
      </div>

      <div className="space-y-3.5 mt-4">
        {QUEUE_WORKLOADS.map((q, idx) => {
          const total = q.queued + q.processing + q.completed;
          const qPct = (q.queued / total) * 100;
          const pPct = (q.processing / total) * 100;
          const cPct = (q.completed / total) * 100;

          return (
            <div key={idx} className="space-y-1.5">
              <div className="flex justify-between items-center text-xs font-mono">
                <div className="flex items-center gap-2">
                  <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                    q.priority === 'P0' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-slate-800 text-slate-300'
                  }`}>{q.priority}</span>
                  <span className="font-bold text-slate-200">{q.layer}</span>
                </div>
                <div className="text-[11px] text-slate-400">
                  {q.queued} queued | {q.processing} active | {q.completed} done
                </div>
              </div>

              {/* Stacked Bar */}
              <div className="w-full h-3.5 bg-[#070c16] rounded flex overflow-hidden border border-[#18243a]">
                <div style={{ width: `${qPct}%` }} className="bg-cyan-500 h-full" title="Queued" />
                <div style={{ width: `${pPct}%` }} className="bg-violet-500 h-full" title="Processing" />
                <div style={{ width: `${cPct}%` }} className="bg-emerald-500 h-full" title="Completed" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
