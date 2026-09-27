import React, { useEffect, useState, useCallback } from 'react';
import { Alert } from '../types';
import { api } from '../api';
import { translations, SupportedLanguage } from '../i18n';
import { SeverityBadge } from '../components/SeverityBadge';
import { AlertDetailModal } from '../components/AlertDetailModal';
import { CheckSquare, RefreshCw, AlertTriangle, ShieldCheck, ChevronRight } from 'lucide-react';

interface VerificationViewProps {
  language: SupportedLanguage;
}

export const VerificationView: React.FC<VerificationViewProps> = ({ language }) => {
  const t = translations[language];
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  const fetchPendingVerifications = useCallback(async (showLoading = false) => {
    if (showLoading) setLoading(true);
    try {
      const data = await api.getAlerts();
      setAlerts(data.filter((a) => !['RESOLVED', 'FALSE_ALARM'].includes(a.status)));
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let ignore = false;
    api.getAlerts()
      .then((data) => {
        if (!ignore) {
          setAlerts(data.filter((a) => !['RESOLVED', 'FALSE_ALARM'].includes(a.status)));
          setError(null);
        }
      })
      .catch((err: any) => {
        if (!ignore) {
          setError(err.message);
        }
      });
    return () => {
      ignore = true;
    };
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">{t.verificationViewTitle}</h2>
          <p className="text-xs text-slate-500">{t.verificationViewSubtitle}</p>
        </div>
        <button
          onClick={() => fetchPendingVerifications(true)}
          disabled={loading}
          aria-label={t.refresh}
          className="px-3 py-2 text-xs font-medium text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 rounded-lg transition flex items-center gap-1.5 self-start"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          {t.refresh}
        </button>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-900 space-y-1">
        <div className="font-bold flex items-center gap-1.5">
          <ShieldCheck className="w-4 h-4 text-amber-700" />
          {t.physicalVerificationRequired}
        </div>
        <p className="text-amber-800">
          Under JalRakshak AI principles, algorithmic anomaly detection does not physically confirm leaks. Only an authorized human operator or resident can verify the physical status of fixtures and meters.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Verification Queue */}
      <div className="space-y-4">
        {alerts.length > 0 ? (
          alerts.map((a) => (
            <div
              key={a.id}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
            >
              <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                  <SeverityBadge severity={a.severity} riskScore={a.risk_score} />
                  <span className="px-2 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-800 border border-slate-200">
                    {a.status}
                  </span>
                  <span className="text-xs font-mono text-slate-400">Incident #{a.id.slice(0, 8)}</span>
                </div>
                <div className="text-sm font-semibold text-slate-800">
                  {t.meterId}: {a.meter_id}
                </div>
                {a.evidence && (
                  <div className="text-xs text-slate-600 flex flex-wrap gap-x-4 gap-y-1">
                    <span>{t.currentReading}: <strong>{a.evidence.current_usage_liters} L</strong></span>
                    <span>{t.expectedBaseline}: <strong>{a.evidence.baseline_liters} L</strong></span>
                    <span className="text-rose-600">{t.deviation}: <strong>+{a.evidence.deviation_pct}%</strong></span>
                    <span className="text-amber-700">{t.estimatedExcess}: <strong>{a.evidence.estimated_excess_liters} L</strong></span>
                  </div>
                )}
              </div>

              <button
                onClick={() => setSelectedAlert(a)}
                className="px-4 py-2 text-xs font-semibold rounded-lg bg-sky-600 text-white hover:bg-sky-700 transition flex items-center gap-1.5 shrink-0"
              >
                {t.beginVerification}
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          ))
        ) : (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-slate-400 space-y-2">
            <CheckSquare className="w-8 h-8 mx-auto text-emerald-400" />
            <div className="text-sm font-medium text-slate-700">{t.noPendingVerifications}</div>
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
            fetchPendingVerifications(true);
          }}
        />
      )}
    </div>
  );
};
