import React from 'react';
import { EvidenceDetail, AlertEvidence } from '../types';
import { SeverityBadge } from './SeverityBadge';
import { AlertTriangle, TrendingUp, TrendingDown, Minus, CheckCircle, HelpCircle } from 'lucide-react';

import { translations, SupportedLanguage } from '../i18n';

interface EvidenceCardProps {
  evidence: EvidenceDetail | AlertEvidence;
  title?: string;
  showBreakdown?: boolean;
  language?: SupportedLanguage;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({
  evidence,
  title,
  showBreakdown = true,
  language = 'en-IN',
}) => {
  const t = translations[language];
  const cardTitle = title || t.evidenceHierarchyTitle;
  const getTrendIcon = (trend: string) => {
    if (trend === 'increasing') return <TrendingUp className="w-4 h-4 text-rose-600 inline" />;
    if (trend === 'decreasing') return <TrendingDown className="w-4 h-4 text-emerald-600 inline" />;
    return <Minus className="w-4 h-4 text-slate-500 inline" />;
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-5 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <h3 className="text-base font-semibold text-slate-900 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-sky-600" />
          {cardTitle}
        </h3>
        <SeverityBadge severity={evidence.severity as any} riskScore={evidence.risk_score} />
      </div>

      {/* Ordered Evidence Display */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
        <div className="bg-slate-50 p-3 rounded border border-slate-100">
          <div className="text-xs text-slate-500">{t.currentReading}</div>
          <div className="text-lg font-bold text-slate-900 mt-1">
            {evidence.current_usage_liters.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })} <span className="text-xs font-normal text-slate-500">{t.litersUnit}</span>
          </div>
        </div>

        <div className="bg-slate-50 p-3 rounded border border-slate-100">
          <div className="text-xs text-slate-500">{t.expectedBaseline}</div>
          <div className="text-lg font-bold text-slate-900 mt-1">
            {evidence.baseline_liters.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })} <span className="text-xs font-normal text-slate-500">{t.litersUnit} (Median)</span>
          </div>
        </div>

        <div className="bg-slate-50 p-3 rounded border border-slate-100">
          <div className="text-xs text-slate-500">{t.deviation}</div>
          <div className={`text-lg font-bold mt-1 ${evidence.deviation_pct > 20 ? 'text-rose-600' : 'text-slate-800'}`}>
            {evidence.deviation_pct >= 0 ? `+${evidence.deviation_pct}%` : `${evidence.deviation_pct}%`}
          </div>
        </div>

        <div className="bg-slate-50 p-3 rounded border border-slate-100">
          <div className="text-xs text-slate-500">{t.persistence}</div>
          <div className="text-lg font-bold text-slate-900 mt-1">
            {evidence.persistence_intervals} <span className="text-xs font-normal text-slate-500">{t.consecutiveIntervals}</span>
          </div>
        </div>

        <div className="bg-slate-50 p-3 rounded border border-slate-100">
          <div className="text-xs text-slate-500">{t.trend}</div>
          <div className="text-lg font-bold text-slate-900 mt-1 flex items-center gap-1.5 capitalize">
            {getTrendIcon(evidence.trend)} {evidence.trend}
          </div>
        </div>

        <div className="bg-slate-50 p-3 rounded border border-slate-100">
          <div className="text-xs text-slate-500">{t.estimatedExcess}</div>
          <div className="text-lg font-bold text-amber-700 mt-1">
            {evidence.estimated_excess_liters.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })} <span className="text-xs font-normal text-slate-500">{t.litersUnit} (Analytical)</span>
          </div>
        </div>
      </div>

      {/* Verification Flag & Risk Component Breakdown */}
      <div className="pt-2 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 border-t border-slate-100 text-xs text-slate-600">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-700">{t.humanVerificationStatus}</span>
          {evidence.verification_required ? (
            <span className="inline-flex items-center gap-1 text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 font-medium">
              <HelpCircle className="w-3.5 h-3.5" /> {t.physicalVerificationRequired}
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-medium">
              <CheckCircle className="w-3.5 h-3.5" /> {t.routineObservation}
            </span>
          )}
        </div>

        <div className="text-slate-400 italic">
          {t.safetyDisclaimer}
        </div>
      </div>

      {showBreakdown && evidence.deviation_score !== undefined && (
        <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs">
          <div className="font-semibold text-slate-700 mb-2">{t.deterministicBreakdownTitle}</div>
          <div className="grid grid-cols-4 gap-2 text-center">
            <div className="bg-white p-1.5 rounded border border-slate-200">
              <div className="text-slate-400">{t.deviationScoreLabel}</div>
              <div className="font-bold text-slate-800 mt-0.5">{evidence.deviation_score}</div>
            </div>
            <div className="bg-white p-1.5 rounded border border-slate-200">
              <div className="text-slate-400">{t.persistenceScoreLabel}</div>
              <div className="font-bold text-slate-800 mt-0.5">{evidence.persistence_score}</div>
            </div>
            <div className="bg-white p-1.5 rounded border border-slate-200">
              <div className="text-slate-400">{t.trendScoreLabel}</div>
              <div className="font-bold text-slate-800 mt-0.5">{evidence.trend_score}</div>
            </div>
            <div className="bg-white p-1.5 rounded border border-slate-200">
              <div className="text-slate-400">{t.lossScoreLabel}</div>
              <div className="font-bold text-slate-800 mt-0.5">{evidence.loss_score}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
