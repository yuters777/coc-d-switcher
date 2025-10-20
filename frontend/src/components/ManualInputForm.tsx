// frontend/src/components/ManualInputForm.tsx
import React, { useState } from 'react';

interface ManualInputFormProps {
  extractedData: any;
  onSubmit: (data: ManualInputData) => void;
  loading: boolean;
}

interface ManualInputData {
  partial_delivery_number: string;
  undelivered_quantity: string;
  sw_version: string;
}

export default function ManualInputForm({ extractedData, onSubmit, loading }: ManualInputFormProps) {
  const [formData, setFormData] = useState<ManualInputData>({
    partial_delivery_number: '',
    undelivered_quantity: '',
    sw_version: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.partial_delivery_number || !formData.undelivered_quantity || !formData.sw_version) {
      alert('Please fill in all required fields');
      return;
    }
    
    onSubmit(formData);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Enter Manual Data</h2>
      
      {extractedData && (
        <div className="mb-6 p-4 bg-blue-50 rounded">
          <h3 className="font-semibold mb-2">Extracted Data Summary:</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div><strong>Contract:</strong> {extractedData.template_vars?.contract_number}</div>
            <div><strong>Shipment:</strong> {extractedData.template_vars?.shipment_no}</div>
            <div><strong>Product:</strong> {extractedData.template_vars?.product_description}</div>
            <div><strong>Quantity:</strong> {extractedData.template_vars?.quantity}</div>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            Partial Delivery Number <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.partial_delivery_number}
            onChange={(e) => setFormData({...formData, partial_delivery_number: e.target.value})}
            placeholder="e.g., 165"
            className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
            value={formData.undelivered_quantity}
            onChange={(e) => setFormData({...formData, undelivered_quantity: e.target.value})}
            placeholder="e.g., 4196 (of 8115)"
            className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
            value={formData.sw_version}
            onChange={(e) => setFormData({...formData, sw_version: e.target.value})}
            placeholder="e.g., 2.2.15.45"
            className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            The software version for this product
          </p>
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
  );
}