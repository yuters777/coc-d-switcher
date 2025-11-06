// frontend/src/pages/ConversionPage.tsx
import React, { useState } from 'react';
import AppNav from '../components/AppNav';

interface ConversionPageProps {
  onSettingsClick: () => void;
}

type WorkflowStep = 1 | 2 | 3 | 4 | 5 | 6;

interface JobState {
  jobId: string | null;
  name: string;
  submittedBy: string;
  files: { coc?: File; packing?: File } | null;
  extractedData: any | null;
  manualData: any | null;
  validationResult: any | null;
  renderedFiles: any | null;
}

export default function ConversionPage({ onSettingsClick }: ConversionPageProps) {
  const [currentStep, setCurrentStep] = useState<WorkflowStep>(1);
  const [jobState, setJobState] = useState<JobState>({
    jobId: null,
    name: '',
    submittedBy: '',
    files: null,
    extractedData: null,
    manualData: null,
    validationResult: null,
    renderedFiles: null
  });
  const [loading, setLoading] = useState(false);

  const API_BASE = 'http://localhost:8000';

  const steps = [
    { number: 1, name: 'Upload', description: 'Upload COC & Packing Slip PDFs' },
    { number: 2, name: 'Parse', description: 'Extract data from PDFs' },
    { number: 3, name: 'Manual', description: 'Add manual data' },
    { number: 4, name: 'Validate', description: 'Validate extracted data' },
    { number: 5, name: 'Render', description: 'Generate Dutch COC' },
    { number: 6, name: 'Download', description: 'Download result' }
  ];

  const handleCreateJob = async () => {
    console.log('Create job clicked', jobState);
    if (!jobState.name || !jobState.submittedBy) {
      alert('Please enter job name and your name');
      return;
    }

    setLoading(true);
    try {
      console.log('Sending request to create job...');
      const response = await fetch(`${API_BASE}/api/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: jobState.name,
          submitted_by: jobState.submittedBy
        })
      });

      console.log('Create job response:', response.status, response.ok);

      if (response.ok) {
        const data = await response.json();
        console.log('Job created:', data);
        setJobState({ ...jobState, jobId: data.job_id });
        alert('Job created! Now upload your files.');
      } else {
        const errorText = await response.text();
        console.error('Failed to create job:', errorText);
        alert('Failed to create job: ' + errorText);
      }
    } catch (error) {
      console.error('Create job error:', error);
      alert('Failed to create job: ' + error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (type: 'coc' | 'packing', file: File) => {
    setJobState({
      ...jobState,
      files: { ...jobState.files, [type]: file }
    });
  };

  const handleUploadFiles = async () => {
    if (!jobState.jobId) {
      await handleCreateJob();
      return;
    }

    if (!jobState.files?.coc || !jobState.files?.packing) {
      alert('Please select both COC and Packing Slip PDFs');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('company_coc', jobState.files.coc);
    formData.append('packing_slip', jobState.files.packing);

    try {
      const response = await fetch(`${API_BASE}/api/jobs/${jobState.jobId}/files`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        alert('Files uploaded successfully! Click "Parse" to extract data.');
        setCurrentStep(2);
      } else {
        alert('Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed: ' + error);
    } finally {
      setLoading(false);
    }
  };

  const handleStepClick = (step: WorkflowStep) => {
    console.log('Step clicked:', step, 'Current step:', currentStep);
    // For now, only allow clicking on the current step or completed steps
    if (step <= currentStep) {
      setCurrentStep(step);
      console.log('Step changed to:', step);
    } else {
      console.log('Step', step, 'is not accessible yet');
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold">Step 1: Create Job & Upload Files</h3>

            {!jobState.jobId ? (
              <div className="bg-white rounded-lg shadow p-6 space-y-4">
                <h4 className="font-semibold">Create New Job</h4>
                <div>
                  <label className="block text-sm font-medium mb-1">Job Name</label>
                  <input
                    type="text"
                    value={jobState.name}
                    onChange={(e) => setJobState({ ...jobState, name: e.target.value })}
                    placeholder="e.g., Shipment 12345"
                    className="w-full p-2 border rounded"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Your Name</label>
                  <input
                    type="text"
                    value={jobState.submittedBy}
                    onChange={(e) => setJobState({ ...jobState, submittedBy: e.target.value })}
                    placeholder="e.g., John Doe"
                    className="w-full p-2 border rounded"
                  />
                </div>
                <button
                  onClick={handleCreateJob}
                  disabled={loading}
                  className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {loading ? 'Creating...' : 'Create Job'}
                </button>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-6 space-y-4">
                <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded">
                  <p className="text-sm text-green-800">✓ Job created: {jobState.name}</p>
                  <p className="text-xs text-green-600">Job ID: {jobState.jobId}</p>
                </div>

                <h4 className="font-semibold">Upload Documents</h4>
                <div>
                  <label className="block text-sm font-medium mb-2">Company COC PDF</label>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => e.target.files && handleFileSelect('coc', e.target.files[0])}
                    className="block w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-100 file:text-blue-700"
                  />
                  {jobState.files?.coc && (
                    <p className="text-xs text-green-600 mt-1">✓ {jobState.files.coc.name}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Packing Slip PDF</label>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => e.target.files && handleFileSelect('packing', e.target.files[0])}
                    className="block w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-100 file:text-blue-700"
                  />
                  {jobState.files?.packing && (
                    <p className="text-xs text-green-600 mt-1">✓ {jobState.files.packing.name}</p>
                  )}
                </div>
                <button
                  onClick={handleUploadFiles}
                  disabled={loading || !jobState.files?.coc || !jobState.files?.packing}
                  className="w-full bg-green-600 text-white py-3 rounded hover:bg-green-700 disabled:bg-gray-400 font-medium"
                >
                  {loading ? 'Uploading...' : 'Upload Files & Continue'}
                </button>
              </div>
            )}
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold">Step 2: Parse Documents</h3>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 mb-4">Extract data from uploaded PDF documents</p>
              <button
                onClick={() => alert('Parse functionality coming soon')}
                className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700 font-medium"
              >
                Parse Documents
              </button>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold">Step 3: Manual Data Entry</h3>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 mb-4">Enter additional required information</p>
              <button
                onClick={() => alert('Manual input functionality coming soon')}
                className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700 font-medium"
              >
                Enter Manual Data
              </button>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold">Step 4: Validate Data</h3>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 mb-4">Verify all extracted and manual data</p>
              <button
                onClick={() => alert('Validation functionality coming soon')}
                className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700 font-medium"
              >
                Validate Data
              </button>
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold">Step 5: Render Document</h3>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 mb-4">Generate the Dutch MoD COC document</p>
              <button
                onClick={() => alert('Render functionality coming soon')}
                className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700 font-medium"
              >
                Generate Document
              </button>
            </div>
          </div>
        );

      case 6:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold">Step 6: Download Result</h3>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 mb-4">Download the generated documents</p>
              <button
                onClick={() => alert('Download functionality coming soon')}
                className="w-full bg-green-600 text-white py-3 rounded hover:bg-green-700 font-medium"
              >
                Download COC-D
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <AppNav title="COC-D Switcher" onSettingsClick={onSettingsClick} />

      <div className="container mx-auto p-6 max-w-5xl">
        {/* Debug info */}
        <div className="mb-4 p-2 bg-blue-100 text-xs text-blue-800 rounded">
          DEBUG: Current Step = {currentStep} | Job ID = {jobState.jobId || 'None'}
        </div>

        {/* Workflow Steps */}
        <div className="mb-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-sm font-semibold text-gray-500 mb-4">CONVERSION WORKFLOW</h2>
          <div className="grid grid-cols-6 gap-2">
            {steps.map((step) => {
              const isActive = currentStep === step.number;
              const isCompleted = currentStep > step.number;
              const isAccessible = step.number <= currentStep;

              return (
                <button
                  key={step.number}
                  onClick={() => handleStepClick(step.number as WorkflowStep)}
                  disabled={!isAccessible}
                  className={`
                    relative p-4 rounded-lg border-2 transition-all
                    ${isActive ? 'border-blue-600 bg-blue-50' : ''}
                    ${isCompleted ? 'border-green-500 bg-green-50' : ''}
                    ${!isAccessible ? 'border-gray-200 bg-gray-50 cursor-not-allowed opacity-50' : 'hover:border-blue-400'}
                    ${isAccessible && !isActive && !isCompleted ? 'border-blue-300' : ''}
                  `}
                >
                  <div className="text-center">
                    <div className={`
                      text-2xl font-bold mb-1
                      ${isActive ? 'text-blue-600' : ''}
                      ${isCompleted ? 'text-green-600' : ''}
                      ${!isAccessible ? 'text-gray-400' : ''}
                    `}>
                      {step.number}
                    </div>
                    <div className={`
                      text-xs font-semibold mb-1
                      ${isActive ? 'text-blue-700' : ''}
                      ${isCompleted ? 'text-green-700' : ''}
                      ${!isAccessible ? 'text-gray-400' : 'text-gray-700'}
                    `}>
                      {step.name}
                    </div>
                    <div className={`
                      text-xs
                      ${isActive ? 'text-blue-600' : ''}
                      ${isCompleted ? 'text-green-600' : ''}
                      ${!isAccessible ? 'text-gray-300' : 'text-gray-500'}
                    `}>
                      {step.description}
                    </div>
                    {isCompleted && (
                      <div className="absolute top-1 right-1 text-green-600">
                        ✓
                      </div>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Step Content */}
        <div>
          {renderStepContent()}
        </div>
      </div>
    </div>
  );
}
