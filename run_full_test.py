#!/usr/bin/env python3
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
    print(f"\nJob ID: {job_id}")
    print(f"Access at: http://localhost:5173")
    
if __name__ == "__main__":
    test_workflow()
