import React, { useState } from 'react';
import { useSimulationEngine } from './hooks/useSimulationEngine';
import { Navbar } from './components/Navbar';
import { MetricsOverview } from './components/MetricsOverview';
import { AgentPipelineVisualizer } from './components/AgentPipelineVisualizer';
import { FailureSimulator } from './components/FailureSimulator';
import { GpuNodeBarChart } from './components/Charts/GpuNodeBarChart';
import { ResolutionComparisonBarChart } from './components/Charts/ResolutionComparisonBarChart';
import { RenderEngineThroughputChart } from './components/Charts/RenderEngineThroughputChart';
import { QueueBacklogBarChart } from './components/Charts/QueueBacklogBarChart';
import { ClusterNodeGrid } from './components/ClusterNodeGrid';
import { LiveLogsTerminal } from './components/LiveLogsTerminal';
import { GeminiDiagnosticModal } from './components/GeminiDiagnosticModal';
import { Activity, ShieldCheck, Sparkles, Cpu, Layers, Terminal, AlertTriangle } from 'lucide-react';

export function App() {
  const {
    nodes,
    activeIncident,
    incidentHistory,
    activeScenario,
    agentStep,
    monitorState,
    diagnoseState,
    remediateState,
    geminiPrompt,
    geminiResponse,
    logs,
    isAutoSimulating,
    setIsAutoSimulating,
    selectedNodeId,
    setSelectedNodeId,
    metricsCount,
    triggerScenario,
    resetSimulation
  } = useSimulationEngine();

  const [isDiagnosticModalOpen, setIsDiagnosticModalOpen] = useState<boolean>(false);
  const [activeChartTab, setActiveChartTab] = useState<'gpu' | 'benchmark' | 'engines' | 'queue'>('gpu');

  return (
    <div className="min-h-screen bg-[#030508] text-slate-100 font-sans selection:bg-cyan-500/30 selection:text-cyan-200 cyber-grid pb-12">
      
      {/* Top Navigation */} 
      <Navbar
        isAutoSimulating={isAutoSimulating}
        setIsAutoSimulating={setIsAutoSimulating}
        resetSimulation={resetSimulation}
        clusterHealth={metricsCount.clusterHealth}
        resolvedCount={metricsCount.resolvedCount}
        onOpenDiagnosticModal={() => setIsDiagnosticModalOpen(true)}
        hasDiagnostic={Boolean(geminiResponse || activeIncident)}
      />

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 lg:px-8 mt-6 space-y-6">
        
        {/* 4 High-Tech Top Telemetry Cards */}
        <MetricsOverview
          nodes={nodes}
          resolvedCount={metricsCount.resolvedCount}
          framesProcessed={metricsCount.framesProcessed}
          clusterHealth={metricsCount.clusterHealth}
          avgTtrSeconds={metricsCount.avgTtrSeconds}
        />

        {/* Multi-Agent Orchestration Visualizer */}
        <AgentPipelineVisualizer
          agentStep={agentStep}
          monitorState={monitorState}
          diagnoseState={diagnoseState}
          remediateState={remediateState}
          activeIncident={activeIncident}
          activeScenario={activeScenario}
          onOpenDiagnosticModal={() => setIsDiagnosticModalOpen(true)}
        />

        {/* Interactive Data Visualizations & Bar Graphs Section */}
        <div className="space-y-4">
          {/* Chart Category Switcher */}
          <div className="flex flex-wrap items-center justify-between gap-3 bg-[#080d17] p-2 rounded-xl border border-[#182338]">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold font-mono text-white uppercase tracking-wider px-2">
                Telemetry & Data Analytics:
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-1.5">
              <button
                onClick={() => setActiveChartTab('gpu')}
                className={`px-3 py-1.5 text-xs font-mono rounded-lg transition-all cursor-pointer ${
                  activeChartTab === 'gpu'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold glow-cyan'
                    : 'text-slate-400 hover:text-white bg-[#0b101b] border border-transparent'
                }`}
              >
                GPU Node Farm Loads
              </button>

              <button
                onClick={() => setActiveChartTab('benchmark')}
                className={`px-3 py-1.5 text-xs font-mono rounded-lg transition-all cursor-pointer ${
                  activeChartTab === 'benchmark'
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold glow-emerald'
                    : 'text-slate-400 hover:text-white bg-[#0b101b] border border-transparent'
                }`}
              >
                Incident Response Benchmark
              </button>

              <button
                onClick={() => setActiveChartTab('engines')}
                className={`px-3 py-1.5 text-xs font-mono rounded-lg transition-all cursor-pointer ${
                  activeChartTab === 'engines'
                    ? 'bg-violet-500/20 text-violet-300 border border-violet-500/40 font-bold glow-purple'
                    : 'text-slate-400 hover:text-white bg-[#0b101b] border border-transparent'
                }`}
              >
                Render Engine Throughput
              </button>

              <button
                onClick={() => setActiveChartTab('queue')}
                className={`px-3 py-1.5 text-xs font-mono rounded-lg transition-all cursor-pointer ${
                  activeChartTab === 'queue'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold glow-amber'
                    : 'text-slate-400 hover:text-white bg-[#0b101b] border border-transparent'
                }`}
              >
                Shot Queue Layers
              </button>
            </div>
          </div>

          {/* Tabbed Displayed Chart */}
          {activeChartTab === 'gpu' && (
            <GpuNodeBarChart
              nodes={nodes}
              selectedNodeId={selectedNodeId}
              onSelectNode={setSelectedNodeId}
            />
          )}

          {activeChartTab === 'benchmark' && (
            <ResolutionComparisonBarChart />
          )}

          {activeChartTab === 'engines' && (
            <RenderEngineThroughputChart />
          )}

          {activeChartTab === 'queue' && (
            <QueueBacklogBarChart />
          )}
        </div>

        {/* Server Rack Cluster Node Grid */}
        <ClusterNodeGrid
          nodes={nodes}
          selectedNodeId={selectedNodeId}
          onSelectNode={setSelectedNodeId}
        />

        {/* 5 Failure Scenarios Simulator Deck */}
        <FailureSimulator
          onTriggerScenario={triggerScenario}
          activeScenarioId={activeScenario?.id}
          disabled={Boolean(activeIncident && activeIncident.status !== 'resolved')}
        />

        {/* Live Terminal & Grafana Audit Feed */}
        <LiveLogsTerminal logs={logs} />

      </main>

      {/* Gemini Diagnostic Modal */}
      <GeminiDiagnosticModal
        isOpen={isDiagnosticModalOpen}
        onClose={() => setIsDiagnosticModalOpen(false)}
        activeIncident={activeIncident}
        activeScenario={activeScenario}
        geminiPrompt={geminiPrompt}
        geminiResponse={geminiResponse}
      />

    </div>
  );
}

export default App;
