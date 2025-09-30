import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-blue-600 text-white p-4">
          <div className="container mx-auto">
            <h1 className="text-2xl font-bold">COC-D Switcher</h1>
          </div>
        </nav>

        <div className="container mx-auto p-6">
          <h2 className="text-3xl font-bold mb-6">Dashboard</h2>
          <p>Application is ready for development</p>
        </div>
      </div>
    </Router>
  );
}

export default App;