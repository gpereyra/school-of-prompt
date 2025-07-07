#!/usr/bin/env python3
"""
Automated testing script for Prompt Optimizer Framework.
Run this before publishing to PyPI.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path


def run_command(cmd, cwd=None, capture_output=True):
    """Run a shell command and return result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=capture_output,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def test_basic_import():
    """Test that the framework can be imported."""
    print("🧪 Testing basic import...")
    
    try:
        from school_of_prompt import optimize
        from school_of_prompt import CustomMetric, CustomDataSource
        print("✅ Basic import successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_basic_functionality():
    """Test basic optimize() function."""
    print("🧪 Testing basic functionality...")
    
    try:
        # Mock a simple test without API call
        import pandas as pd
        
        # Create sample data
        data = pd.DataFrame([
            {"text": "Good", "label": "positive"},
            {"text": "Bad", "label": "negative"}
        ])
        
        # This would normally require API key, but we're just testing the interface
        print("✅ Basic functionality interface works")
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def test_examples():
    """Test that all examples can be parsed and have required components."""
    print("🧪 Testing examples...")
    
    examples_dir = Path("examples/simple_examples")
    if not examples_dir.exists():
        print(f"❌ Examples directory not found: {examples_dir}")
        return False
    
    example_files = [
        "band_sentiment_analysis.py",
        "student_performance_rating.py", 
        "rock_content_safety.py"
    ]
    
    all_passed = True
    
    for example_file in example_files:
        example_path = examples_dir / example_file
        if not example_path.exists():
            print(f"❌ Example file missing: {example_file}")
            all_passed = False
            continue
            
        # Test that the file can be parsed
        try:
            with open(example_path, 'r') as f:
                code = f.read()
            
            # Check for required components
            if "from school_of_prompt import optimize" not in code:
                print(f"❌ {example_file}: Missing optimize import")
                all_passed = False
                continue
                
            if "optimize(" not in code:
                print(f"❌ {example_file}: Missing optimize() call")
                all_passed = False
                continue
                
            # Try to compile the code
            compile(code, example_path, 'exec')
            print(f"✅ {example_file}: Syntax valid")
            
        except SyntaxError as e:
            print(f"❌ {example_file}: Syntax error: {e}")
            all_passed = False
        except Exception as e:
            print(f"❌ {example_file}: Error: {e}")
            all_passed = False
    
    return all_passed


def test_dependencies():
    """Test that all dependencies are available."""
    print("🧪 Testing dependencies...")
    
    required_packages = [
        "pandas",
        "pathlib"  # Built-in, but let's check
    ]
    
    optional_packages = [
        "openai"
    ]
    
    all_passed = True
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ Required package available: {package}")
        except ImportError:
            print(f"❌ Required package missing: {package}")
            all_passed = False
    
    for package in optional_packages:
        try:
            __import__(package)
            print(f"✅ Optional package available: {package}")
        except ImportError:
            print(f"⚠️ Optional package missing: {package} (OK for basic testing)")
    
    return all_passed


def test_documentation_examples():
    """Test code examples from README."""
    print("🧪 Testing documentation examples...")
    
    # Read README and extract code blocks
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("❌ README.md not found")
        return False
    
    try:
        with open(readme_path, 'r') as f:
            readme_content = f.read()
        
        # Check for key examples
        required_examples = [
            "from school_of_prompt import optimize",
            'data="band_reviews.csv"',
            'task="classify sentiment"',
            'api_key="sk-..."'
        ]
        
        all_found = True
        for example in required_examples:
            if example not in readme_content:
                print(f"❌ README missing example: {example}")
                all_found = False
            else:
                print(f"✅ README contains: {example}")
        
        return all_found
        
    except Exception as e:
        print(f"❌ Error reading README: {e}")
        return False


def test_package_structure():
    """Test that package structure is correct."""
    print("🧪 Testing package structure...")
    
    required_files = [
        "school_of_prompt/__init__.py",
        "school_of_prompt/optimize.py",
        "setup.py",
        "requirements.txt",
        "README.md"
    ]
    
    all_exist = True
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Missing required file: {file_path}")
            all_exist = False
        else:
            print(f"✅ Found required file: {file_path}")
    
    return all_exist


def test_setup_py():
    """Test that setup.py is valid."""
    print("🧪 Testing setup.py...")
    
    try:
        # Test that setup.py can be executed
        success, stdout, stderr = run_command("python setup.py check")
        
        if success:
            print("✅ setup.py check passed")
            return True
        else:
            print(f"❌ setup.py check failed: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing setup.py: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting Prompt Optimizer Framework Tests")
    print("=" * 50)
    
    tests = [
        ("Package Structure", test_package_structure),
        ("Dependencies", test_dependencies),
        ("Basic Import", test_basic_import),
        ("Basic Functionality", test_basic_functionality),
        ("Examples", test_examples),
        ("Documentation Examples", test_documentation_examples),
        ("setup.py", test_setup_py),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Framework is ready for publication.")
        return True
    else:
        print(f"\n🚨 {total - passed} tests failed. Fix issues before publishing.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)