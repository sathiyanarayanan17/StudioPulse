import React from 'react';
import { Clock, TrendingDown, CheckCircle2, Shield, DollarSign } from 'lucide-react';
import { BENCHMARK_COMPARISONS } from '../../mock/simulationData';

export const ResolutionComparisonBarChart: React.FC = () => {
  const manualTotalMin = BENCHMARK_COMPARISONS.reduce((acc, b) => acc + b.manualTimeMin, 0);
  const autoTotalSec = BENCHMARK_COMPARISONS.reduce((acc, b) => acc + b.autonomousTimeSec, 0);
  const autoTotalMin = (autoTotalSec / 60).toFixed(2);

  return (
    <div className="glass-panel rounded-2xl p-5 border border-[#1b273d] flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-[#182236]">
          <div>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-emerald-400" />
              <h3 className="text-base font-bold font-sans text-white tracking-tight uppercase tracking-wider">
                Incident Response Benchmark: Manual Ops vs StudioPulse AI
              </h3>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Comparison across 4 operational response phases: Triage, Metric Correlation, Root Cause Reasoning, Remediation
            </p>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <span className="inline-flex items-center text-xs font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/30">
              <TrendingDown className="w-3.5 h-3.5 mr-1" /> 35x Faster Resolution
            </span>
          </div>
        </div>

        {/* Comparative Horizontal Bar List */}
        <div className="space-y-4 mt-5">
          {BENCHMARK_COMPARISONS.map((item, idx) => {
            const manualPercent = Math.min(100, (item.manualTimeMin / 20) * 100);
            const autoMinutes = (item.autonomousTimeSec / 60).toFixed(2);
            const autoPercent = Math.max(3, (Number(autoMinutes) / 20) * 100);

            return (
              <div key={idx} className="space-y-1.5">
                <div className="flex justify-between items-center text-xs font-mono">
                  <span className="font-bold text-slate-200">{item.phase}</span>
                  <div className="flex items-center gap-3 text-[11px]">
                    <span className="text-rose-400">Manual: {item.manualTimeMin} min</span>
                    <span className="text-slate-500">vs</span>
                    <span className="text-emerald-400 font-bold">StudioPulse: {item.autonomousTimeSec} sec</span>
                  </div>
                </div>

                {/* Stacked Comparative Bars */}
                <div className="space-y-1 bg-[#070b13] p-1.5 rounded-lg border border-[#162134]">
                  {/* Manual Ops Bar */}
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-rose-400 w-16 shrink-0">Manual Ops</span>
                    <div className="w-full h-3 bg-[#0d1422] rounded overflow-hidden">
                      <div
                        style={{ width: `${manualPercent}%` }}
                        className="h-full bg-gradient-to-r from-rose-700 to-rose-500 rounded transition-all duration-500"
                      />
                    </div>
                  </div>

                  {/* StudioPulse AI Bar */}
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-emerald-400 font-bold w-16 shrink-0">Autonomous</span>
                    <div className="w-full h-3 bg-[#0d1422] rounded overflow-hidden">
                      <div
                        style={{ width: `${autoPercent}%` }}
                        className="h-full bg-gradient-to-r from-emerald-500 to-cyan-400 rounded shadow-[0_0_10px_rgba(0,230,118,0.4)] transition-all duration-500"
                      />
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Summary Scorecard */}
      <div className="mt-5 pt-3.5 border-t border-[#182236] grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
        <div className="p-2.5 rounded-lg bg-[#070b14] border border-[#182338]">
          <span className="text-slate-400 text-[10px] uppercase block">Total Traditional Downtime</span>
          <span className="text-lg font-bold text-rose-400 font-mono">{manualTotalMin.toFixed(1)} Minutes</span>
        </div>

        <div className="p-2.5 rounded-lg bg-[#070b14] border border-emerald-500/30 glow-emerald">
          <span className="text-emerald-400 text-[10px] uppercase block font-semibold">StudioPulse Total MTTR</span>
          <span className="text-lg font-bold text-emerald-300 font-mono">{autoTotalMin} Minutes ({autoTotalSec.toFixed(0)}s)</span>
        </div>

        <div className="p-2.5 rounded-lg bg-[#070b14] border border-[#182338]">
          <span className="text-slate-400 text-[10px] uppercase block">Est. Compute Cost Saved</span>
          <span className="text-lg font-bold text-cyan-300 font-mono">$14,250 / Incident</span>
        </div>
      </div>
    </div>
  );
};
