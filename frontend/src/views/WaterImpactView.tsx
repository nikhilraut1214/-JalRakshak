import React, { useState } from 'react';
import { translations, SupportedLanguage } from '../i18n';
import { Droplet, Info, Calculator, TrendingUp } from 'lucide-react';

interface WaterImpactViewProps {
  language: SupportedLanguage;
}

export const WaterImpactView: React.FC<WaterImpactViewProps> = ({ language }) => {
  const t = translations[language];
  const [avoidedFraction, setAvoidedFraction] = useState(0.70); // 70% assumed avoided with early detection
  const [excessLiters, setExcessLiters] = useState(1250);

  const potentialSavings = Math.round(excessLiters * avoidedFraction);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900">{t.waterImpact}</h2>
        <p className="text-xs text-slate-500">
          Estimated water conservation impact and early-intervention potential savings models
        </p>
      </div>

      {/* Trust Notice (Design System Section 17 & Phase 4) */}
      <div className="bg-sky-50 border border-sky-200 rounded-xl p-4 text-xs text-sky-900 space-y-1">
        <div className="font-bold flex items-center gap-1.5 text-sky-900">
          <Info className="w-4 h-4 text-sky-700" />
          Estimation Disclosure
        </div>
        <p className="text-sky-800">
          Potential savings values are analytical projections based on user-configured assumption fractions (e.g. prompt human shutoff avoiding a percentage of subsequent excess). They are <strong>never presented as guaranteed physical measurements</strong>.
        </p>
      </div>

      {/* Interactive Impact Calculator */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4">
          <div className="font-bold text-sm text-slate-900 flex items-center gap-2">
            <Calculator className="w-4 h-4 text-sky-600" />
            Impact Assumption Parameters
          </div>

          <div className="space-y-4 text-xs">
            <div>
              <div className="flex justify-between font-medium text-slate-700 mb-1">
                <span>Avoided Fraction Assumption:</span>
                <span className="font-bold text-sky-700">{Math.round(avoidedFraction * 100)}%</span>
              </div>
              <input
                type="range"
                min="0.1"
                max="0.95"
                step="0.05"
                value={avoidedFraction}
                onChange={(e) => setAvoidedFraction(parseFloat(e.target.value))}
                className="w-full accent-sky-600"
              />
              <div className="text-[11px] text-slate-400 mt-1">
                Portion of estimated excess prevented through prompt human verification and shutoff.
              </div>
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">
                Simulated Estimated Excess (Liters):
              </label>
              <input
                type="number"
                min="0"
                value={excessLiters}
                onChange={(e) => setExcessLiters(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-slate-300 rounded-md focus:ring-1 focus:ring-sky-500 outline-none"
              />
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-sky-50 to-white p-5 rounded-xl border border-sky-200 shadow-xs space-y-4 flex flex-col justify-between">
          <div className="space-y-1">
            <div className="text-xs font-bold uppercase tracking-wider text-sky-800">
              Projected Avoided Water Loss
            </div>
            <div className="text-3xl font-extrabold text-sky-900">
              ~{potentialSavings.toLocaleString()} <span className="text-sm font-normal text-slate-600">Liters</span>
            </div>
            <div className="text-xs text-slate-500 pt-1">
              Formula: <code className="bg-sky-100/60 px-1 py-0.5 rounded text-sky-900 font-mono">estimated_excess × avoided_fraction</code>
            </div>
          </div>

          <div className="bg-white p-3 rounded-lg border border-sky-100 text-xs text-slate-600 space-y-1">
            <div className="font-semibold text-slate-800">Equivalency Perspective:</div>
            <div>• ~{Math.round(potentialSavings / 20)} domestic 20L water cans saved.</div>
            <div>• ~{Math.round(potentialSavings / 150)} daily average individual drinking/sanitation allowances.</div>
          </div>
        </div>
      </div>
    </div>
  );
};
