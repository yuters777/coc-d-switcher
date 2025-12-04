import { useState } from 'react';
import ConversionPage from './pages/ConversionPage';
import SettingsPage from './pages/SettingsPage';

type AppView = 'conversion' | 'settings';

function App() {
  const [currentView, setCurrentView] = useState<AppView>('conversion');

  return (
    <div className="min-h-screen bg-gray-50">
      {currentView === 'conversion' ? (
        <ConversionPage onSettingsClick={() => setCurrentView('settings')} />
      ) : (
        <SettingsPage onBack={() => setCurrentView('conversion')} />
      )}
    </div>
  );
}

export default App;
