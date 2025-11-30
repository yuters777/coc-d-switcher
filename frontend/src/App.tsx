import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import SettingsPage from './pages/SettingsPage';
import FileUpload from './components/FileUpload';

function ConversionWorkflow() {
  const [currentStep, setCurrentStep] = useState(1);
  const [jobId, setJobId] = useState<string | null>(null);

  const steps = [
    { num: 1, title: 'Upload', desc: 'Upload Company COC and Packing Slip PDFs' },
    { num: 2, title: 'Complete', desc: 'Process and generate document' },
    { num: 3, title: 'Download', desc: 'Download the Dutch COC' },
  ];

  const createJob = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: 'New Conversion', submitted_by: 'User' })
      });
      const data = await response.json();
      setJobId(data.job_id);
      return data.job_id;
    } catch (error) {
      console.error('Failed to create job:', error);
      return null;
    }
  };

  const handleStartConversion = async () => {
    const newJobId = await createJob();
    if (newJobId) {
      setCurrentStep(1);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      {/* Workflow Steps Header */}
      <div className="mb-8">
        <div className="flex justify-center items-center gap-4">
          {steps.map((step, idx) => (
            <div key={step.num} className="flex items-center">
              <div className={`flex flex-col items-center ${currentStep >= step.num ? 'text-blue-600' : 'text-gray-400'}`}>
                <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg ${
                  currentStep > step.num ? 'bg-green-500 text-white' :
                  currentStep === step.num ? 'bg-blue-600 text-white' :
                  'bg-gray-200 text-gray-500'
                }`}>
                  {currentStep > step.num ? '✓' : step.num}
                </div>
                <div className="text-sm mt-2 font-medium text-center">{step.title}</div>
              </div>
              {idx < steps.length - 1 && (
                <div className={`w-20 h-1 mx-4 ${currentStep > step.num ? 'bg-green-500' : 'bg-gray-200'}`} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Main Content Area */}
      {!jobId ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <h2 className="text-2xl font-bold mb-4">Start New Conversion</h2>
          <p className="text-gray-600 mb-6">
            Convert Company Certificate of Conformance (COC) to Dutch format
          </p>
          <button
            onClick={handleStartConversion}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            Start New Conversion
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-6">
          {currentStep === 1 && (
            <FileUpload
              jobId={jobId}
              onUploadComplete={() => setCurrentStep(2)}
            />
          )}
          {currentStep === 2 && (
            <div className="text-center">
              <div className="text-6xl mb-4">✅</div>
              <h3 className="text-xl font-semibold mb-4">Processing Complete</h3>
              <p className="text-gray-600 mb-6">Your Dutch COC document has been generated successfully.</p>
              <button
                onClick={() => setCurrentStep(3)}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
              >
                Continue to Download
              </button>
            </div>
          )}
          {currentStep === 3 && (
            <div className="text-center">
              <div className="text-6xl mb-4">📄</div>
              <h3 className="text-xl font-semibold mb-4">Download Your Document</h3>
              <p className="text-gray-600 mb-6">Your Dutch COC is ready for download.</p>
              <div className="space-x-4">
                <button
                  onClick={() => alert('Download DOCX coming soon!')}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                >
                  Download DOCX
                </button>
                <button
                  onClick={() => alert('Download PDF coming soon!')}
                  className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-medium"
                >
                  Download PDF
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Reset Button */}
      {jobId && (
        <div className="mt-4 text-center">
          <button
            onClick={() => { setJobId(null); setCurrentStep(1); }}
            className="text-gray-500 hover:text-gray-700 text-sm"
          >
            ← Start Over
          </button>
        </div>
      )}
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
                <div className="container mx-auto flex justify-between items-center">
                  <h1 className="text-2xl font-bold">COC-D Switcher</h1>
                  <Link
                    to="/settings"
                    className="px-4 py-2 bg-blue-700 rounded hover:bg-blue-800 flex items-center gap-2"
                  >
                    <span>⚙️</span>
                    <span>Settings</span>
                  </Link>
                </div>
              </nav>
              <ConversionWorkflow />
            </>
          } />
          <Route path="/settings" element={<SettingsWrapper />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;