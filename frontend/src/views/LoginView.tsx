import React, { useState } from 'react';
import { api, setAuthToken } from '../api';
import { UserProfile } from '../types';
import {
  Droplet, Shield, Lock, Mail, ArrowRight, AlertTriangle,
  RefreshCw, User, Building, Sprout, Landmark
} from 'lucide-react';

interface LoginViewProps {
  onLoginSuccess: (user: UserProfile) => void;
}

interface DemoPreset {
  role: string;
  email: string;
  label: string;
  desc: string;
  icon: React.ReactNode;
}

export const LoginView: React.FC<LoginViewProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('resident@jalrakshak.local');
  const [password, setPassword] = useState('JalRakshak@2026');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const presets: DemoPreset[] = [
    {
      role: 'RESIDENT',
      email: 'resident@jalrakshak.local',
      label: 'Resident',
      desc: 'Access owned domestic meter & personal alerts',
      icon: <User className="w-4 h-4 text-blue-600" />,
    },
    {
      role: 'SOCIETY_MANAGER',
      email: 'manager@jalrakshak.local',
      label: 'Society Manager',
      desc: 'Manage community meters & collective water loss',
      icon: <Building className="w-4 h-4 text-indigo-600" />,
    },
    {
      role: 'FARM_OPERATOR',
      email: 'farmer@jalrakshak.local',
      label: 'Farm Operator',
      desc: 'Monitor agricultural irrigation windows & pumps',
      icon: <Sprout className="w-4 h-4 text-emerald-600" />,
    },
    {
      role: 'INSTITUTION_ADMIN',
      email: 'institution@jalrakshak.local',
      label: 'Institution Admin',
      desc: 'Campus/facility multi-building monitoring',
      icon: <Landmark className="w-4 h-4 text-amber-600" />,
    },
    {
      role: 'ADMINISTRATOR',
      email: 'admin@jalrakshak.local',
      label: 'System Admin',
      desc: 'Full system-wide monitoring & evaluation audit',
      icon: <Shield className="w-4 h-4 text-rose-600" />,
    },
  ];

  const handleLogin = async (loginEmail: string, loginPass: string) => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.login(loginEmail, loginPass);
      setAuthToken(res.access_token);
      onLoginSuccess(res.user);
    } catch (err: any) {
      setError(err?.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) {
      setError('Please provide an email address.');
      return;
    }
    handleLogin(email, password);
  };

  const selectPreset = (preset: DemoPreset) => {
    setEmail(preset.email);
    setPassword('JalRakshak@2026');
    handleLogin(preset.email, 'JalRakshak@2026');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-sky-50/30 to-slate-100 flex items-center justify-center p-4 sm:p-6 font-sans">
      <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-12 gap-6 bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden">
        {/* Left Side: Brand and Architecture Value */}
        <div className="md:col-span-5 bg-gradient-to-br from-sky-900 via-slate-900 to-sky-950 p-8 text-white flex flex-col justify-between space-y-6">
          <div className="space-y-4">
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-xl bg-sky-500/20 border border-sky-400/40 flex items-center justify-center text-sky-400">
                <Droplet className="w-6 h-6 fill-sky-400/30 text-sky-300" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight text-white">JalRakshak AI</h1>
                <div className="text-[11px] text-sky-300 font-medium">जल रक्षक — Decision Support</div>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed pt-2">
              Hardware-independent water-consumption early-warning and decision-support platform.
            </p>

            <div className="p-3.5 bg-white/5 border border-white/10 rounded-xl text-xs space-y-2">
              <div className="text-[11px] font-bold text-sky-300 uppercase tracking-wider">
                Authoritative Invariant
              </div>
              <p className="text-slate-200 text-xs italic leading-relaxed">
                &ldquo;Analytics detects. Evidence supports. AI explains. Humans verify.&rdquo;
              </p>
            </div>
          </div>

          <div className="space-y-2 text-[11px] text-slate-400 border-t border-white/10 pt-4">
            <div className="flex items-center gap-1.5 text-sky-300 font-semibold">
              <Shield className="w-3.5 h-3.5" />
              Cryptographic Backend RBAC
            </div>
            <p>
              Authentication establishes identity. The FastAPI backend verifies the signed JWT and independently enforces role and meter authorization.
            </p>
          </div>
        </div>

        {/* Right Side: Sign-in Form & Canonical Identity Presets */}
        <div className="md:col-span-7 p-6 sm:p-8 space-y-6">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Sign In to JalRakshak</h2>
            <p className="text-xs text-slate-500">
              Enter your credentials or choose a canonical test identity below
            </p>
          </div>

          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Quick-Select Canonical Test Identities */}
          <div className="space-y-2">
            <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500">
              Canonical Identity Presets (1-Click Authenticated Sign-In)
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {presets.map((preset) => (
                <button
                  key={preset.role}
                  type="button"
                  onClick={() => selectPreset(preset)}
                  disabled={loading}
                  className="p-2.5 rounded-lg border border-slate-200 hover:border-sky-300 hover:bg-sky-50/50 text-left transition flex items-start gap-2.5 cursor-pointer disabled:opacity-50"
                >
                  <div className="p-1.5 bg-slate-50 border border-slate-200 rounded-md shrink-0">
                    {preset.icon}
                  </div>
                  <div className="min-w-0">
                    <div className="text-xs font-bold text-slate-800 flex items-center gap-1">
                      {preset.label}
                    </div>
                    <div className="text-[10px] text-slate-500 truncate">{preset.email}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="relative flex py-1 items-center">
            <div className="flex-grow border-t border-slate-200"></div>
            <span className="flex-shrink mx-3 text-[11px] text-slate-400 font-medium">Or enter credentials manually</span>
            <div className="flex-grow border-t border-slate-200"></div>
          </div>

          {/* Manual Credentials Form */}
          <form onSubmit={onSubmit} className="space-y-3.5">
            <div>
              <label htmlFor="login-email-input" className="block text-xs font-semibold text-slate-700 mb-1">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  id="login-email-input"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="resident@jalrakshak.local"
                  required
                  className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-sky-500 bg-white text-slate-800 outline-none"
                />
              </div>
            </div>

            <div>
              <label htmlFor="login-password-input" className="block text-xs font-semibold text-slate-700 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  id="login-password-input"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-1 focus:ring-sky-500 bg-white text-slate-800 outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 bg-sky-600 hover:bg-sky-700 text-white font-semibold text-xs rounded-lg transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-xs disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Verifying Cryptographic Session...
                </>
              ) : (
                <>
                  Authenticate & Enter System
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
