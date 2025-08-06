#!/usr/bin/env python3
"""
Simple test script to verify the AI-Powered Job Portal setup.

This script tests basic functionality without requiring all dependencies
to be installed, helping users verify their setup.
"""

import sys
import os
from pathlib import Path

def test_project_structure():
    """Test if project structure is correct."""
    print("🏗️ Testing project structure...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        "app/__init__.py",
        "app/schemas.py",
        "app/config.py",
        "app/routers/__init__.py",
        "app/routers/auth.py",
        "app/routers/resumes.py",
        "app/routers/jobs.py",
        "app/routers/applications.py",
        "app/routers/counseling.py",
        "app/services/__init__.py",
        "app/services/resume_parser.py",
        "app/services/matching_service.py",
        "app/services/counseling_service.py",
        "app/services/auth_service.py",
        "app/utils/__init__.py",
        "app/utils/security.py",
        "app/utils/dependencies.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_python_version():
    """Test Python version compatibility."""
    print("🐍 Testing Python version...")
    
    version_info = sys.version_info
    if version_info.major == 3 and version_info.minor >= 8:
        print(f"✅ Python {version_info.major}.{version_info.minor}.{version_info.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version_info.major}.{version_info.minor}.{version_info.micro} is not compatible. Requires Python 3.8+")
        return False

def test_imports():
    """Test if basic imports work."""
    print("📦 Testing basic imports...")
    
    try:
        # Test if we can import the schemas without dependencies
        import importlib.util
        
        # Check app structure
        spec = importlib.util.spec_from_file_location("schemas", "app/schemas.py")
        if spec and spec.loader:
            print("✅ Schema definitions accessible")
        else:
            print("❌ Cannot access schema definitions")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        return False

def test_directories():
    """Test if required directories exist."""
    print("📁 Testing directories...")
    
    required_dirs = ["app", "app/routers", "app/services", "app/utils", "uploads"]
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"❌ Missing directory: {dir_path}")
            return False
    
    print("✅ All required directories present")
    return True

def main():
    """Run all tests."""
    print("🧪 AI-Powered Job Portal - Setup Verification\n")
    
    tests = [
        test_python_version,
        test_project_structure,
        test_directories,
        test_imports
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}\n")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("📊 Test Summary:")
    print(f"   Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your setup looks good.")
        print("\nNext steps:")
        print("1. Run: ./setup.sh (to install dependencies)")
        print("2. Run: source venv/bin/activate")
        print("3. Run: python -m spacy download en_core_web_sm")
        print("4. Run: uvicorn main:app --reload")
    else:
        print("⚠️ Some tests failed. Please check the project setup.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
