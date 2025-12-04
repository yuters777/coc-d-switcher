import { useState } from 'react';
import FileUpload from './components/FileUpload';
import ManualInputForm from './components/ManualInputForm';
import ValidationPanel from './components/ValidationPanel';

// API base URL
const API_URL = 'http://localhost:8000';

interface Job {
  id: string;
  name: string;
  status: string;
  extracted_data?: any;
  validation?: any;
}

function App() {
  const [step, setStep] = useState<'create' | 'upload' | 'manual' | 'review' | 'generate'>('create');
  const [currentJob, setCurrentJob] = useState<Job | null>(null);
  const [jobName, setJobName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedFile, setGeneratedFile] = useState<string | null>(null);

  // Create a new job
  const handleCreateJob = async () => {
    if (!jobName.trim()) {
      setError('Please enter a job name');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: jobName,
          submitted_by: 'User'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentJob({ id: data.job_id, name: jobName, status: 'created' });
        setStep('upload');
      } else {
        throw new Error('Failed to create job');
      }
    } catch (err) {
      setError('Failed to create job: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // Handle file upload complete
  const handleUploadComplete = async () => {
    if (!currentJob) return;

    // Fetch updated job data
    try {
      const response = await fetch(`${API_URL}/api/jobs/${currentJob.id}`);
      if (response.ok) {
        const data = await response.json();
        setCurrentJob(data);
        setStep('manual');
      }
    } catch (err) {
      setError('Failed to fetch job data');
    }
  };

  // Handle manual input submission
  const handleManualSubmit = async (manualData: any) => {
    if (!currentJob) return;

    setLoading(true);
    try {
      // Merge manual data with extracted data
      const updatedData = {
        ...currentJob.extracted_data,
        template_vars: {
          ...currentJob.extracted_data?.template_vars,
          partial_delivery_number: manualData.partial_delivery_number,
          undelivered_quantity: manualData.undelivered_quantity,
          remarks: `SW Ver. # ${manualData.sw_version}`
        }
      };

      // Save to job
      const response = await fetch(`${API_URL}/api/jobs/${currentJob.id}/data`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedData)
      });

      if (response.ok) {
        setCurrentJob({...currentJob, extracted_data: updatedData});
        setStep('review');
      }
    } catch (err) {
      setError('Failed to save data');
    } finally {
      setLoading(false);
    }
  };

  // Generate document
  const handleGenerate = async () => {
    if (!currentJob) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/jobs/${currentJob.id}/render`, {
        method: 'POST'
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedFile(data.download_url || data.file_path);
        setStep('generate');
      } else {
        throw new Error('Failed to generate document');
      }
    } catch (err) {
      setError('Failed to generate document: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  // Reset to start new job
  const handleNewJob = () => {
    setCurrentJob(null);
    setJobName('');
    setStep('create');
    setError(null);
    setGeneratedFile(null);
  };

  // Get template vars for validation display
  const getTemplateVars = () => {
    return currentJob?.extracted_data?.template_vars || {};
  };

  // Get validation data
  const getValidation = () => {
    return currentJob?.validation || { errors: [], warnings: [] };
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-blue-600 text-white p-4 shadow-lg">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">COC-D Switcher</h1>
          {currentJob && (
            <div className="text-sm">
              Job: <span className="font-semibold">{currentJob.name}</span>
            </div>
          )}
        </div>
      </nav>

      {/* Progress Steps */}
      <div className="bg-white shadow">
        <div className="container mx-auto py-4">
          <div className="flex items-center justify-center space-x-4">
            {['Create Job', 'Upload Files', 'Manual Input', 'Review', 'Generate'].map((label, idx) => {
              const stepMap = ['create', 'upload', 'manual', 'review', 'generate'];
              const isActive = stepMap[idx] === step;
              const isPast = stepMap.indexOf(step) > idx;

              return (
                <div key={label} className="flex items-center">
                  <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold
                    ${isActive ? 'bg-blue-600 text-white' : isPast ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-600'}`}>
                    {isPast ? '✓' : idx + 1}
                  </div>
                  <span className={`ml-2 text-sm ${isActive ? 'font-semibold text-blue-600' : 'text-gray-600'}`}>
                    {label}
                  </span>
                  {idx < 4 && <div className="w-8 h-px bg-gray-300 ml-4"></div>}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="container mx-auto mt-4">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
            <button onClick={() => setError(null)} className="float-right font-bold">×</button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="container mx-auto p-6">
        {/* Step 1: Create Job */}
        {step === 'create' && (
          <div className="max-w-md mx-auto">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-2xl font-bold mb-6">Create New COC-D Job</h2>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Job Name</label>
                <input
                  type="text"
                  value={jobName}
                  onChange={(e) => setJobName(e.target.value)}
                  placeholder="e.g., COC_SV_Del240_04.12.2025"
                  className="w-full p-3 border rounded focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                onClick={handleCreateJob}
                disabled={loading}
                className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700 disabled:bg-gray-400 font-medium"
              >
                {loading ? 'Creating...' : 'Create Job'}
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Upload Files */}
        {step === 'upload' && currentJob && (
          <div className="max-w-md mx-auto">
            <FileUpload jobId={currentJob.id} onUploadComplete={handleUploadComplete} />

            {/* Demo mode - skip upload for testing */}
            <div className="mt-4 text-center">
              <button
                onClick={() => setStep('manual')}
                className="text-blue-600 text-sm hover:underline"
              >
                Skip upload (demo mode)
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Manual Input */}
        {step === 'manual' && (
          <div className="max-w-md mx-auto">
            <ManualInputForm
              extractedData={currentJob?.extracted_data}
              onSubmit={handleManualSubmit}
              loading={loading}
            />

            {/* Demo mode - skip for testing */}
            <div className="mt-4 text-center">
              <button
                onClick={() => setStep('review')}
                className="text-blue-600 text-sm hover:underline"
              >
                Skip manual input (demo mode)
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Review & Validate */}
        {step === 'review' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ValidationPanel
              validation={getValidation()}
              templateVars={getTemplateVars()}
            />

            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Review Data</h2>

              <div className="space-y-3 text-sm">
                {Object.entries(getTemplateVars()).map(([key, value]) => (
                  <div key={key} className="flex border-b pb-2">
                    <span className="font-medium w-48 text-gray-600">{key}:</span>
                    <span className="flex-1">{String(value).substring(0, 100)}</span>
                  </div>
                ))}
              </div>

              <div className="mt-6 flex gap-4">
                <button
                  onClick={() => setStep('manual')}
                  className="flex-1 border border-gray-300 py-3 rounded hover:bg-gray-50"
                >
                  Back to Edit
                </button>
                <button
                  onClick={handleGenerate}
                  disabled={loading}
                  className="flex-1 bg-green-600 text-white py-3 rounded hover:bg-green-700 disabled:bg-gray-400"
                >
                  {loading ? 'Generating...' : 'Generate Document'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 5: Generated */}
        {step === 'generate' && (
          <div className="max-w-md mx-auto text-center">
            <div className="bg-white p-8 rounded-lg shadow">
              <div className="text-6xl mb-4">✅</div>
              <h2 className="text-2xl font-bold mb-4 text-green-600">Document Generated!</h2>

              {generatedFile && (
                <a
                  href={generatedFile}
                  download
                  className="block w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700 mb-4"
                >
                  Download DOCX
                </a>
              )}

              <button
                onClick={handleNewJob}
                className="w-full border border-gray-300 py-3 rounded hover:bg-gray-50"
              >
                Create New Job
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
