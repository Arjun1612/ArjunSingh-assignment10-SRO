import time
import requests
import statistics
from dataclasses import dataclass
from typing import List, Callable

@dataclass
class Hypothesis:
    name: str
    description: str
    steady_state_condition: Callable
    chaos_action: Callable
    expected_outcome: str
    tolerance_threshold: float

class HypothesisTest:
    def __init__(self):
        self.results = []

    def measure_steady_state(self, condition_func, duration=60, interval=1):
        """Measure steady state performance"""
        measurements = []
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                measurement = condition_func()
                measurements.append(measurement)
            except Exception as e:
                measurements.append(None)
            time.sleep(interval)
        return measurements

    def run_hypothesis_test(self, hypothesis: Hypothesis):
        """Run a complete hypothesis test"""
        print(f"Testing Hypothesis: {hypothesis.name}")
        print(f"Description: {hypothesis.description}")
        print(f"Expected: {hypothesis.expected_outcome}")
        # Step 1: Measure steady state
        print("Measuring steady state...")
        steady_state = self.measure_steady_state(hypothesis.steady_state_condition, 30, 1)
        steady_state_avg = statistics.mean([m for m in steady_state if m is not None])
        print(f"Steady state average: {steady_state_avg:.2f}")
        # Step 2: Introduce chaos
        print("Introducing chaos...")
        chaos_start = time.time()
        hypothesis.chaos_action()
        # Step 3: Measure during chaos
        print("Measuring during chaos...")
        chaos_state = self.measure_steady_state(hypothesis.steady_state_condition, 60, 1)
        chaos_state_avg = statistics.mean([m for m in chaos_state if m is not None])
        print(f"Chaos state average: {chaos_state_avg:.2f}")
        # Step 4: Analyze results
        degradation = ((steady_state_avg - chaos_state_avg) / steady_state_avg) * 100
        result = {
            "hypothesis": hypothesis.name,
            "steady_state_avg": steady_state_avg,
            "chaos_state_avg": chaos_state_avg,
            "degradation_percent": degradation,
            "within_tolerance": abs(degradation) <= hypothesis.tolerance_threshold,
            "timestamp": time.time()
        }
        self.results.append(result)
        print("Results:")
        print(f"Degradation: {degradation:.1f}%")
        print(f"Within tolerance ({hypothesis.tolerance_threshold}%): {result['within_tolerance']}")
        return result

def api_response_time():
    """Measure API response time"""
    try:
        response = requests.get('http://localhost:5000/api/data', timeout=2)
        return response.elapsed.total_seconds()
    except:
        return None

if __name__ == '__main__':
    # Example usage (not provided in OCR but implied)
    tester = HypothesisTest()
    hypothesis = Hypothesis(
        name="API Response Time",
        description="Test API response time under chaos",
        steady_state_condition=api_response_time,
        chaos_action=lambda: None,  # Placeholder for chaos action
        expected_outcome="Response time degradation within 20%",
        tolerance_threshold=20.0
    )
    results = tester.run_hypothesis_test(hypothesis)
    print("\nSummary of all tests:")
    for result in tester.results:
        status = "PASS" if result['within_tolerance'] else "FAIL"
        print(f"{status} {result['hypothesis']}: {result['degradation_percent']:.1f}%")