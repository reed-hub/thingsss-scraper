#!/usr/bin/env python3
"""
Comprehensive Test Suite for Thingsss Scraping API Service
==========================================================

This test suite validates the deployment and functionality of the scraping service
across different strategies and site types. It's designed to be run both during
development and in CI/CD pipelines.

Features:
- Health check validation
- API endpoint testing
- Strategy verification
- Performance benchmarking
- Error handling validation
- Real-world site testing

Usage:
    # Run all tests
    python3 test_deployment.py
    
    # Run with custom URL
    DEPLOYMENT_URL=https://custom-url.railway.app python3 test_deployment.py
    
    # Run specific test category
    python3 test_deployment.py --category health
    
Author: Thingsss Team
Version: 2.0.0
"""

import asyncio
import httpx
import json
import time
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

# Configuration
DEPLOYMENT_URL = os.getenv(
    "DEPLOYMENT_URL", 
    "https://thingsss-scraper-production.up.railway.app"
)

# Test configuration
DEFAULT_TIMEOUT = 30
EXTENDED_TIMEOUT = 90
MAX_RETRIES = 3


@dataclass
class TestResult:
    """Test result data structure."""
    name: str
    success: bool
    duration: float
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class TestSuite:
    """Comprehensive test suite for the scraping service."""
    
    def __init__(self, base_url: str = DEPLOYMENT_URL):
        self.base_url = base_url.rstrip('/')
        self.results: List[TestResult] = []
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test categories and return comprehensive results."""
        print(f"🚀 Testing Thingsss Scraping API at: {self.base_url}")
        print("=" * 70)
        
        start_time = time.time()
        
        # Test categories in order of importance
        test_categories = [
            ("Health Check", self.test_health_endpoint),
            ("API Structure", self.test_api_structure),
            ("Basic HTTP Scraping", self.test_http_scraping),
            ("Browser Automation", self.test_browser_scraping),
            ("Strategy Selection", self.test_strategy_selection),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance),
            ("Real-world Sites", self.test_real_world_sites),
        ]
        
        for category_name, test_func in test_categories:
            print(f"\n🧪 Running {category_name} Tests...")
            try:
                await test_func()
            except Exception as e:
                print(f"❌ {category_name} tests crashed: {e}")
                self.results.append(TestResult(
                    name=f"{category_name} (crashed)",
                    success=False,
                    duration=0.0,
                    error=str(e)
                ))
        
        # Generate summary
        total_time = time.time() - start_time
        summary = self._generate_summary(total_time)
        
        return summary
    
    async def test_health_endpoint(self):
        """Test service health and basic connectivity."""
        # Basic health check
        result = await self._make_request("GET", "/health")
        if result.success and result.details:
            data = result.details
            expected_fields = ["status", "service", "version"]
            
            if all(field in data for field in expected_fields):
                if data["status"] == "healthy":
                    self.results.append(TestResult(
                        name="Basic Health Check",
                        success=True,
                        duration=result.duration,
                        details=data
                    ))
                else:
                    self.results.append(TestResult(
                        name="Basic Health Check",
                        success=False,
                        duration=result.duration,
                        error=f"Service status: {data.get('status', 'unknown')}"
                    ))
            else:
                missing = [f for f in expected_fields if f not in data]
                self.results.append(TestResult(
                    name="Health Response Structure",
                    success=False,
                    duration=result.duration,
                    error=f"Missing fields: {missing}"
                ))
        else:
            self.results.append(TestResult(
                name="Health Endpoint Connectivity",
                success=False,
                duration=result.duration,
                error=result.error
            ))
    
    async def test_api_structure(self):
        """Test API structure and available endpoints."""
        # Test strategies endpoint
        result = await self._make_request("GET", "/api/v1/strategies")
        if result.success and result.details:
            strategies = result.details.get("strategies", [])
            expected_strategies = ["auto", "http", "browser", "hybrid"]
            
            available_strategies = [s["name"] for s in strategies if isinstance(s, dict)]
            missing_strategies = [s for s in expected_strategies if s not in available_strategies]
            
            if not missing_strategies:
                self.results.append(TestResult(
                    name="Strategies Endpoint",
                    success=True,
                    duration=result.duration,
                    details={"strategies": available_strategies}
                ))
            else:
                self.results.append(TestResult(
                    name="Strategies Completeness",
                    success=False,
                    duration=result.duration,
                    error=f"Missing strategies: {missing_strategies}"
                ))
        
        # Test test endpoint
        result = await self._make_request("POST", "/api/v1/test")
        if result.success:
            self.results.append(TestResult(
                name="Test Endpoint",
                success=True,
                duration=result.duration,
                details=result.details
            ))
        else:
            self.results.append(TestResult(
                name="Test Endpoint",
                success=False,
                duration=result.duration,
                error=result.error
            ))
    
    async def test_http_scraping(self):
        """Test HTTP-based scraping functionality."""
        test_cases = [
            {
                "name": "Simple HTTP - Example.com",
                "url": "https://example.com",
                "strategy": "http",
                "expected_title": "Example Domain"
            },
            {
                "name": "HTTP with Custom Fields",
                "url": "https://httpbin.org/html",
                "strategy": "http",
                "extract_fields": ["title", "description"],
                "expected_title_contains": "Herman Melville"
            }
        ]
        
        for test_case in test_cases:
            await self._test_scraping_request(test_case)
    
    async def test_browser_scraping(self):
        """Test browser-based scraping functionality."""
        test_cases = [
            {
                "name": "Browser - Example.com",
                "url": "https://example.com",
                "strategy": "browser",
                "timeout": 45,
                "expected_title": "Example Domain"
            }
        ]
        
        for test_case in test_cases:
            await self._test_scraping_request(test_case)
    
    async def test_strategy_selection(self):
        """Test automatic strategy selection."""
        test_cases = [
            {
                "name": "Auto Strategy - Simple Site",
                "url": "https://example.com",
                "strategy": "auto",
                "expected_strategy": "http"
            }
        ]
        
        for test_case in test_cases:
            result = await self._test_scraping_request(test_case, check_strategy=True)
    
    async def test_error_handling(self):
        """Test error handling and edge cases."""
        test_cases = [
            {
                "name": "Invalid URL",
                "url": "not-a-valid-url",
                "strategy": "http",
                "expect_error": True
            },
            {
                "name": "Non-existent Domain",
                "url": "https://this-domain-should-not-exist-12345.com",
                "strategy": "http",
                "expect_error": True,
                "timeout": 10
            },
            {
                "name": "Timeout Test",
                "url": "https://httpbin.org/delay/5",
                "strategy": "http",
                "timeout": 2,
                "expect_error": True
            }
        ]
        
        for test_case in test_cases:
            await self._test_scraping_request(test_case)
    
    async def test_performance(self):
        """Test performance characteristics."""
        # Performance benchmark
        start_time = time.time()
        
        # Test concurrent requests
        tasks = []
        for i in range(3):  # Small concurrent test
            task = self._make_scraping_request({
                "url": "https://example.com",
                "strategy": "http"
            })
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        concurrent_time = time.time() - start_time
        
        successful_requests = sum(1 for r in results if isinstance(r, TestResult) and r.success)
        
        self.results.append(TestResult(
            name="Concurrent Requests",
            success=successful_requests >= 2,  # At least 2 out of 3 should succeed
            duration=concurrent_time,
            details={
                "concurrent_requests": 3,
                "successful": successful_requests,
                "total_time": concurrent_time
            }
        ))
        
        # Response time test
        if successful_requests > 0:
            avg_response_time = sum(
                r.duration for r in results 
                if isinstance(r, TestResult) and r.success
            ) / successful_requests
            
            self.results.append(TestResult(
                name="Response Time Performance",
                success=avg_response_time < 10.0,  # Should be under 10 seconds
                duration=avg_response_time,
                details={"average_response_time": avg_response_time}
            ))
    
    async def test_real_world_sites(self):
        """Test with real-world sites that have historically been problematic."""
        test_cases = [
            {
                "name": "CB2 Product Page",
                "url": "https://www.cb2.com/burl-35.5-rotating-coffee-table/s151251",
                "strategy": "browser",
                "timeout": 60,
                "extract_fields": ["title", "description", "images", "price"],
                "expected_title_contains": "Burl"
            }
        ]
        
        for test_case in test_cases:
            await self._test_scraping_request(test_case)
    
    async def _test_scraping_request(
        self, 
        test_case: Dict[str, Any], 
        check_strategy: bool = False
    ) -> TestResult:
        """Test a scraping request with given parameters."""
        name = test_case["name"]
        expect_error = test_case.get("expect_error", False)
        
        payload = {
            "url": test_case["url"],
            "strategy": test_case["strategy"],
            "timeout": test_case.get("timeout", DEFAULT_TIMEOUT)
        }
        
        if "extract_fields" in test_case:
            payload["extract_fields"] = test_case["extract_fields"]
        
        result = await self._make_scraping_request(payload)
        
        if expect_error:
            # For error cases, success means we got an error as expected
            success = not result.success or (
                result.details and not result.details.get("success", True)
            )
            error = None if success else "Expected error but request succeeded"
        else:
            success = result.success
            error = result.error
            
            # Additional validation for successful requests
            if success and result.details:
                data = result.details
                
                # Check if scraping was successful
                if not data.get("success", False):
                    success = False
                    error = f"Scraping failed: {data.get('error', 'Unknown error')}"
                
                # Check expected title
                elif "expected_title" in test_case:
                    title = data.get("data", {}).get("title")
                    if title != test_case["expected_title"]:
                        success = False
                        error = f"Expected title '{test_case['expected_title']}', got '{title}'"
                
                # Check title contains
                elif "expected_title_contains" in test_case:
                    title = data.get("data", {}).get("title", "")
                    if test_case["expected_title_contains"] not in title:
                        success = False
                        error = f"Title '{title}' doesn't contain '{test_case['expected_title_contains']}'"
                
                # Check strategy used
                if check_strategy and "expected_strategy" in test_case:
                    used_strategy = data.get("strategy_used")
                    if used_strategy != test_case["expected_strategy"]:
                        # This is a warning, not a failure
                        print(f"⚠️  Expected strategy {test_case['expected_strategy']}, got {used_strategy}")
        
        test_result = TestResult(
            name=name,
            success=success,
            duration=result.duration,
            error=error,
            details=result.details
        )
        
        self.results.append(test_result)
        return test_result
    
    async def _make_scraping_request(self, payload: Dict[str, Any]) -> TestResult:
        """Make a scraping request and return the result."""
        return await self._make_request("POST", "/api/v1/scrape", json_data=payload)
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        json_data: Optional[Dict[str, Any]] = None
    ) -> TestResult:
        """Make an HTTP request and return a TestResult."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            timeout = EXTENDED_TIMEOUT if json_data else DEFAULT_TIMEOUT
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method == "GET":
                    response = await client.get(url)
                elif method == "POST":
                    response = await client.post(url, json=json_data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        return TestResult(
                            name=f"{method} {endpoint}",
                            success=True,
                            duration=duration,
                            details=data
                        )
                    except json.JSONDecodeError:
                        return TestResult(
                            name=f"{method} {endpoint}",
                            success=False,
                            duration=duration,
                            error="Invalid JSON response"
                        )
                else:
                    return TestResult(
                        name=f"{method} {endpoint}",
                        success=False,
                        duration=duration,
                        error=f"HTTP {response.status_code}: {response.text[:200]}"
                    )
                    
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name=f"{method} {endpoint}",
                success=False,
                duration=duration,
                error=str(e)
            )
    
    def _generate_summary(self, total_time: float) -> Dict[str, Any]:
        """Generate comprehensive test summary."""
        passed = sum(1 for result in self.results if result.success)
        failed = len(self.results) - passed
        
        # Print detailed results
        print("\n" + "=" * 70)
        print("📊 DETAILED TEST RESULTS")
        print("=" * 70)
        
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"{result.name:.<45} {status} ({result.duration:.2f}s)")
            
            if not result.success and result.error:
                print(f"    Error: {result.error}")
            
            if result.details and isinstance(result.details, dict):
                if "data" in result.details:
                    data = result.details["data"]
                    if isinstance(data, dict) and "title" in data:
                        title = data["title"]
                        if title and len(title) > 50:
                            title = title[:47] + "..."
                        print(f"    Title: {title}")
        
        # Print summary
        print("\n" + "=" * 70)
        print("📈 TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {len(self.results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.results)*100):.1f}%")
        print(f"Total Duration: {total_time:.2f} seconds")
        
        # Performance metrics
        if self.results:
            avg_duration = sum(r.duration for r in self.results) / len(self.results)
            max_duration = max(r.duration for r in self.results)
            print(f"Average Response Time: {avg_duration:.2f}s")
            print(f"Slowest Response: {max_duration:.2f}s")
        
        # Final verdict
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Deployment is successful! 🎉")
            verdict = "SUCCESS"
        elif failed <= 2:
            print(f"\n⚠️  {failed} test(s) failed. Deployment mostly functional.")
            verdict = "PARTIAL_SUCCESS"
        else:
            print(f"\n❌ {failed} test(s) failed. Check deployment.")
            verdict = "FAILURE"
        
        return {
            "verdict": verdict,
            "total_tests": len(self.results),
            "passed": passed,
            "failed": failed,
            "success_rate": passed / len(self.results) * 100,
            "total_duration": total_time,
            "results": [
                {
                    "name": r.name,
                    "success": r.success,
                    "duration": r.duration,
                    "error": r.error
                }
                for r in self.results
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "deployment_url": self.base_url
        }


async def main():
    """Main test execution function."""
    # Parse command line arguments
    if len(sys.argv) > 1:
        if "--help" in sys.argv or "-h" in sys.argv:
            print(__doc__)
            return
        
        # Custom deployment URL
        for arg in sys.argv[1:]:
            if arg.startswith("--url="):
                global DEPLOYMENT_URL
                DEPLOYMENT_URL = arg.split("=", 1)[1]
    
    # Initialize and run test suite
    test_suite = TestSuite(DEPLOYMENT_URL)
    summary = await test_suite.run_all_tests()
    
    # Exit with appropriate code
    if summary["verdict"] == "SUCCESS":
        sys.exit(0)
    elif summary["verdict"] == "PARTIAL_SUCCESS":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    """
    Run the comprehensive test suite.
    
    Environment Variables:
        DEPLOYMENT_URL: Override default deployment URL
        
    Exit Codes:
        0: All tests passed
        1: Some tests failed (partial success)
        2: Many tests failed (deployment issues)
    """
    print("🤖 Thingsss Scraping API - Comprehensive Test Suite")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Test suite interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 Test suite crashed: {e}")
        sys.exit(3) 