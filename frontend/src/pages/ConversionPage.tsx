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

  const handleParse = async () => {
    if (!jobState.jobId) {
      alert('No job found. Please create a job and upload files first.');
      return;
    }

    setLoading(true);
    try {
      console.log('Parsing documents for job:', jobState.jobId);
      const response = await fetch(`${API_BASE}/api/jobs/${jobState.jobId}/parse`, {
        method: 'POST'
      });

      console.log('Parse response:', response.status, response.ok);

      if (response.ok) {
        const data = await response.json();
        console.log('Parsed data:', data);
        setJobState({
          ...jobState,
          extractedData: data.extracted_data
        });
        alert('Documents parsed successfully! Click "Manual" to add additional data.');
        setCurrentStep(3);
      } else {
        const errorText = await response.text();
        console.error('Failed to parse:', errorText);
        alert('Failed to parse documents: ' + errorText);
      }
    } catch (error) {
      console.error('Parse error:', error);
      alert('Failed to parse documents: ' + error);
    } finally {
      setLoading(false);
    }
  };

  const handleManualDataSubmit = async (manualData: {
    partial_delivery_number: string;
    undelivered_quantity: string;
    sw_version: string;
  }) => {
    if (!jobState.jobId) {
      alert('No job found.');
      return;
    }

    setLoading(true);
    try {
      console.log('Submitting manual data for job:', jobState.jobId, manualData);
      const response = await fetch(`${API_BASE}/api/jobs/${jobState.jobId}/manual`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(manualData)
      });

      console.log('Manual data response:', response.status, response.ok);

      if (response.ok) {
        const data = await response.json();
        console.log('Manual data saved:', data);
        setJobState({
          ...jobState,
          manualData: data.manual_data
        });
        alert('Manual data saved successfully! Click "Validate" to verify all data.');
        setCurrentStep(4);
      } else {
        const errorText = await response.text();
        console.error('Failed to save manual data:', errorText);
        alert('Failed to save manual data: ' + errorText);
      }
    } catch (error) {
      console.error('Manual data error:', error);
      alert('Failed to save manual data: ' + error);
    } finally {
      setLoading(false);
    }
  };

  const handleValidate = async () => {
    if (!jobState.jobId) {
      alert('No job found.');
      return;
    }

    setLoading(true);
    try {
      console.log('Validating data for job:', jobState.jobId);
      const response = await fetch(`${API_BASE}/api/jobs/${jobState.jobId}/validate`, {
        method: 'POST'
      });

      console.log('Validation response:', response.status, response.ok);

      if (response.ok) {
        const data = await response.json();
        console.log('Validation result:', data);
        setJobState({
          ...jobState,
          validationResult: data.validation
        });

        if (data.has_errors) {
          alert(`Validation completed with ${data.validation.errors.length} error(s). Please review and fix before proceeding.`);
        } else if (data.has_warnings) {
          alert(`Validation completed with ${data.validation.warnings.length} warning(s). You may proceed to render.`);
          setCurrentStep(5);
        } else {
          alert('Validation passed! All data is valid. Click "Render" to generate the document.');
          setCurrentStep(5);
        }
      } else {
        const errorText = await response.text();
        console.error('Failed to validate:', errorText);
        alert('Failed to validate data: ' + errorText);
      }
    } catch (error) {
      console.error('Validation error:', error);
      alert('Failed to validate data: ' + error);
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

              {jobState.extractedData ? (
                <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded">
                  <p className="text-sm text-green-800 font-semibold mb-2">✓ Documents parsed successfully</p>
                  <div className="text-xs text-gray-600">
                    <p>Extracted data is ready for manual input</p>
                  </div>
                </div>
              ) : (
                <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded">
                  <p className="text-sm text-blue-800">
                    Files ready: {jobState.files?.coc && '✓ COC'} {jobState.files?.packing && '✓ Packing Slip'}
                  </p>
                </div>
              )}

              <button
                onClick={handleParse}
                disabled={loading || !!jobState.extractedData}
                className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700 disabled:bg-gray-400 font-medium"
              >
                {loading ? 'Parsing...' : jobState.extractedData ? 'Already Parsed' : 'Parse Documents'}
              </button>

              {jobState.extractedData && (
                <button
                  onClick={() => setCurrentStep(3)}
                  className="w-full mt-3 bg-green-600 text-white py-3 rounded hover:bg-green-700 font-medium"
                >
                  Continue to Manual Input →
                </button>
              )}
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold">Step 3: Manual Data Entry</h3>

            {jobState.manualData ? (
              <div className="bg-white rounded-lg shadow p-6">
                <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded">
                  <p className="text-sm text-green-800 font-semibold mb-2">✓ Manual data submitted successfully</p>
                  <div className="text-xs text-gray-600 space-y-1">
                    <p><strong>Partial Delivery #:</strong> {jobState.manualData.partial_delivery_number}</p>
                    <p><strong>Undelivered Quantity:</strong> {jobState.manualData.undelivered_quantity}</p>
                    <p><strong>Software Version:</strong> {jobState.manualData.sw_version}</p>
                  </div>
                </div>
                <button
                  onClick={() => setCurrentStep(4)}
                  className="w-full bg-green-600 text-white py-3 rounded hover:bg-green-700 font-medium"
                >
                  Continue to Validation →
                </button>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-6">
                <p className="text-gray-600 mb-4">Enter required information and fill in any missing extracted data</p>

                <form onSubmit={(e) => {
                  e.preventDefault();
                  const formData = new FormData(e.currentTarget);
                  const data: any = {
                    partial_delivery_number: formData.get('partial_delivery_number') as string,
                    undelivered_quantity: formData.get('undelivered_quantity') as string,
                    sw_version: formData.get('sw_version') as string
                  };

                  // Add optional extracted data fields if provided
                  const contract = formData.get('contract_number') as string;
                  if (contract) data.contract_number = contract;

                  const shipment = formData.get('shipment_no') as string;
                  if (shipment) data.shipment_no = shipment;

                  const product = formData.get('product_description') as string;
                  if (product) data.product_description = product;

                  const qty = formData.get('quantity') as string;
                  if (qty) data.quantity = parseInt(qty);

                  handleManualDataSubmit(data);
                }} className="space-y-4">

                  {/* Extracted Data Section - Optional Fields */}
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded">
                    <h4 className="font-semibold text-blue-900 mb-3">📄 Extracted Data (Fill in if missing)</h4>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Contract Number
                        </label>
                        <input
                          type="text"
                          name="contract_number"
                          placeholder="e.g., 4500012345"
                          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Fill in if missing from extracted data
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Shipment Number
                        </label>
                        <input
                          type="text"
                          name="shipment_no"
                          placeholder="e.g., SH123456"
                          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Product Description
                        </label>
                        <input
                          type="text"
                          name="product_description"
                          placeholder="e.g., Radio System XYZ"
                          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Quantity
                        </label>
                        <input
                          type="number"
                          name="quantity"
                          placeholder="e.g., 100"
                          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Manual Data Section - Required Fields */}
                  <div className="p-4 bg-green-50 border border-green-200 rounded">
                    <h4 className="font-semibold text-green-900 mb-3">✏️ Manual Data (Required)</h4>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium mb-2">
                          Partial Delivery Number <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          name="partial_delivery_number"
                          placeholder="e.g., 165"
                          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-green-500 focus:border-transparent"
                          required
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          The partial delivery sequence number for this shipment
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">
                          Undelivered Quantity <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          name="undelivered_quantity"
                          placeholder="e.g., 4196 (of 8115)"
                          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-green-500 focus:border-transparent"
                          required
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Format: remaining quantity (of total ordered)
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">
                          Software Version <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          name="sw_version"
                          placeholder="e.g., 2.2.15.45"
                          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-green-500 focus:border-transparent"
                          required
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          The software version for this product
                        </p>
                      </div>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-green-600 text-white py-3 rounded hover:bg-green-700 disabled:bg-gray-400 font-medium"
                  >
                    {loading ? 'Saving...' : 'Save and Continue'}
                  </button>
                </form>
              </div>
            )}
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold">Step 4: Validate Data</h3>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 mb-4">Verify all extracted and manual data</p>

              {jobState.validationResult ? (
                <div className="space-y-4">
                  {/* Errors */}
                  {jobState.validationResult.errors && jobState.validationResult.errors.length > 0 && (
                    <div className="p-4 bg-red-50 border-2 border-red-300 rounded">
                      <h4 className="font-semibold text-red-800 mb-2">
                        ❌ Errors ({jobState.validationResult.errors.length})
                      </h4>
                      <div className="space-y-2">
                        {jobState.validationResult.errors.map((error: any, idx: number) => (
                          <div key={idx} className="text-sm">
                            <p className="font-semibold text-red-700">{error.code}</p>
                            <p className="text-red-600">{error.message}</p>
                            <p className="text-xs text-red-500">Location: {error.where}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Warnings */}
                  {jobState.validationResult.warnings && jobState.validationResult.warnings.length > 0 && (
                    <div className="p-4 bg-yellow-50 border-2 border-yellow-300 rounded">
                      <h4 className="font-semibold text-yellow-800 mb-2">
                        ⚠️ Warnings ({jobState.validationResult.warnings.length})
                      </h4>
                      <div className="space-y-2">
                        {jobState.validationResult.warnings.map((warning: any, idx: number) => (
                          <div key={idx} className="text-sm">
                            <p className="font-semibold text-yellow-700">{warning.code}</p>
                            <p className="text-yellow-600">{warning.message}</p>
                            <p className="text-xs text-yellow-500">Location: {warning.where}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Success */}
                  {(!jobState.validationResult.errors || jobState.validationResult.errors.length === 0) &&
                   (!jobState.validationResult.warnings || jobState.validationResult.warnings.length === 0) && (
                    <div className="p-4 bg-green-50 border-2 border-green-300 rounded">
                      <h4 className="font-semibold text-green-800">
                        ✓ Validation Passed
                      </h4>
                      <p className="text-sm text-green-600 mt-1">
                        All data is valid and ready for document generation.
                      </p>
                    </div>
                  )}

                  {/* Action buttons */}
                  <div className="space-y-2">
                    {jobState.validationResult.errors && jobState.validationResult.errors.length > 0 ? (
                      <div className="text-center text-sm text-red-600 py-2">
                        Please fix the errors above before proceeding.
                      </div>
                    ) : (
                      <button
                        onClick={() => setCurrentStep(5)}
                        className="w-full bg-green-600 text-white py-3 rounded hover:bg-green-700 font-medium"
                      >
                        Continue to Render →
                      </button>
                    )}
                    <button
                      onClick={handleValidate}
                      disabled={loading}
                      className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
                    >
                      {loading ? 'Validating...' : 'Re-validate'}
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={handleValidate}
                  disabled={loading}
                  className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700 disabled:bg-gray-400 font-medium"
                >
                  {loading ? 'Validating...' : 'Validate Data'}
                </button>
              )}
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
