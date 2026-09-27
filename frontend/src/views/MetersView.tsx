import React, { useEffect, useState, useCallback, useRef } from 'react';
import { Meter, AnalyzeResult } from '../types';
import { api } from '../api';
import { translations, SupportedLanguage } from '../i18n';
import { EvidenceCard } from '../components/EvidenceCard';
import { useFocusTrap } from '../hooks/useFocusTrap';
import { Gauge, Plus, RefreshCw, AlertTriangle, Info, X } from 'lucide-react';

interface MetersViewProps {
  language: SupportedLanguage;
}

export const MetersView: React.FC<MetersViewProps> = ({ language }) => {
  const t = translations[language];
  const [meters, setMeters] = useState<Meter[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [name, setName] = useState('');
  const [locationLabel, setLocationLabel] = useState('');
  const [meterType, setMeterType] = useState('water');
  const [analysisResult, setAnalysisResult] = useState<AnalyzeResult | null>(null);
  const [analyzingMeterId, setAnalyzingMeterId] = useState<string | null>(null);

  const openCreateModalButtonRef = useRef<HTMLButtonElement | null>(null);
  const firstInputRef = useRef<HTMLInputElement | null>(null);

  const modalRef = useFocusTrap<HTMLDivElement>({
    isOpen: showCreateModal,
    onClose: () => setShowCreateModal(false),
    initialFocusRef: firstInputRef,
    triggerRef: openCreateModalButtonRef,
  });

  const fetchMeters = useCallback(async (showLoading = false) => {
    if (showLoading) setLoading(true);
    try {
      const data = await api.getMeters();
      setMeters(data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let ignore = false;
    api.getMeters()
      .then((data) => {
        if (!ignore) {
          setMeters(data);
          setError(null);
          setLoading(false);
        }
      })
      .catch((err: any) => {
        if (!ignore) {
          setError(err.message);
          setLoading(false);
        }
      });
    return () => {
      ignore = true;
    };
  }, []);

  const handleCreateMeter = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      await api.createMeter({ name, location_label: locationLabel, meter_type: meterType });
      setShowCreateModal(false);
      setName('');
      setLocationLabel('');
      fetchMeters(true);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async (meterId: string) => {
    try {
      setAnalyzingMeterId(meterId);
      setError(null);
      const res = await api.analyzeMeter(meterId);
      setAnalysisResult(res);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setAnalyzingMeterId(null);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">{t.meters}</h2>
          <p className="text-xs text-slate-500">{t.activeMetersList}</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => fetchMeters(true)}
            aria-label={t.refresh}
            className="px-3 py-2 text-xs font-medium text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 rounded-lg transition flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            {t.refresh}
          </button>
          <button
            ref={openCreateModalButtonRef}
            onClick={() => setShowCreateModal(true)}
            className="px-3.5 py-2 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded-lg transition flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" />
            {t.registerNewMeter}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Analysis Output Panel if recently run */}
      {analysisResult && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
              {t.analyticsOutcomeTitle}
            </h3>
            <button
              onClick={() => setAnalysisResult(null)}
              className="text-xs text-slate-400 hover:text-slate-600"
            >
              {t.close}
            </button>
          </div>

          {analysisResult.status === 'INSUFFICIENT_HISTORY' ? (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-1.5 text-xs text-amber-900">
              <div className="font-bold flex items-center gap-1.5">
                <Info className="w-4 h-4 text-amber-700" />
                {t.insufficientHistory}
              </div>
              <p>{analysisResult.insufficient_history?.message}</p>
              <div className="text-[11px] text-amber-800">
                Found {analysisResult.insufficient_history?.readings_count} reading(s). Minimum {analysisResult.insufficient_history?.required_count} readings required to establish a baseline.
              </div>
            </div>
          ) : analysisResult.evidence ? (
            <EvidenceCard
              evidence={analysisResult.evidence}
              language={language}
              title={`Meter #${analysisResult.meter_id.slice(0, 8)} Analysis`}
            />
          ) : null}
        </div>
      )}

      {/* Meters Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">{t.meterName}</th>
                <th className="py-3 px-4">{t.zone}</th>
                <th className="py-3 px-4">{t.category}</th>
                <th className="py-3 px-4">{t.meterId}</th>
                <th className="py-3 px-4 text-right">{t.actions}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {meters.length > 0 ? (
                meters.map((meter) => (
                  <tr key={meter.id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3 px-4 font-semibold text-slate-900 flex items-center gap-2">
                      <Gauge className="w-4 h-4 text-sky-600 shrink-0" />
                      {meter.name}
                    </td>
                    <td className="py-3 px-4 text-slate-600">{meter.location_label}</td>
                    <td className="py-3 px-4 text-slate-600 capitalize">{meter.meter_type}</td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-400">{meter.id}</td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleAnalyze(meter.id)}
                        disabled={analyzingMeterId === meter.id}
                        className="px-2.5 py-1 text-xs font-medium rounded-md bg-sky-50 text-sky-700 border border-sky-200 hover:bg-sky-100 transition"
                      >
                        {analyzingMeterId === meter.id ? t.loading : 'Analyze'}
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-400">
                    {t.noMetersFound}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Meter Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div
            ref={modalRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby="create-meter-title"
            className="bg-white rounded-xl shadow-lg border border-slate-200 w-full max-w-md p-6 space-y-4 animate-in fade-in zoom-in-95 duration-150"
          >
            <div className="flex items-center justify-between border-b border-slate-100 pb-2">
              <h3 id="create-meter-title" className="text-base font-bold text-slate-900">
                {t.registerNewMeter}
              </h3>
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                aria-label={t.closeModal}
                className="p-1 rounded text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreateMeter} className="space-y-4 text-xs">
              <div>
                <label htmlFor="meter-name" className="block font-medium text-slate-700 mb-1">
                  {t.meterName}
                </label>
                <input
                  ref={firstInputRef}
                  id="meter-name"
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g., Block B Primary Inflow"
                  className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-1 focus:ring-sky-500 outline-none"
                />
              </div>

              <div>
                <label htmlFor="location-label" className="block font-medium text-slate-700 mb-1">
                  {t.zone}
                </label>
                <input
                  id="location-label"
                  type="text"
                  required
                  value={locationLabel}
                  onChange={(e) => setLocationLabel(e.target.value)}
                  placeholder="e.g., Sector 4, Building 2"
                  className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-1 focus:ring-sky-500 outline-none"
                />
              </div>

              <div>
                <label htmlFor="meter-type" className="block font-medium text-slate-700 mb-1">
                  {t.category}
                </label>
                <select
                  id="meter-type"
                  value={meterType}
                  onChange={(e) => setMeterType(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-1 focus:ring-sky-500 outline-none bg-white"
                >
                  <option value="water">{t.residential}</option>
                  <option value="irrigation">{t.agricultural}</option>
                  <option value="commercial">{t.commercial}</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded-md"
                >
                  {t.cancel}
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-1.5 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded-md"
                >
                  {t.registerButton}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
