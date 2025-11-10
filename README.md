# COC-D Switcher

A web application for converting Elbit/Company Certificates of Conformity (COC) into Dutch Ministry of Defence (MoD) Certificate of Conformity format.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

COC-D Switcher automates the process of converting company certificates of conformity to Dutch MoD format by:
1. Extracting data from source PDF documents (COC and Packing Slip)
2. Allowing manual data entry for missing or additional fields
3. Validating all data against requirements
4. Generating formatted DOCX documents using customizable templates
5. Providing downloadable output documents

## ✨ Features

### Core Functionality
- **PDF Upload & Parsing**: Upload Company COC and Packing Slip PDFs
- **Data Extraction**: Automatic extraction of contract number, product details, quantities, etc.
- **Manual Data Entry**: Fill in missing data or override extracted values
- **Data Validation**: Comprehensive validation with error and warning reporting
- **Template-Based Rendering**: Generate documents using DOCX templates with Jinja2 variables
- **Template Management**: Upload, manage, and version control templates

### User Experience
- **6-Step Workflow**: Clear progression from upload to download
- **Real-time Validation**: Immediate feedback on data completeness
- **Flexible Data Entry**: Optional fields with confirmation dialogs
- **Edit Capability**: Modify data at any step before finalizing
- **Progress Tracking**: Visual workflow with step completion indicators

### Technical Features
- **REST API**: FastAPI-based backend with OpenAPI documentation
- **Type Safety**: Pydantic models for request/response validation
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **File Management**: Automatic cleanup and organization of uploads/outputs
- **Logging**: Comprehensive logging for debugging and auditing

## 🏗️ Architecture

### System Components

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  Frontend (UI)  │────────▶│  Backend API    │────────▶│  File System    │
│  React + Vite   │  HTTP   │  FastAPI        │         │  Templates      │
│                 │◀────────│                 │         │  Uploads        │
└─────────────────┘         └─────────────────┘         │  Rendered       │
                                    │                    └─────────────────┘
                                    │
                                    ▼
                            ┌─────────────────┐
                            │                 │
                            │  Processing     │
                            │  - PDF Extract  │
                            │  - Validation   │
                            │  - Rendering    │
                            └─────────────────┘
```

### Data Flow

```
1. Upload PDFs → 2. Parse/Extract → 3. Manual Input → 4. Validate → 5. Render → 6. Download
                                           ↓
                                    Merge Data
                                           ↓
                              Template + Context = DOCX
```

## 🔧 Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Runtime**: Python 3.12+
- **Server**: Uvicorn 0.24.0
- **Validation**: Pydantic 2.5.0
- **PDF Processing**: pdfplumber 0.10.3
- **Document Generation**: python-docx 0.8.11, docxtpl 0.16.7
- **File Upload**: python-multipart 0.0.6
- **Testing**: pytest 7.4.3

### Frontend
- **Framework**: React 18.3.1
- **Build Tool**: Vite 5.4.2
- **Language**: TypeScript 5.5.3
- **Styling**: Tailwind CSS 3.4.10
- **HTTP Client**: Native Fetch API

### Development Tools
- **Package Management**: npm (frontend), pip (backend)
- **Version Control**: Git
- **Code Quality**: TypeScript strict mode, Python type hints

## 📦 Prerequisites

### Required Software
- **Node.js**: v18 or higher
- **npm**: v9 or higher
- **Python**: 3.12 or higher
- **pip**: Latest version

### Operating System
- Windows 10/11
- Linux (Ubuntu 20.04+, RHEL 8+)
- macOS 11+

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yuters777/coc-d-switcher.git
cd coc-d-switcher
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\Activate.ps1
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create templates directory (if not exists)
mkdir -p templates
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

### 4. Template Setup

Place your Dutch MoD COC template (DOCX format with Jinja2 variables) in `backend/templates/`.

**Template Variable Format:**
```
{{ variable_name }}
```

**Supported Variables:**
- `{{ supplier_serial_no }}`
- `{{ contract_number }}`
- `{{ acquirer }}`
- `{{ delivery_address }}`
- `{{ partial_delivery_number }}`
- `{{ final_delivery_number }}`
- `{{ contract_item }}`
- `{{ product_description }}`
- `{{ quantity }}`
- `{{ shipment_no }}`
- `{{ undelivered_quantity }}`
- `{{ remarks }}`
- `{{ date }}`
- `{{ job_id }}`
- `{{ job_name }}`
- `{{ submitted_by }}`

## 🎮 Usage

### Starting the Application

**Terminal 1 - Backend:**
```bash
cd backend
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/Mac
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access the Application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Workflow Steps

