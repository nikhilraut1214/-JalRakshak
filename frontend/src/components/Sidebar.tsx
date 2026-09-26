import React from 'react';
import { translations, SupportedLanguage } from '../i18n';
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
} from 'lucide-react';

interface SidebarProps {
  activeModule: string;
  onSelectModule: (module: string) => void;
  language: SupportedLanguage;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeModule,
  onSelectModule,
  language,
}) => {
  const t = translations[language];

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

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 h-screen sticky top-0 border-r border-slate-800">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold text-lg border border-sky-500/30">
          <Droplet className="w-5 h-5 text-sky-400 fill-sky-400/20" />
        </div>
        <div>
          <h1 className="text-base font-bold text-white tracking-tight">{t.appName}</h1>
          <p className="text-[10px] text-slate-400 truncate max-w-[160px]">Water Anomaly Decision Support</p>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeModule === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectModule(item.id)}
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
        <div className="font-semibold text-slate-300 mb-1">Core Principle:</div>
        <div className="leading-tight text-slate-400 italic">
          &quot;{t.tagline}&quot;
        </div>
      </div>
    </aside>
  );
};
