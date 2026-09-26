import React from 'react';
import { SupportedLanguage } from '../i18n';
import { Languages, Shield, User as UserIcon } from 'lucide-react';

interface HeaderProps {
  language: SupportedLanguage;
  onLanguageChange: (lang: SupportedLanguage) => void;
  currentRole: string;
  onRoleChange: (role: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  language,
  onLanguageChange,
  currentRole,
  onRoleChange,
}) => {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Active Environment:
        </span>
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          Backend API Connected
        </span>
      </div>

      <div className="flex items-center gap-4">
        {/* Role Selector (Simulate RBAC) */}
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-slate-400" />
          <span className="text-xs font-medium text-slate-600 hidden sm:inline">Role:</span>
          <select
            value={currentRole}
            onChange={(e) => onRoleChange(e.target.value)}
            className="text-xs border border-slate-300 rounded-md px-2 py-1 bg-white text-slate-800 font-medium focus:ring-1 focus:ring-sky-500 outline-none"
          >
            <option value="RESIDENT">Resident (Own Meter)</option>
            <option value="SOCIETY_MANAGER">Society Manager (Community)</option>
            <option value="FARM_OPERATOR">Farm Operator (Irrigation)</option>
            <option value="INSTITUTION_ADMIN">Institution Admin</option>
            <option value="ADMINISTRATOR">Administrator (System-wide)</option>
          </select>
        </div>

        <div className="h-5 w-px bg-slate-200" />

        {/* Language Selector */}
        <div className="flex items-center gap-2">
          <Languages className="w-4 h-4 text-slate-400" />
          <select
            value={language}
            onChange={(e) => onLanguageChange(e.target.value as SupportedLanguage)}
            className="text-xs border border-slate-300 rounded-md px-2 py-1 bg-white text-slate-800 font-medium focus:ring-1 focus:ring-sky-500 outline-none"
          >
            <option value="en-IN">English (en-IN)</option>
            <option value="mr-IN">मराठी (mr-IN)</option>
            <option value="hi-IN">हिन्दी (hi-IN)</option>
          </select>
        </div>

        <div className="h-5 w-px bg-slate-200" />

        {/* User indicator */}
        <div className="flex items-center gap-2 text-xs text-slate-600 font-medium">
          <div className="w-7 h-7 rounded-full bg-sky-100 text-sky-800 flex items-center justify-center font-bold">
            <UserIcon className="w-4 h-4" />
          </div>
          <span className="hidden md:inline">Supabase Authenticated</span>
        </div>
      </div>
    </header>
  );
};
