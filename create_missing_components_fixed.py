#!/usr/bin/env python3
"""Create missing frontend components for COC-D Switcher"""

from pathlib import Path

def create_file(path, content):
    """Create file with proper encoding"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created {path}")

def create_missing_files():
    print("Creating missing frontend components...")
    
    # Create directories
    Path('frontend/src/pages').mkdir(parents=True, exist_ok=True)
    Path('frontend/src/components').mkdir(parents=True, exist_ok=True)
    Path('frontend/src/store').mkdir(parents=True, exist_ok=True)
    Path('testing/input_samples').mkdir(parents=True, exist_ok=True)
    Path('testing/output_samples').mkdir(parents=True, exist_ok=True)
    
    # Create SerialEditor component
    create_file('frontend/src/components/SerialEditor.tsx', '''import React, { useState } from 'react';

interface SerialEditorProps {
  serials: string[];
  onChange: (serials: string[]) => void;
}

export default function SerialEditor({ serials, onChange }: SerialEditorProps) {
  const [text, setText] = useState(serials.join('\\n'));

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    const newSerials = e.target.value.split('\\n').filter(s => s.trim());
    onChange(newSerials);
  };

  return (
    <div className="p-4">
      <h3 className="font-semibold mb-2">Serial Numbers ({serials.length})</h3>
      <textarea
        value={text}
        onChange={handleChange}
        className="w-full h-64 p-2 border rounded font-mono text-sm"
        placeholder="Enter serial numbers, one per line"
      />
    </div>
  );
}''')

    # Create ValidationPanel
    create_file('frontend/src/components/ValidationPanel.tsx', '''import React from 'react';

interface ValidationIssue {
  code: string;
  message: string;
  where: string;
}

interface ValidationPanelProps {
  errors: ValidationIssue[];
  warnings: ValidationIssue[];
}

export default function ValidationPanel({ errors, warnings }: ValidationPanelProps) {
  return (
    <div className="p-4 space-y-4">
      {errors.length > 0 && (
        <div>
          <h3 className="font-semibold text-red-600 mb-2">Errors ({errors.length})</h3>
          {errors.map((error, i) => (
            <div key={i} className="bg-red-50 border border-red-200 rounded p-2 mb-2">
              <p className="font-medium text-red-700">{error.code}</p>
              <p className="text-sm text-red-600">{error.message}</p>
              <p className="text-xs text-gray-500">Location: {error.where}</p>
            </div>
          ))}
        </div>
      )}
      
      {warnings.length > 0 && (
        <div>
          <h3 className="font-semibold text-yellow-600 mb-2">Warnings ({warnings.length})</h3>
          {warnings.map((warning, i) => (
            <div key={i} className="bg-yellow-50 border border-yellow-200 rounded p-2 mb-2">
              <p className="font-medium text-yellow-700">{warning.code}</p>
              <p className="text-sm text-yellow-600">{warning.message}</p>
              <p className="text-xs text-gray-500">Location: {warning.where}</p>
            </div>
          ))}
        </div>
      )}
      
      {errors.length === 0 && warnings.length === 0 && (
        <div className="text-green-600">
          Validation passed successfully
        </div>
      )}
    </div>
  );
}''')

    # Create TemplatePreview
    create_file('frontend/src/components/TemplatePreview.tsx', '''import React from 'react';

export default function TemplatePreview() {
  return (
    <div className="flex-1 p-4 bg-white">
      <div className="border rounded p-8" style={{ minHeight: '800px' }}>
        <h2 className="text-center font-bold text-lg mb-4">
          Certificate of Conformity - Part I
        </h2>
        <div className="space-y-4 text-sm">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="font-semibold">1. Supplier Serial No:</label>
              <p>COC_SV_Del165_20.03.2025.docx</p>
            </div>
            <div>
              <label className="font-semibold">3. Contract Number:</label>
              <p>697.12.5011.01</p>
            </div>
          </div>
          <div>
            <label className="font-semibold">2. Supplier:</label>
            <p>Elbit Systems C4I and Cyber Ltd</p>
            <p>2 Hamachshev, Netanya, Israel</p>
          </div>
          <div>
            <label className="font-semibold">6. Acquirer:</label>
            <p>NETHERLANDS MINISTRY OF DEFENCE</p>
          </div>
        </div>
      </div>
    </div>
  );
}''')

    # Create test runner
    create_file('run_full_test.py', '''#!/usr/bin/env python3
"""Full workflow test for COC-D Switcher"""

import requests
import json
import time
from pathlib import Path

API_URL = "http://localhost:8000"

def test_workflow():
    print("Testing COC-D Switcher Full Workflow")
    print("=" * 50)
    
    # 1. Create job
    print("1. Creating job...")
    resp = requests.post(f"{API_URL}/api/jobs", json={
        "name": "Test Shipment 6SH264587",
        "submitted_by": "Test User"
    })
    job_id = resp.json()["job_id"]
    print(f"   Job created: {job_id}")
    
    # 2. Upload files if they exist
    coc_file = Path("testing/input_samples/COC_6SH264587.pdf")
    pack_file = Path("testing/input_samples/Packing Slip_6SH264587.pdf")
    
    if coc_file.exists() and pack_file.exists():
        print("2. Uploading PDFs...")
        with open(coc_file, 'rb') as f1, open(pack_file, 'rb') as f2:
            files = {
                'company_coc': ('coc.pdf', f1, 'application/pdf'),
                'packing_slip': ('packing.pdf', f2, 'application/pdf')
            }
            resp = requests.post(f"{API_URL}/api/jobs/{job_id}/files", files=files)
            print(f"   Files uploaded")
    else:
        print("2. No PDFs found, will use fixtures")
    
    # 3. Parse
    print("3. Parsing documents...")
    resp = requests.post(f"{API_URL}/api/jobs/{job_id}/parse")
    data = resp.json()
    print(f"   Extracted {len(data.get('part_I', {}).get('serials', []))} serials")
    
    # 4. Validate
    print("4. Validating...")
    resp = requests.post(f"{API_URL}/api/jobs/{job_id}/validate")
    validation = resp.json()
    print(f"   {len(validation['errors'])} errors, {len(validation['warnings'])} warnings")
    
    if validation['errors']:
        print("   Errors found:")
        for err in validation['errors']:
            print(f"     - {err['code']}: {err['message']}")
    
    # 5. Render
    print("5. Rendering Dutch COC...")
    resp = requests.post(f"{API_URL}/api/jobs/{job_id}/render")
    if resp.status_code == 200:
        print("   Documents rendered")
    else:
        print(f"   Render failed: {resp.text}")
    
    # 6. Get job details
    print("6. Getting final job status...")
    resp = requests.get(f"{API_URL}/api/jobs/{job_id}")
    job = resp.json()
    print(f"   Status: {job['status']}")
    
    print("=" * 50)
    print("Test complete!")
    print(f"\\nJob ID: {job_id}")
    print(f"Access at: http://localhost:5173")
    
if __name__ == "__main__":
    test_workflow()
''')
    
    print("All missing components created!")
    print("\nNext steps:")
    print("1. Copy your PDF samples to testing/input_samples/")
    print("2. Start the backend: cd backend && uvicorn app.main:app --reload")
    print("3. Start the frontend: cd frontend && npm install && npm run dev")
    print("4. Run the test: python run_full_test.py")

if __name__ == "__main__":
    create_missing_files()