import subprocess
import sys
import time
from pathlib import Path

def run_command(cmd, description):
    """Execute a command and display the result"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes max
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Duration: {duration:.2f}s")
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout:
                print("\n📋 Results:")
                print(result.stdout)
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr:
                print("\n🚨 Errors:")
                print(result.stderr)
            if result.stdout:
                print("\n📋 Output:")
                print(result.stdout)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT (>5min)")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False

def check_dependencies():
    """Check that pytest is installed"""
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ pytest installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ pytest not found")
            return False
    except Exception:
        print("❌ Error checking pytest")
        return False

def install_dependencies():
    """Install test dependencies"""
    print("📦 Installing test dependencies...")
    
    packages = [
        "pytest",
        "pytest-asyncio", 
        "pytest-mock",
        "httpx",
        "pytest-cov"
    ]
    
    cmd = [sys.executable, "-m", "pip", "install"] + packages
    
    return run_command(cmd, "Installing dependencies")

def main():
    """Main function"""
    print("🌟 LAUNCHING FINBOT TESTS")
    print("=" * 60)
    
    # Check that we are in the correct directory
    if not Path("test_Agent01.py").exists() or not Path("config_test.py").exists():
        print("❌ Test files not found. Make sure you are in the abacus_testing folder.")
        print("💡 Expected structure in abacus_testing/:")
        print("   abacus_testing/")
        print("   ├── config_test.py")
        print("   ├── test_Agent01.py")
        print("   ├── test_Agent02.py")
        print("   ├── test_Agent03.py")
        print("   ├── test_routes.py")
        print("   └── run_tests.py")
        print("\n🔧 You must be INSIDE the abacus_testing folder to run this script")
        return False
    
    # Check pytest
    if not check_dependencies():
        print("\n💡 Installing required dependencies...")
        if not install_dependencies():
            print("❌ Unable to install dependencies")
            return False
    
    # Tests to execute
    test_suites = [
        {
            "name": "Agent01 Tests (Functions + Routes)",
            "cmd": [sys.executable, "-m", "pytest", "test_Agent01.py", "-v"],
            "critical": True
        },
        {
            "name": "Routes Tests",
            "cmd": [sys.executable, "-m", "pytest", "test_routes.py", "-v"],
            "critical": True
        },
        {
            "name": "Complete Agent02 Tests",
            "cmd": [sys.executable, "-m", "pytest", "test_Agent02.py", "-v"],
            "critical": False
        },
        {
            "name": "Complete Agent03 Tests",
            "cmd": [sys.executable, "-m", "pytest", "test_Agent03.py", "-v"],
            "critical": False
        }
    ]
    
    # Execute the tests
    results = []
    critical_failures = 0
    
    for suite in test_suites:
        success = run_command(suite["cmd"], suite["name"])
        results.append({
            "name": suite["name"],
            "success": success,
            "critical": suite["critical"]
        })
        
        if not success and suite["critical"]:
            critical_failures += 1
    
    # Coverage tests (if all critical tests pass)
    if critical_failures == 0:
        coverage_cmd = [
            sys.executable, "-m", "pytest", 
            ".",
            "--cov=../Agent01", 
            "--cov=../Agent02", 
            "--cov=../Agent03",
            "--cov=../config",
            "--cov-report=term",
            "--cov-report=html",
            "-v"
        ]
        
        coverage_success = run_command(coverage_cmd, "Tests with Code Coverage")
        
        if coverage_success:
            print("\n📊 HTML coverage report generated in: htmlcov/index.html")
    
    # Final summary
    print(f"\n{'='*60}")
    print("📋 FINAL SUMMARY")
    print(f"{'='*60}")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    critical_passed = sum(1 for r in results if r["success"] and r["critical"])
    total_critical = sum(1 for r in results if r["critical"])
    
    print(f"📊 Tests passed: {passed_tests}/{total_tests}")
    print(f"🎯 Critical tests: {critical_passed}/{total_critical}")
    
    print(f"\n📋 Details by suite:")
    for result in results:
        status = "✅" if result["success"] else "❌"
        critical_mark = " (CRITICAL)" if result["critical"] else ""
        print(f"  {status} {result['name']}{critical_mark}")
    
    # Recommendations
    if critical_failures > 0:
        print(f"\n🚨 {critical_failures} critical test(s) failed")
        print("💡 Check your imports and basic configuration")
        print("🔧 Useful commands for debugging:")
        print("   python -c \"import sys; sys.path.append('..'); from main import app; print('✅ Import main OK')\"")
        print("   python -c \"import sys; sys.path.append('..'); from config import settings; print('✅ Import config OK')\"")
        print("   pytest test_Agent01.py -v --tb=long")
        return False
    elif passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✨ Your code is ready for production")
        print("📊 Check the coverage report: htmlcov/index.html")
        return True
    else:
        print(f"\n⚠️  Main tests OK, but {total_tests - passed_tests} optional test(s) failed")
        print("💡 The code works but some features may be unavailable")
        print("🔍 Failed tests (non-critical):")
        for result in results:
            if not result["success"] and not result["critical"]:
                print(f"   - {result['name']}")
        return True

if __name__ == "__main__":
    success = main()
    
    print(f"\n{'='*60}")
    if success:
        print("🏆 TESTS COMPLETED SUCCESSFULLY")
        print("\n🚀 Next steps:")
        print("   1. Check htmlcov/index.html for coverage")
        print("   2. Your application is ready!")
    else:
        print("💥 TESTS FAILED - CHECK THE ERRORS ABOVE")
        print("\n🔧 Recommended actions:")
        print("   1. Check your imports (main.py, config.py)")
        print("   2. Make sure you are at the project root")
        print("   3. Run: pytest abacus_testing/ -v --tb=short")
    print(f"{'='*60}")
    
    sys.exit(0 if success else 1)