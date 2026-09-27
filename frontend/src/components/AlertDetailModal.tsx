import React, { useState, useRef } from 'react';
import { Alert, ExplainResponse } from '../types';
import { SeverityBadge } from './SeverityBadge';
import { EvidenceCard } from './EvidenceCard';
import { api } from '../api';
import { translations, SupportedLanguage } from '../i18n';
import { useFocusTrap } from '../hooks/useFocusTrap';
import { X, CheckCircle, ShieldAlert, Bot, FileText, ChevronRight, AlertCircle, Wrench } from 'lucide-react';

interface AlertDetailModalProps {
  alert: Alert;
  language: SupportedLanguage;
  onClose: () => void;
  onAlertUpdated: (updated: Alert) => void;
}

export const AlertDetailModal: React.FC<AlertDetailModalProps> = ({
  alert,
  language,
  onClose,
  onAlertUpdated,
}) => {
  const t = translations[language];
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [explanation, setExplanation] = useState<ExplainResponse | null>(null);
  const [note, setNote] = useState('');

  const closeButtonRef = useRef<HTMLButtonElement | null>(null);
  const modalRef = useFocusTrap<HTMLDivElement>({
    isOpen: true,
    onClose,
    initialFocusRef: closeButtonRef,
  });

  const ev = alert.evidence;

  const handleAcknowledge = async () => {
    try {
      setLoading(true);
      setError(null);
      const updated = await api.acknowledgeAlert(alert.id, note);
      onAlertUpdated(updated);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTransition = async (resolution: string) => {
    try {
      setLoading(true);
      setError(null);
      const updated = await api.resolveAlert(alert.id, resolution, note);
      onAlertUpdated(updated);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestExplanation = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.explainAlert(alert.id, language);
      setExplanation(res);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="alert-modal-title"
        className="bg-white rounded-xl shadow-xl border border-slate-200 w-full max-w-3xl overflow-hidden animate-in fade-in zoom-in-95 duration-150"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50">
          <div className="flex items-center gap-3">
            <ShieldAlert className="w-6 h-6 text-sky-700" />
            <div>
              <div id="alert-modal-title" className="text-sm font-semibold text-slate-900">
                {t.incidentDetails} #{alert.id.slice(0, 8)}
              </div>
              <div className="text-xs text-slate-500">
                {t.meterIdLabel}: {alert.meter_id} · {t.statusLabel}: <strong className="text-slate-800">{alert.status}</strong>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <SeverityBadge severity={alert.severity} riskScore={alert.risk_score} />
            <button
              ref={closeButtonRef}
              onClick={onClose}
              aria-label={t.closeModal}
              className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-200 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6 max-h-[75vh] overflow-y-auto">
          {error && (
            <div className="p-3 text-xs bg-rose-50 border border-rose-200 text-rose-800 rounded-md flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              {error}
            </div>
          )}

          {/* Section 1: What Changed & Measured Evidence */}
          {ev ? (
            <EvidenceCard
              evidence={ev}
              language={language}
              showBreakdown={true}
            />
          ) : (
            <div className="text-sm text-slate-500 italic p-4 bg-slate-50 rounded-lg border border-slate-200">
              {t.noEvidenceRecorded}
            </div>
          )}

          {/* Section 2: AI / Deterministic Explanation Card */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">{t.aiExplanationTitle}</h4>
              {!explanation && (
                <button
                  onClick={handleRequestExplanation}
                  disabled={loading}
                  className="px-3 py-1 text-xs font-medium rounded-md bg-sky-50 text-sky-700 border border-sky-200 hover:bg-sky-100 transition flex items-center gap-1.5"
                >
                  <Bot className="w-3.5 h-3.5" />
                  {t.generateExplanation}
                </button>
              )}
            </div>

            {explanation ? (
              <div className="bg-sky-50/50 border border-sky-200 rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between border-b border-sky-100 pb-2">
                  <span className="text-xs font-bold text-sky-900 flex items-center gap-1.5">
                    <FileText className="w-4 h-4 text-sky-700" />
                    {explanation.source === 'groq' ? t.sourceGroq : t.sourceDeterministic}
                  </span>
                  <span className="text-xs text-sky-600 font-mono">{t.languageLabel} {explanation.language}</span>
                </div>
                <div className="text-sm text-slate-800 whitespace-pre-line leading-relaxed">
                  {explanation.explanation}
                </div>
              </div>
            ) : (
              <div className="p-4 rounded-lg border border-dashed border-slate-200 text-center text-xs text-slate-400">
                {t.clickToGenerateExplanation}
              </div>
            )}
          </div>

          {/* Section 3: Physical Verification Checklist */}
          <div className="bg-amber-50/60 border border-amber-200 rounded-lg p-4 space-y-2">
            <h4 className="text-xs font-bold text-amber-900 flex items-center gap-1.5">
              <Wrench className="w-4 h-4 text-amber-700" />
              {t.physicalVerificationGuidanceTitle}
            </h4>
            <ul className="text-xs text-amber-900/90 space-y-1.5 list-disc list-inside">
              <li>{t.verificationStep1}</li>
              <li>{t.verificationStep2}</li>
              <li>{t.verificationStep3}</li>
              <li>{t.verificationStep4}</li>
            </ul>
          </div>

          {/* Section 4: Lifecycle Actions (Strict Transition Matrix) */}
          <div className="space-y-3 pt-2 border-t border-slate-100">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">{t.authorizedLifecycleActions}</h4>
            
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder={t.auditNotePlaceholder}
                aria-label={t.auditNotePlaceholder}
                className="text-xs px-3 py-2 border border-slate-300 rounded-md flex-1 focus:ring-1 focus:ring-sky-500 outline-none"
              />
            </div>

            <div className="flex flex-wrap items-center gap-3 pt-2">
              {alert.status === 'DETECTED' && (
                <button
                  onClick={handleAcknowledge}
                  disabled={loading}
                  className="px-4 py-2 text-xs font-semibold rounded-md bg-sky-700 text-white hover:bg-sky-800 transition flex items-center gap-1.5"
                >
                  <CheckCircle className="w-3.5 h-3.5" />
                  {t.acknowledge}
                </button>
              )}

              {alert.status === 'ACKNOWLEDGED' && (
                <button
                  onClick={() => handleTransition('VERIFYING')}
                  disabled={loading}
                  className="px-4 py-2 text-xs font-semibold rounded-md bg-indigo-700 text-white hover:bg-indigo-800 transition flex items-center gap-1.5"
                >
                  <ChevronRight className="w-3.5 h-3.5" />
                  {t.beginVerification}
                </button>
              )}

              {alert.status === 'VERIFYING' && (
                <>
                  <button
                    onClick={() => handleTransition('CONFIRMED')}
                    disabled={loading}
                    className="px-3.5 py-2 text-xs font-semibold rounded-md bg-amber-700 text-white hover:bg-amber-800 transition"
                  >
                    {t.confirmAbnormal}
                  </button>
                  <button
                    onClick={() => handleTransition('FALSE_ALARM')}
                    disabled={loading}
                    className="px-3.5 py-2 text-xs font-semibold rounded-md bg-slate-600 text-white hover:bg-slate-700 transition"
                  >
                    {t.markFalseAlarm}
                  </button>
                  <button
                    onClick={() => handleTransition('INVESTIGATING')}
                    disabled={loading}
                    className="px-3.5 py-2 text-xs font-semibold rounded-md bg-blue-700 text-white hover:bg-blue-800 transition"
                  >
                    {t.investigate}
                  </button>
                </>
              )}

              {(alert.status === 'CONFIRMED' || alert.status === 'FALSE_ALARM' || alert.status === 'INVESTIGATING') && (
                <button
                  onClick={() => handleTransition('RESOLVED')}
                  disabled={loading}
                  className="px-4 py-2 text-xs font-semibold rounded-md bg-emerald-700 text-white hover:bg-emerald-800 transition flex items-center gap-1.5"
                >
                  <CheckCircle className="w-3.5 h-3.5" />
                  {t.resolveIncident}
                </button>
              )}

              {alert.status === 'RESOLVED' && (
                <span className="text-xs font-medium text-emerald-800 bg-emerald-50 px-3 py-1.5 rounded-md border border-emerald-200">
                  {t.incidentResolvedMessage}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
