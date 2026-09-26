import React, { useEffect, useState } from 'react';
import { DashboardSummary, Alert } from '../types';
import { api } from '../api';
import { translations, SupportedLanguage } from '../i18n';
import { SeverityBadge } from '../components/SeverityBadge';
import { EvidenceCard } from '../components/EvidenceCard';
import { AlertDetailModal } from '../components/AlertDetailModal';
import {
  Activity,
  AlertTriangle,
  Droplet,
  Gauge,
  TrendingUp,
  ShieldAlert,
  ArrowRight,
  Info,
  RefreshCw,
} from 'lucide-react';

interface DashboardViewProps {
  language: SupportedLanguage;
  onNavigate: (module: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  language,
  onNavigate,
}) => {
  const t = translations[language];
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getDashboardSummary();
      setSummary(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  if (loading && !summary) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-3 text-slate-500 text-sm">
          <RefreshCw className="w-5 h-5 animate-spin text-sky-600" />
          Loading authoritative analytics...
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Banner / Next Action Guidance */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <div className="text-xs font-semibold text-sky-700 uppercase tracking-wider mb-1">
            {t.nextAction}
          </div>
          <div className="text-base font-semibold text-slate-900">
            {summary?.next_verification_action || 'Monitoring active consumption streams.'}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchSummary}
            className="px-3 py-1.5 text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-md transition flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            {t.refresh}
          </button>
          <button
            onClick={() => onNavigate('scenario_lab')}
            className="px-3 py-1.5 text-xs font-medium text-white bg-sky-600 hover:bg-sky-700 rounded-md transition flex items-center gap-1.5"
          >
            Run Seeded Scenario
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Total Meters */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">{t.totalMeters}</span>
            <Gauge className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {summary?.total_meters ?? 0}
          </div>
          <div className="text-[11px] text-slate-400">Authorized for active role</div>
        </div>

        {/* Active Alerts */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">{t.activeAlerts}</span>
            <AlertTriangle className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {summary?.active_alerts_count ?? 0}
          </div>
          <div className="text-[11px] text-amber-700 font-medium">
            {summary?.critical_alerts_count ?? 0} Critical · {summary?.high_alerts_count ?? 0} High
          </div>
        </div>

        {/* Latest Aggregate Consumption */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">{t.recentConsumption}</span>
            <Droplet className="w-4 h-4 text-sky-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900">
            {summary?.recent_consumption_liters?.toLocaleString() ?? 0} <span className="text-xs font-normal text-slate-500">Liters</span>
          </div>
          <div className="text-[11px] text-slate-400">
            Baseline: {summary?.expected_baseline_liters?.toLocaleString() ?? 0} L
          </div>
        </div>

        {/* Max Risk & Overall Severity */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-1">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-medium">{t.overallSeverity}</span>
            <ShieldAlert className="w-4 h-4 text-rose-500" />
          </div>
          <div className="pt-0.5">
            <SeverityBadge
              severity={summary?.overall_severity || 'LOW'}
              riskScore={summary?.max_risk_score ?? 0}
              size="md"
            />
          </div>
          <div className="text-[11px] text-slate-400">Analytical score (not probability)</div>
        </div>
      </div>

      {/* Insufficient History Warning (Design System Section 8) */}
      {summary && summary.insufficient_history_meters_count > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 space-y-2">
          <div className="flex items-center gap-2 text-amber-900 font-semibold text-sm">
            <Info className="w-4 h-4 text-amber-700" />
            {t.insufficientHistory} ({summary.insufficient_history_meters_count} Meter{summary.insufficient_history_meters_count > 1 ? 's' : ''})
          </div>
          <p className="text-xs text-amber-800 leading-relaxed">
            {t.insufficientHistoryDesc}
          </p>
          <div className="pt-1">
            <button
              onClick={() => onNavigate('readings')}
              className="text-xs font-medium text-amber-900 underline hover:text-amber-950"
            >
              Go to Readings / Import to add readings →
            </button>
          </div>
        </div>
      )}

      {/* Evidence Highlights */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
            {t.evidenceHierarchyTitle}
          </h2>
          <button
            onClick={() => onNavigate('evidence')}
            className="text-xs text-sky-700 hover:text-sky-800 font-medium"
          >
            View all evidence streams →
          </button>
        </div>

        {summary && summary.evidence_highlights.length > 0 ? (
          <div className="grid grid-cols-1 gap-4">
            {summary.evidence_highlights.map((ev, idx) => (
              <EvidenceCard key={idx} evidence={ev} title={`Incident Evidence Stream #${idx + 1}`} />
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-500 text-sm">
            <Activity className="w-8 h-8 text-slate-300 mx-auto mb-2" />
            No elevated anomaly streams detected. All meters are within expected baseline intervals.
          </div>
        )}
      </div>

      {selectedAlert && (
        <AlertDetailModal
          alert={selectedAlert}
          language={language}
          onClose={() => setSelectedAlert(null)}
          onAlertUpdated={() => {
            setSelectedAlert(null);
            fetchSummary();
          }}
        />
      )}
    </div>
  );
};
