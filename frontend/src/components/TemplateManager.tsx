// frontend/src/components/TemplateManager.tsx
import React, { useState, useEffect } from 'react';

interface Template {
  id: string;
  name: string;
  version: string;
  filename: string;
  uploaded_at: string;
  is_default: boolean;
}

export default function TemplateManager() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  
  const [uploadData, setUploadData] = useState({
    file: null as File | null,
    name: '',
    version: '',
    set_as_default: false
  });

  const API_BASE = 'http://localhost:8000';

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/templates`);
      const data = await response.json();
      setTemplates(data.templates);
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTemplates();
  }, []);

  const handleUpload = async () => {
    if (!uploadData.file || !uploadData.name || !uploadData.version) {
      return; // Form validation prevents this
    }

    const formData = new FormData();
    formData.append('file', uploadData.file);
    formData.append('name', uploadData.name);
    formData.append('version', uploadData.version);
    formData.append('set_as_default', String(uploadData.set_as_default));

    setUploading(true);
    try {
      const response = await fetch(`${API_BASE}/api/templates/upload`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        // Success - close form and refresh list (no popup needed)
        setShowUpload(false);
        setUploadData({ file: null, name: '', version: '', set_as_default: false });
        loadTemplates();
      } else {
        const error = await response.json();
        console.error('Upload failed:', error.detail);
      }
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  const handleSetDefault = async (templateId: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/templates/${templateId}/set-default`, {
        method: 'PUT'
      });

      if (response.ok) {
        loadTemplates();
      }
    } catch (error) {
      console.error('Failed to set default:', error);
    }
  };

  const handleDelete = async (templateId: string) => {
    if (!confirm('Are you sure you want to delete this template?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/templates/${templateId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        loadTemplates();
      } else {
        const error = await response.json();
        console.error('Delete failed:', error.detail);
      }
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  };

  const handleDownload = (templateId: string) => {
    window.open(`${API_BASE}/api/templates/${templateId}/download`, '_blank');
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Template Management</h2>
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          {showUpload ? 'Cancel' : 'Upload New Template'}
        </button>
      </div>

      {/* Upload Form */}
      {showUpload && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="font-semibold mb-3">Upload New Template</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium mb-1">Template File (DOCX)</label>
              <input
                type="file"
                accept=".docx"
                onChange={(e) => setUploadData({ ...uploadData, file: e.target.files?.[0] || null })}
                className="block w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-100 file:text-blue-700"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Template Name</label>
              <input
                type="text"
                value={uploadData.name}
                onChange={(e) => setUploadData({ ...uploadData, name: e.target.value })}
                placeholder="e.g., Dutch COC Template"
                className="w-full p-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Version</label>
              <input
                type="text"
                value={uploadData.version}
                onChange={(e) => setUploadData({ ...uploadData, version: e.target.value })}
                placeholder="e.g., 1.0"
                className="w-full p-2 border rounded"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={uploadData.set_as_default}
                onChange={(e) => setUploadData({ ...uploadData, set_as_default: e.target.checked })}
                className="w-4 h-4"
              />
              <label className="text-sm">Set as default template</label>
            </div>
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 disabled:bg-gray-400"
            >
              {uploading ? 'Uploading...' : 'Upload Template'}
            </button>
          </div>
        </div>
      )}

      {/* Templates List */}
      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading templates...</div>
      ) : templates.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p className="mb-2">No templates uploaded yet.</p>
          <p className="text-sm">Upload a DOCX template to get started.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {templates.map((template) => (
            <div
              key={template.id}
              className={`p-4 rounded-lg border ${
                template.is_default ? 'border-green-500 bg-green-50' : 'border-gray-300 bg-white'
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-lg">{template.name}</h3>
                    {template.is_default && (
                      <span className="px-2 py-1 bg-green-600 text-white text-xs rounded">
                        DEFAULT
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mt-1">Version: {template.version}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Uploaded: {new Date(template.uploaded_at).toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">ID: {template.id}</p>
                </div>
                <div className="flex gap-2">
                  {!template.is_default && (
                    <button
                      onClick={() => handleSetDefault(template.id)}
                      className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                    >
                      Set Default
                    </button>
                  )}
                  <button
                    onClick={() => handleDownload(template.id)}
                    className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                  >
                    Download
                  </button>
                  <button
                    onClick={() => handleDelete(template.id)}
                    className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}