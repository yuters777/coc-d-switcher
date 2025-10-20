import React, { useState } from 'react';

interface FileUploadProps {
  jobId: string;
  onUploadComplete: () => void;
}

export default function FileUpload({ jobId, onUploadComplete }: FileUploadProps) {
  const [files, setFiles] = useState<{ coc?: File; packing?: File }>({});
  const [uploading, setUploading] = useState(false);

  const handleFileSelect = (type: 'coc' | 'packing', file: File) => {
    setFiles(prev => ({ ...prev, [type]: file }));
  };

  const handleUpload = async () => {
    if (!files.coc || !files.packing) {
      alert('Please select both files');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('company_coc', files.coc);
    formData.append('packing_slip', files.packing);

    try {
      const response = await fetch(`http://localhost:8000/api/jobs/${jobId}/files`, {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        alert('Files uploaded successfully');
        onUploadComplete();
      }
    } catch (error) {
      alert('Upload failed: ' + error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">Upload Documents</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Company COC PDF</label>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => e.target.files && handleFileSelect('coc', e.target.files[0])}
            className="block w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">Packing Slip PDF</label>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => e.target.files && handleFileSelect('packing', e.target.files[0])}
            className="block w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>
        
        <button
          onClick={handleUpload}
          disabled={uploading || !files.coc || !files.packing}
          className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 disabled:bg-gray-400"
        >
          {uploading ? 'Uploading...' : 'Upload Files'}
        </button>
      </div>
    </div>
  );
}