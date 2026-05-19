from datetime import datetime, timezone
from tester.tests import TESTS


def percentile(values, p):
    if not values:
        return 0

    values = sorted(values)
    k = (len(values) - 1) * (p / 100)
    lower = int(k)
    upper = min(lower + 1, len(values) - 1)

    if lower == upper:
        return values[lower]

    return values[lower] + (values[upper] - values[lower]) * (k - lower)


def run_all_tests():
    test_results = []

    for test_function in TESTS:
        try:
            test_results.append(test_function())
        except Exception as exc:
            test_results.append({
                "name": test_function.__name__,
                "status": "FAIL",
                "latency_ms": 0,
                "details": f"Erreur pendant le test : {exc}"
            })

    total = len(test_results)
    passed = sum(1 for test in test_results if test["status"] == "PASS")
    failed = total - passed

    latencies = [
        test["latency_ms"]
        for test in test_results
        if isinstance(test.get("latency_ms"), (int, float))
    ]

    latency_avg = round(sum(latencies) / len(latencies), 2) if latencies else 0
    latency_p95 = round(percentile(latencies, 95), 2) if latencies else 0
    error_rate = round(failed / total, 3) if total else 0
    availability = round((passed / total) * 100, 2) if total else 0

    return {
        "api": "Frankfurter API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "error_rate": error_rate,
            "availability_percent": availability,
            "latency_ms_avg": latency_avg,
            "latency_ms_p95": latency_p95
        },
        "tests": test_results
    }