#### Step 1: Upload Files
1. Enter Job Name (e.g., "Shipment 12345")
2. Enter Your Name
3. Upload Company COC PDF (optional)
4. Upload Packing Slip PDF (required)

#### Step 2: Parse Documents
- Click "Parse Documents"
- System extracts data from PDFs automatically

#### Step 3: Manual Data Entry
**Required Fields:**
- Partial Delivery Number
- Undelivered Quantity
- Software Version

**Optional Fields (Fill if missing from extraction):**
- Contract Number
- Shipment Number
- Product Description
- Quantity

#### Step 4: Validate Data
- Click "Validate Data"
- Review any errors or warnings
- Fix issues by going back to Step 3, or skip validation (not recommended)

#### Step 5: Render Document
- Click "Generate Document"
- System creates DOCX using template and your data

#### Step 6: Download Result
- Click "Download COC-D Document"
- Open in Microsoft Word or compatible application
- Click "Start New Job" to begin another conversion

### Template Management

**Access Settings:**
Click the ⚙️ Settings button in the top navigation.

**Upload New Template:**
1. Select DOCX file with Jinja2 variables
2. Enter Template Name
3. Enter Version
4. Optionally set as default
5. Click Upload

**Manage Templates:**
- Download: Get a copy of the template
- Set as Default: Use this template for rendering
- Delete: Remove template (cannot delete if only one remains)

## 📚 API Documentation

### Job Management

#### Create Job
```http
POST /api/jobs
Content-Type: application/json

{
  "name": "Shipment 12345",
  "submitted_by": "John Doe"
}

Response: {
  "job_id": "uuid",
  "name": "Shipment 12345",
  "submitted_by": "John Doe",
  "status": "draft"
}
```

#### Upload Files
```http
POST /api/jobs/{job_id}/files
Content-Type: multipart/form-data

company_coc: file.pdf (optional)
packing_slip: file.pdf (required)

Response: {
  "message": "Files uploaded successfully",
  "files": {...}
}
```

#### Parse Documents
```http
POST /api/jobs/{job_id}/parse

Response: {
  "message": "Parsing complete",
  "extracted_data": {...}
}
```

#### Submit Manual Data
```http
POST /api/jobs/{job_id}/manual
Content-Type: application/json

{
  "partial_delivery_number": "165",
  "undelivered_quantity": "1000(5000)",
  "sw_version": "2.2.15.45",
  "contract_number": "454545",  // optional
  "product_description": "Radio System"  // optional
}

Response: {
  "message": "Manual data saved successfully",
  "manual_data": {...}
}
```

#### Validate Data
```http
POST /api/jobs/{job_id}/validate

Response: {
  "validation": {
    "errors": [],
    "warnings": []
  },
  "has_errors": false,
  "has_warnings": false
}
```

#### Render Document
```http
POST /api/jobs/{job_id}/render

Response: {
  "message": "Document rendered successfully",
  "rendered_file": "COC-D_uuid.docx",
  "template_used": {...}
}
```

#### Download Document
```http
GET /api/jobs/{job_id}/download

Response: DOCX file download
```

### Template Management

#### List Templates
```http
GET /api/templates

Response: {
  "templates": [...]
}
```

#### Upload Template
```http
POST /api/templates/upload
Content-Type: multipart/form-data

file: template.docx
name: "Dutch COC Template"
version: "1.0"
set_as_default: "true"

Response: {
  "message": "Template uploaded successfully",
  "template": {...}
}
```

#### Download Template
```http
GET /api/templates/{template_id}/download

Response: DOCX file download
```

#### Set Default Template
```http
PUT /api/templates/{template_id}/set-default

Response: {
  "message": "Template set as default"
}
```

#### Delete Template
```http
DELETE /api/templates/{template_id}

Response: {
  "message": "Template deleted successfully"
}
```

## 📁 Project Structure

