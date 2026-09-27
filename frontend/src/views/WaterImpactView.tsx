import React, { useState, useEffect, useCallback } from 'react';
import { translations, SupportedLanguage } from '../i18n';
import { api } from '../api';
import { WaterImpactSummaryResponse } from '../types';
import {
  Droplet, Info, Calculator, TrendingUp, AlertTriangle,
  CheckCircle2, RefreshCw, Sprout, ShieldAlert
} from 'lucide-react';

interface WaterImpactViewProps {
  language: SupportedLanguage;
}

export const WaterImpactView: React.FC<WaterImpactViewProps> = ({ language }) => {
  const t = translations[language];
  const [avoidedFraction, setAvoidedFraction] = useState(0.70); // 70% documented default assumption
  const [selectedMeterId, setSelectedMeterId] = useState<string | undefined>(undefined);
  const [data, setData] = useState<WaterImpactSummaryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchImpact = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getWaterImpact(avoidedFraction, selectedMeterId);
      setData(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to load water impact data');
    } finally {
      setLoading(false);
    }
  }, [avoidedFraction, selectedMeterId]);

  useEffect(() => {
    fetchImpact();
  }, [fetchImpact]);

  const potentialSavings = data?.potential_savings_liters ?? 0;
  const totalExcess = data?.total_estimated_excess_liters ?? 0;
  const activeCount = data?.active_anomalies_count ?? 0;
  const agriCount = data?.contextual_agricultural_meters_count ?? 0;
  const agriExcess = data?.contextual_agricultural_excess_liters ?? 0;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Droplet className="w-5 h-5 text-sky-600" />
            {t.waterImpact}
          </h2>
          <p className="text-xs text-slate-500">
            Authoritative deterministic excess metrics & analytical potential savings projections
          </p>
        </div>
        <button
          onClick={fetchImpact}
          disabled={loading}
          className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors shadow-2xs cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-sky-600' : 'text-slate-500'}`} />
          {t.refresh}
        </button>
      </div>

      {/* Trust Notice (Design System Section 17 & Phase 4) */}
      <div className="bg-sky-50 border border-sky-200 rounded-xl p-4 text-xs text-sky-900 space-y-1">
        <div className="font-bold flex items-center gap-1.5 text-sky-900">
          <Info className="w-4 h-4 text-sky-700" />
          Estimation Disclosure & Authority Boundaries
        </div>
        <p className="text-sky-800">
          Estimated excess water is computed deterministically by the analytics engine using baseline deviations and persistence intervals: <code className="bg-sky-100/80 px-1 py-0.5 rounded font-mono">max(observed - baseline, 0) × persistence</code>.
          Potential savings values are analytical projections based on user-configured assumption fractions (e.g. prompt human shutoff avoiding an assumed fraction of subsequent excess). They are <strong>never presented as guaranteed physical measurements</strong>.
        </p>
      </div>

      {error && (
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-xs text-rose-800 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Interactive Controls & Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Assumption Slider & Scope Selector */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-2xs space-y-4">
          <div className="font-bold text-sm text-slate-900 flex items-center gap-2">
            <Calculator className="w-4 h-4 text-sky-600" />
            Impact Assumption Parameters
          </div>

          <div className="space-y-4 text-xs">
            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>Avoided Fraction Assumption:</span>
                <span className="font-bold text-sky-700">{Math.round(avoidedFraction * 100)}%</span>
              </div>
              <input
                type="range"
                min="0.10"
                max="0.95"
                step="0.05"
                value={avoidedFraction}
                onChange={(e) => setAvoidedFraction(parseFloat(e.target.value))}
                className="w-full accent-sky-600 cursor-pointer"
              />
              <div className="text-[11px] text-slate-500 mt-1">
                Hypothetical portion of ongoing excess prevented through prompt human verification and shutoff.
                <span className="block font-semibold text-slate-600 mt-0.5">
                  (Assumption, not measured physical savings)
                </span>
              </div>
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">
                Scope Filter:
              </label>
              <select
                value={selectedMeterId !== undefined ? selectedMeterId : ''}
                onChange={(e) => {
                  const val = e.target.value;
                  setSelectedMeterId(val ? val : undefined);
                }}
                className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-sky-500 bg-white text-slate-800 outline-none"
              >
                <option value="">All Authorized Active Anomalies (Aggregate)</option>
                {data?.items.map((item) => (
                  <option key={item.meter_id} value={item.meter_id}>
                    {item.meter_code} ({item.meter_type}) - {item.location_label || 'Location N/A'} [{item.severity}]
                  </option>
                ))}
              </select>
              <div className="text-[11px] text-slate-500 mt-1">
                Filter potential savings calculation to a specific active meter or view aggregate authorized meters.
              </div>
            </div>
          </div>
        </div>

        {/* Projected Avoided Loss Output */}
        <div className="bg-gradient-to-br from-sky-50 via-white to-sky-50/40 p-5 rounded-xl border border-sky-200 shadow-2xs space-y-4 flex flex-col justify-between">
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-sky-800">
                Projected Avoided Water Loss
              </span>
              <span className="text-[10px] font-medium bg-sky-100 text-sky-800 px-2 py-0.5 rounded-full">
                {Math.round(avoidedFraction * 100)}% Avoidable Factor
              </span>
            </div>
            <div className="text-3xl font-extrabold text-sky-900">
              ~{potentialSavings.toLocaleString()} <span className="text-sm font-normal text-slate-600">Liters</span>
            </div>
            <div className="text-xs text-slate-500 pt-1 space-y-0.5">
              <div>
                Authoritative Excess Baseline: <strong className="text-slate-800">{totalExcess.toLocaleString()} L</strong> across {activeCount} domestic/commercial {activeCount === 1 ? 'anomaly' : 'anomalies'}.
              </div>
              <div className="font-mono text-[11px] text-slate-600">
                potential_savings = max(estimated_excess, 0) × avoided_fraction
              </div>
            </div>
          </div>

          <div className="bg-white p-3 rounded-lg border border-sky-100 text-xs text-slate-600 space-y-1 shadow-2xs">
            <div className="font-semibold text-slate-800 flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5 text-sky-600" />
              Equivalency Perspective:
            </div>
            <div>• ~{Math.round(potentialSavings / 20).toLocaleString()} standard 20L water cans saved.</div>
            <div>• ~{Math.round(potentialSavings / 150).toLocaleString()} daily drinking/sanitation allowances (at 150L/day/person).</div>
          </div>
        </div>
      </div>

      {/* Contextual Agricultural Notice (if any agricultural meters exist) */}
      {agriCount > 0 && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-xs text-emerald-900 space-y-1.5">
          <div className="font-bold flex items-center gap-1.5 text-emerald-900">
            <Sprout className="w-4 h-4 text-emerald-700" />
            Contextual Agricultural Operational Notice
          </div>
          <p className="text-emerald-800 leading-relaxed">
            <strong>{agriCount} agricultural {agriCount === 1 ? 'meter' : 'meters'}</strong> identified with <strong>{agriExcess.toLocaleString()} L</strong> consumption during scheduled irrigation windows.
            Under JalRakshak domain rules, scheduled agricultural irrigation pumping is classified as <strong>operational consumption</strong> and is explicitly <strong>excluded</strong> from domestic water waste and potential savings calculations.
          </p>
        </div>
      )}

      {/* Active Anomalies Breakdown Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
        <div className="p-4 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              Active Meter Breakdown ({data?.items.length ?? 0})
            </h3>
            <p className="text-xs text-slate-500">
              Deterministic excess values and projected savings per active meter
            </p>
          </div>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-slate-500 flex items-center justify-center gap-2">
            <RefreshCw className="w-4 h-4 animate-spin text-sky-600" />
            Loading authoritative water impact telemetry...
          </div>
        ) : !data || data.items.length === 0 ? (
          <div className="p-8 text-center space-y-2">
            <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto" />
            <div className="text-sm font-semibold text-slate-800">
              No Active Anomalies Detected
            </div>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              All authorized meters are operating within normal baseline consumption limits. Total estimated excess is 0 L, and potential savings is 0 L.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 font-medium">
                <tr>
                  <th className="py-2.5 px-4">Meter</th>
                  <th className="py-2.5 px-4">Type / Location</th>
                  <th className="py-2.5 px-4">Severity</th>
                  <th className="py-2.5 px-4 text-right">Usage (L)</th>
                  <th className="py-2.5 px-4 text-right">Baseline (L)</th>
                  <th className="py-2.5 px-4 text-right">Excess (L)</th>
                  <th className="py-2.5 px-4 text-right">Projected Savings (L)</th>
                  <th className="py-2.5 px-4 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.items.map((item) => (
                  <tr key={item.alert_id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3 px-4 font-mono font-medium text-slate-800">
                      {item.meter_code}
                    </td>
                    <td className="py-3 px-4 text-slate-600">
                      <div className="flex items-center gap-1.5">
                        <span className={`px-1.5 py-0.5 text-[10px] font-medium rounded ${
                          item.is_contextual_agricultural
                            ? 'bg-emerald-100 text-emerald-800'
                            : item.meter_type === 'commercial'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {item.meter_type}
                        </span>
                        <span>{item.location_label || 'N/A'}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 text-[10px] font-semibold rounded-full ${
                        item.severity === 'CRITICAL'
                          ? 'bg-rose-100 text-rose-800'
                          : item.severity === 'HIGH'
                          ? 'bg-orange-100 text-orange-800'
                          : item.severity === 'MEDIUM'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-slate-100 text-slate-800'
                      }`}>
                        {item.severity} ({Math.round(item.risk_score)})
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-slate-700">
                      {item.current_usage_liters.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-slate-500">
                      {item.baseline_liters.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-semibold text-rose-600">
                      +{item.estimated_excess_liters.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-sky-700">
                      {item.is_contextual_agricultural ? (
                        <span className="text-[11px] text-slate-400 font-normal italic">
                          Exempt (Operational)
                        </span>
                      ) : (
                        `~${item.potential_savings_liters.toLocaleString()} L`
                      )}
                    </td>
                    <td className="py-3 px-4 text-center">
                      {item.is_contextual_agricultural ? (
                        <span className="inline-flex items-center gap-1 text-[11px] text-emerald-700 font-medium">
                          <Sprout className="w-3.5 h-3.5" />
                          Contextual
                        </span>
                      ) : item.verification_required ? (
                        <span className="inline-flex items-center gap-1 text-[11px] text-amber-700 font-medium">
                          <ShieldAlert className="w-3.5 h-3.5" />
                          Verification Required
                        </span>
                      ) : (
                        <span className="text-[11px] text-slate-400">
                          Verified
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
