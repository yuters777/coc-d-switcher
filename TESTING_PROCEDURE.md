# COC-D Switcher Testing Procedure

Complete step-by-step testing guide for the COC-D Switcher application.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Test (Docker)](#quick-test-docker)
3. [Backend Testing](#backend-testing)
4. [Frontend Testing](#frontend-testing)
5. [Integration Testing](#integration-testing)
6. [End-to-End Testing](#end-to-end-testing)
7. [Manual Testing](#manual-testing)
8. [Performance Testing](#performance-testing)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- Python 3.9 or higher
- Node.js 18.x or higher
- Docker and Docker Compose (for containerized testing)
- Git

### Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd coc-d-switcher

# Verify structure
ls -la
# Should see: backend/, frontend/, docker-compose.yml, README.md
```

---

## Quick Test (Docker)

**Best for:** Quick validation that everything works together.

### Step 1: Build and Start Services
```bash
# From project root
docker-compose up --build
```

**Expected Output:**
- Backend starts on port 8000
- Frontend starts on port 5173
- No error messages in logs

### Step 2: Verify Services
```bash
# In a new terminal
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:5173
```

### Step 3: Run Full Workflow Test
```bash
# While services are running
python3 run_full_test.py
```

**Expected Output:**
```
Testing COC-D Switcher Full Workflow
==================================================
1. Creating job...
   Job created: <job_id>
2. Uploading PDFs...
   Files uploaded
3. Parsing documents...
   Extracted X serials
4. Validating...
   0 errors, X warnings
5. Rendering Dutch COC...
   Documents rendered
6. Getting final job status...
   Status: completed
==================================================
Test complete!
```

### Step 4: Stop Services
```bash
# Press Ctrl+C in docker-compose terminal
docker-compose down
```

---

## Backend Testing

### Setup Backend Environment

#### Step 1: Navigate to Backend
```bash
cd backend
```

#### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

**Verify installation:**
```bash
pip list | grep -E "(pytest|fastapi|pdfplumber)"
```

### Run Backend Tests

#### Step 4: Run All Tests
```bash
# From backend directory with venv activated
./run_tests.sh
```

**Expected Output Structure:**
```
Running COC-D Switcher Test Suite
==================================
Running unit tests...
tests/test_unit/ ✓✓✓✓✓✓

Running API tests...
tests/test_api/ ✓✓✓✓✓✓

Running integration tests...
tests/test_integration.py ✓✓✓

Generating coverage report...
Coverage: XX%
```

#### Step 5: Run Tests by Category

**Unit Tests Only:**
```bash
pytest tests/test_unit/ -v
```

**API Tests Only:**
```bash
pytest tests/test_api/ -v
```

**Integration Tests Only:**
```bash
pytest tests/test_integration.py -v
```

**Specific Test File:**
```bash
pytest tests/test_extraction.py -v
```

**Single Test Function:**
```bash
pytest tests/test_basic.py::test_health_check -v
```

#### Step 6: Generate Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
```

**View HTML report:**
```bash
# Report generated at: htmlcov/index.html
python3 -m http.server 8080 --directory htmlcov
# Open http://localhost:8080 in browser
```

#### Step 7: Run Specific Backend Tests

**Test PDF Extraction:**
```bash
python3 test_pdf_extraction.py
```

**Test Document Rendering:**
```bash
python3 test_rendering.py
```

**Test Full Backend Flow:**
```bash
python3 test_full_backend_flow.py
```

---

## Frontend Testing

### Setup Frontend Environment

#### Step 1: Navigate to Frontend
```bash
cd frontend
```

#### Step 2: Install Dependencies
```bash
npm install
```

**Verify installation:**
```bash
npm list react react-dom
```

#### Step 3: Add Test Dependencies (if not present)
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event vitest jsdom
```

#### Step 4: Run Frontend Tests
```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

**Expected Output:**
```
✓ tests/App.test.tsx (3)
  ✓ renders main heading
  ✓ create job button works
  ✓ displays validation errors

Tests: 3 passed (3 total)
```

---

## Integration Testing

**Purpose:** Test interaction between backend and frontend.

### Step 1: Start Backend Server
```bash
# Terminal 1
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Wait for:** `Application startup complete`

### Step 2: Run Integration Tests
```bash
# Terminal 2
cd backend
source venv/bin/activate
pytest tests/test_integration.py -v
```

**Expected Tests:**
- ✓ Job creation
- ✓ File upload
- ✓ PDF parsing
- ✓ Validation workflow
- ✓ Document rendering

### Step 3: Check API Documentation
```bash
# With backend running, open in browser:
http://localhost:8000/docs
```

**Manual API Testing:**
1. Click "POST /api/jobs"
2. Click "Try it out"
3. Enter test data:
```json
{
  "name": "Test Job",
  "submitted_by": "Tester"
}
```
4. Click "Execute"
5. Verify 200 response with job_id

---

## End-to-End Testing

**Purpose:** Test complete user workflow from frontend to backend.

### Step 1: Start Both Services

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 2: Access Application
```bash
# Open in browser:
http://localhost:5173
```

### Step 3: Test Complete Workflow

#### 3.1 Create New Job
1. Click "Create New Job" button
2. Enter job details:
   - Name: `Test Shipment 6SH264587`
   - Submitted by: `Test User`
3. Click "Create"
4. **Verify:** Job appears in list with "pending" status

#### 3.2 Upload Documents
1. Click on created job
2. Click "Upload Files"
3. Select files:
   - Company COC (PDF)
   - Packing Slip (PDF)
4. Click "Upload"
5. **Verify:** Files appear in file list

#### 3.3 Parse Documents
1. Click "Parse Documents" button
2. Wait for processing
3. **Verify:**
   - Status changes to "parsed"
   - Extracted data appears in preview
   - Serial numbers are listed
   - Part information is visible

#### 3.4 Validate Data
1. Review extracted data
2. Click "Validate" button
3. **Verify:**
   - Validation panel shows results
   - Errors (if any) are highlighted in red
   - Warnings (if any) are shown in yellow
   - Serial count matches

#### 3.5 Render Dutch COC
1. If validation passes (no errors)
2. Click "Render COC-D" button
3. Wait for generation
4. **Verify:**
   - Status changes to "completed"
   - Download button appears
   - Preview shows generated document

#### 3.6 Download Result
1. Click "Download COC-D" button
2. **Verify:**
   - DOCX file downloads
   - File opens correctly
   - Contains all required sections:
     - Part I (Article Description)
     - Part II (Packaging Data)
     - Part III (Transportation Data)

### Step 4: Run Automated E2E Test
```bash
# With both services running
python3 run_full_test.py
```

---

## Manual Testing

### Test Cases

#### TC-001: Job Creation
**Steps:**
1. Navigate to http://localhost:5173
2. Click "Create New Job"
3. Enter: Name = "Test Job", Submitted by = "Tester"
4. Click "Create"

**Expected:**
- Job created successfully
- Job ID generated
- Job appears in list
- Status = "pending"

#### TC-002: File Upload
**Steps:**
1. Select a job
2. Click "Upload Files"
3. Select valid PDF files
4. Click "Upload"

**Expected:**
- Files upload successfully
- File names appear in list
- File sizes shown correctly
- No error messages

#### TC-003: PDF Parsing
**Steps:**
1. Job with uploaded files
2. Click "Parse Documents"
3. Wait for completion

**Expected:**
- Parsing completes within 30 seconds
- Extracted data appears
- Serial numbers extracted
- Part information extracted
- No parsing errors

#### TC-004: Data Validation
**Steps:**
1. Job with parsed data
2. Review extracted data
3. Click "Validate"

**Expected:**
- Validation completes within 5 seconds
- Errors displayed if present
- Warnings displayed if present
- Validation summary shown

#### TC-005: Document Rendering
**Steps:**
1. Job with validated data (no errors)
2. Click "Render COC-D"
3. Wait for generation

**Expected:**
- Rendering completes within 20 seconds
- Download button appears
- Status changes to "completed"
- Generated document is valid DOCX

#### TC-006: Error Handling
**Steps:**
1. Try to upload invalid file (e.g., .txt)
2. Try to parse without files
3. Try to render with validation errors

**Expected:**
- Appropriate error messages
- User cannot proceed with invalid state
- System remains stable

---

## Performance Testing

### Step 1: Run Performance Tests
```bash
cd backend
source venv/bin/activate
pytest tests/test_performance.py -v
```

### Step 2: Test with Multiple Jobs
```bash
# Create 10 test jobs
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/jobs \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"Test Job $i\",\"submitted_by\":\"Tester\"}"
done
```

### Step 3: Monitor Resource Usage
```bash
# While running tests
docker stats
```

**Expected Performance:**
- Job creation: < 100ms
- File upload (5MB): < 2s
- PDF parsing: < 30s
- Validation: < 5s
- Rendering: < 20s

---

## Troubleshooting

### Backend Issues

#### Backend won't start
```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check if port is in use
lsof -i :8000
# If occupied, kill process or use different port

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Tests fail with import errors
```bash
# Ensure you're in backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run tests again
pytest tests/ -v
```

#### PDF parsing fails
```bash
# Check pdfplumber installation
pip show pdfplumber

# Reinstall if needed
pip install --upgrade pdfplumber

# Test with sample
python3 test_pdf_extraction.py
```

### Frontend Issues

#### Frontend won't start
```bash
# Check Node version
node --version  # Should be 18.x+

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for port conflicts
lsof -i :5173
```

#### Tests fail
```bash
# Clear cache
npm run test -- --clearCache

# Reinstall test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest jsdom
```

### Docker Issues

#### Docker services won't start
```bash
# Check Docker is running
docker ps

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

#### Services can't connect
```bash
# Check network
docker network ls
docker network inspect coc-d-switcher_default

# Check logs
docker-compose logs backend
docker-compose logs frontend
```

### Integration Test Issues

#### Backend/Frontend can't connect
```bash
# Check backend is running
curl http://localhost:8000/health

# Check frontend API URL configuration
# Should point to http://localhost:8000

# Check CORS settings in backend
# backend/app/main.py should allow localhost:5173
```

---

## Test Summary Checklist

Use this checklist to verify all testing is complete:

- [ ] Docker quick test passes
- [ ] All backend unit tests pass
- [ ] All backend API tests pass
- [ ] Backend integration tests pass
- [ ] Frontend tests pass
- [ ] Manual test cases TC-001 through TC-006 pass
- [ ] End-to-end workflow test passes
- [ ] Performance tests meet targets
- [ ] No errors in backend logs
- [ ] No errors in frontend console
- [ ] Documentation is accurate

---

## Continuous Testing

### Pre-commit Testing
```bash
# Before committing code
cd backend
./run_tests.sh

cd ../frontend
npm test
```

### Automated CI/CD
If using CI/CD (GitHub Actions, GitLab CI, etc.):
1. All tests run automatically on push
2. Docker build tests run on PRs
3. Coverage reports generated
4. Performance benchmarks tracked

---

## Additional Resources

- **API Documentation:** http://localhost:8000/docs (when backend running)
- **Coverage Reports:** backend/htmlcov/index.html
- **Sample Test Data:** testing/input_samples/
- **Backend Tests:** backend/tests/
- **Frontend Tests:** frontend/src/__tests__/

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review test output for specific error messages
3. Refer to troubleshooting section above
4. Check README.md for setup instructions

---

**Last Updated:** 2025-11-04
**Version:** 1.0.0
