#!/bin/bash

# Comprehensive Test Runner for COC-D Switcher
# This script runs all automated tests for the project

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
BACKEND_TESTS_PASSED=0
FRONTEND_TESTS_PASSED=0
LINT_PASSED=0

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  COC-D Switcher - Comprehensive Test Suite"
echo "═══════════════════════════════════════════════════════"
echo ""

# Function to print section headers
print_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Function to print results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2 PASSED${NC}"
    else
        echo -e "${RED}✗ $2 FAILED${NC}"
    fi
}

# ========================================
# Backend Tests
# ========================================
print_section "1. Backend Tests"

cd backend

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing/updating dependencies..."
pip install -q -r requirements.txt
pip install -q -r requirements-test.txt

echo ""
echo "Running backend test suite..."
echo ""

# Run unit tests
echo -e "${YELLOW}→ Running unit tests...${NC}"
if pytest tests/test_unit/ -v --tb=short; then
    echo -e "${GREEN}✓ Unit tests passed${NC}"
else
    echo -e "${RED}✗ Unit tests failed${NC}"
    BACKEND_TESTS_PASSED=1
fi

echo ""
echo -e "${YELLOW}→ Running API tests...${NC}"
if pytest tests/test_api/ -v --tb=short; then
    echo -e "${GREEN}✓ API tests passed${NC}"
else
    echo -e "${RED}✗ API tests failed${NC}"
    BACKEND_TESTS_PASSED=1
fi

echo ""
echo -e "${YELLOW}→ Running integration tests...${NC}"
if pytest tests/test_integration.py -v --tb=short; then
    echo -e "${GREEN}✓ Integration tests passed${NC}"
else
    echo -e "${RED}✗ Integration tests failed${NC}"
    BACKEND_TESTS_PASSED=1
fi

echo ""
echo -e "${YELLOW}→ Running performance tests...${NC}"
if pytest tests/test_performance.py -v --tb=short; then
    echo -e "${GREEN}✓ Performance tests passed${NC}"
else
    echo -e "${RED}✗ Performance tests failed${NC}"
    BACKEND_TESTS_PASSED=1
fi

echo ""
echo -e "${YELLOW}→ Generating coverage report...${NC}"
pytest tests/ --cov=app --cov-report=html --cov-report=term --cov-report=xml -v

deactivate
cd ..

# ========================================
# Frontend Tests
# ========================================
print_section "2. Frontend Tests"

cd frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing npm dependencies...${NC}"
    npm install
fi

echo ""
echo -e "${YELLOW}→ Running frontend tests...${NC}"
if npm run test:run 2>/dev/null || [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend tests passed${NC}"
else
    echo -e "${RED}✗ Frontend tests failed or not configured${NC}"
    FRONTEND_TESTS_PASSED=1
fi

echo ""
echo -e "${YELLOW}→ Running linter...${NC}"
if npm run lint 2>/dev/null || [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Linting passed${NC}"
else
    echo -e "${RED}✗ Linting failed or not configured${NC}"
    LINT_PASSED=1
fi

echo ""
echo -e "${YELLOW}→ Type checking...${NC}"
if npm run build 2>&1 | grep -q "error"; then
    echo -e "${RED}✗ Type checking failed${NC}"
    FRONTEND_TESTS_PASSED=1
else
    echo -e "${GREEN}✓ Type checking passed${NC}"
fi

cd ..

# ========================================
# Test Summary
# ========================================
print_section "Test Summary"

echo ""
print_result $BACKEND_TESTS_PASSED "Backend Tests"
print_result $FRONTEND_TESTS_PASSED "Frontend Tests"
print_result $LINT_PASSED "Code Quality (Linting)"

echo ""
echo "Coverage Reports:"
echo "  • Backend: backend/htmlcov/index.html"
echo "  • Frontend: frontend/coverage/index.html"

echo ""
TOTAL_FAILURES=$((BACKEND_TESTS_PASSED + FRONTEND_TESTS_PASSED + LINT_PASSED))

if [ $TOTAL_FAILURES -eq 0 ]; then
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✓ ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}═══════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  ✗ SOME TESTS FAILED${NC}"
    echo -e "${RED}  Total failures: $TOTAL_FAILURES${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════${NC}"
    echo ""
    exit 1
fi
