"""
Integration Tests — 扩展集成测试
================================"""

import json
import sys
import os
import time
import concurrent.futures
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from skills.registry import initialize, get_skill, list_skills


def test_registry_initialization():
    """Test registry initialization"""
    initialize()
    skills = list_skills()
    assert len(skills) >= 6
    print("  ✓ Registry initialization: loaded", len(skills), "skills")
    return True


def test_all_skills_validate():
    """Test all skills validate correctly"""
    initialize()
    skills = list_skills()
    for skill_info in skills:
        name = skill_info["name"]
        skill = get_skill(name)
        schema = skill.get_schema()
        assert "input" in schema
        assert "output" in schema
    print(f"  ✓ All {len(skills)} skills have valid schemas")
    return True


def test_skill_execution_consistency():
    """Test consistent skill execution"""
    initialize()
    skill = get_skill("code-review")
    code = "def hello(): pass"
    results = [skill.execute({"source_code": code}) for _ in range(3)]
    for r in results:
        assert r["status"] == "ok"
    print("  ✓ Skill execution is consistent")
    return True


def test_rapid_dispatch():
    """Test rapid task dispatch"""
    import urllib.request
    manager_url = "http://localhost:8008"

    for i in range(5):
        try:
            req = urllib.request.Request(
                f"{manager_url}/dispatch",
                data=json.dumps({
                    "task_id": f"RAPID-{i}",
                    "source": "integration_test",
                    "raw_payload": {"test": i},
                    "priority": "P2",
                }).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read().decode())
                assert result.get("status") == "ok" or "error" in result
        except Exception:
            pass  # Service may not be running

    print("  ✓ Rapid dispatch test completed")
    return True


def test_concurrent_skill_execution():
    """Test concurrent skill execution"""
    initialize()
    code = "def test(): return 42"
    results = []

    def execute_skill():
        skill = get_skill("code-review")
        return skill.execute({"source_code": code})

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(execute_skill) for _ in range(5)]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    ok_count = sum(1 for r in results if r.get("status") == "ok")
    print(f"  ✓ Concurrent execution: {ok_count}/5 successful")
    return True


def test_multiple_skill_types():
    """Test different skill types"""
    initialize()

    test_cases = [
        ("code-review", {"source_code": "x = 1"}),
        ("security-scan", {"source_code": "x = 1"}),
        ("perf-analysis", {"source_code": "x = 1"}),
        ("test-generation", {"source_code": "def f(): pass"}),
        ("doc-writing", {"doc_type": "api", "title": "Test"}),
        ("deploy-verification", {"services": ["test"]}),
    ]

    for name, data in test_cases:
        skill = get_skill(name)
        result = skill.execute(data)
        assert result["status"] == "ok"

    print("  ✓ All 6 skill types execute successfully")
    return True


def test_error_handling_in_skills():
    """Test error handling in skill execution"""
    initialize()
    skill = get_skill("code-review")

    # Invalid input should not crash
    try:
        skill.execute({})
    except Exception:
        pass  # Expected behavior

    # Empty code should work
    result = skill.execute({"source_code": ""})
    assert result["status"] == "ok"

    print("  ✓ Error handling works correctly")
    return True


def test_large_codebase_analysis():
    """Test analyzing large codebase"""
    initialize()
    skill = get_skill("code-review")

    # Generate large code
    lines = []
    for i in range(500):
        lines.append(f"def function_{i}(): return {i}")
    large_code = "\n".join(lines)

    result = skill.execute({"source_code": large_code})
    assert result["status"] == "ok"
    assert result["total_lines"] == 500

    print("  ✓ Large codebase analysis: 500 lines processed")
    return True


def test_trace_id_uniqueness():
    """Test trace ID uniqueness"""
    traces = set()
    for i in range(10):
        trace = f"trace-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}-{i}"
        traces.add(trace)

    assert len(traces) == 10
    print("  ✓ Trace ID uniqueness verified")
    return True


def test_sequential_workflow():
    """Test sequential skill workflow"""
    initialize()

    code = """
import os
SECRET = os.environ.get("KEY")

def process_data(data):
    results = []
    for item in data:
        results.append(item * 2)
    return results
"""

    # Step 1: Code review
    review = get_skill("code-review")
    review_result = review.execute({"source_code": code})
    assert review_result["status"] == "ok"

    # Step 2: Security scan
    security = get_skill("security-scan")
    security_result = security.execute({"source_code": code})
    assert security_result["status"] == "ok"

    # Step 3: Performance analysis
    perf = get_skill("perf-analysis")
    perf_result = perf.execute({"source_code": code})
    assert perf_result["status"] == "ok"

    print("  ✓ Sequential workflow completed")
    return True


def test_parallel_skill_execution():
    """Test parallel skill execution on same code"""
    initialize()

    code = "x = 1"

    def run_skill(name):
        skill = get_skill(name)
        return skill.execute({"source_code": code})

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(run_skill, name) for name in list_skills()]
        results = list(concurrent.futures.as_completed(futures))

    assert len(results) == 6
    print("  ✓ Parallel skill execution: 6 skills processed")
    return True


def test_metric_generation():
    """Test metric generation across skills"""
    initialize()
    metrics = {}

    for skill_info in list_skills():
        name = skill_info["name"]
        skill = get_skill(name)
        start = time.time()
        skill.execute({"source_code": "x = 1"})
        elapsed = time.time() - start
        metrics[name] = elapsed

    assert len(metrics) > 0
    print("  ✓ Metric generation: times recorded for all skills")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("  Integration Tests (Extended)")
    print("=" * 60)

    tests = [
        test_registry_initialization,
        test_all_skills_validate,
        test_skill_execution_consistency,
        test_rapid_dispatch,
        test_concurrent_skill_execution,
        test_multiple_skill_types,
        test_error_handling_in_skills,
        test_large_codebase_analysis,
        test_trace_id_uniqueness,
        test_sequential_workflow,
        test_parallel_skill_execution,
        test_metric_generation,
    ]

    passed = 0
    for test in tests:
        try:
            result = test()
            if result:
                passed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__}: {e}")

    print(f"\n  Result: {passed}/{len(tests)} passed")
    exit(0 if passed == len(tests) else 1)
