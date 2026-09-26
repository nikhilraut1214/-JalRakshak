import { useState } from 'react';
import { SupportedLanguage } from './i18n';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardView } from './views/DashboardView';
import { MetersView } from './views/MetersView';
import { ReadingsView } from './views/ReadingsView';
import { AlertsView } from './views/AlertsView';
import { EvidenceView } from './views/EvidenceView';
import { VerificationView } from './views/VerificationView';
import { ScenarioLabView } from './views/ScenarioLabView';
import { EvaluationView } from './views/EvaluationView';
import { WaterImpactView } from './views/WaterImpactView';
import { SettingsView } from './views/SettingsView';

export function App() {
  const [activeModule, setActiveModule] = useState<string>('dashboard');
  const [language, setLanguage] = useState<SupportedLanguage>('en-IN');
  const [currentRole, setCurrentRole] = useState<string>('RESIDENT');

  const renderActiveView = () => {
    switch (activeModule) {
      case 'dashboard':
        return <DashboardView language={language} onNavigate={setActiveModule} />;
      case 'meters':
        return <MetersView language={language} />;
      case 'readings':
        return <ReadingsView language={language} />;
      case 'alerts':
        return <AlertsView language={language} />;
      case 'evidence':
        return <EvidenceView language={language} />;
      case 'verification':
        return <VerificationView language={language} />;
      case 'scenario_lab':
        return <ScenarioLabView language={language} onNavigate={setActiveModule} />;
      case 'evaluation':
        return <EvaluationView language={language} />;
      case 'water_impact':
        return <WaterImpactView language={language} />;
      case 'settings':
        return <SettingsView language={language} />;
      default:
        return <DashboardView language={language} onNavigate={setActiveModule} />;
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-50 font-sans text-slate-900">
      <Sidebar
        activeModule={activeModule}
        onSelectModule={setActiveModule}
        language={language}
      />
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          language={language}
          onLanguageChange={setLanguage}
          currentRole={currentRole}
          onRoleChange={setCurrentRole}
        />
        <main className="flex-1 overflow-y-auto">
          {renderActiveView()}
        </main>
      </div>
    </div>
  );
}

export default App;
