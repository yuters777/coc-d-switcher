// frontend/src/pages/SettingsPage.tsx (NEW FILE)
import React from 'react';
import TemplateManager from '../components/TemplateManager';

interface SettingsPageProps {
  onBack: () => void;
}

export default function SettingsPage({ onBack }: SettingsPageProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-blue-600 text-white p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">Settings</h1>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-blue-700 rounded hover:bg-blue-800"
          >
            ← Back to Conversion
          </button>
        </div>
      </nav>
      
      <div className="container mx-auto p-6 max-w-6xl">
        <div className="mb-6">
          <h2 className="text-xl text-gray-600">Administrator Settings</h2>
          <p className="text-sm text-gray-500 mt-1">
            Manage templates and system configuration
          </p>
        </div>
        
        {/* Template Management Section */}
        <TemplateManager />
        
        {/* Future sections can be added here */}
        {/* 
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-3">Other Settings</h3>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-500">More configuration options coming soon...</p>
          </div>
        </div>
        */}
      </div>
    </div>
  );
}