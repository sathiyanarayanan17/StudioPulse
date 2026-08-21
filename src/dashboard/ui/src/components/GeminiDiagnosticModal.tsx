import React, { useState } from 'react';
import { X, Sparkles, ShieldCheck, CheckCircle2, Copy, Check, Terminal } from 'lucide-react';
import { Incident, FailureScenario } from '../types';

interface GeminiDiagnosticModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeIncident: Incident | null;
  activeScenario: FailureScenario | null;
  geminiPrompt: string;
  geminiResponse: any;
}

export const GeminiDiagnosticModal: React.FC<GeminiDiagnosticModalProps> = ({
  isOpen,
  onClose,
  activeIncident,
  activeScenario,
  geminiPrompt,
  geminiResponse
}) => {
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<'json' | 'prompt' | 'factors'>('json');

  if (!isOpen) return null;

  const displayJson = geminiResponse || {
    model: 'vertex-ai/gemini-2.0-flash',
    confidenceScore: activeScenario?.diagnosisOutput.confidence || 98.8,
    rootCauseSummary: activeScenario?.diagnosisOutput.summary || 'Texture buffer allocation exceeded ceiling on GPU node.',
    contributingFactors: activeScenario?.diagnosisOutput.factors || [
      'Unbounded texture cache pool size',
      'Thermal throttling at 88C',
      '1418% surge in frame render latency'
    ],
    recommendedActionPlan: activeScenario?.diagnosisOutput.remedy || [
      'Drain active render pod safely',
      'Trigger rolling restart on Arnold daemonset',
      'Auto-scale temporary overflow worker on GKE'
    ],
    safetyValidation: 'Passed: 100% allowlist compliant, zero destructive operations.'
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(displayJson, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="w-full max-w-4xl max-h-[90vh] bg-[#070b14] border border-[#202e48] rounded-2xl shadow-2xl flex flex-col overflow-hidden glow-purple">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between p-5 border-b border-[#182338] bg-[#0a0f1c]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-violet-500/10 border border-violet-500/30 flex items-center justify-center text-violet-400 glow-purple">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold font-sans text-white">Google Gemini 2.0 Diagnostic Intelligence</h3>
                <span className="px-2 py-0.5 text-[10px] font-mono bg-violet-500/20 border border-violet-500/40 text-violet-300 rounded">
                  Vertex AI / Flash
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                Structured Root Cause Analysis, Multi-Factor Correlation & Safe Cloud Remediation Plan
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-all cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Confidence & Scorecard Banner */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 bg-[#050810] border-b border-[#182338] text-xs font-mono">
          <div className="p-3 rounded-xl bg-[#090e1a] border border-[#1b283f]">
            <span className="text-slate-400 text-[10px] uppercase block">Gemini Confidence Score</span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-bold text-violet-400">{displayJson.confidenceScore}%</span>
              <span className="text-emerald-400 text-xs font-semibold">High Precision</span>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-[#090e1a] border border-[#1b283f]">
            <span className="text-slate-400 text-[10px] uppercase block">Safety Validation</span>
            <div className="flex items-center gap-1.5 mt-1.5 text-emerald-400 font-semibold">
              <ShieldCheck className="w-4 h-4" />
              <span>Allowlist Verified</span>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-[#090e1a] border border-[#1b283f]">
            <span className="text-slate-400 text-[10px] uppercase block">Audit Trail Link</span>
            <span className="text-amber-300 font-mono block mt-1.5 truncate">Grafana Annotation #ann-892410</span>
          </div>
        </div>

        {/* Modal Navigation Tabs */}
        <div className="flex items-center justify-between px-5 py-2.5 bg-[#080d18] border-b border-[#182338]">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab('json')}
              className={`px-3 py-1 text-xs font-mono rounded-lg transition-all cursor-pointer ${
                activeTab === 'json'
                  ? 'bg-violet-500/20 text-violet-300 border border-violet-500/40 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Structured Output (JSON)
            </button>
            <button
              onClick={() => setActiveTab('factors')}
              className={`px-3 py-1 text-xs font-mono rounded-lg transition-all cursor-pointer ${
                activeTab === 'factors'
                  ? 'bg-violet-500/20 text-violet-300 border border-violet-500/40 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Diagnostic Factors & Remedies
            </button>
            <button
              onClick={() => setActiveTab('prompt')}
              className={`px-3 py-1 text-xs font-mono rounded-lg transition-all cursor-pointer ${
                activeTab === 'prompt'
                  ? 'bg-violet-500/20 text-violet-300 border border-violet-500/40 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Correlated Prompt Inspector
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-mono rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-all cursor-pointer"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy JSON'}</span>
          </button>
        </div>

        {/* Modal Tab Body */}
        <div className="p-5 overflow-y-auto max-h-[50vh] text-xs font-mono bg-[#03060c]">
          {activeTab === 'json' && (
            <pre className="text-slate-300 p-4 rounded-xl bg-[#060a14] border border-[#162134] overflow-x-auto leading-relaxed">
              {JSON.stringify(displayJson, null, 2)}
            </pre>
          )}

          {activeTab === 'factors' && (
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-bold text-white font-sans mb-1">Root Cause Summary</h4>
                <p className="text-xs text-slate-300 font-sans p-3 rounded-lg bg-[#080e1b] border border-[#1a2840]">
                  {displayJson.rootCauseSummary}
                </p>
              </div>

              <div>
                <h4 className="text-sm font-bold text-white font-sans mb-2">Contributing Telemetry Factors</h4>
                <div className="space-y-1.5">
                  {displayJson.contributingFactors.map((f: string, i: number) => (
                    <div key={i} className="flex items-start gap-2 p-2.5 rounded-lg bg-[#080e1b] border border-[#1a2840] text-slate-300">
                      <CheckCircle2 className="w-4 h-4 text-violet-400 shrink-0 mt-0.5" />
                      <span>{f}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-sm font-bold text-white font-sans mb-2">Executed Safe Remediation Plan</h4>
                <div className="space-y-1.5">
                  {displayJson.recommendedActionPlan.map((r: string, i: number) => (
                    <div key={i} className="flex items-start gap-2 p-2.5 rounded-lg bg-[#080e1b] border border-[#1a2840] text-emerald-300">
                      <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span>Step {i + 1}: {r}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'prompt' && (
            <div className="p-4 rounded-xl bg-[#060a14] border border-[#162134] text-slate-300 whitespace-pre-wrap leading-relaxed">
              {geminiPrompt || `System: You are StudioPulse AI Root Cause Diagnostic Agent.
Analyze firing Grafana Alert on VFX Render Cluster.

Target Resource: GKE-GPU-NODE-03 (NVIDIA H100 SXM5)
GPU Load: 99.4% | VRAM: 78.8 GB / 80.0 GB
Thermal Sensor: 88.0 C | Frame Rate: 0.2 fps
Correlated Dashboards: /dashboards/vfx/gpu-clusters | /dashboards/vfx/queue-depth

Analyze the anomaly, determine root cause, compute confidence score, and output ranked safe remediation commands.`}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-[#182338] bg-[#070b14] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-mono font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-white transition-all cursor-pointer"
          >
            Close Inspector
          </button>
        </div>

      </div>
    </div>
  );
};
