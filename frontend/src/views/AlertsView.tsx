import React, { useEffect, useState } from 'react';
import { Alert } from '../types';
import { api } from '../api';
import { translations, SupportedLanguage } from '../i18n';
import { SeverityBadge } from '../components/SeverityBadge';
import { AlertDetailModal } from '../components/AlertDetailModal';
import { AlertTriangle, Filter, RefreshCw, Eye } from 'lucide-react';

interface AlertsViewProps {
  language: SupportedLanguage;
}

export const AlertsView: React.FC<AlertsViewProps> = ({ language }) => {
  const t = translations[language];
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getAlerts({
        severity: severityFilter || undefined,
        status: statusFilter || undefined,
      });
      setAlerts(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [severityFilter, statusFilter]);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">{t.alerts}</h2>
          <p className="text-xs text-slate-500">Anomaly alerts requiring human verification or lifecycle resolution</p>
        </div>
        <button
          onClick={fetchAlerts}
          className="px-3 py-2 text-xs font-medium text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 rounded-lg transition flex items-center gap-1.5 self-start"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          {t.refresh}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center gap-4 text-xs">
        <div className="flex items-center gap-2 font-medium text-slate-700">
          <Filter className="w-3.5 h-3.5 text-slate-500" />
          Filters:
        </div>

        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="border border-slate-300 rounded-md px-3 py-1.5 bg-white text-slate-800 focus:ring-1 focus:ring-sky-500 outline-none"
        >
          <option value="">{t.allSeverities}</option>
          <option value="CRITICAL">CRITICAL</option>
          <option value="HIGH">HIGH</option>
          <option value="MEDIUM">MEDIUM</option>
          <option value="LOW">LOW</option>
        </select>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="border border-slate-300 rounded-md px-3 py-1.5 bg-white text-slate-800 focus:ring-1 focus:ring-sky-500 outline-none"
        >
          <option value="">{t.allStatuses}</option>
          <option value="DETECTED">DETECTED</option>
          <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
          <option value="VERIFYING">VERIFYING</option>
          <option value="INVESTIGATING">INVESTIGATING</option>
          <option value="CONFIRMED">CONFIRMED</option>
          <option value="FALSE_ALARM">FALSE_ALARM</option>
          <option value="RESOLVED">RESOLVED</option>
        </select>
      </div>

      {/* Alerts Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase">
              <tr>
                <th className="py-3 px-4">Severity & Risk</th>
                <th className="py-3 px-4">Lifecycle Status</th>
                <th className="py-3 px-4">Meter ID</th>
                <th className="py-3 px-4">Excess Est.</th>
                <th className="py-3 px-4">Detected At</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {alerts.length > 0 ? (
                alerts.map((a) => (
                  <tr key={a.id} className="hover:bg-slate-50 transition">
                    <td className="py-3 px-4">
                      <SeverityBadge severity={a.severity} riskScore={a.risk_score} />
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-block px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-800 border border-slate-200">
                        {a.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-600">{a.meter_id.slice(0, 8)}...</td>
                    <td className="py-3 px-4 font-bold text-slate-800">
                      {a.evidence ? `${a.evidence.estimated_excess_liters} L` : '—'}
                    </td>
                    <td className="py-3 px-4 text-slate-500">{new Date(a.created_at).toLocaleString()}</td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => setSelectedAlert(a)}
                        className="px-2.5 py-1 text-xs font-medium rounded-md bg-sky-50 text-sky-700 border border-sky-200 hover:bg-sky-100 transition inline-flex items-center gap-1"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        Inspect & Action
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-400">
                    No alerts match the selected criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {selectedAlert && (
        <AlertDetailModal
          alert={selectedAlert}
          language={language}
          onClose={() => setSelectedAlert(null)}
          onAlertUpdated={(updated) => {
            setSelectedAlert(null);
            fetchAlerts();
          }}
        />
      )}
    </div>
  );
};