```
coc-d-switcher/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application & all endpoints
│   │   ├── config.py            # Configuration management
│   │   ├── schemas.py           # Pydantic models
│   │   ├── extract.py           # PDF extraction logic
│   │   ├── validate.py          # Data validation
│   │   ├── render.py            # DOCX rendering with docxtpl
│   │   └── templates.py         # Template management
│   ├── templates/
│   │   ├── metadata.json        # Template registry
│   │   └── *.docx              # Template files
│   ├── requirements.txt         # Python dependencies
│   ├── diagnose_template.py    # Template diagnostic tool
│   ├── test_template.py        # Template testing tool
│   └── fix_template.py         # Template repair tool
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AppNav.tsx      # Navigation bar
│   │   │   ├── ConfirmationModal.tsx  # Reusable modal
│   │   │   └── TemplateManager.tsx    # Template upload/management
│   │   ├── pages/
│   │   │   ├── ConversionPage.tsx     # Main workflow (6 steps)
│   │   │   └── SettingsPage.tsx       # Template management page
│   │   ├── App.tsx             # Root component & routing
│   │   ├── main.tsx            # Entry point
│   │   └── index.css           # Tailwind imports
│   ├── package.json            # Frontend dependencies
│   ├── tsconfig.json           # TypeScript configuration
│   ├── vite.config.ts          # Vite build configuration
│   └── tailwind.config.js      # Tailwind CSS configuration
└── README.md                   # This file
```

## 🛠️ Development

### Backend Development

**Running in Development Mode:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Testing:**
```bash
pytest
```

**Template Diagnostics:**
```bash
# Analyze template for issues
python diagnose_template.py path/to/template.docx

# Test template rendering
python test_template.py path/to/template.docx
```

### Frontend Development

**Running Development Server:**
```bash
cd frontend
npm run dev
```

**Building for Production:**
```bash
npm run build
npm run preview  # Preview production build
```

**Type Checking:**
```bash
npm run build  # Includes TypeScript checking
```

### Code Quality

**Python:**
- Use type hints for all functions
- Follow PEP 8 style guide
- Add docstrings to public functions
- Use Pydantic models for validation

**TypeScript:**
- Enable strict mode
- Use explicit types
- Avoid `any` type
- Use functional components with hooks

## 🐛 Troubleshooting

### Template Variables Not Rendering

**Issue:** Variables remain as `{{ variable }}` in output

**Solution:**
1. Run diagnostic tool:
   ```bash
   python backend/diagnose_template.py backend/templates/your_template.docx
   ```
2. Check for text boxes (docxtpl can't process these)
3. Verify variable names match exactly (case-sensitive)
4. Ensure no extra spaces: `{{variable}}` not `{{ variable }}`

### CORS Errors

**Issue:** Frontend can't connect to backend

**Solution:**
Update `backend/app/main.py` CORS origins:
```python
cors_origins = os.getenv("CORS_ORIGINS",
    "http://localhost:5173,http://10.2.11.7:5173,http://127.0.0.1:5173"
).split(",")
```

### File Upload Fails

**Issue:** Upload returns 404 or 400

**Solution:**
1. Check file is PDF format
2. Verify job was created first (Step 1)
3. Check backend logs for details
4. Ensure temp directory is writable

### Template Not Found

**Issue:** "Template file not found on disk"

**Solution:**
1. Check `backend/templates/metadata.json` path is correct
2. Verify template file exists at specified path
3. Use relative path from backend directory
4. Restart backend after fixing metadata

### PDF Extraction Returns Empty

**Issue:** No data extracted from PDFs

**Solution:**
1. Verify PDFs contain actual text (not scanned images)
2. Check PDF isn't password protected
3. Review extraction logic in `backend/app/extract.py`
4. Consider implementing OCR for scanned PDFs

## 🎯 Implementation Status

### ✅ Fully Implemented
- All 12 REST API endpoints (jobs, templates, rendering)
- 6-step workflow UI with React + TypeScript
- PDF extraction with pdfplumber
- DOCX rendering with docxtpl
- Template management system
- Data validation with errors/warnings
- Manual data entry with optional fields
- Confirmation modals for user decisions
- Progress tracking and step navigation
- File upload/download functionality

### 📋 Features
- Cross-platform support (Windows, Linux, macOS)
- Hot reload for development
- Comprehensive error handling
- Logging and debugging tools
- Template diagnostic utilities

## 📝 License

[Add your license information here]

## 👥 Contributors

[Add contributor information here]

## 🔗 Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [docxtpl Documentation](https://docxtpl.readthedocs.io/)
- [pdfplumber Documentation](https://github.com/jsvine/pdfplumber)

## 📞 Support

For issues, questions, or contributions, please [open an issue](https://github.com/yuters777/coc-d-switcher/issues) on GitHub.

---

**Last Updated:** November 2025
**Version:** 1.0.0
**Status:** Production Ready ✅
**End-to-End Tested:** ✅
