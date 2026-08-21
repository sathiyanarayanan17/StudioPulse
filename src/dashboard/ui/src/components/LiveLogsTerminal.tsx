import React, { useState } from 'react';
import { Terminal, Search, Copy, Check } from 'lucide-react';
import { LogEntry } from '../types';

interface LiveLogsTerminalProps {
  logs: LogEntry[];
}

export const LiveLogsTerminal: React.FC<LiveLogsTerminalProps> = ({ logs }) => {
  const [filterAgent, setFilterAgent] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [copied, setCopied] = useState<boolean>(false);

  const filteredLogs = logs.filter(log => {
    if (filterAgent !== 'ALL' && log.agent !== filterAgent) return false;
    if (searchQuery && !log.message.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const handleCopyLogs = () => {
    const text = filteredLogs.map(l => `[${l.timestamp}] [${l.agent}] [${l.level}] ${l.message}`).join('\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-[#1b273d]">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-4 border-b border-[#182236]">
        <div>
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <h3 className="text-base font-bold font-sans text-white tracking-tight uppercase tracking-wider">
              Live Telemetry & Grafana Audit Stream
            </h3>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Structured event log for Sentinel Monitor, Gemini 2.0 Detective, and Remediate Agent actions
          </p>
        </div>

        {/* Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Search Input */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5 pointer-events-none" />
            <input
              type="text"
              placeholder="Search logs..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-1 text-xs font-mono bg-[#090d16] border border-[#1b263b] rounded-lg text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500/50 w-36 sm:w-44"
            />
          </div>

          {/* Agent Filter */}
          <select
            value={filterAgent}
            onChange={e => setFilterAgent(e.target.value)}
            className="px-2 py-1 text-xs font-mono bg-[#090d16] border border-[#1b263b] rounded-lg text-slate-300 focus:outline-none focus:border-cyan-500/50 cursor-pointer"
          >
            <option value="ALL">All Agents</option>
            <option value="Monitor">Monitor Agent</option>
            <option value="Diagnose">Diagnose Agent</option>
            <option value="Remediate">Remediate Agent</option>
            <option value="Gemini">Google Gemini</option>
            <option value="Grafana">Grafana Cloud</option>
            <option value="System">System</option>
          </select>

          {/* Copy logs */}
          <button
            onClick={handleCopyLogs}
            className="flex items-center gap-1 px-2.5 py-1 text-xs font-mono bg-[#090d16] border border-[#1b263b] rounded-lg text-slate-300 hover:text-white hover:border-slate-500 transition-all cursor-pointer"
            title="Copy filtered logs to clipboard"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
        </div>
      </div>

      {/* Terminal Output Window */}
      <div className="mt-4 p-4 rounded-xl bg-[#04060b] border border-[#151f33] h-64 overflow-y-auto font-mono text-xs space-y-2">
        {filteredLogs.length === 0 ? (
          <div className="text-slate-500 text-center py-10">No logs matching filter criteria.</div>
        ) : (
          filteredLogs.map(log => {
            let levelBadge = 'text-slate-400 bg-slate-800/40 border-slate-700';
            if (log.level === 'ERROR') levelBadge = 'text-rose-400 bg-rose-500/10 border-rose-500/30';
            if (log.level === 'WARN') levelBadge = 'text-amber-400 bg-amber-500/10 border-amber-500/30';
            if (log.level === 'SUCCESS') levelBadge = 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
            if (log.level === 'AGENT') levelBadge = 'text-violet-400 bg-violet-500/10 border-violet-500/30';

            let agentColor = 'text-slate-300';
            if (log.agent === 'Monitor') agentColor = 'text-cyan-400';
            if (log.agent === 'Diagnose' || log.agent === 'Gemini') agentColor = 'text-violet-400';
            if (log.agent === 'Remediate') agentColor = 'text-emerald-400';
            if (log.agent === 'Grafana') agentColor = 'text-amber-400';

            return (
              <div key={log.id} className="flex items-start gap-2.5 leading-relaxed hover:bg-white/[0.02] p-1 rounded transition-colors">
                <span className="text-slate-500 text-[11px] shrink-0">[{log.timestamp}]</span>
                <span className={`px-1.5 py-0.2 rounded border text-[10px] font-bold shrink-0 ${levelBadge}`}>
                  {log.level}
                </span>
                <span className={`font-bold shrink-0 ${agentColor}`}>
                  [{log.agent}]
                </span>
                <span className="text-slate-300 break-words flex-1">
                  {log.message}
                  {log.details && (
                    <span className="block text-[11px] text-slate-400 mt-0.5 border-l-2 border-[#1c2942] pl-2">
                      {log.details}
                    </span>
                  )}
                </span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
