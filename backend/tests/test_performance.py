import pytest
import time
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

# Mock pdfplumber
import unittest.mock as mock
sys.modules['pdfplumber'] = mock.MagicMock()

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_response_time():
    """Ensure API responds quickly"""
    start = time.time()
    response = client.get("/")
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 1.0, f"API took {elapsed:.2f}s to respond"

def test_job_creation_performance():
    """Test multiple job creation"""
    times = []
    
    for i in range(5):
        start = time.time()
        response = client.post("/api/jobs", json={
            "name": f"Perf Test {i}",
            "submitted_by": "Tester"
        })
        elapsed = time.time() - start
        times.append(elapsed)
        assert response.status_code == 200
    
    avg_time = sum(times) / len(times)
    assert avg_time < 0.5, f"Average job creation took {avg_time:.2f}s"
    print(f"\n⏱️ Average job creation time: {avg_time:.3f}s")