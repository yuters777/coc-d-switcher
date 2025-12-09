// frontend/src/pages/ConversionPage.tsx
import React, { useState } from 'react';
import AppNav from '../components/AppNav';
import ConfirmationModal from '../components/ConfirmationModal';

interface ConversionPageProps {
  onSettingsClick: () => void;
}

type WorkflowStep = 1 | 2 | 3;

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
  const [loadingMessage, setLoadingMessage] = useState('');
  const [showMissingDataModal, setShowMissingDataModal] = useState(false);
  const [missingDataFields, setMissingDataFields] = useState<string[]>([]);
  const [pendingManualData, setPendingManualData] = useState<any>(null);
  const [showValidationErrorModal, setShowValidationErrorModal] = useState(false);
  const [previousNames, setPreviousNames] = useState<string[]>([]);

  const API_BASE = 'http://localhost:8000';

  // Load previous names from localStorage on component mount
  React.useEffect(() => {
    const storedNames = localStorage.getItem('coc_previous_names');
    if (storedNames) {
      try {
        const names = JSON.parse(storedNames);
        setPreviousNames(names);
      } catch (e) {
        console.error('Error loading previous names:', e);
      }
    }
  }, []);

  // Save name to localStorage when creating a job
  const saveNameToHistory = (name: string) => {
    if (!name || name.trim() === '') return;

    const trimmedName = name.trim();
    // Add to list if not already present
    const updatedNames = previousNames.includes(trimmedName)
      ? previousNames
      : [trimmedName, ...previousNames].slice(0, 10); // Keep only last 10 names

    setPreviousNames(updatedNames);
    localStorage.setItem('coc_previous_names', JSON.stringify(updatedNames));
  };

  const steps = [
    { number: 1, name: 'Upload', description: 'Upload COC & Packing Slip PDFs' },
    { number: 2, name: 'Complete', description: 'Review & complete data' },
    { number: 3, name: 'Download', description: 'Download result' }
  ];

  const handleCreateJob = async () => {
    console.log('Create job clicked', jobState);
    if (!jobState.name || !jobState.submittedBy) {
      return; // Form validation
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

        // Save the name to history for future use
        saveNameToHistory(jobState.submittedBy);

        setJobState({ ...jobState, jobId: data.job_id });

      } else {
        const errorText = await response.text();
        console.error('Failed to create job:', errorText);
        console.error('Failed to create job:', errorText);
      }
    } catch (error) {
      console.error('Create job error:', error);
      console.error('Failed to create job:', error);
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
    console.log('handleUploadFiles called', { jobId: jobState.jobId, files: jobState.files });

    // Packing slip is required, COC is optional
    if (!jobState.files?.packing) {
      console.log('No packing slip file selected');
      alert('Please select a Packing Slip PDF file');
      return;
    }

    setLoading(true);
    setLoadingMessage('Creating job...');

    let currentJobId = jobState.jobId;

    // Auto-create job if not exists
    if (!currentJobId) {
      try {
        // Generate auto name from packing slip filename
        const packingFileName = jobState.files.packing.name.replace('.pdf', '').replace('.PDF', '');
        const autoJobName = `COC-${packingFileName}`;

        console.log('Auto-creating job:', autoJobName);
        const response = await fetch(`${API_BASE}/api/jobs`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: autoJobName,
            submitted_by: 'Auto'
          })
        });

        if (response.ok) {
          const data = await response.json();
          currentJobId = data.job_id;
          setJobState(prev => ({ ...prev, jobId: currentJobId, name: autoJobName }));
          console.log('Job auto-created:', currentJobId);
        } else {
          const errorText = await response.text();
          console.error('Failed to auto-create job:', errorText);
          alert('Failed to create job. Please try again.');
          setLoading(false);
          setLoadingMessage('');
          return;
        }
      } catch (error) {
        console.error('Error auto-creating job:', error);
        alert('Failed to create job. Please check your connection.');
        setLoading(false);
        setLoadingMessage('');
        return;
      }
    }

    setLoadingMessage('Uploading files...');
    const formData = new FormData();

    // Add COC file if provided (optional)
    if (jobState.files.coc) {
      formData.append('company_coc', jobState.files.coc);
      console.log('Added COC file to form:', jobState.files.coc.name);
    }

    // Add packing slip (required)
    formData.append('packing_slip', jobState.files.packing);
    console.log('Added packing slip to form:', jobState.files.packing.name);

    try {
      console.log('Sending upload request to:', `${API_BASE}/api/jobs/${currentJobId}/files`);
      const response = await fetch(`${API_BASE}/api/jobs/${currentJobId}/files`, {
        method: 'POST',
        body: formData
      });

      console.log('Upload response:', response.status, response.ok);

      if (response.ok) {
        const data = await response.json();
        console.log('Upload successful:', data);
        // Automatically parse after upload (pass currentJobId since state may not be updated yet)
        setLoadingMessage('Extracting data from PDFs...');
        await handleParse(currentJobId);
      } else {
        const errorText = await response.text();
        console.error('Upload failed:', response.status, errorText);
        alert(`Upload failed: ${errorText}`);
        setLoading(false);
        setLoadingMessage('');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert(`Upload error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setLoading(false);
      setLoadingMessage('');
    }
  };

  const handleParse = async (overrideJobId?: string) => {
    const jobId = overrideJobId || jobState.jobId;
    if (!jobId) {
      console.error('No job found');
      return;
    }

    try {
      console.log('Parsing documents for job:', jobId);
      const response = await fetch(`${API_BASE}/api/jobs/${jobId}/parse`, {
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
        // Auto-progress to step 2 (manual data entry)
        setCurrentStep(2);
        setLoading(false);
        setLoadingMessage('');
      } else {
        const errorText = await response.text();
        console.error('Failed to parse:', errorText);
        setLoading(false);
        setLoadingMessage('');
      }
    } catch (error) {
      console.error('Parse error:', error);
      setLoading(false);
      setLoadingMessage('');
    }
  };

  const handleManualDataSubmit = async (manualData: {
    partial_delivery_number: string;
    undelivered_quantity: string;
    remarks: string;
  }) => {
    if (!jobState.jobId) {
      console.error('No job found');
      return;
    }

    setLoading(true);
    setLoadingMessage('Saving data...');
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

        // Automatically validate and render
        setLoadingMessage('Validating data...');
        await handleValidateAndRender();
      } else {
        const errorText = await response.text();
        console.error('Failed to save manual data:', errorText);
        setLoading(false);
        setLoadingMessage('');
      }
    } catch (error) {
      console.error('Manual data error:', error);
      setLoading(false);
      setLoadingMessage('');
    }
  };

  const handleValidateAndRender = async () => {
    if (!jobState.jobId) {
      console.error('No job found');
      return;
    }

    try {
      // Validate
      console.log('Validating data for job:', jobState.jobId);
      const validateResponse = await fetch(`${API_BASE}/api/jobs/${jobState.jobId}/validate`, {
        method: 'POST'
      });

      if (validateResponse.ok) {
        const validateData = await validateResponse.json();
        console.log('Validation result:', validateData);
        setJobState(prev => ({
          ...prev,
          validationResult: validateData.validation
        }));

        // If validation has blocking errors, stop here
        if (validateData.has_errors) {
          setShowValidationErrorModal(true);
          setLoading(false);
          setLoadingMessage('');
          return;
        }

        // Render
        setLoadingMessage('Generating document...');
        console.log('Rendering document for job:', jobState.jobId);
        const renderResponse = await fetch(`${API_BASE}/api/jobs/${jobState.jobId}/render`, {
          method: 'POST'
        });

        if (renderResponse.ok) {
          const renderData = await renderResponse.json();
          console.log('Render result:', renderData);
          // Handle both old format (rendered_file) and new format (files.docx)
          const docxFile = renderData.rendered_file || renderData.files?.docx || 'document.docx';
          setJobState(prev => ({
            ...prev,
            renderedFiles: {
              docx: docxFile,
              template: renderData.template_used || { name: 'Default', version: '1.0' }
            }
          }));
          // Auto-progress to download (step 3)
          setCurrentStep(3);
          setLoading(false);
          setLoadingMessage('');
        } else {
          const errorText = await renderResponse.text();
          console.error('Failed to render:', errorText);
          setLoading(false);
          setLoadingMessage('');
        }
      } else {
        const errorText = await validateResponse.text();
        console.error('Failed to validate:', errorText);
        setLoading(false);
        setLoadingMessage('');
      }
    } catch (error) {
      console.error('Validate/Render error:', error);
      setLoading(false);
      setLoadingMessage('');
    }
  };

  const handleValidate = async () => {
    if (!jobState.jobId) {
      console.error('No job found'); return;
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
          // Show validation error modal instead of just an alert
          setShowValidationErrorModal(true);
        } else if (data.has_warnings) {
          // Validation has warnings but can proceed - auto-progress to render
          setCurrentStep(5);
        } else {
          // Auto-progress to render step
          setCurrentStep(5);
        }
      } else {
        const errorText = await response.text();
        console.error('Failed to validate:', errorText);
        console.error('Failed to validate data:', errorText);
      }
    } catch (error) {
      console.error('Validation error:', error);
      console.error('Failed to validate data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRender = async () => {
    if (!jobState.jobId) {
      console.error('No job found'); return;
      return;
    }

    setLoading(true);
    try {
      console.log('Rendering document for job:', jobState.jobId);
      const response = await fetch(`${API_BASE}/api/jobs/${jobState.jobId}/render`, {
        method: 'POST'
      });

      console.log('Render response:', response.status, response.ok);

      if (response.ok) {
        const data = await response.json();
        console.log('Render result:', data);
        setJobState({
          ...jobState,
          renderedFiles: {
            docx: data.rendered_file,
            template: data.template_used
          }
        });
        // Auto-progress to download
        setCurrentStep(6);
      } else {
        const errorText = await response.text();
        console.error('Failed to render:', errorText);
        console.error('Failed to render document:', errorText);
      }
    } catch (error) {
      console.error('Render error:', error);
      console.error('Failed to render document:', error);
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
            <h3 className="text-xl font-semibold">Step 1: Upload Files</h3>

            <div className="bg-white rounded-lg shadow p-6 space-y-4">
              <h4 className="font-semibold">Upload Documents</h4>
              <p className="text-sm text-gray-600">
                Upload the Packing Slip PDF (required) and optionally the Company COC PDF to extract data.
              </p>
              <div>
                <label className="block text-sm font-medium mb-2">
                  Company COC PDF <span className="text-gray-500 font-normal">(Optional)</span>
                </label>
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
                <label className="block text-sm font-medium mb-2">
                  Packing Slip PDF <span className="text-red-500">*</span>
                </label>
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
                disabled={loading || !jobState.files?.packing}
                className="w-full bg-green-600 text-white py-3 rounded hover:bg-green-700 disabled:bg-gray-400 font-medium"
              >
                {loading ? loadingMessage || 'Processing...' : 'Upload Files & Continue'}
              </button>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold">Step 2: Review & Complete Data</h3>

            {jobState.manualData ? (
              <div className="bg-white rounded-lg shadow p-6">
                <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded">
                  <p className="text-sm text-green-800 font-semibold mb-2">✓ Manual data submitted successfully</p>
                  <div className="text-xs text-gray-600 space-y-1">
                    <p><strong>Partial Delivery #:</strong> {jobState.manualData.partial_delivery_number}</p>
                    <p><strong>Undelivered Quantity:</strong> {jobState.manualData.undelivered_quantity}</p>
                    {jobState.manualData.remarks && (
                      <p><strong>Remarks:</strong> {jobState.manualData.remarks}</p>
                    )}
                    {jobState.manualData.contract_number && (
                      <p><strong>Contract Number:</strong> {jobState.manualData.contract_number}</p>
                    )}
                    {jobState.manualData.shipment_no && (
                      <p><strong>Shipment Number:</strong> {jobState.manualData.shipment_no}</p>
                    )}
                    {jobState.manualData.product_description && (
                      <p><strong>Product Description:</strong> {jobState.manualData.product_description}</p>
                    )}
                    {jobState.manualData.quantity && (
                      <p><strong>Quantity:</strong> {jobState.manualData.quantity}</p>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      // Clear manual data to show the form again
                      setJobState({
                        ...jobState,
                        manualData: null
                      });
                    }}
                    className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700 font-medium"
                  >
                    ✏️ Edit Data
                  </button>
                  <button
                    onClick={() => setCurrentStep(4)}
                    className="flex-1 bg-green-600 text-white py-2 rounded hover:bg-green-700 font-medium"
                  >
                    Continue to Validation →
                  </button>
                </div>
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
                    remarks: formData.get('remarks') as string || ''
                  };

                  // Check for optional extracted data fields
                  const contract = formData.get('contract_number') as string;
                  const shipment = formData.get('shipment_no') as string;
                  const product = formData.get('product_description') as string;
                  const qty = formData.get('quantity') as string;

                  // Add optional extracted data fields if provided (BEFORE checking for missing)
                  if (contract && contract.trim() !== '') data.contract_number = contract;
                  if (shipment && shipment.trim() !== '') data.shipment_no = shipment;
                  if (product && product.trim() !== '') data.product_description = product;
                  if (qty && qty.trim() !== '') data.quantity = parseInt(qty);

                  // Track which optional fields are missing
                  const missingFields: string[] = [];
                  if (!contract || contract.trim() === '') missingFields.push('Contract Number');
                  if (!shipment || shipment.trim() === '') missingFields.push('Shipment Number');
                  if (!product || product.trim() === '') missingFields.push('Product Description');
                  if (!qty || qty.trim() === '') missingFields.push('Quantity');

                  // If any optional fields are missing, ask for confirmation
                  if (missingFields.length > 0) {
                    // Store the data (now includes filled optional fields!) and show custom modal
                    setPendingManualData(data);
                    setMissingDataFields(missingFields);
                    setShowMissingDataModal(true);
                    return;
                  }

                  handleManualDataSubmit(data);
                }} className="space-y-4">

                  {/* Extracted Data Section - Optional Fields */}
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded">
                    <h4 className="font-semibold text-blue-900 mb-3">📄 Extracted Data from PDFs</h4>
                    <p className="text-xs text-gray-600 mb-3">
                      These fields were automatically extracted. Verify the values and fill in any missing data.
                    </p>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Contract Number
                        </label>
                        <input
                          type="text"
                          name="contract_number"
                          defaultValue={jobState.extractedData?.part_I?.contract_number || ''}
                          placeholder={jobState.extractedData?.part_I?.contract_number ? '' : 'Enter contract number if missing'}
                          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        />
                        {jobState.extractedData?.part_I?.contract_number && (
                          <p className="text-xs text-green-600 mt-1">
                            ✓ Auto-filled from PDF
                          </p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Shipment Number
                        </label>
                        <input
                          type="text"
                          name="shipment_no"
                          defaultValue={jobState.extractedData?.part_I?.shipment_no || ''}
                          placeholder={jobState.extractedData?.part_I?.shipment_no ? '' : 'Enter shipment number if missing'}
                          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        />
                        {jobState.extractedData?.part_I?.shipment_no && (
                          <p className="text-xs text-green-600 mt-1">
                            ✓ Auto-filled from PDF
                          </p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Product Description
                        </label>
                        <input
                          type="text"
                          name="product_description"
                          defaultValue={jobState.extractedData?.part_I?.product_description || ''}
                          placeholder={jobState.extractedData?.part_I?.product_description ? '' : 'Enter product description if missing'}
                          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        />
                        {jobState.extractedData?.part_I?.product_description && (
                          <p className="text-xs text-green-600 mt-1">
                            ✓ Auto-filled from PDF
                          </p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          Quantity
                        </label>
                        <input
                          type="number"
                          name="quantity"
                          defaultValue={jobState.extractedData?.part_I?.quantity || ''}
                          placeholder={jobState.extractedData?.part_I?.quantity ? '' : 'Enter quantity if missing'}
                          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        />
                        {jobState.extractedData?.part_I?.quantity && (
                          <p className="text-xs text-green-600 mt-1">
                            ✓ Auto-filled from PDF
                          </p>
                        )}
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
                        <textarea
                          name="undelivered_quantity"
                          placeholder="Single item: 4196 (of 8115)&#10;&#10;Multiple items (one per line):&#10;813 (of 1472)&#10;95 (of 542)&#10;0 (of 234)"
                          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-green-500 focus:border-transparent"
                          rows={4}
                          required
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Format: remaining qty (of total ordered). For multiple items in the Packing Slip, enter each on a new line in the same order as listed.
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">
                          Remarks or Comments
                        </label>
                        <textarea
                          name="remarks"
                          placeholder="Enter any additional information or comments..."
                          className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-green-500 focus:border-transparent"
                          rows={3}
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Additional information or comments for this shipment (optional)
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

      case 3:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold">Step 3: Download Result</h3>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 mb-4">Download your generated Dutch MoD COC document</p>

              {jobState.renderedFiles ? (
                <div className="space-y-4">
                  <div className="p-4 bg-green-50 border-2 border-green-300 rounded">
                    <h4 className="font-semibold text-green-800 mb-2">🎉 Conversion Complete!</h4>
                    <div className="text-sm text-green-700 space-y-2">
                      <p>Your COC-D document has been successfully generated and is ready for download.</p>
                      <div className="mt-3 p-3 bg-white rounded border border-green-200">
                        <p className="font-semibold">Document Details:</p>
                        <p className="text-xs mt-1"><strong>Job:</strong> {jobState.name}</p>
                        <p className="text-xs"><strong>Submitted by:</strong> {jobState.submittedBy}</p>
                        <p className="text-xs"><strong>File:</strong> {jobState.renderedFiles.docx}</p>
                        <p className="text-xs"><strong>Template:</strong> {jobState.renderedFiles.template?.name} v{jobState.renderedFiles.template?.version}</p>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      window.open(`${API_BASE}/api/jobs/${jobState.jobId}/download`, '_blank');
                    }}
                    className="w-full bg-green-600 text-white py-3 rounded hover:bg-green-700 font-medium flex items-center justify-center gap-2"
                  >
                    <span>⬇️</span>
                    <span>Download COC-D Document</span>
                  </button>

                  <div className="flex gap-2">
                    <button
                      onClick={() => setCurrentStep(2)}
                      className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700 text-sm"
                    >
                      ← Back to Step 2
                    </button>
                    <button
                      onClick={() => {
                        setCurrentStep(1);
                        setJobState({
                          jobId: null,
                          name: '',
                          submittedBy: '',
                          files: null,
                          extractedData: null,
                          manualData: null,
                          validationResult: null,
                          renderedFiles: null
                        });
                      }}
                      className="flex-1 bg-gray-600 text-white py-2 rounded hover:bg-gray-700 text-sm"
                    >
                      Start New Job
                    </button>
                  </div>
                </div>
              ) : (
                <div className="p-4 bg-yellow-50 border border-yellow-300 rounded">
                  <p className="text-sm text-yellow-800">
                    ⚠️ No document has been rendered yet. Please go back to Step 2 and complete the process.
                  </p>
                  <button
                    onClick={() => setCurrentStep(2)}
                    className="mt-3 w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
                  >
                    Go to Step 2
                  </button>
                </div>
              )}
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

      {/* Confirmation Modal for Missing Data */}
      <ConfirmationModal
        isOpen={showMissingDataModal}
        title="Missing Extracted Data"
        message="The following fields are empty. These fields are optional, but leaving them empty may cause validation errors later."
        items={missingDataFields}
        onConfirm={() => {
          // User confirmed - proceed with incomplete data
          setShowMissingDataModal(false);
          if (pendingManualData) {
            handleManualDataSubmit(pendingManualData);
            setPendingManualData(null);
          }
        }}
        onCancel={() => {
          // User cancelled - stay on form to fill in fields
          setShowMissingDataModal(false);
          setPendingManualData(null);
          setMissingDataFields([]);
        }}
        confirmText="Proceed Anyway"
        cancelText="Go Back & Fill In"
        type="warning"
      />

      {/* Validation Error Modal */}
      <ConfirmationModal
        isOpen={showValidationErrorModal}
        title="Validation Errors Found"
        message="The following validation errors were found. You can fix them or proceed anyway (not recommended)."
        items={jobState.validationResult?.errors?.map((err: any) => err.message) || []}
        onConfirm={() => {
          // User wants to skip validation
          setShowValidationErrorModal(false);
          if (confirm('⚠️ Final Warning\n\nProceeding with validation errors may result in incomplete or incorrect documents.\n\nAre you absolutely sure?')) {
            setCurrentStep(5);
          }
        }}
        onCancel={() => {
          // User wants to fix errors - go back to Step 3
          setShowValidationErrorModal(false);
          setCurrentStep(3);
        }}
        confirmText="Skip Validation (Not Recommended)"
        cancelText="Go Back to Step 3 & Fix"
        type="error"
      />

      <div className="container mx-auto p-6 max-w-5xl">
        {/* Debug info */}
        <div className="mb-4 p-2 bg-blue-100 text-xs text-blue-800 rounded">
          DEBUG: Current Step = {currentStep} | Job ID = {jobState.jobId || 'None'}
        </div>

        {/* Workflow Steps */}
        <div className="mb-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-sm font-semibold text-gray-500 mb-4">CONVERSION WORKFLOW</h2>
          <div className="grid grid-cols-3 gap-4">
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

        {/* Loading Overlay */}
        {loading && loadingMessage && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-8 max-w-md mx-4 text-center">
              <div className="mb-4">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
              <p className="text-lg font-semibold text-gray-800">{loadingMessage}</p>
              <p className="text-sm text-gray-500 mt-2">Please wait...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
