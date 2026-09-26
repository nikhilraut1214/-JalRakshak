import React from 'react';
import { EvidenceDetail } from '../types';
import { SeverityBadge } from './SeverityBadge';
import { AlertTriangle, TrendingUp, TrendingDown, Minus, CheckCircle, HelpCircle } from 'lucide-react';

interface EvidenceCardProps {
  evidence: EvidenceDetail;
  title?: string;
  showBreakdown?: boolean;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({
  evidence,
  title = 'Deterministic Evidence Hierarchy',
  showBreakdown = true,
}) => {
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
          {title}
        </h3>
        <SeverityBadge severity={evidence.severity} riskScore={evidence.risk_score} />
      </div>

      {/* Ordered Evidence Display */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
        <div className="bg-slate-50 p-3 rounded border border-slate-100">
          <div className="text-xs text-slate-500">1. Current Reading</div>
          <div className="text-lg font-bold text-slate-900 mt-1">
            {evidence.current_usage_liters.toLocaleString()} <span className="text-xs font-normal text-slate-500">Liters</span>
          </div>
        </div>

        <div className="bg-slate-50 p-3 rounded border border-slate-100">
          <div className="text-xs text-slate-500">2. Expected / Baseline</div>
          <div className="text-lg font-bold text-slate-900 mt-1">
            {evidence.baseline_liters.toLocaleString()} <span className="text-xs font-normal text-slate-500">Liters (Median)</span>
          </div>
        </div>

        <div className="bg-slate-50 p-3 rounded border border-slate-100">
          <div className="text-xs text-slate-500">3. Deviation</div>
          <div className={`text-lg font-bold mt-1 ${evidence.deviation_pct > 20 ? 'text-rose-600' : 'text-slate-800'}`}>
            {evidence.deviation_pct >= 0 ? `+${evidence.deviation_pct}%` : `${evidence.deviation_pct}%`}
          </div>
        </div>

        <div className="bg-slate-50 p-3 rounded border border-slate-100">
          <div className="text-xs text-slate-500">4. Persistence</div>
          <div className="text-lg font-bold text-slate-900 mt-1">
            {evidence.persistence_intervals} <span className="text-xs font-normal text-slate-500">consecutive intervals</span>
          </div>
        </div>

        <div className="bg-slate-50 p-3 rounded border border-slate-100">
          <div className="text-xs text-slate-500">5. Trend</div>
          <div className="text-lg font-bold text-slate-900 mt-1 flex items-center gap-1.5 capitalize">
            {getTrendIcon(evidence.trend)} {evidence.trend}
          </div>
        </div>

        <div className="bg-slate-50 p-3 rounded border border-slate-100">
          <div className="text-xs text-slate-500">6. Estimated Excess</div>
          <div className="text-lg font-bold text-amber-700 mt-1">
            {evidence.estimated_excess_liters.toLocaleString()} <span className="text-xs font-normal text-slate-500">Liters (Analytical)</span>
          </div>
        </div>
      </div>

      {/* Verification Flag & Risk Component Breakdown */}
      <div className="pt-2 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 border-t border-slate-100 text-xs text-slate-600">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-700">7. Human Verification Status:</span>
          {evidence.verification_required ? (
            <span className="inline-flex items-center gap-1 text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 font-medium">
              <HelpCircle className="w-3.5 h-3.5" /> Physical Verification Required
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-medium">
              <CheckCircle className="w-3.5 h-3.5" /> Routine Observation
            </span>
          )}
        </div>

        <div className="text-slate-400 italic">
          * Analytical score derived from 45/25/20/10 weighting. Not a leak probability.
        </div>
      </div>

      {showBreakdown && evidence.deviation_score !== undefined && (
        <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs">
          <div className="font-semibold text-slate-700 mb-2">Authoritative Risk Weighting Breakdown (0–100):</div>
          <div className="grid grid-cols-4 gap-2 text-center">
            <div className="bg-white p-1.5 rounded border border-slate-200">
              <div className="text-slate-400">Deviation (45%)</div>
              <div className="font-bold text-slate-800 mt-0.5">{evidence.deviation_score}</div>
            </div>
            <div className="bg-white p-1.5 rounded border border-slate-200">
              <div className="text-slate-400">Persistence (25%)</div>
              <div className="font-bold text-slate-800 mt-0.5">{evidence.persistence_score}</div>
            </div>
            <div className="bg-white p-1.5 rounded border border-slate-200">
              <div className="text-slate-400">Trend (20%)</div>
              <div className="font-bold text-slate-800 mt-0.5">{evidence.trend_score}</div>
            </div>
            <div className="bg-white p-1.5 rounded border border-slate-200">
              <div className="text-slate-400">Loss (10%)</div>
              <div className="font-bold text-slate-800 mt-0.5">{evidence.loss_score}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
