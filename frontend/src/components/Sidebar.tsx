import React, { useRef } from 'react';
import { translations, SupportedLanguage } from '../i18n';
import { useFocusTrap } from '../hooks/useFocusTrap';
import {
  LayoutDashboard,
  Gauge,
  UploadCloud,
  AlertTriangle,
  FileSearch,
  CheckSquare,
  FlaskConical,
  BarChart2,
  Droplet,
  Settings as SettingsIcon,
  X,
} from 'lucide-react';

interface SidebarProps {
  activeModule: string;
  onSelectModule: (module: string) => void;
  language: SupportedLanguage;
  isMobileNavOpen?: boolean;
  onCloseMobileNav?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeModule,
  onSelectModule,
  language,
  isMobileNavOpen = false,
  onCloseMobileNav = () => {},
}) => {
  const t = translations[language];

  const closeButtonRef = useRef<HTMLButtonElement | null>(null);
  const drawerRef = useFocusTrap<HTMLElement>({
    isOpen: isMobileNavOpen,
    onClose: onCloseMobileNav,
    initialFocusRef: closeButtonRef,
  });

  const navItems = [
    { id: 'dashboard', label: t.dashboard, icon: LayoutDashboard },
    { id: 'meters', label: t.meters, icon: Gauge },
    { id: 'readings', label: t.readings, icon: UploadCloud },
    { id: 'alerts', label: t.alerts, icon: AlertTriangle },
    { id: 'evidence', label: t.incidentEvidence, icon: FileSearch },
    { id: 'verification', label: t.verification, icon: CheckSquare },
    { id: 'scenario_lab', label: t.scenarioLab, icon: FlaskConical },
    { id: 'evaluation', label: t.evaluation, icon: BarChart2 },
    { id: 'water_impact', label: t.waterImpact, icon: Droplet },
    { id: 'settings', label: t.settings, icon: SettingsIcon },
  ];

  const renderNavContent = (isMobile = false) => (
    <>
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold text-lg border border-sky-500/30">
            <Droplet className="w-5 h-5 text-sky-400 fill-sky-400/20" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white tracking-tight">{t.appName}</h1>
            <p className="text-[10px] text-slate-400 truncate max-w-[160px]">{t.waterAnomalyDecisionSupport}</p>
          </div>
        </div>
        {isMobile && onCloseMobileNav && (
          <button
            ref={closeButtonRef}
            type="button"
            onClick={onCloseMobileNav}
            aria-label={t.closeMenu}
            className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Navigation List */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto" aria-label="Main Navigation">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeModule === item.id;
          return (
            <button
              key={item.id}
              onClick={() => {
                onSelectModule(item.id);
                if (isMobile && onCloseMobileNav) onCloseMobileNav();
              }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors text-left ${
                isActive
                  ? 'bg-sky-600 text-white font-semibold shadow-xs'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span className="truncate">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Core Principle Footer */}
      <div className="p-4 border-t border-slate-800 text-[11px] text-slate-400 bg-slate-950/40">
        <div className="font-semibold text-slate-300 mb-1">{t.corePrincipleTitle}</div>
        <div className="leading-tight text-slate-400 italic">
          &quot;{t.tagline}&quot;
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Desktop Persistent Sidebar */}
      <aside className="hidden md:flex md:w-64 bg-slate-900 text-slate-300 flex-col shrink-0 h-screen sticky top-0 border-r border-slate-800">
        {renderNavContent(false)}
      </aside>

      {/* Mobile Drawer Backdrop & Dialog */}
      {isMobileNavOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div
            className="fixed inset-0 bg-slate-950/70 backdrop-blur-xs transition-opacity"
            onClick={onCloseMobileNav}
            aria-hidden="true"
          />
          <aside
            ref={drawerRef}
            role="dialog"
            aria-modal="true"
            aria-label={t.openMenu}
            className="fixed inset-y-0 left-0 z-50 w-72 bg-slate-900 text-slate-300 flex flex-col shadow-2xl animate-in slide-in-from-left duration-200"
          >
            {renderNavContent(true)}
          </aside>
        </div>
      )}
    </>
  );
};
