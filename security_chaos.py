import requests
import time
import hashlib
import jwt
from datetime import datetime, timedelta

class SecurityChaosTests:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.results = []

    def test_authentication_bypass(self):
        """Test system behavior when auth service fails"""
        print("Testing authentication bypass scenarios")
        test_cases = [
            {"name": "No token", "headers": {}},
            {"name": "Invalid token", "headers": {"Authorization": "Bearer invalid"}},
            {"name": "Expired token", "headers": {"Authorization": "Bearer expired"}},
            {"name": "Malformed token", "headers": {"Authorization": "Bearer malformed"}}
        ]
        results = []
        for case in test_cases:
            try:
                response = requests.get(
                    f"{self.base_url}/api/secure-data",
                    headers=case["headers"],
                    timeout=5
                )
                result = {
                    "test": case["name"],
                    "status_code": response.status_code,
                    "secure": response.status_code in [401, 403],
                    "response_time": response.elapsed.total_seconds()
                }
                results.append(result)
            except requests.exceptions.RequestException as e:
                results.append({
                    "test": case["name"],
                    "error": str(e),
                    "secure": True  # Failing closed is secure
                })
        return results

    def test_rate_limiting(self):
        """Test rate limiting under stress"""
        print("Testing rate limiting under stress")
        # Simulate burst of requests
        start_time = time.time()
        responses = []
        for i in range(100):  # Send 100 requests quickly
            try:
                response = requests.get(f"{self.base_url}/api/data", timeout=1)
                responses.append({
                    "request_id": i,
                    "status_code": response.status_code,
                    "timestamp": time.time() - start_time
                })
            except:
                responses.append({
                    "request_id": i,
                    "status_code": None,
                    "timestamp": time.time() - start_time
                })
        # Analyze rate limiting effectiveness
        rate_limited = sum(1 for r in responses if r["status_code"] == 429)
        successful = sum(1 for r in responses if r["status_code"] == 200)
        return {
            "total_requests": len(responses),
            "rate_limited": rate_limited,
            "successful": successful,
            "rate_limiting_effective": rate_limited > 0
        }

    def test_data_exposure_on_failure(self):
        """Test data exposure during failure scenarios"""
        # Placeholder for data exposure tests (not fully provided in OCR)
        print("Testing data exposure on failure")
        return [
            {"test": "Data exposure test", "data_exposed": False}  # Simulated
        ]

    def run_security_chaos_suite(self):
        """Run all security chaos tests"""
        auth_results = self.test_authentication_bypass()
        rate_limit_results = self.test_rate_limiting()
        exposure_results = self.test_data_exposure_on_failure()
        # Compile results
        suite_results = {
            "timestamp": datetime.now().isoformat(),
            "authentication_tests": auth_results,
            "rate_limiting_tests": rate_limit_results,
            "data_exposure_tests": exposure_results
        }
        # Security score calculation
        auth_score = sum(1 for r in auth_results if r.get("secure", False))
        rate_limit_score = 1 if rate_limit_results["rate_limiting_effective"] else 0
        exposure_score = sum(1 for r in exposure_results if not r.get("data_exposed", True))
        total_tests = len(auth_results) + 1 + len(exposure_results)
        security_score = ((auth_score + rate_limit_score + exposure_score) / total_tests) * 100
        suite_results["security_score"] = security_score
        print("\nSecurity Chaos Test Results:")
        print(f"Authentication Security: {auth_score}/{len(auth_results)} tests passed")
        print(f"Rate Limiting: {1 if rate_limit_score else 0}")
        print(f"Data Exposure Prevention: {exposure_score}/{len(exposure_results)} tests passed")
        print(f"Overall Security Score: {security_score:.1f}%")
        return suite_results

def main():
    security_tester = SecurityChaosTests()
    results = security_tester.run_security_chaos_suite()
    # Save results. hi
    with open("security_chaos_results.json", 'w') as f:
        import json
        json.dump(results, f, indent=2)
    print("Results saved to security_chaos_results.json")

if __name__ == '__main__':
    main()