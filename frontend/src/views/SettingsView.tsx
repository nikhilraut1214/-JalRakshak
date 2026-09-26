import React, { useState } from 'react';
import { translations, SupportedLanguage } from '../i18n';
import { Settings as SettingsIcon, Shield, Server, Bot, Check, Key } from 'lucide-react';
import { setAuthToken, getAuthToken } from '../api';

interface SettingsViewProps {
  language: SupportedLanguage;
}

export const SettingsView: React.FC<SettingsViewProps> = ({ language }) => {
  const t = translations[language];
  const [tokenInput, setTokenInput] = useState(getAuthToken());
  const [savedTokenMsg, setSavedTokenMsg] = useState(false);

  const handleSaveToken = () => {
    setAuthToken(tokenInput);
    setSavedTokenMsg(true);
    setTimeout(() => setSavedTokenMsg(false), 2000);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900">{t.settings}</h2>
        <p className="text-xs text-slate-500">System configurations, security credentials, and AI parameters</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Supabase Auth Settings */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2 font-bold text-sm text-slate-900">
            <Shield className="w-4 h-4 text-emerald-600" />
            Supabase Authentication (MVP Choice)
          </div>

          <div className="text-xs text-slate-600 space-y-3">
            <p>
              Supabase Auth issues JWT access tokens verified cryptographically by the FastAPI backend on every request.
            </p>

            <div>
              <label className="block font-semibold text-slate-700 mb-1 flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5 text-slate-400" />
                Custom Bearer JWT Token (Test / Override)
              </label>
              <textarea
                rows={3}
                value={tokenInput}
                onChange={(e) => setTokenInput(e.target.value)}
                placeholder="Paste Bearer JWT token to test custom claims..."
                className="w-full px-3 py-2 border border-slate-300 rounded-md font-mono text-[11px] focus:ring-1 focus:ring-sky-500 outline-none"
              />
            </div>

            <div className="flex items-center justify-between">
              <button
                onClick={handleSaveToken}
                className="px-3 py-1.5 bg-sky-600 hover:bg-sky-700 text-white rounded-md font-semibold text-xs transition"
              >
                Apply Token
              </button>
              {savedTokenMsg && (
                <span className="text-emerald-600 font-medium flex items-center gap-1">
                  <Check className="w-3.5 h-3.5" /> Token applied
                </span>
              )}
            </div>
          </div>
        </div>

        {/* AI & Groq Boundaries */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2 font-bold text-sm text-slate-900">
            <Bot className="w-4 h-4 text-indigo-600" />
            AI Explanation Engine (Groq + Deterministic)
          </div>

          <div className="text-xs text-slate-600 space-y-2">
            <p>
              Groq LLM is utilized exclusively as an <strong>explanation and translation layer</strong>. The system automatically engages deterministic offline templates whenever Groq is unconfigured or unreachable.
            </p>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-md space-y-1">
              <div className="font-semibold text-slate-700">Enforced AI Guardrails:</div>
              <ul className="list-disc list-inside space-y-1 text-slate-600 text-[11px]">
                <li>Zero authority over risk score or severity</li>
                <li>No physical leak confirmation claims</li>
                <li>Strict Pydantic JSON schema validation</li>
                <li>Full multilingual support (English, Marathi, Hindi)</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Backend Architectural Authority */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4 md:col-span-2">
          <div className="flex items-center gap-2 font-bold text-sm text-slate-900">
            <Server className="w-4 h-4 text-sky-600" />
            Backend Analytical Authority
          </div>

          <div className="text-xs text-slate-600 space-y-2">
            <p>
              The JalRakshak frontend functions solely as a client interface. All baselines, z-scores, persistence counters, slopes, risk scoring (45/25/20/10 weighting), and severity classifications are computed exclusively on the FastAPI backend.
            </p>
            <div className="font-mono text-[11px] text-slate-500 bg-slate-50 p-2.5 rounded border border-slate-200">
              API Base URL: /api · Health Check: /api/health
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
