import { useState, useEffect } from 'react';
import { SupportedLanguage } from './i18n';
import { api, getAuthToken, clearAuthToken, onUnauthorized } from './api';
import { UserProfile } from './types';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { LoginView } from './views/LoginView';
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
import { RefreshCw } from 'lucide-react';

type AuthState = 'AUTH_LOADING' | 'AUTHENTICATED' | 'UNAUTHENTICATED';

export function App() {
  const [authState, setAuthState] = useState<AuthState>('AUTH_LOADING');
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [activeModule, setActiveModule] = useState<string>('dashboard');
  const [language, setLanguage] = useState<SupportedLanguage>('en-IN');
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);

  useEffect(() => {
    onUnauthorized(() => {
      clearAuthToken();
      setCurrentUser(null);
      setAuthState('UNAUTHENTICATED');
    });

    const initAuth = async () => {
      const token = getAuthToken();
      if (!token) {
        setAuthState('UNAUTHENTICATED');
        return;
      }
      try {
        const user = await api.getMe();
        setCurrentUser(user);
        setAuthState('AUTHENTICATED');
      } catch {
        clearAuthToken();
        setCurrentUser(null);
        setAuthState('UNAUTHENTICATED');
      }
    };

    initAuth();
  }, []);

  const handleLogout = async () => {
    try {
      await api.logout();
    } catch {
      // Best-effort logout
    } finally {
      clearAuthToken();
      setCurrentUser(null);
      setAuthState('UNAUTHENTICATED');
    }
  };

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

  if (authState === 'AUTH_LOADING') {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
        <div className="flex items-center gap-2.5 text-sky-700 font-semibold text-xs bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <RefreshCw className="w-4 h-4 animate-spin text-sky-600" />
          <span>Verifying cryptographic session...</span>
        </div>
      </div>
    );
  }

  if (authState === 'UNAUTHENTICATED' || !currentUser) {
    return (
      <LoginView
        onLoginSuccess={(user) => {
          setCurrentUser(user);
          setAuthState('AUTHENTICATED');
        }}
      />
    );
  }

  return (
    <div className="flex min-h-screen bg-slate-50 font-sans text-slate-900">
      <Sidebar
        activeModule={activeModule}
        onSelectModule={(mod) => {
          setActiveModule(mod);
          setIsMobileNavOpen(false);
        }}
        language={language}
        isMobileNavOpen={isMobileNavOpen}
        onCloseMobileNav={() => setIsMobileNavOpen(false)}
      />
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          language={language}
          onLanguageChange={setLanguage}
          currentUser={currentUser}
          onLogout={handleLogout}
          isMobileNavOpen={isMobileNavOpen}
          onToggleMobileNav={() => setIsMobileNavOpen((prev) => !prev)}
        />
        <main className="flex-1 overflow-y-auto">
          {renderActiveView()}
        </main>
      </div>
    </div>
  );
}

export default App;
