#!/usr/bin/env python3
"""Run all tests and generate summary report"""

import subprocess
import sys

def run_tests():
    print("=" * 60)
    print("COC-D SWITCHER TEST SUITE")
    print("=" * 60)
    
    test_suites = [
        ("Unit Tests", "tests/test_basic.py"),
        ("API Tests", "tests/test_api_simple.py"),
    ]
    
    results = []
    
    for name, test_file in test_suites:
        print(f"\n📋 Running {name}...")
        print("-" * 40)
        
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {name} PASSED")
            results.append((name, "PASSED"))
        else:
            print(f"❌ {name} FAILED")
            results.append((name, "FAILED"))
            print(result.stdout)
    
    # Generate coverage report
    print("\n📊 Coverage Report")
    print("-" * 40)
    subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", "--cov=app", 
        "--cov-report=term-missing",
        "--cov-report=html"
    ])
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, status in results:
        emoji = "✅" if status == "PASSED" else "❌"
        print(f"{emoji} {name}: {status}")
    
    print("\n📁 HTML Coverage Report: htmlcov/index.html")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()