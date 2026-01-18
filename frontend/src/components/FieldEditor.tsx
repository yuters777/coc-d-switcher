import { useState, useEffect } from 'react';

interface FieldEditorProps {
  jobId: string;
  data: any;
  onSave: (data: any) => void;
}

export default function FieldEditor({ jobId: _jobId, data, onSave }: FieldEditorProps) {
  const [fields, setFields] = useState(data || {});
  const [serials, setSerials] = useState<string[]>([]);

  useEffect(() => {
    if (data?.part_I?.serials) {
      setSerials(data.part_I.serials);
    }
  }, [data]);

  const handleFieldChange = (path: string, value: any) => {
    setFields((prev: any) => {
      const newData = { ...prev };
      const keys = path.split('.');
      let current = newData;
      
      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) current[keys[i]] = {};
        current = current[keys[i]];
      }
      current[keys[keys.length - 1]] = value;
      return newData;
    });
  };

  const handleSerialsChange = (text: string) => {
    const newSerials = text.split('\n').filter(s => s.trim());
    setSerials(newSerials);
    handleFieldChange('part_I.serials', newSerials);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">Edit Extracted Data</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Contract Number</label>
          <input
            type="text"
            value={fields?.part_I?.contract_number || ''}
            onChange={(e) => handleFieldChange('part_I.contract_number', e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Shipment Number</label>
          <input
            type="text"
            value={fields?.part_I?.applicable_to || ''}
            onChange={(e) => handleFieldChange('part_I.applicable_to', e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Quantity</label>
          <input
            type="number"
            value={fields?.part_I?.items?.[0]?.quantity || 0}
            onChange={(e) => handleFieldChange('part_I.items.0.quantity', parseInt(e.target.value))}
            className="w-full p-2 border rounded"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Serial Numbers ({serials.length})</label>
          <textarea
            value={serials.join('\n')}
            onChange={(e) => handleSerialsChange(e.target.value)}
            rows={10}
            className="w-full p-2 border rounded font-mono text-sm"
            placeholder="Enter serial numbers, one per line"
          />
        </div>

        <button
          onClick={() => onSave(fields)}
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
        >
          Save Changes
        </button>
      </div>
    </div>
  );
}