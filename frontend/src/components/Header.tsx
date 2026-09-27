import React from 'react';
import { translations, SupportedLanguage } from '../i18n';
import { UserProfile } from '../types';
import { Languages, User as UserIcon, LogOut, Building, Menu } from 'lucide-react';

interface HeaderProps {
  language: SupportedLanguage;
  onLanguageChange: (lang: SupportedLanguage) => void;
  currentUser: UserProfile;
  onLogout: () => void;
  isMobileNavOpen?: boolean;
  onToggleMobileNav?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  language,
  onLanguageChange,
  currentUser,
  onLogout,
  isMobileNavOpen = false,
  onToggleMobileNav,
}) => {
  const t = translations[language];

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'ADMINISTRATOR':
        return 'bg-rose-100 text-rose-800 border-rose-200';
      case 'FARM_OPERATOR':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'SOCIETY_MANAGER':
        return 'bg-indigo-100 text-indigo-800 border-indigo-200';
      case 'INSTITUTION_ADMIN':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30 shadow-2xs">
      <div className="flex items-center gap-3">
        {onToggleMobileNav && (
          <button
            type="button"
            onClick={onToggleMobileNav}
            aria-label={isMobileNavOpen ? t.closeMenu : t.openMenu}
            aria-expanded={isMobileNavOpen}
            className="p-1.5 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 md:hidden transition"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:inline">
          {t.environment}
        </span>
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          {t.apiConnected}
        </span>
      </div>

      <div className="flex items-center gap-3 sm:gap-4">
        {/* Language Selector */}
        <div className="flex items-center gap-1.5">
          <Languages className="w-4 h-4 text-slate-400" />
          <select
            value={language}
            aria-label={t.languageSettingsTitle}
            onChange={(e) => onLanguageChange(e.target.value as SupportedLanguage)}
            className="text-xs border border-slate-300 rounded-md px-2 py-1 bg-white text-slate-800 font-medium focus:ring-1 focus:ring-sky-500 outline-none"
          >
            <option value="en-IN">English (en-IN)</option>
            <option value="mr-IN">मराठी (mr-IN)</option>
            <option value="hi-IN">हिन्दी (hi-IN)</option>
          </select>
        </div>

        <div className="h-5 w-px bg-slate-200" />

        {/* Real Authenticated User Identity */}
        <div className="flex items-center gap-2 text-xs">
          <div className="w-8 h-8 rounded-full bg-sky-100 text-sky-800 flex items-center justify-center font-bold shrink-0">
            <UserIcon className="w-4 h-4" />
          </div>
          <div className="hidden md:flex flex-col">
            <span className="font-semibold text-slate-800 text-xs leading-none">
              {currentUser.email}
            </span>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className={`px-1.5 py-0.2 text-[10px] font-bold rounded border ${getRoleBadgeColor(currentUser.role)}`}>
                {currentUser.role}
              </span>
              {currentUser.organization_id && (
                <span className="text-[10px] text-slate-400 flex items-center gap-0.5">
                  <Building className="w-2.5 h-2.5" />
                  {currentUser.organization_id}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="h-5 w-px bg-slate-200" />

        {/* Logout Button */}
        <button
          onClick={onLogout}
          title={t.logout}
          aria-label={t.logout}
          className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-slate-600 hover:text-rose-600 hover:bg-rose-50 rounded-md transition-colors cursor-pointer border border-transparent hover:border-rose-200"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">{t.logout}</span>
        </button>
      </div>
    </header>
  );
};
