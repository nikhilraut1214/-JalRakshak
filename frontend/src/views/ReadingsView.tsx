import React, { useEffect, useState, useCallback } from 'react';
import { Meter, Reading } from '../types';
import { api } from '../api';
import { translations, SupportedLanguage } from '../i18n';
import {
  UploadCloud,
  Plus,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  FileText,
} from 'lucide-react';

interface ReadingsViewProps {
  language: SupportedLanguage;
}

export const ReadingsView: React.FC<ReadingsViewProps> = ({ language }) => {
  const t = translations[language];
  const [meters, setMeters] = useState<Meter[]>([]);
  const [selectedMeterId, setSelectedMeterId] = useState<string>('');
  const [readings, setReadings] = useState<Reading[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Manual reading state
  const [timestamp, setTimestamp] = useState(new Date().toISOString().slice(0, 16));
  const [liters, setLiters] = useState('');

  // CSV upload state
  const [csvFile, setCsvFile] = useState<File | null>(null);

  const loadReadings = useCallback(async (mId: string, showLoading = false) => {
    if (showLoading) setLoading(true);
    try {
      const data = await api.getMeterReadings(mId);
      setReadings(data);
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
      .then((m) => {
        if (!ignore) {
          setMeters(m);
          if (m.length > 0) {
            setSelectedMeterId(m[0].id);
          }
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

  useEffect(() => {
    if (!selectedMeterId) return;
    let ignore = false;
    api.getMeterReadings(selectedMeterId)
      .then((data) => {
        if (!ignore) {
          setReadings(data);
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
  }, [selectedMeterId]);

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMeterId) return;
    try {
      setLoading(true);
      setError(null);
      const dateIso = new Date(timestamp).toISOString();
      await api.submitReading({
        meter_id: selectedMeterId,
        timestamp: dateIso,
        reading_liters: parseFloat(liters),
      });
      setSuccessMsg('Manual reading saved successfully.');
      setLiters('');
      loadReadings(selectedMeterId);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCsvUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!csvFile) return;
    try {
      setLoading(true);
      setError(null);
      const res = await api.uploadCsv(csvFile);
      setSuccessMsg(`Successfully imported ${res.inserted_readings_count} readings across ${res.meters_updated} meter(s).`);
      setCsvFile(null);
      if (selectedMeterId) {
        loadReadings(selectedMeterId);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900">{t.readingsTitle}</h2>
        <p className="text-xs text-slate-500">{t.readingsSubtitle}</p>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {successMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-sm flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          {successMsg}
        </div>
      )}

      {/* Ingestion Panels: Manual & CSV */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Manual Reading Form */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2 font-bold text-sm text-slate-900">
            <Plus className="w-4 h-4 text-sky-600" />
            {t.manualReadingTitle}
          </div>

          <form onSubmit={handleManualSubmit} className="space-y-3 text-xs">
            <div>
              <label htmlFor="manual-meter-select" className="block font-medium text-slate-700 mb-1">
                {t.selectMeterPrompt}
              </label>
              <select
                id="manual-meter-select"
                value={selectedMeterId}
                onChange={(e) => setSelectedMeterId(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-1 focus:ring-sky-500 outline-none bg-white"
              >
                {meters.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name} ({m.location_label})
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="manual-timestamp-input" className="block font-medium text-slate-700 mb-1">
                  {t.readingTimestamp}
                </label>
                <input
                  id="manual-timestamp-input"
                  type="datetime-local"
                  required
                  value={timestamp}
                  onChange={(e) => setTimestamp(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-1 focus:ring-sky-500 outline-none"
                />
              </div>

              <div>
                <label htmlFor="manual-liters-input" className="block font-medium text-slate-700 mb-1">
                  {t.readingValueLiters}
                </label>
                <input
                  id="manual-liters-input"
                  type="number"
                  step="0.1"
                  min="0"
                  required
                  value={liters}
                  onChange={(e) => setLiters(e.target.value)}
                  placeholder="e.g. 180.5"
                  className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-1 focus:ring-sky-500 outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || !selectedMeterId}
              className="w-full py-2 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-700 rounded-md transition"
            >
              {loading ? t.loading : t.submitReading}
            </button>
          </form>
        </div>

        {/* CSV Upload Form */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2 font-bold text-sm text-slate-900">
            <UploadCloud className="w-4 h-4 text-indigo-600" />
            {t.uploadCsvTitle}
          </div>

          <form onSubmit={handleCsvUpload} className="space-y-3 text-xs">
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-md space-y-1">
              <div className="font-semibold text-slate-700 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-slate-500" />
                {t.uploadCsvDesc}
              </div>
              <code className="block text-[11px] font-mono text-slate-600 bg-white p-1.5 rounded border border-slate-200">
                meter_id,timestamp,reading_liters
              </code>
            </div>

            <div>
              <label htmlFor="csv-file-upload" className="sr-only">
                {t.selectCsvFile}
              </label>
              <input
                id="csv-file-upload"
                type="file"
                accept=".csv"
                required
                onChange={(e) => setCsvFile(e.target.files ? e.target.files[0] : null)}
                className="w-full text-xs text-slate-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
            </div>

            <button
              type="submit"
              disabled={loading || !csvFile}
              className="w-full py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-md transition"
            >
              {loading ? t.uploading : t.uploadCsvButton}
            </button>
          </form>
        </div>
      </div>

      {/* Historical Readings Table for Selected Meter */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs space-y-3 p-5">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900">
            {t.recentTelemetry} ({readings.length})
          </h3>
          <button
            onClick={() => selectedMeterId && loadReadings(selectedMeterId)}
            aria-label={t.refresh}
            className="text-xs text-slate-500 hover:text-slate-700 flex items-center gap-1"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            {t.refresh}
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase">
              <tr>
                <th className="py-2.5 px-4">{t.readingTimestamp}</th>
                <th className="py-2.5 px-4">{t.readingValueLiters}</th>
                <th className="py-2.5 px-4">Type</th>
                <th className="py-2.5 px-4">Record ID</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {readings.length > 0 ? (
                readings.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50">
                    <td className="py-2.5 px-4 font-mono text-slate-700">{new Date(r.timestamp).toLocaleString()}</td>
                    <td className="py-2.5 px-4 font-bold text-slate-900">
                      {r.reading_liters.toLocaleString(language === 'en-IN' ? 'en-IN' : language === 'mr-IN' ? 'mr-IN' : 'hi-IN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })} {t.litersUnit}
                    </td>
                    <td className="py-2.5 px-4 text-slate-500 capitalize">{r.raw_or_derived}</td>
                    <td className="py-2.5 px-4 font-mono text-[11px] text-slate-400">{r.id.slice(0, 8)}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="py-8 text-center text-slate-400 italic">
                    {t.noReadingsFound}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
