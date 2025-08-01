#!/usr/bin/env python3
"""
Simple script to run all tests from the project root.
"""

import sys
import subprocess
from pathlib import Path

def run_test(test_file):
    """Run a specific test file."""
    print(f"🧪 Running {test_file}...")
    try:
        result = subprocess.run([sys.executable, test_file], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {test_file} passed")
            return True
        else:
            print(f"❌ {test_file} failed")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Running Valorant Skin Prices Tests")
    print("=" * 50)
    
    tests = [
        "tests/test_conversion.py",
        "tests/test_skin_verification.py"
    ]
    
    passed = 0
    total = len(tests)
    
    for test_file in tests:
        if Path(test_file).exists():
            if run_test(test_file):
                passed += 1
        else:
            print(f"⚠️  {test_file} not found")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 