import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import SettingsPage from './pages/SettingsPage';
import FileUpload from './components/FileUpload';

function ConversionWorkflow() {
  const [currentStep, setCurrentStep] = useState(1);
  const [jobId, setJobId] = useState<string | null>(null);

  const steps = [
    { num: 1, title: 'Upload Documents', desc: 'Upload Company COC and Packing Slip PDFs' },
    { num: 2, title: 'Review & Edit', desc: 'Review extracted data and make corrections' },
    { num: 3, title: 'Validate', desc: 'Check all fields are correct' },
    { num: 4, title: 'Generate', desc: 'Create Dutch COC document' },
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
        <div className="flex justify-between items-center">
          {steps.map((step, idx) => (
            <div key={step.num} className="flex items-center">
              <div className={`flex flex-col items-center ${currentStep >= step.num ? 'text-blue-600' : 'text-gray-400'}`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                  currentStep > step.num ? 'bg-green-500 text-white' :
                  currentStep === step.num ? 'bg-blue-600 text-white' :
                  'bg-gray-200 text-gray-500'
                }`}>
                  {currentStep > step.num ? '✓' : step.num}
                </div>
                <div className="text-xs mt-1 font-medium text-center">{step.title}</div>
              </div>
              {idx < steps.length - 1 && (
                <div className={`w-16 h-1 mx-2 ${currentStep > step.num ? 'bg-green-500' : 'bg-gray-200'}`} />
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
            <div>
              <h3 className="text-lg font-semibold mb-4">Step 2: Review & Edit Data</h3>
              <p className="text-gray-600 mb-4">Review the extracted data and make any necessary corrections.</p>
              <button
                onClick={() => setCurrentStep(3)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Continue to Validation
              </button>
            </div>
          )}
          {currentStep === 3 && (
            <div>
              <h3 className="text-lg font-semibold mb-4">Step 3: Validate</h3>
              <p className="text-gray-600 mb-4">All fields have been validated.</p>
              <button
                onClick={() => setCurrentStep(4)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Continue to Generate
              </button>
            </div>
          )}
          {currentStep === 4 && (
            <div>
              <h3 className="text-lg font-semibold mb-4">Step 4: Generate Document</h3>
              <p className="text-gray-600 mb-4">Ready to generate the Dutch COC document.</p>
              <button
                onClick={() => alert('Document generation coming soon!')}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Generate Dutch COC
              </button>
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