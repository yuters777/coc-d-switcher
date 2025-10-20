#!/bin/bash
echo "Running COC-D Switcher Test Suite"
echo "=================================="

# Unit tests
echo "Running unit tests..."
pytest tests/test_unit/ -v --tb=short

# API tests
echo "Running API tests..."
pytest tests/test_api/ -v --tb=short

# Integration tests
echo "Running integration tests..."
pytest tests/test_integration.py -v --tb=short

# Coverage report
echo "Generating coverage report..."
pytest tests/ --cov=app --cov-report=html --cov-report=term

echo "Test suite complete!"