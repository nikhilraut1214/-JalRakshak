import React from 'react';

interface SeverityBadgeProps {
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  riskScore?: number;
  size?: 'sm' | 'md' | 'lg';
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({
  severity,
  riskScore,
  size = 'md',
}) => {
  const styles = {
    LOW: 'bg-emerald-50 text-emerald-800 border-emerald-300',
    MEDIUM: 'bg-amber-50 text-amber-800 border-amber-300',
    HIGH: 'bg-orange-50 text-orange-800 border-orange-300',
    CRITICAL: 'bg-rose-50 text-rose-800 border-rose-300',
  }[severity] || 'bg-slate-50 text-slate-700 border-slate-300';

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3.5 py-1.5 font-semibold',
  }[size];

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md border font-medium tracking-tight ${styles} ${sizeClasses}`}
    >
      {riskScore !== undefined ? (
        <span>
          <strong className="font-semibold">{Math.round(riskScore)}</strong> / 100 · {severity}
        </span>
      ) : (
        <span>{severity}</span>
      )}
    </span>
  );
};
