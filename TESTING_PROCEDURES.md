# Comprehensive Testing Procedures for COC-D Switcher

**Document Version:** 1.0
**Last Updated:** November 4, 2025
**Project:** COC-D Switcher

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Automated Testing Overview](#automated-testing-overview)
3. [Running Tests](#running-tests)
4. [Backend Testing](#backend-testing)
5. [Frontend Testing](#frontend-testing)
6. [Integration Testing](#integration-testing)
7. [Manual Testing Procedures](#manual-testing-procedures)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Coverage Requirements](#coverage-requirements)
10. [Troubleshooting](#troubleshooting)

---

## Executive Summary

### Current Test Status

✅ **Backend Core Tests:** 26/26 passing (100%)
✅ **Frontend Tests:** 3/3 passing (100%)
⚠️ **Integration/Template Tests:** Require additional implementation

### Test Automation Level

- **Unit Tests:** Fully automated
- **API Tests:** Fully automated
- **Performance Tests:** Fully automated
- **Integration Tests:** Partially automated
- **E2E Tests:** Manual (procedures provided below)

---

## Automated Testing Overview

### Test Infrastructure Components

```
coc-d-switcher/
├── backend/
│   ├── pytest.ini                 # Pytest configuration
│   ├── requirements-test.txt      # Test dependencies
│   ├── run_tests.sh              # Backend test runner
│   └── tests/                    # Test suites
│       ├── conftest.py           # Fixtures and setup
│       ├── test_basic.py         # Basic functionality tests
│       ├── test_unit/            # Unit tests
│       ├── test_api/             # API endpoint tests
│       ├── test_integration.py   # Integration tests
│       └── test_performance.py   # Performance benchmarks
├── frontend/
│   ├── vitest.config.ts          # Vitest configuration
│   ├── src/setupTests.ts         # Test setup
│   └── src/__tests__/            # Frontend tests
├── .github/workflows/ci.yml      # CI/CD pipeline
└── run_all_tests.sh             # Comprehensive test runner

```

### Test Categories

#### 1. Unit Tests (Backend)
- **Location:** `backend/tests/test_unit/`
- **Purpose:** Test individual functions in isolation
- **Tests:**
  - `test_extract.py`: PDF extraction logic
  - `test_validate.py`: Data validation rules

#### 2. API Tests (Backend)
- **Location:** `backend/tests/test_api/`
- **Purpose:** Test REST API endpoints
- **Coverage:**
  - Job creation and management
  - File upload
  - Parsing and validation
  - Rendering

#### 3. Integration Tests (Backend)
- **Location:** `backend/tests/test_integration.py`
- **Purpose:** Test complete workflows
- **Scenarios:**
  - Full job workflow (create → upload → parse → validate → render)
  - Error handling paths

#### 4. Performance Tests (Backend)
- **Location:** `backend/tests/test_performance.py`
- **Purpose:** Ensure API response times meet requirements
- **Benchmarks:**
  - API response < 1 second
  - Job creation < 0.5 seconds

#### 5. Component Tests (Frontend)
- **Location:** `frontend/src/__tests__/`
- **Purpose:** Test React components
- **Current Coverage:**
  - App rendering
  - UI element presence

---

## Running Tests

### Quick Start

#### Run ALL Tests (Backend + Frontend)
```bash
./run_all_tests.sh
```

### Backend Tests Only

#### Option 1: Run all backend tests
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

#### Option 2: Run specific test categories
```bash
# Unit tests only
pytest tests/test_unit/ -v

# API tests only
pytest tests/test_api/ -v

# Integration tests only
pytest tests/test_integration.py -v

# Performance tests only
pytest tests/test_performance.py -v
```

#### Option 3: Run with coverage report
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term
# View coverage: open backend/htmlcov/index.html
```

### Frontend Tests Only

```bash
cd frontend

# Run tests once
npm run test:run

# Run tests in watch mode (for development)
npm run test:watch

# Run with coverage
npm run test:coverage

# Run with UI
npm run test:ui
```

### Running Tests by Marker (Backend)

Tests are categorized with pytest markers:

```bash
# Run only unit tests
pytest -m unit

# Run only API tests
pytest -m api

# Run only performance tests
pytest -m performance

# Run only smoke tests
pytest -m smoke
```

---

## Backend Testing

### Test Environment Setup

1. **Create virtual environment:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

3. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

### Key Test Files

#### `tests/test_unit/test_validate.py`

Tests validation logic:
- ✅ Serial count matches quantity
- ✅ Serial count mismatch detection
- ✅ Missing contract number detection
- ✅ Empty data handling
- ✅ Missing serials detection
- ✅ Zero quantity with serials
- ✅ Multiple items validation
- ✅ Malformed data structure handling

#### `tests/test_unit/test_extract.py`

Tests PDF extraction:
- ✅ Extract returns required structure
- ✅ Date normalization
- ✅ Handling missing files
- ✅ Supplier serial number generation

#### `tests/test_api/test_endpoints.py`

Tests API endpoints:
- ✅ Root endpoint
- ✅ Create job
- ✅ Get nonexistent job (404)
- ✅ List jobs
- ✅ Upload files
- ✅ Parse job
- ✅ Validate job

#### `tests/test_performance.py`

Performance benchmarks:
- ✅ API response time < 1s
- ✅ Job creation performance < 0.5s average

### Adding New Tests

To add a new backend test:

1. Create test file in appropriate directory:
   ```python
   # tests/test_unit/test_mynewfeature.py
   import pytest

   def test_my_feature():
       # Arrange
       input_data = {...}

       # Act
       result = my_function(input_data)

       # Assert
       assert result == expected_value
   ```

2. Add markers if needed:
   ```python
   @pytest.mark.unit
   @pytest.mark.smoke
   def test_critical_feature():
       ...
   ```

3. Run your new test:
   ```bash
   pytest tests/test_unit/test_mynewfeature.py -v
   ```

---

## Frontend Testing

### Test Environment Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Run tests:**
   ```bash
   npm run test:run
   ```

### Current Frontend Tests

#### `src/__tests__/App.test.tsx`

- ✅ Renders main heading "COC-D Switcher"
- ✅ Renders dashboard heading
- ✅ Displays ready message

### Testing Stack

- **Test Runner:** Vitest
- **Testing Library:** @testing-library/react
- **Assertions:** @testing-library/jest-dom
- **Coverage:** v8

### Adding New Frontend Tests

```typescript
// src/__tests__/MyComponent.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import MyComponent from '../components/MyComponent';

describe('MyComponent', () => {
  test('renders correctly', () => {
    render(<MyComponent />);
    const element = screen.getByText(/expected text/i);
    expect(element).toBeInTheDocument();
  });

  test('handles click event', () => {
    render(<MyComponent />);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    // Assert expected behavior
  });
});
```

---

## Integration Testing

### End-to-End Workflow Test

The file `run_full_test.py` provides an automated E2E test that requires a running backend:

```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Run E2E test
python run_full_test.py
```

### What the E2E Test Covers

1. ✅ Job creation
2. ✅ PDF file upload
3. ✅ Document parsing
4. ✅ Data validation
5. ✅ Dutch COC rendering
6. ✅ Final job status retrieval

---

## Manual Testing Procedures

### Required Manual Tests

These functions require manual verification due to their visual, interactive, or external dependency nature:

---

### 1. PDF Upload and Parsing

**Purpose:** Verify PDF files are correctly uploaded and parsed

**Prerequisites:**
- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:5173`
- Sample PDF files:
  - `testing/input_samples/COC_6SH264587.pdf`
  - `testing/input_samples/Packing Slip_6SH264587.pdf`

**Procedure:**

1. **Navigate to application**
   - Open browser to `http://localhost:5173`
   - ✅ Verify: Application loads without errors

2. **Create new job**
   - Click "Create New Job" (or equivalent button)
   - Enter job name: "Manual Test Job 001"
   - Enter submitted by: "QA Tester"
   - Click "Create"
   - ✅ Verify: Job ID is generated
   - ✅ Verify: Job appears in jobs list

3. **Upload PDFs**
   - Select job from list
   - Click "Upload Files"
   - Upload Company COC PDF
   - Upload Packing Slip PDF
   - ✅ Verify: Both files show "Uploaded" status
   - ✅ Verify: File sizes are displayed correctly

4. **Parse documents**
   - Click "Parse Documents"
   - Wait for processing
   - ✅ Verify: Extracted data appears in preview
   - ✅ Verify: Contract number is extracted
   - ✅ Verify: Serial numbers are extracted
   - ✅ Verify: Item quantities are extracted

**Expected Results:**
- All fields are populated with extracted data
- No error messages
- Extracted data matches PDF contents

**Pass/Fail Criteria:**
- ✅ PASS: All verification steps complete successfully
- ❌ FAIL: Any verification step fails or errors occur

---

### 2. Data Validation

**Purpose:** Verify validation rules are correctly applied

**Procedure:**

1. **Test serial count validation**
   - After parsing, modify serial count in UI
   - Remove one serial number
   - Click "Validate"
   - ✅ Verify: Error appears: "Serial count (N) does not match quantity (M)"
   - ✅ Verify: Error highlights the serials field
   - ✅ Verify: Cannot proceed to render while error exists

2. **Test missing contract number**
   - Clear contract number field
   - Click "Validate"
   - ✅ Verify: Error appears: "Contract number is missing"
   - ✅ Verify: Field is highlighted in red

3. **Test valid data**
   - Restore all data to correct values
   - Click "Validate"
   - ✅ Verify: Green checkmark or "Validation Passed" message
   - ✅ Verify: No errors or warnings

**Expected Results:**
- Validation errors are clear and specific
- Errors prevent progression to next step
- Valid data passes without issues

---

### 3. Dutch COC Rendering

**Purpose:** Verify correct generation of Dutch MoD COC documents

**Procedure:**

1. **Render DOCX**
   - Complete job with valid data
   - Click "Render Dutch COC"
   - Wait for processing
   - ✅ Verify: "Rendering complete" message
   - ✅ Verify: Download button appears

2. **Download and inspect DOCX**
   - Click "Download DOCX"
   - Open file in Microsoft Word or LibreOffice
   - ✅ Verify: Document opens without errors
   - ✅ Verify: Contract number is present
   - ✅ Verify: Serial numbers are correctly formatted
   - ✅ Verify: Supplier serial number follows format: `COC_SV_Del###_DD.MM.YYYY.docx`
   - ✅ Verify: All tables are properly formatted
   - ✅ Verify: Date format is DD.MM.YYYY
   - ✅ Verify: No template placeholders remain (e.g., {{variable_name}})

3. **Render PDF**
   - Click "Render PDF"
   - Download PDF
   - Open in PDF viewer
   - ✅ Verify: PDF matches DOCX content
   - ✅ Verify: All formatting is preserved
   - ✅ Verify: Text is selectable (not images)

**Expected Results:**
- Documents match Dutch MoD COC format
- All data is correctly populated
- No formatting issues

---

### 4. Template Management

**Purpose:** Verify template upload, selection, and management

**Procedure:**

1. **List templates**
   - Navigate to Templates section
   - ✅ Verify: Existing templates are listed
   - ✅ Verify: Default template is marked

2. **Upload new template**
   - Click "Upload Template"
   - Select valid DOCX file with template variables
   - Enter template name: "Dutch COC v2"
   - Enter version: "2.0"
   - ✅ Verify: Upload progress shows
   - ✅ Verify: Template appears in list
   - ✅ Verify: Template metadata is correct

3. **Set as default**
   - Select newly uploaded template
   - Click "Set as Default"
   - ✅ Verify: Template is marked as default
   - ✅ Verify: Previous default is unmarked

4. **Download template**
   - Click download icon for template
   - ✅ Verify: File downloads
   - ✅ Verify: Filename matches template name
   - ✅ Verify: File opens correctly

5. **Delete template**
   - Upload a second template (to avoid deleting last one)
   - Select non-default template
   - Click "Delete"
   - Confirm deletion
   - ✅ Verify: Template is removed from list
   - ✅ Verify: Cannot delete last remaining template

**Expected Results:**
- Template management works smoothly
- Only DOCX files are accepted
- Cannot delete last template

---

### 5. Multi-Job Workflow

**Purpose:** Verify system handles multiple concurrent jobs

**Procedure:**

1. **Create multiple jobs**
   - Create Job A: "Shipment 001"
   - Create Job B: "Shipment 002"
   - Create Job C: "Shipment 003"
   - ✅ Verify: All jobs appear in list

2. **Work on jobs in parallel**
   - Upload files for Job A
   - Switch to Job B, upload files
   - Return to Job A, parse documents
   - Switch to Job C, upload files
   - ✅ Verify: Each job maintains its own state
   - ✅ Verify: No data mixing between jobs

3. **Complete jobs**
   - Complete Job A fully (parse, validate, render)
   - Complete Job B fully
   - Leave Job C incomplete
   - ✅ Verify: Job statuses are correct
   - ✅ Verify: Can access completed jobs
   - ✅ Verify: Can resume incomplete job

**Expected Results:**
- Jobs are independent
- No data corruption
- Clear job status indicators

---

### 6. Error Handling

**Purpose:** Verify graceful error handling

**Procedure:**

1. **Invalid file upload**
   - Try uploading non-PDF file (e.g., .txt, .jpg)
   - ✅ Verify: Error message: "Only PDF files are allowed"
   - ✅ Verify: File is not uploaded

2. **Network error simulation**
   - Stop backend server
   - Attempt to create job
   - ✅ Verify: User-friendly error message
   - ✅ Verify: No application crash
   - ✅ Verify: Can retry after backend restarts

3. **Corrupted PDF**
   - Upload corrupted or empty PDF file
   - Attempt to parse
   - ✅ Verify: Error message indicates parsing failure
   - ✅ Verify: Job can be deleted or retried

**Expected Results:**
- All errors have clear messages
- No system crashes
- User can recover from errors

---

### 7. Performance and Load Testing

**Purpose:** Verify system performance under load

**Procedure:**

1. **Response time**
   - Time job creation (should be < 1 second)
   - Time file upload (depends on file size, should show progress)
   - Time parsing (should complete within 10 seconds for typical PDFs)
   - ✅ Verify: All operations feel responsive

2. **Large file handling**
   - Upload PDFs > 10MB
   - ✅ Verify: Upload progress is shown
   - ✅ Verify: Parsing completes successfully
   - ✅ Verify: No timeout errors

3. **Concurrent users** (requires multiple browsers/devices)
   - Have 2-3 users work simultaneously
   - ✅ Verify: No slowdown
   - ✅ Verify: No data mixing

**Expected Results:**
- System remains responsive
- Large files are handled
- Multiple users supported

---

### 8. Browser Compatibility

**Purpose:** Verify application works across browsers

**Test Matrix:**

| Browser | Version | Status |
|---------|---------|--------|
| Chrome  | Latest  | ⬜ Test |
| Firefox | Latest  | ⬜ Test |
| Safari  | Latest  | ⬜ Test |
| Edge    | Latest  | ⬜ Test |

**Procedure for each browser:**
1. Open application
2. Create job
3. Upload files
4. Parse and validate
5. Render documents
6. Download files

**Expected Results:**
- Full functionality in all browsers
- Consistent UI/UX
- No JavaScript errors

---

### 9. Accessibility Testing

**Purpose:** Verify application is accessible

**Procedure:**

1. **Keyboard navigation**
   - Tab through all interactive elements
   - ✅ Verify: All buttons/inputs are reachable
   - ✅ Verify: Focus indicators are visible
   - ✅ Verify: Can complete full workflow without mouse

2. **Screen reader** (NVDA, JAWS, or VoiceOver)
   - Navigate application with screen reader
   - ✅ Verify: All text is read correctly
   - ✅ Verify: Form labels are announced
   - ✅ Verify: Error messages are announced

3. **Color contrast**
   - Check contrast ratios with browser tools
   - ✅ Verify: Text meets WCAG AA standards (4.5:1)

**Expected Results:**
- Fully keyboard accessible
- Screen reader compatible
- Sufficient color contrast

---

## CI/CD Pipeline

### GitHub Actions Workflow

The CI/CD pipeline is defined in `.github/workflows/ci.yml` and runs automatically on:
- Push to `main`, `develop`, or `claude/*` branches
- Pull requests to `main` or `develop`

### Pipeline Stages

1. **Backend Tests**
   - Python 3.11 setup
   - Dependencies installation
   - Unit tests
   - API tests
   - Integration tests
   - Performance tests
   - Coverage report generation

2. **Frontend Tests**
   - Node.js 18 setup
   - Dependencies installation
   - ESLint checks
   - Unit tests
   - Type checking (TypeScript)
   - Coverage report generation

3. **Docker Build Test**
   - Build Docker images
   - Start containers
   - Health check
   - Shutdown

4. **Security Scanning**
   - Trivy vulnerability scanner
   - SARIF report upload to GitHub Security

5. **Test Summary**
   - Aggregate all test results
   - Report pass/fail status

### Viewing CI Results

- Go to repository → Actions tab
- Click on latest workflow run
- View logs for each job
- Download coverage reports from artifacts

---

## Coverage Requirements

### Current Coverage

- **Backend:** 54% (Aiming for 70%)
- **Frontend:** Baseline established

### Coverage Goals

| Component | Current | Target |
|-----------|---------|--------|
| Unit Tests | 100% | 100% |
| API Tests | 57% | 80% |
| Integration | Partial | 70% |
| Frontend | Baseline | 70% |

### Improving Coverage

To improve test coverage:

1. **Identify uncovered code:**
   ```bash
   cd backend
   pytest --cov=app --cov-report=html
   open htmlcov/index.html
   ```

2. **Add tests for uncovered lines**

3. **Run coverage check:**
   ```bash
   pytest --cov=app --cov-report=term-missing --cov-fail-under=70
   ```

---

## Troubleshooting

### Backend Test Issues

#### Issue: Import errors
```bash
# Solution: Ensure you're in venv and dependencies are installed
cd backend
source venv/bin/activate
pip install -r requirements-test.txt
```

#### Issue: Tests fail with "fixture not found"
```bash
# Solution: Check conftest.py is present
ls tests/conftest.py
```

#### Issue: Coverage too low
```bash
# Solution: Review coverage report and add missing tests
pytest --cov=app --cov-report=html
```

### Frontend Test Issues

#### Issue: Module not found
```bash
# Solution: Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

#### Issue: Tests fail in CI but pass locally
```bash
# Solution: Ensure Node version matches CI (18.x)
node -v
nvm use 18
```

#### Issue: setupTests.ts not found
```bash
# Solution: Verify file exists
ls frontend/src/setupTests.ts
```

### General Issues

#### Issue: Port already in use
```bash
# Solution: Kill process on port
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:5173 | xargs kill -9  # Frontend
```

#### Issue: Docker tests fail
```bash
# Solution: Ensure Docker is running
docker ps
docker-compose up --build
```

---

## Quick Reference

### Run All Tests
```bash
./run_all_tests.sh
```

### Run Backend Tests Only
```bash
cd backend && source venv/bin/activate && pytest tests/ -v
```

### Run Frontend Tests Only
```bash
cd frontend && npm run test:run
```

### Generate Coverage Reports
```bash
# Backend
cd backend && pytest --cov=app --cov-report=html

# Frontend
cd frontend && npm run test:coverage
```

### Continuous Testing (Watch Mode)
```bash
# Frontend only
cd frontend && npm run test:watch
```

---

## Appendix: Test Naming Conventions

### Backend (Pytest)

- Test files: `test_*.py` or `*_test.py`
- Test functions: `test_*`
- Test classes: `Test*`

### Frontend (Vitest)

- Test files: `*.test.tsx` or `*.spec.tsx`
- Test suites: `describe('Component Name', () => {...})`
- Test cases: `test('should do something', () => {...})`

---

## Appendix: Useful Commands

```bash
# Install all dependencies
./setup_all.py

# Run backend in dev mode
cd backend && uvicorn app.main:app --reload

# Run frontend in dev mode
cd frontend && npm run dev

# Run full E2E test
python run_full_test.py

# Check backend code coverage
cd backend && pytest --cov-report term-missing --cov=app tests/

# Check frontend code coverage
cd frontend && npm run test:coverage

# Run only smoke tests
cd backend && pytest -m smoke

# Run tests with detailed output
pytest -vv --tb=long

# Run specific test file
pytest tests/test_unit/test_validate.py -v

# Run specific test function
pytest tests/test_unit/test_validate.py::TestValidation::test_serial_count_mismatch -v
```

---

## Support and Maintenance

### Updating Tests

When adding new features:
1. Write tests first (TDD approach)
2. Ensure tests pass locally
3. Update this documentation
4. Verify CI pipeline passes

### Reporting Issues

If tests fail unexpectedly:
1. Check recent code changes
2. Review test logs
3. Verify environment setup
4. Check dependencies versions

---

**Document Maintained By:** Development Team
**Next Review Date:** December 4, 2025
