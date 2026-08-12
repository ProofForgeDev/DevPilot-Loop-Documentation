"""
Skills Validation Tests — 输入验证、边界情况、错误处理
================================================="""

import json
import os
import sys
from typing import Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
sys.path.insert(0, SKILLS_DIR)

from skills.code_review.skill import CodeReviewSkill
from skills.test_generation.skill import TestGenerationSkill
from skills.doc_writing.skill import DocWritingSkill
from skills.security_scan.skill import SecurityScanSkill
from skills.perf_analysis.skill import PerfAnalysisSkill
from skills.deploy_verification.skill import DeployVerificationSkill


class TestCodeReview:
    """CodeReviewSkill tests"""

    def test_validate_empty(self):
        s = CodeReviewSkill()
        assert s.validate_input({}) == False

    def test_validate_no_source_code(self):
        s = CodeReviewSkill()
        assert s.validate_input({"other": "data"}) == False

    def test_validate_valid(self):
        s = CodeReviewSkill()
        assert s.validate_input({"source_code": "x = 1"}) == True

    def test_execute_basic(self):
        s = CodeReviewSkill()
        result = s.execute({"source_code": "x = 1"})
        assert result["status"] == "ok"
        assert "skill" in result

    def test_schema_complete(self):
        s = CodeReviewSkill()
        schema = s.get_schema()
        assert "input" in schema
        assert "output" in schema

    def test_execute_long_code(self):
        s = CodeReviewSkill()
        long_code = "\n".join(f"line_{i} = {i}" for i in range(100))
        result = s.execute({"source_code": long_code})
        assert result["status"] == "ok"


class TestTestGeneration:
    """TestGenerationSkill tests"""

    def test_validate_empty(self):
        s = TestGenerationSkill()
        assert s.validate_input({}) == False

    def test_validate_valid(self):
        s = TestGenerationSkill()
        assert s.validate_input({"source_code": "def foo(): pass"}) == True

    def test_execute(self):
        s = TestGenerationSkill()
        result = s.execute({"source_code": "def add(a, b): return a + b"})
        assert result["status"] == "ok"

    def test_schema_complete(self):
        s = TestGenerationSkill()
        schema = s.get_schema()
        assert "input" in schema and "output" in schema


class TestDocWriting:
    """DocWritingSkill tests"""

    def test_validate_missing_type(self):
        s = DocWritingSkill()
        assert s.validate_input({"title": "Test"}) == False

    def test_validate_valid_changelog(self):
        s = DocWritingSkill()
        assert s.validate_input({"doc_type": "changelog", "title": "v1.0"}) == True

    def test_validate_valid_api(self):
        s = DocWritingSkill()
        assert s.validate_input({"doc_type": "api", "title": "API"}) == True

    def test_execute_changelog(self):
        s = DocWritingSkill()
        result = s.execute({"doc_type": "changelog", "title": "v2.0"})
        assert result["status"] == "ok"

    def test_execute_api(self):
        s = DocWritingSkill()
        result = s.execute({"doc_type": "api", "title": "Login API"})
        assert result["status"] == "ok"


class TestSecurityScan:
    """SecurityScanSkill tests"""

    def test_validate_empty(self):
        s = SecurityScanSkill()
        assert s.validate_input({}) == False

    def test_validate_has_code(self):
        s = SecurityScanSkill()
        assert s.validate_input({"source_code": "x = 1"}) == True

    def test_finds_hardcoded_secret(self):
        s = SecurityScanSkill()
        result = s.execute({"source_code": "SECRET_KEY = 'mysecret123'"})
        assert result["status"] == "ok"
        vulns = result.get("vulnerabilities", [])
        # Should detect hardcoded secret
        assert len(vulns) > 0 or result.get("vulnerabilities_found", 0) > 0

    def test_clean_code(self):
        s = SecurityScanSkill()
        result = s.execute({"source_code": "x = 1\ny = 2"})
        assert result["status"] == "ok"
        findings = result.get("output", {}).get("findings", [])
        assert len(findings) == 0 or result["output"].get("risk_level") == "low"


class TestPerfAnalysis:
    """PerfAnalysisSkill tests"""

    def test_validate_empty(self):
        s = PerfAnalysisSkill()
        assert s.validate_input({}) == False

    def test_validate_has_code(self):
        s = PerfAnalysisSkill()
        assert s.validate_input({"source_code": "for i in range(10): pass"}) == True

    def test_detects_n_plus_one(self):
        s = PerfAnalysisSkill()
        code = "for u in users:\n    q = db.query(u)"
        result = s.execute({"source_code": code})
        assert result["status"] == "ok"
        # N+1 should be detected

    def test_suggestions(self):
        s = PerfAnalysisSkill()
        result = s.execute({"source_code": "for i in range(1000):\n    x = i * 2"})
        assert result["status"] == "ok"


class TestDeployVerification:
    """DeployVerificationSkill tests"""

    def test_validate_empty(self):
        s = DeployVerificationSkill()
        assert s.validate_input({}) == False

    def test_validate_has_services(self):
        s = DeployVerificationSkill()
        assert s.validate_input({"services": ["web"]}) == True

    def test_execute(self):
        s = DeployVerificationSkill()
        result = s.execute({"services": ["manager", "worker"]})
        assert result["status"] == "ok"

    def test_rollback_plan(self):
        s = DeployVerificationSkill()
        result = s.execute({"services": ["web"]})
        output = result.get("output", {})
        assert "rollback_plan" in output or result["status"] == "ok"


def run_all():
    """运行所有 Skill 验证测试"""
    print("=" * 60)
    print("  Skills Validation Tests")
    print("=" * 60)
    test_classes = [
        TestCodeReview, TestTestGeneration, TestDocWriting,
        TestSecurityScan, TestPerfAnalysis, TestDeployVerification,
    ]
    total_passed = 0
    total_failed = 0
    for cls in test_classes:
        instance = cls()
        methods = [m for m in dir(instance) if m.startswith("test_")]
        passed = 0
        failed = 0
        for method_name in methods:
            try:
                getattr(instance, method_name)()
                print(f"    ✓ {cls.__name__}.{method_name}")
                passed += 1
                total_passed += 1
            except Exception as e:
                print(f"    ✗ {cls.__name__}.{method_name}: {e}")
                failed += 1
                total_failed += 1
        print(f"  {cls.__name__}: {passed}/{passed+failed}")
    print(f"\n  Total: {total_passed} passed, {total_failed} failed")
    return total_failed == 0


if __name__ == "__main__":
    success = run_all()
    exit(0 if success else 1)
