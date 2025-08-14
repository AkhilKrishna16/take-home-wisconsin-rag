#!/usr/bin/env python3
"""
Comprehensive Test Runner for Legal RAG System

Runs all tests in organized categories with proper reporting.
"""

import subprocess
import sys
import os
import time
from pathlib import Path
from datetime import datetime

class TestRunner:
    """Orchestrates running all tests with proper organization and reporting."""
    
    def __init__(self):
        self.backend_dir = Path(__file__).parent
        self.frontend_dir = self.backend_dir.parent / "frontend"
        self.results = {
            'unit': {},
            'integration': {},
            'performance': {},
            'frontend': {}
        }
        
    def run_backend_unit_tests(self):
        """Run all backend unit tests."""
        print("🧪 Running Backend Unit Tests")
        print("=" * 50)
        
        unit_tests = [
            "tests/unit/document_unit_test.py",
            "tests/unit/test_langchain_safety_features.py"
        ]
        
        for test_file in unit_tests:
            test_path = self.backend_dir / test_file
            if test_path.exists():
                print(f"\n📋 Running {test_file}...")
                start_time = time.time()
                
                try:
                    result = subprocess.run(
                        [sys.executable, str(test_path)],
                        cwd=self.backend_dir,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    
                    duration = time.time() - start_time
                    
                    if result.returncode == 0:
                        print(f"   ✅ PASSED ({duration:.1f}s)")
                        self.results['unit'][test_file] = {'status': 'PASSED', 'duration': duration}
                    else:
                        print(f"   ❌ FAILED ({duration:.1f}s)")
                        print(f"   Error: {result.stderr[:200]}...")
                        self.results['unit'][test_file] = {'status': 'FAILED', 'duration': duration, 'error': result.stderr}
                        
                except subprocess.TimeoutExpired:
                    print(f"   ⏰ TIMEOUT (>60s)")
                    self.results['unit'][test_file] = {'status': 'TIMEOUT', 'duration': 60}
                except Exception as e:
                    print(f"   💥 ERROR: {e}")
                    self.results['unit'][test_file] = {'status': 'ERROR', 'error': str(e)}
            else:
                print(f"   ⚠️ MISSING: {test_file}")
                
    def run_backend_integration_tests(self):
        """Run all backend integration tests."""
        print("\n🔗 Running Backend Integration Tests")
        print("=" * 50)
        
        integration_tests = [
            "tests/integration/test_flask_app.py",
            "tests/integration/test_advanced_rag.py"
        ]
        
        for test_file in integration_tests:
            test_path = self.backend_dir / test_file
            if test_path.exists():
                print(f"\n📋 Running {test_file}...")
                start_time = time.time()
                
                try:
                    result = subprocess.run(
                        [sys.executable, str(test_path)],
                        cwd=self.backend_dir,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    duration = time.time() - start_time
                    
                    if result.returncode == 0:
                        print(f"   ✅ PASSED ({duration:.1f}s)")
                        self.results['integration'][test_file] = {'status': 'PASSED', 'duration': duration}
                    else:
                        print(f"   ❌ FAILED ({duration:.1f}s)")
                        print(f"   Error: {result.stderr[:200]}...")
                        self.results['integration'][test_file] = {'status': 'FAILED', 'duration': duration, 'error': result.stderr}
                        
                except subprocess.TimeoutExpired:
                    print(f"   ⏰ TIMEOUT (>120s)")
                    self.results['integration'][test_file] = {'status': 'TIMEOUT', 'duration': 120}
                except Exception as e:
                    print(f"   💥 ERROR: {e}")
                    self.results['integration'][test_file] = {'status': 'ERROR', 'error': str(e)}
            else:
                print(f"   ⚠️ MISSING: {test_file}")
                
    def run_backend_performance_tests(self):
        """Run backend performance tests."""
        print("\n📊 Running Backend Performance Tests")
        print("=" * 50)
        
        performance_tests = [
            "tests/performance/test_performance_metrics.py"
        ]
        
        for test_file in performance_tests:
            test_path = self.backend_dir / test_file
            if test_path.exists():
                print(f"\n📋 Running {test_file}...")
                start_time = time.time()
                
                try:
                    result = subprocess.run(
                        [sys.executable, str(test_path)],
                        cwd=self.backend_dir,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    duration = time.time() - start_time
                    
                    if result.returncode == 0:
                        print(f"   ✅ PASSED ({duration:.1f}s)")
                        print("   📁 Performance report generated")
                        self.results['performance'][test_file] = {'status': 'PASSED', 'duration': duration}
                    else:
                        print(f"   ❌ FAILED ({duration:.1f}s)")
                        print(f"   Error: {result.stderr[:200]}...")
                        self.results['performance'][test_file] = {'status': 'FAILED', 'duration': duration, 'error': result.stderr}
                        
                except subprocess.TimeoutExpired:
                    print(f"   ⏰ TIMEOUT (>300s)")
                    self.results['performance'][test_file] = {'status': 'TIMEOUT', 'duration': 300}
                except Exception as e:
                    print(f"   💥 ERROR: {e}")
                    self.results['performance'][test_file] = {'status': 'ERROR', 'error': str(e)}
            else:
                print(f"   ⚠️ MISSING: {test_file}")
                
    def run_frontend_tests(self):
        """Run frontend tests using npm."""
        print("\n⚛️ Running Frontend Tests")
        print("=" * 50)
        
        if not self.frontend_dir.exists():
            print("   ⚠️ Frontend directory not found")
            return
            
        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            print("   ⚠️ Frontend package.json not found")
            return
            
        print(f"\n📋 Running frontend test suite...")
        start_time = time.time()
        
        try:
            result = subprocess.run(
                ["npm", "run", "test:run"],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"   ✅ PASSED ({duration:.1f}s)")
                # Parse test results from output
                if "passing" in result.stdout:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "passing" in line and "failing" in line:
                            print(f"   📊 {line.strip()}")
                            break
                self.results['frontend']['npm_test'] = {'status': 'PASSED', 'duration': duration}
            else:
                print(f"   ❌ FAILED ({duration:.1f}s)")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}...")
                self.results['frontend']['npm_test'] = {'status': 'FAILED', 'duration': duration, 'error': result.stderr}
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ TIMEOUT (>120s)")
            self.results['frontend']['npm_test'] = {'status': 'TIMEOUT', 'duration': 120}
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            self.results['frontend']['npm_test'] = {'status': 'ERROR', 'error': str(e)}
            
    def print_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "=" * 60)
        print("🏆 TEST SUMMARY REPORT")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for category, tests in self.results.items():
            if not tests:
                continue
                
            print(f"\n📂 {category.upper()} TESTS:")
            category_passed = 0
            category_total = 0
            
            for test_name, result in tests.items():
                status = result['status']
                duration = result.get('duration', 0)
                
                if status == 'PASSED':
                    print(f"   ✅ {test_name} ({duration:.1f}s)")
                    category_passed += 1
                    passed_tests += 1
                elif status == 'FAILED':
                    print(f"   ❌ {test_name} ({duration:.1f}s)")
                    failed_tests += 1
                elif status == 'TIMEOUT':
                    print(f"   ⏰ {test_name} (TIMEOUT)")
                    failed_tests += 1
                elif status == 'ERROR':
                    print(f"   💥 {test_name} (ERROR)")
                    failed_tests += 1
                    
                category_total += 1
                total_tests += 1
            
            if category_total > 0:
                success_rate = (category_passed / category_total) * 100
                print(f"   📊 Success Rate: {success_rate:.1f}% ({category_passed}/{category_total})")
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        
        if total_tests > 0:
            overall_success = (passed_tests / total_tests) * 100
            print(f"   Success Rate: {overall_success:.1f}%")
            
            if overall_success >= 90:
                print("   🎉 EXCELLENT - System ready for production!")
            elif overall_success >= 75:
                print("   ✅ GOOD - Minor issues to address")
            elif overall_success >= 50:
                print("   ⚠️ NEEDS WORK - Several issues to fix")
            else:
                print("   ❌ CRITICAL - Major issues need attention")
        
        print("\n" + "=" * 60)
        
    def run_all_tests(self):
        """Run all test suites."""
        print("🚀 Legal RAG System - Comprehensive Test Suite")
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test categories
        self.run_backend_unit_tests()
        self.run_backend_integration_tests()
        self.run_backend_performance_tests()
        self.run_frontend_tests()
        
        total_duration = time.time() - start_time
        
        # Print comprehensive summary
        self.print_summary()
        
        print(f"\n⏱️ Total Test Duration: {total_duration:.1f} seconds")
        print(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
def main():
    """Main entry point."""
    runner = TestRunner()
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "unit":
            runner.run_backend_unit_tests()
        elif test_type == "integration":
            runner.run_backend_integration_tests()
        elif test_type == "performance":
            runner.run_backend_performance_tests()
        elif test_type == "frontend":
            runner.run_frontend_tests()
        elif test_type == "all":
            runner.run_all_tests()
        else:
            print("Usage: python run_tests.py [unit|integration|performance|frontend|all]")
            sys.exit(1)
    else:
        runner.run_all_tests()

if __name__ == "__main__":
    main()
