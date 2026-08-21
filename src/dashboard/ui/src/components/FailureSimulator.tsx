import React from 'react';
import { AlertTriangle, Play, Flame, Layers, HardDrive, Cpu, Radio } from 'lucide-react';
import { FAILURE_SCENARIOS } from '../mock/simulationData';
import { FailureScenario } from '../types';

interface FailureSimulatorProps {
  onTriggerScenario: (scenarioId: string) => void;
  activeScenarioId: string | undefined;
  disabled: boolean;
}

export const FailureSimulator: React.FC<FailureSimulatorProps> = ({
  onTriggerScenario,
  activeScenarioId,
  disabled
}) => {
  return (
    <div className="glass-panel rounded-2xl p-5 border border-[#1b273d]">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-[#182236]">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-rose-400 animate-ping" />
            <h2 className="text-base font-bold font-sans text-white tracking-tight uppercase tracking-wider">
              Media Pipeline Simulator: 5 Failure Scenarios
            </h2>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Inject realistic VFX rendering infrastructure failures to test autonomous multi-agent self-healing
          </p>
        </div>
        <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-[#090e18] border border-[#1c2940] text-slate-300 self-start sm:self-auto">
          Demo Mode: Active
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3 mt-4">
        {FAILURE_SCENARIOS.map((scenario) => {
          const isActive = activeScenarioId === scenario.id;
          return (
            <div
              key={scenario.id}
              className={`p-3.5 rounded-xl border flex flex-col justify-between transition-all ${
                isActive
                  ? 'bg-rose-950/25 border-rose-500/60 glow-rose ring-1 ring-rose-500/30'
                  : 'bg-[#090d16] border-[#182338] hover:border-slate-700 hover:bg-[#0c1220]'
              }`}
            >
              <div>
                <div className="flex items-center justify-between gap-1 mb-2">
                  <span className="text-[9px] font-mono font-bold tracking-wider px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20">
                    {scenario.badge}
                  </span>
                  <span className="text-[10px] font-mono text-emerald-400">
                    ~{scenario.expectedTtrSec}s TTR
                  </span>
                </div>

                <h3 className="text-xs font-bold font-sans text-white line-clamp-2 leading-snug mb-1.5">
                  {scenario.name}
                </h3>

                <p className="text-[11px] text-slate-400 font-sans line-clamp-3 leading-relaxed mb-3">
                  {scenario.description}
                </p>
              </div>

              <button
                onClick={() => onTriggerScenario(scenario.id)}
                disabled={disabled}
                className={`w-full flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-mono font-semibold transition-all cursor-pointer ${
                  isActive
                    ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/30'
                    : 'bg-[#121c30] hover:bg-rose-600/20 border border-[#223352] hover:border-rose-500/50 text-slate-200 hover:text-rose-200'
                } ${disabled && !isActive ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <Play className="w-3 h-3" />
                <span>{isActive ? 'Mitigating Live...' : 'Inject Fault'}</span>
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};
