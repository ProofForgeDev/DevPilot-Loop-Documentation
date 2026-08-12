#!/usr/bin/env python3
"""
DevPilot Loop - Benchmark Script
================================
Performance benchmarking for the multi-agent system
"""

import json
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone


BASE_URLS = {
    "manager": "http://localhost:8008",
    "intake": "http://localhost:8001",
    "analyst": "http://localhost:8002",
    "fixer": "http://localhost:8003",
}


def benchmark_health(url: str, name: str) -> dict:
    """Benchmark health endpoint"""
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(f"{url}/health", timeout=5) as resp:
            data = json.loads(resp.read())
            elapsed = time.perf_counter() - start
            return {"name": name, "endpoint": "/health", "status": data.get("status"), "latency_ms": round(elapsed * 1000, 2)}
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {"name": name, "endpoint": "/health", "status": "error", "error": str(e), "latency_ms": round(elapsed * 1000, 2)}


def benchmark_dispatch(url: str) -> dict:
    """Benchmark task dispatch"""
    start = time.perf_counter()
    payload = {
        "task_id": f"BENCH-{int(time.time())}",
        "source": "benchmark",
        "raw_payload": {"test": True},
        "priority": "P1",
        "target_worker": "intake",
    }
    try:
        req = urllib.request.Request(
            f"{url}/dispatch",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            elapsed = time.perf_counter() - start
            return {"endpoint": "/dispatch", "status": data.get("status"), "latency_ms": round(elapsed * 1000, 2)}
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {"endpoint": "/dispatch", "status": "error", "error": str(e), "latency_ms": round(elapsed * 1000, 2)}


def benchmark_concurrent_dispatch(url: str, count: int = 10) -> dict:
    """Benchmark concurrent task dispatch"""
    start = time.perf_counter()

    def dispatch_one(i: int) -> dict:
        payload = {
            "task_id": f"BENCH-CONC-{i}",
            "source": "benchmark",
            "raw_payload": {"test": True, "index": i},
            "priority": "P1",
            "target_worker": "intake",
        }
        req = urllib.request.Request(
            f"{url}/dispatch",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())

    with ThreadPoolExecutor(max_workers=count) as executor:
        futures = [executor.submit(dispatch_one, i) for i in range(count)]
        results = list(as_completed(futures))

    elapsed = time.perf_counter() - start
    success = sum(1 for f in results if f.result().get("status") == "ok")

    return {
        "endpoint": "/dispatch (concurrent)",
        "count": count,
        "success": success,
        "total_time_ms": round(elapsed * 1000, 2),
        "throughput_qps": round(success / elapsed, 2) if elapsed > 0 else 0,
    }


def run_benchmarks() -> dict:
    """Run all benchmarks"""
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "health_check": [],
        "single_dispatch": [],
        "concurrent_dispatch": [],
    }

    # Health checks
    for name, url in BASE_URLS.items():
        results["health_check"].append(benchmark_health(url, name))

    # Single dispatch
    results["single_dispatch"].append(benchmark_dispatch(BASE_URLS["manager"]))

    # Concurrent dispatch
    results["concurrent_dispatch"].append(benchmark_concurrent_dispatch(BASE_URLS["manager"], 10))

    return results


if __name__ == "__main__":
    print("=" * 60)
    print("  DevPilot Loop Benchmark")
    print("=" * 60)
    results = run_benchmarks()
    print(json.dumps(results, indent=2))

    # Save results
    with open("poc/evidence/benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to poc/evidence/benchmark_results.json")
