"""Performance tests for customer service API.

This module contains performance and stress tests to verify:
- Single request response time (target: 2-3s)
- Concurrent request handling (target: 10+ concurrent users)
- System stability under load
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
import json


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    response_times: List[float] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    errors: List[str] = field(default_factory=list)

    @property
    def total_requests(self) -> int:
        return self.success_count + self.failure_count

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.success_count / self.total_requests) * 100

    @property
    def avg_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)

    @property
    def median_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return statistics.median(self.response_times)

    @property
    def p95_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[min(index, len(sorted_times) - 1)]

    @property
    def p99_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.99)
        return sorted_times[min(index, len(sorted_times) - 1)]

    @property
    def min_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return min(self.response_times)

    @property
    def max_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return max(self.response_times)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": round(self.success_rate, 2),
            "avg_response_time_ms": round(self.avg_response_time * 1000, 2),
            "median_response_time_ms": round(self.median_response_time * 1000, 2),
            "p95_response_time_ms": round(self.p95_response_time * 1000, 2),
            "p99_response_time_ms": round(self.p99_response_time * 1000, 2),
            "min_response_time_ms": round(self.min_response_time * 1000, 2),
            "max_response_time_ms": round(self.max_response_time * 1000, 2),
        }


class APIClient:
    """Simple HTTP client for performance testing."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def query(self, question: str, session_id: str = None) -> Dict[str, Any]:
        """Send a query request to the API."""
        import urllib.request
        import urllib.error

        url = f"{self.base_url}/api/query"
        data = json.dumps({
            "query": question,
            "session_id": session_id
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                elapsed = time.time() - start_time
                return {
                    "success": True,
                    "response_time": elapsed,
                    "status_code": response.status
                }
        except urllib.error.HTTPError as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "response_time": elapsed,
                "status_code": e.code,
                "error": str(e)
            }
        except urllib.error.URLError as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "response_time": elapsed,
                "error": str(e)
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "response_time": elapsed,
                "error": str(e)
            }

    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        import urllib.request
        import urllib.error

        url = f"{self.base_url}/api/health"

        start_time = time.time()
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                elapsed = time.time() - start_time
                return {
                    "success": True,
                    "response_time": elapsed,
                    "status_code": response.status
                }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "response_time": elapsed,
                "error": str(e)
            }


def run_single_request_test(client: APIClient, num_requests: int = 10) -> PerformanceMetrics:
    """Run single request test (sequential)."""
    metrics = PerformanceMetrics()
    questions = [
        "如何申请退款？",
        "订单状态如何查询？",
        "我的订单到哪里了？",
        "怎么联系客服？",
        "退货流程是什么？",
        "如何修改收货地址？",
        "支付失败怎么办？",
        "优惠券怎么使用？",
        "会员有什么特权？",
        "发货时间是多久？",
    ]

    for i in range(num_requests):
        question = questions[i % len(questions)]
        result = client.query(question, session_id=f"perf-test-{i}")

        if result["success"]:
            metrics.success_count += 1
            metrics.response_times.append(result["response_time"])
        else:
            metrics.failure_count += 1
            metrics.errors.append(result.get("error", "Unknown error"))

    return metrics


def run_concurrent_test(client: APIClient, num_concurrent: int = 10, requests_per_user: int = 5) -> PerformanceMetrics:
    """Run concurrent requests test."""
    metrics = PerformanceMetrics()
    questions = [
        "如何申请退款？",
        "订单状态如何查询？",
        "我的订单到哪里了？",
        "怎么联系客服？",
        "退货流程是什么？",
    ]

    def make_request(user_id: int, request_id: int) -> Dict[str, Any]:
        question = questions[request_id % len(questions)]
        session_id = f"concurrent-user-{user_id}"
        return client.query(question, session_id=session_id)

    with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = []
        for user_id in range(num_concurrent):
            for request_id in range(requests_per_user):
                futures.append(executor.submit(make_request, user_id, request_id))

        for future in as_completed(futures):
            result = future.result()
            if result["success"]:
                metrics.success_count += 1
                metrics.response_times.append(result["response_time"])
            else:
                metrics.failure_count += 1
                metrics.errors.append(result.get("error", "Unknown error"))

    return metrics


