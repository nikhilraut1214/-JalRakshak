import React, { useEffect, useState, useCallback } from 'react';
import { Alert } from '../types';
import { api } from '../api';
import { translations, SupportedLanguage } from '../i18n';
import { EvidenceCard } from '../components/EvidenceCard';
import { FileSearch, RefreshCw, AlertTriangle, Layers } from 'lucide-react';

interface EvidenceViewProps {
  language: SupportedLanguage;
}

export const EvidenceView: React.FC<EvidenceViewProps> = ({ language }) => {
  const t = translations[language];
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEvidence = useCallback(async (showLoading = false) => {
    if (showLoading) setLoading(true);
    try {
      const data = await api.getAlerts();
      setAlerts(data.filter((a) => a.evidence !== null && a.evidence !== undefined));
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
          setAlerts(data.filter((a) => a.evidence !== null && a.evidence !== undefined));
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
          <h2 className="text-xl font-bold text-slate-900">{t.incidentEvidence}</h2>
          <p className="text-xs text-slate-500">{t.evidenceSubtitle}</p>
        </div>
        <button
          onClick={() => fetchEvidence(true)}
          disabled={loading}
          aria-label={t.refresh}
          className="px-3 py-2 text-xs font-medium text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 rounded-lg transition flex items-center gap-1.5 self-start"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          {t.refresh}
        </button>
      </div>

      {/* Information Banner */}
      <div className="bg-sky-50 border border-sky-200 rounded-xl p-4 text-xs text-sky-900 space-y-1">
        <div className="font-bold flex items-center gap-1.5">
          <Layers className="w-4 h-4 text-sky-700" />
          {t.evidencePrincipleTitle}
        </div>
        <p className="text-sky-800">
          {t.evidencePrincipleDesc}
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Evidence Cards List */}
      <div className="space-y-6">
        {alerts.length > 0 ? (
          alerts.map((a) => (
            <div key={a.id} className="space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span className="font-semibold text-slate-700">{t.incidentDetails} #{a.id.slice(0, 8)} · {t.meterIdLabel}: {a.meter_id.slice(0, 8)}...</span>
                <span>{t.status}: <strong className="text-slate-800">{a.status}</strong> · {t.detectedAt}: {new Date(a.created_at).toLocaleString()}</span>
              </div>
              {a.evidence && (
                <EvidenceCard
                  evidence={a.evidence}
                  language={language}
                  title={`${t.incidentEvidence} (${a.status})`}
                  showBreakdown={true}
                />
              )}
            </div>
          ))
        ) : (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-slate-400 space-y-2">
            <FileSearch className="w-8 h-8 mx-auto text-slate-300" />
            <div className="text-sm font-medium text-slate-600">{t.noData}</div>
            <div className="text-xs">Run a scenario in the Scenario Lab to generate seeded evidence.</div>
          </div>
        )}
      </div>
    </div>
  );
};
