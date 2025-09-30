#!/usr/bin/env python3
"""
Complete COC-D Switcher Project Setup Script
Creates all necessary files and folders for the application
"""

import os
import json

def create_file(path, content):
    """Create a file with the given content"""
    # Create directory if it doesn't exist
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    
    # Write content to file
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created {path}")

def setup_project():
    """Set up the complete project structure and files"""
    
    print("🚀 Setting up COC-D Switcher project...")
    print("=" * 50)
    
    # Create all project files
    files = {
        # Root files
        ".gitignore": """# Python
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/

# Node
node_modules/
dist/
.npm
*.log

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Project
/tmp/
*.pdf
*.docx
!templates/*.docx

# Environment
.env
""",

        "docker-compose.yml": """version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/app:/app/app
      - ./backend/templates:/app/templates
    environment:
      - PYTHONUNBUFFERED=1
      - CORS_ORIGINS=http://localhost:5173
      - TEMPLATE_PATH=/app/templates/COC_SV_Del165_20.03.2025.docx

  frontend:
    build: ./frontend
    ports:
      - "5173:80"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://localhost:8000
""",

        "README.md": """# COC-D Switcher

Convert Elbit/Company COCs and Packing Slips into Dutch MoD Certificate of Conformity format.

## Architecture

- **Frontend**: React + TypeScript + Vite + Redux Toolkit + Tailwind CSS
- **Backend**: Python FastAPI + pdfplumber + python-docx
- **Deployment**: Docker + docker-compose

## Quick Start

### Using Docker (Recommended)
```bash