def run_stress_test(client: APIClient, duration_seconds: int = 30, max_concurrent: int = 20) -> PerformanceMetrics:
    """Run stress test for specified duration."""
    metrics = PerformanceMetrics()
    questions = [
        "如何申请退款？",
        "订单状态如何查询？",
        "我的订单到哪里了？",
    ]

    stop_flag = {"stop": False}
    lock = asyncio.Lock()

    async def worker(worker_id: int):
        import aiohttp

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            request_count = 0
            while not stop_flag["stop"]:
                question = questions[request_count % len(questions)]
                session_id = f"stress-worker-{worker_id}-{request_count}"

                start_time = time.time()
                try:
                    async with session.post(
                        f"{client.base_url}/api/query",
                        json={"query": question, "session_id": session_id}
                    ) as response:
                        elapsed = time.time() - start_time
                        if response.status == 200:
                            async with lock:
                                metrics.success_count += 1
                                metrics.response_times.append(elapsed)
                        else:
                            async with lock:
                                metrics.failure_count += 1
                                metrics.errors.append(f"Status {response.status}")
                except Exception as e:
                    elapsed = time.time() - start_time
                    async with lock:
                        metrics.failure_count += 1
                        metrics.errors.append(str(e))
                        metrics.response_times.append(elapsed)

                request_count += 1
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.1)

    async def run_test():
        workers = [asyncio.create_task(worker(i)) for i in range(max_concurrent)]

        # Run for specified duration
        await asyncio.sleep(duration_seconds)

        # Stop workers
        stop_flag["stop"] = True
        await asyncio.gather(*workers, return_exceptions=True)

    asyncio.run(run_test())
    return metrics


def print_metrics(metrics: PerformanceMetrics, test_name: str):
    """Print performance metrics in a formatted way."""
    print("\n" + "=" * 60)
    print(f" {test_name} - Performance Metrics")
    print("=" * 60)

    data = metrics.to_dict()

    print(f"\n📊 Request Statistics:")
    print(f"   Total Requests:    {data['total_requests']}")
    print(f"   Successful:        {data['success_count']}")
    print(f"   Failed:            {data['failure_count']}")
    print(f"   Success Rate:      {data['success_rate']}%")

    print(f"\n⏱️  Response Time Statistics:")
    print(f"   Average:           {data['avg_response_time_ms']:.2f} ms ({data['avg_response_time_ms']/1000:.2f} s)")
    print(f"   Median:            {data['median_response_time_ms']:.2f} ms")
    print(f"   P95:               {data['p95_response_time_ms']:.2f} ms")
    print(f"   P99:               {data['p99_response_time_ms']:.2f} ms")
    print(f"   Min:               {data['min_response_time_ms']:.2f} ms")
    print(f"   Max:               {data['max_response_time_ms']:.2f} ms")

    # Check against targets
    print(f"\n🎯 Target Validation (2-3s response, 10+ concurrent):")
    avg_seconds = data['avg_response_time_ms'] / 1000
    if avg_seconds <= 3.0:
        print(f"   ✅ Average response time ({avg_seconds:.2f}s) meets target (≤3s)")
    else:
        print(f"   ⚠️  Average response time ({avg_seconds:.2f}s) exceeds target (≤3s)")

    if metrics.errors:
        print(f"\n❌ Errors ({len(metrics.errors)}):")
        for error in metrics.errors[:5]:  # Show first 5 errors
            print(f"   - {error}")

    print("=" * 60 + "\n")


def main():
    """Run all performance tests."""
    import argparse

    parser = argparse.ArgumentParser(description="Run performance tests for customer service API")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--single-requests", type=int, default=10, help="Number of sequential requests")
    parser.add_argument("--concurrent-users", type=int, default=10, help="Number of concurrent users")
    parser.add_argument("--requests-per-user", type=int, default=5, help="Requests per concurrent user")
    parser.add_argument("--stress-duration", type=int, default=30, help="Stress test duration in seconds")
    parser.add_argument("--stress-workers", type=int, default=20, help="Number of workers for stress test")
    parser.add_argument("--test", choices=["single", "concurrent", "stress", "all"], default="all",
                        help="Which test to run")

    args = parser.parse_args()

    client = APIClient(base_url=args.base_url)

    # First, check if API is available
    print("Checking API availability...")
    health = client.health_check()
    if not health["success"]:
        print(f"❌ API health check failed: {health.get('error', 'Unknown error')}")
        print("   Please make sure the API server is running:")
        print("   poetry run python -m uvicorn src.api.routes:app --host 0.0.0.0 --port 8000")
        return

    print(f"✅ API is healthy (response time: {health['response_time']*1000:.2f} ms)\n")

    if args.test in ["single", "all"]:
        # Test 1: Single request performance
        print("🚀 Running Single Request Test...")
        single_metrics = run_single_request_test(client, num_requests=args.single_requests)
        print_metrics(single_metrics, "Single Request Test")

    if args.test in ["concurrent", "all"]:
        # Test 2: Concurrent requests
        print("🚀 Running Concurrent Request Test...")
        concurrent_metrics = run_concurrent_test(
            client,
            num_concurrent=args.concurrent_users,
            requests_per_user=args.requests_per_user
        )
        print_metrics(concurrent_metrics, "Concurrent Request Test")

    if args.test in ["stress", "all"]:
        # Test 3: Stress test
        print("🚀 Running Stress Test...")
        print(f"   Duration: {args.stress_duration} seconds, Workers: {args.stress_workers}")
        stress_metrics = run_stress_test(
            client,
            duration_seconds=args.stress_duration,
            max_concurrent=args.stress_workers
        )
        print_metrics(stress_metrics, "Stress Test")


if __name__ == "__main__":
    main()
