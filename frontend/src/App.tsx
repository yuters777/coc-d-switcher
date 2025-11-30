import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import SettingsPage from './pages/SettingsPage';

function Dashboard() {
  return (
    <div className="container mx-auto p-6">
      <h2 className="text-3xl font-bold mb-6">Dashboard</h2>
      <p className="mb-4">Application is ready for development</p>
      <Link
        to="/settings"
        className="inline-block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Administrator Settings
      </Link>
    </div>
  );
}

function SettingsWrapper() {
  const navigate = useNavigate();
  return <SettingsPage onBack={() => navigate('/')} />;
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={
            <>
              <nav className="bg-blue-600 text-white p-4">
                <div className="container mx-auto">
                  <h1 className="text-2xl font-bold">COC-D Switcher</h1>
                </div>
              </nav>
              <Dashboard />
            </>
          } />
          <Route path="/settings" element={<SettingsWrapper />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;