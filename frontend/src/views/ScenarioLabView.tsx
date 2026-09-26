import React, { useState } from 'react';
import { DemoScenarioResult, AnalyzeResult } from '../types';
import { api } from '../api';
import { translations, SupportedLanguage } from '../i18n';
import { EvidenceCard } from '../components/EvidenceCard';
import { FlaskConical, Play, CheckCircle, AlertTriangle, Info, ArrowRight } from 'lucide-react';

interface ScenarioLabViewProps {
  language: SupportedLanguage;
  onNavigate: (module: string) => void;
}

export const ScenarioLabView: React.FC<ScenarioLabViewProps> = ({
  language,
  onNavigate,
}) => {
  const t = translations[language];
  const [selectedScenario, setSelectedScenario] = useState('PERSISTENT_LEAK');
  const [seed, setSeed] = useState(42);
  const [loading, setLoading] = useState(false);
  const [scenarioResult, setScenarioResult] = useState<DemoScenarioResult | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalyzeResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const scenariosList = [
    {
      id: 'NORMAL_HOME',
      name: 'Normal Household',
      expected: 'NORMAL',
      desc: 'Typical diurnal usage with morning and evening domestic peaks and low baseline night usage.',
    },
    {
      id: 'SINGLE_SPIKE',
      name: 'Single Transient Spike',
      expected: 'ISOLATED_EVENT',
      desc: 'Normal baseline followed by a single transient spike (e.g. tank fill or vehicle wash).',
    },
    {
      id: 'PERSISTENT_LEAK',
      name: 'Persistent Leak',
      expected: 'SUSPECTED_PERSISTENT_LEAK',
      desc: 'Normal historical baseline followed by continuous elevated night consumption persisting across multiple intervals.',
    },
    {
      id: 'BURST_USE',
      name: 'High-Volume Burst',
      expected: 'HIGH_VOLUME_BURST',
      desc: 'Sudden extreme continuous draw lasting 2-3 intervals.',
    },
    {
      id: 'FARM_IRRIGATION',
      name: 'Farm Irrigation Run',
      expected: 'SCHEDULED_IRRIGATION',
      desc: 'Scheduled high-volume agricultural pumping cycles in a rural farm meter.',
    },
    {
      id: 'DATA_QUALITY',
      name: 'Data Quality (Sparse History)',
      expected: 'INSUFFICIENT_HISTORY',
      desc: 'Fewer than required minimum readings (3 readings) to verify baseline guard behavior.',
    },
  ];

  const handleRunScenario = async () => {
    try {
      setLoading(true);
      setError(null);
      setScenarioResult(null);
      setAnalysisResult(null);

      // 1. Seed scenario in backend
      const res = await api.runDemoScenario(selectedScenario, seed);
      setScenarioResult(res);

      // 2. Trigger analysis
      const ana = await api.analyzeMeter(res.meter_id);
      setAnalysisResult(ana);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900">{t.scenarioLab}</h2>
        <p className="text-xs text-slate-500">
          Run reproducible, seeded synthetic scenarios to evaluate detection and data quality behavior
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Scenario Selector & Controls */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-3">
          <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block">
            Select Canonical Scenario
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {scenariosList.map((scen) => {
              const isSelected = selectedScenario === scen.id;
              return (
                <div
                  key={scen.id}
                  onClick={() => setSelectedScenario(scen.id)}
                  className={`p-4 rounded-xl border text-xs cursor-pointer transition space-y-1.5 ${
                    isSelected
                      ? 'border-sky-500 bg-sky-50/50 shadow-xs ring-1 ring-sky-500'
                      : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900">{scen.name}</span>
                    <span className="font-mono text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                      {scen.id}
                    </span>
                  </div>
                  <p className="text-slate-600 line-clamp-2">{scen.desc}</p>
                  <div className="text-[10px] text-sky-700 font-medium pt-1">
                    Ground Truth: {scen.expected}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Execution Settings Card */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4 h-fit">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
            <FlaskConical className="w-4 h-4 text-sky-600" />
            Execution Parameters
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Random Seed (Ground Truth Reproducibility)</label>
              <input
                type="number"
                value={seed}
                onChange={(e) => setSeed(parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-1 focus:ring-sky-500 outline-none"
              />
              <div className="text-[11px] text-slate-400 mt-1">Deterministic seed guarantees exact reproducible numbers.</div>
            </div>

            <button
              onClick={handleRunScenario}
              disabled={loading}
              className="w-full py-2.5 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded-lg transition flex items-center justify-center gap-2"
            >
              <Play className="w-4 h-4 fill-white" />
              {loading ? 'Synthesizing & Analyzing...' : 'Run Scenario Simulation'}
            </button>
          </div>
        </div>
      </div>

      {/* Scenario Output & Reconciled Evaluation */}
      {scenarioResult && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
            <div>
              <div className="text-xs text-slate-500">Simulation Run Result</div>
              <div className="text-base font-bold text-slate-900">
                {scenarioResult.scenario} (Seed: {scenarioResult.seed})
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-600">Ground Truth:</span>
              <span className="px-2.5 py-1 text-xs font-mono font-bold rounded-md bg-slate-100 text-slate-800 border border-slate-200">
                {scenarioResult.ground_truth}
              </span>
            </div>
          </div>

          <p className="text-xs text-slate-600">{scenarioResult.description}</p>

          {/* Insufficient History Check or Evidence */}
          {analysisResult && (
            <div className="pt-2 space-y-4">
              {analysisResult.status === 'INSUFFICIENT_HISTORY' ? (
                <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl space-y-1 text-xs text-amber-900">
                  <div className="font-bold flex items-center gap-2">
                    <Info className="w-4 h-4 text-amber-700" />
                    Correctly Triggered Insufficient-History Guard
                  </div>
                  <p>{analysisResult.insufficient_history?.message}</p>
                  <p className="text-slate-600 italic">
                    The backend safely suppressed risk calculation and alert generation as mandated by FR-05.
                  </p>
                </div>
              ) : analysisResult.evidence ? (
                <div className="space-y-4">
                  <EvidenceCard
                    evidence={analysisResult.evidence}
                    title="Seeded Scenario Evidence Packet"
                  />
                  {analysisResult.alert && (
                    <div className="flex items-center justify-between p-3 bg-sky-50 border border-sky-200 rounded-lg text-xs text-sky-900">
                      <span>Alert automatically generated in status <strong>{analysisResult.alert.status}</strong></span>
                      <button
                        onClick={() => onNavigate('alerts')}
                        className="font-semibold text-sky-700 hover:text-sky-900 flex items-center gap-1"
                      >
                        Inspect in Alerts Queue <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  )}
                </div>
              ) : null}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
