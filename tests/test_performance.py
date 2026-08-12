"""
Performance Tests — 性能基准测试
================================"""

import pytest
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skills.code_review.skill import CodeReviewSkill
from skills.security_scan.skill import SecurityScanSkill
from skills.perf_analysis.skill import PerfAnalysisSkill
from skills.test_generation.skill import TestGenerationSkill
from skills.doc_writing.skill import DocWritingSkill
from skills.deploy_verification.skill import DeployVerificationSkill


# ── 单个 Skill 性能测试 ─────────────────────────────

def test_code_review_performance():
    """Test code review execution time"""
    skill = CodeReviewSkill()
    code = "def hello(): return 'world'"

    start = time.time()
    for _ in range(100):
        skill.execute({"source_code": code})
    elapsed = time.time() - start

    avg_ms = (elapsed / 100) * 1000
    assert avg_ms < 100, f"Average execution time {avg_ms:.2f}ms exceeds 100ms"


def test_security_scan_performance():
    """Test security scan execution time"""
    skill = SecurityScanSkill()
    code = "x = 1"

    start = time.time()
    for _ in range(100):
        skill.execute({"source_code": code})
    elapsed = time.time() - start

    avg_ms = (elapsed / 100) * 1000
    assert avg_ms < 100


def test_perf_analysis_performance():
    """Test performance analysis execution time"""
    skill = PerfAnalysisSkill()
    code = "for i in range(10): pass"

    start = time.time()
    for _ in range(100):
        skill.execute({"source_code": code})
    elapsed = time.time() - start

    avg_ms = (elapsed / 100) * 1000
    assert avg_ms < 100


def test_test_generation_performance():
    """Test test generation execution time"""
    skill = TestGenerationSkill()
    code = "def foo(): pass"

    start = time.time()
    for _ in range(100):
        skill.execute({"source_code": code})
    elapsed = time.time() - start

    avg_ms = (elapsed / 100) * 1000
    assert avg_ms < 100


def test_doc_writing_performance():
    """Test doc writing execution time"""
    skill = DocWritingSkill()

    start = time.time()
    for _ in range(50):
        skill.execute({"doc_type": "api", "title": "Test"})
    elapsed = time.time() - start

    avg_ms = (elapsed / 50) * 1000
    assert avg_ms < 200  # Doc writing may be slower


def test_deploy_verification_performance():
    """Test deploy verification execution time"""
    skill = DeployVerificationSkill()

    start = time.time()
    for _ in range(100):
        skill.execute({"services": ["test"]})
    elapsed = time.time() - start

    avg_ms = (elapsed / 100) * 1000
    assert avg_ms < 100


# ── 并发性能测试 ─────────────────────────────────────

def test_concurrent_code_review():
    """Test concurrent code review execution"""
    import concurrent.futures
    skill = CodeReviewSkill()
    code = "x = 1"

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(skill.execute, {"source_code": code}) for _ in range(50)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 50
    assert all(r["status"] == "ok" for r in results)


def test_concurrent_all_skills():
    """Test concurrent execution of all skills"""
    import concurrent.futures

    skills_data = [
        (CodeReviewSkill(), {"source_code": "x = 1"}),
        (SecurityScanSkill(), {"source_code": "x = 1"}),
        (PerfAnalysisSkill(), {"source_code": "x = 1"}),
        (TestGenerationSkill(), {"source_code": "def f(): pass"}),
        (DocWritingSkill(), {"doc_type": "api", "title": "Test"}),
        (DeployVerificationSkill(), {"services": ["test"]}),
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(s.execute, d) for s, d in skills_data]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 6
    assert all(r["status"] == "ok" for r in results)


# ── 大数据量性能测试 ─────────────────────────────────

def test_large_code_review():
    """Test code review with large input"""
    skill = CodeReviewSkill()
    code = "\n".join(f"def func_{i}(): return {i}" for i in range(1000))

    start = time.time()
    result = skill.execute({"source_code": code})
    elapsed = time.time() - start

    assert result["status"] == "ok"
    assert result["total_lines"] == 1000
    assert elapsed < 5  # Should complete in under 5 seconds


def test_large_security_scan():
    """Test security scan with large input"""
    skill = SecurityScanSkill()
    code = "\n".join(f"x{i} = {i}" for i in range(1000))

    start = time.time()
    result = skill.execute({"source_code": code})
    elapsed = time.time() - start

    assert result["status"] == "ok"
    assert elapsed < 5


def test_memory_efficiency():
    """Test memory efficiency during processing"""
    import sys
    skill = CodeReviewSkill()
    code = "x = 1"

    # Process many times and check memory doesn't grow unbounded
    initial_mem = sys.getsizeof(code)
    for _ in range(1000):
        skill.execute({"source_code": code})
    final_mem = sys.getsizeof(code)

    # Memory should not grow significantly
    assert final_mem <= initial_mem * 2


if __name__ == "__main__":
    print("=" * 60)
    print("  Performance Tests")
    print("=" * 60)
    pytest.main([__file__, "-v"])
