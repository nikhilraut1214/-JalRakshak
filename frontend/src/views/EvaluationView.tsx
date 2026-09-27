import React, { useState } from 'react';
import { translations, SupportedLanguage } from '../i18n';
import { api } from '../api';
import { EvaluationBenchmarkResult } from '../types';
import { ShieldCheck, Play, CheckCircle2, AlertCircle, Clock, Cpu, BarChart2, Check, RefreshCw } from 'lucide-react';
import clsx from 'clsx';

interface EvaluationViewProps {
  language: SupportedLanguage;
}

export const EvaluationView: React.FC<EvaluationViewProps> = ({ language }) => {
  const t = translations[language];
  const [evaluating, setEvaluating] = useState(false);
  const [evalResults, setEvalResults] = useState<EvaluationBenchmarkResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runBenchmark = async () => {
    try {
      setEvaluating(true);
      setError(null);
      const data = await api.runEvaluation(42);
      setEvalResults(data);
    } catch (err: any) {
      console.error(err);
      setError(err?.message || 'Failed to execute benchmark evaluation');
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">{t.evaluation}</h2>
          <p className="text-xs text-slate-500">
            System performance evaluation, algorithmic benchmarks, and ground-truth validation
          </p>
        </div>
        <button
          onClick={runBenchmark}
          disabled={evaluating}
          className="px-4 py-2 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 disabled:bg-slate-400 rounded-lg transition flex items-center gap-1.5 self-start cursor-pointer shadow-xs"
        >
          {evaluating ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              Evaluating Benchmark Matrix...
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-white" />
              Run Benchmark Evaluation
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 p-3 rounded-xl text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Honest Metric Reporting Guard */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs text-slate-700 space-y-1">
        <div className="font-bold flex items-center gap-1.5 text-slate-900">
          <ShieldCheck className="w-4 h-4 text-sky-700" />
          Scientific Ground-Truth Reporting Standards
        </div>
        <p>
          Metrics are reported only when verified against seeded scenarios or empirical runtime measurements. Features lacking longitudinal production telemetry are explicitly reported as <strong>Not yet measured</strong>.
        </p>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Card 1: Classification Performance */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">Benchmark F1 Score</span>
            <BarChart2 className="w-4 h-4 text-sky-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {evalResults?.classification?.f1 !== undefined && evalResults.classification.f1 !== null
              ? evalResults.classification.f1.toFixed(2)
              : '—'}
          </div>
          <div className="text-[11px] text-slate-500 flex items-center justify-between pt-1 border-t border-slate-100">
            <span>
              Precision: {evalResults?.classification?.precision !== undefined && evalResults.classification.precision !== null
                ? evalResults.classification.precision.toFixed(2)
                : '—'}
            </span>
            <span>
              Recall: {evalResults?.classification?.recall !== undefined && evalResults.classification.recall !== null
                ? evalResults.classification.recall.toFixed(2)
                : '—'}
            </span>
          </div>
        </div>

        {/* Card 2: Ground-Truth Alignment & Confusion Matrix */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">Confusion Matrix & Alert Rate</span>
            <Check className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 font-mono text-xs rounded font-semibold border border-emerald-200">
              TP: {evalResults?.classification?.confusion_matrix ? evalResults.classification.confusion_matrix.true_positives : '—'}
            </span>
            <span className="px-2 py-0.5 bg-blue-50 text-blue-700 font-mono text-xs rounded font-semibold border border-blue-200">
              TN: {evalResults?.classification?.confusion_matrix ? evalResults.classification.confusion_matrix.true_negatives : '—'}
            </span>
            <span className="px-2 py-0.5 bg-amber-50 text-amber-700 font-mono text-xs rounded font-semibold border border-amber-200">
              FP: {evalResults?.classification?.confusion_matrix ? evalResults.classification.confusion_matrix.false_positives : '—'}
            </span>
            <span className="px-2 py-0.5 bg-rose-50 text-rose-700 font-mono text-xs rounded font-semibold border border-rose-200">
              FN: {evalResults?.classification?.confusion_matrix ? evalResults.classification.confusion_matrix.false_negatives : '—'}
            </span>
          </div>
          <div className="text-[11px] text-slate-500 pt-1 border-t border-slate-100">
            False Alert Rate:{' '}
            <span className="font-semibold text-slate-700">
              {evalResults?.classification?.false_alert_rate !== undefined && evalResults.classification.false_alert_rate !== null
                ? `${(evalResults.classification.false_alert_rate * 100).toFixed(1)}%`
                : '—'}
            </span>
          </div>
        </div>

        {/* Card 3: Measured Latency */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">Operational Latency</span>
            <Clock className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {evalResults?.latency?.avg_processing_latency_ms !== undefined
              ? `${evalResults.latency.avg_processing_latency_ms.toFixed(2)} ms`
              : '—'}
          </div>
          <div className="text-[11px] text-slate-500 pt-1 border-t border-slate-100 flex items-center justify-between">
            <span>
              Range: {evalResults?.latency ? `${evalResults.latency.min_processing_latency_ms.toFixed(2)} – ${evalResults.latency.max_processing_latency_ms.toFixed(2)} ms` : '—'}
            </span>
            <span className="truncate max-w-[130px]" title={evalResults?.latency?.measurement_scope}>
              In-process analytics
            </span>
          </div>
        </div>

        {/* Card 4: Numerical Accuracy (MAE) */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">Numerical Accuracy (MAE)</span>
            <BarChart2 className="w-4 h-4 text-cyan-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {evalResults?.numerical_accuracy?.benchmark_mae !== undefined && evalResults.numerical_accuracy.benchmark_mae !== null
              ? `${evalResults.numerical_accuracy.benchmark_mae.toFixed(2)} L`
              : '—'}
          </div>
          <div className="text-[11px] text-slate-500 pt-1 border-t border-slate-100 flex items-center justify-between">
            <span>Benchmark MAE</span>
            <span className="font-semibold text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded">
              Field: {evalResults?.numerical_accuracy?.field_telemetry_mae_status || 'Not yet measured'}
            </span>
          </div>
        </div>

        {/* Card 5: AI & Fallback Reliability */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">AI & Fallback Coverage</span>
            <Cpu className="w-4 h-4 text-violet-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {evalResults?.ai_metrics?.fallback_coverage_rate !== undefined
              ? `${evalResults.ai_metrics.fallback_coverage_rate.toFixed(0)}%`
              : '—'}
          </div>
          <div className="text-[11px] text-slate-500 pt-1 border-t border-slate-100 flex items-center justify-between">
            <span>Fallback: en, mr, hi</span>
            <span className="text-slate-700 font-medium">
              {evalResults?.ai_metrics?.groq_configured ? 'Live Groq + Fallback' : 'Offline Fallback'}
            </span>
          </div>
        </div>

        {/* Card 6: Alert Workflow Completion */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">Alert Workflow Completion</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {evalResults?.workflow?.completion_rate !== undefined
              ? `${evalResults.workflow.completion_rate.toFixed(0)}%`
              : '—'}
          </div>
          <div className="text-[11px] text-slate-500 pt-1 border-t border-slate-100 flex items-center justify-between">
            <span>
              {evalResults?.workflow ? `${evalResults.workflow.steps_completed}/${evalResults.workflow.steps_total} steps verified` : '—'}
            </span>
            <span className="text-emerald-700 font-semibold">
              {evalResults?.workflow?.workflow_tested ? 'DETECTED → RESOLVED' : 'Not tested'}
            </span>
          </div>
        </div>
      </div>

      {/* Scenario Benchmark Breakdown */}
      {evalResults && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h3 className="text-sm font-bold text-slate-900">
                Seeded Scenario Ground-Truth Benchmark Results
              </h3>
              <p className="text-xs text-slate-500">
                Evaluated {evalResults.scenarios_tested} scenarios with deterministic seed against ground-truth intent
              </p>
            </div>
            <div className="text-xs text-slate-500 font-mono">
              Scope: {evalResults.latency.measurement_scope}
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase">
                <tr>
                  <th className="py-2.5 px-3">Scenario</th>
                  <th className="py-2.5 px-3">Ground Truth</th>
                  <th className="py-2.5 px-3">Alert (Exp / Act)</th>
                  <th className="py-2.5 px-3">Class</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Risk</th>
                  <th className="py-2.5 px-3">Excess (L)</th>
                  <th className="py-2.5 px-3">Latency</th>
                  <th className="py-2.5 px-3">Result</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {evalResults.items.map((row, i) => (
                  <tr key={i} className="hover:bg-slate-50 transition-colors">
                    <td className="py-2.5 px-3 font-semibold text-slate-800">{row.scenario}</td>
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-600">{row.ground_truth}</td>
                    <td className="py-2.5 px-3 text-slate-700">
                      {row.expected_alert === null || row.expected_alert === undefined ? (
                        <span className="text-slate-500 italic">
                          {row.classification === 'GUARDRAIL_PASS' ? 'Guard (None)' : 'Contextual'}
                        </span>
                      ) : (
                        <>
                          <span className={clsx('font-medium', row.expected_alert ? 'text-amber-700' : 'text-slate-600')}>
                            {row.expected_alert ? 'Alert' : 'None'}
                          </span>
                          {' / '}
                          <span className={clsx('font-medium', row.actual_alert ? 'text-amber-700' : 'text-slate-600')}>
                            {row.actual_alert ? 'Alert' : 'None'}
                          </span>
                        </>
                      )}
                    </td>
                    <td className="py-2.5 px-3 font-bold font-mono">
                      <span
                        className={clsx(
                          'px-1.5 py-0.5 rounded text-[10px]',
                          row.classification === 'TP' && 'bg-emerald-100 text-emerald-800',
                          row.classification === 'TN' && 'bg-blue-100 text-blue-800',
                          row.classification === 'FP' && 'bg-amber-100 text-amber-800',
                          row.classification === 'FN' && 'bg-rose-100 text-rose-800',
                          row.classification === 'GUARDRAIL_PASS' && 'bg-purple-100 text-purple-800',
                          row.classification === 'CONTEXTUAL_PASS' && 'bg-cyan-100 text-cyan-800'
                        )}
                      >
                        {row.classification}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-700">{row.status}</td>
                    <td className="py-2.5 px-3 font-medium text-slate-800">{row.severity}</td>
                    <td className="py-2.5 px-3 font-bold text-slate-900">{row.risk_score.toFixed(1)}</td>
                    <td className="py-2.5 px-3 text-slate-700 font-mono">{row.estimated_excess_liters.toFixed(1)}</td>
                    <td className="py-2.5 px-3 text-slate-600 font-mono">{row.processing_latency_ms.toFixed(2)} ms</td>
                    <td className="py-2.5 px-3">
                      {row.passed ? (
                        <span className="inline-flex items-center gap-1 text-emerald-700 font-semibold">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Pass
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-rose-700 font-semibold">
                          <AlertCircle className="w-3.5 h-3.5" /> Fail
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
