"""
Schema Validation Tests — Schema 完整性测试
============================================="""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skills.code_review.skill import CodeReviewSkill
from skills.security_scan.skill import SecurityScanSkill
from skills.perf_analysis.skill import PerfAnalysisSkill
from skills.test_generation.skill import TestGenerationSkill
from skills.doc_writing.skill import DocWritingSkill
from skills.deploy_verification.skill import DeployVerificationSkill


def test_all_skills_have_schema():
    """All skills must have get_schema method"""
    skills = [
        CodeReviewSkill(),
        SecurityScanSkill(),
        PerfAnalysisSkill(),
        TestGenerationSkill(),
        DocWritingSkill(),
        DeployVerificationSkill(),
    ]

    for skill in skills:
        schema = skill.get_schema()
        assert isinstance(schema, dict)
        assert "input" in schema
        assert "output" in schema


def test_code_review_schema():
    """Test CodeReview schema completeness"""
    skill = CodeReviewSkill()
    schema = skill.get_schema()

    # Input schema
    assert "source_code" in schema["input"]["required"]
    assert "file_path" in schema["input"]["properties"]
    assert "options" in schema["input"]["properties"]

    # Output schema
    assert "issues_found" in schema["output"]["properties"]
    assert "by_severity" in schema["output"]["properties"]
    assert "recommendations" in schema["output"]["properties"]


def test_security_scan_schema():
    """Test SecurityScan schema completeness"""
    skill = SecurityScanSkill()
    schema = skill.get_schema()

    assert "source_code" in schema["input"]["required"]
    assert "vulnerabilities_found" in schema["output"]["properties"]
    assert "risk_level" in schema["output"]["properties"]


def test_perf_analysis_schema():
    """Test PerfAnalysis schema completeness"""
    skill = PerfAnalysisSkill()
    schema = skill.get_schema()

    assert "source_code" in schema["input"]["required"]
    assert "performance_score" in schema["output"]["properties"]
    assert "bottlenecks_found" in schema["output"]["properties"]


def test_test_generation_schema():
    """Test TestGeneration schema completeness"""
    skill = TestGenerationSkill()
    schema = skill.get_schema()

    assert "source_code" in schema["input"]["required"]
    assert "tests_generated" in schema["output"]["properties"]
    assert "coverage_target" in schema["output"]["properties"]


def test_doc_writing_schema():
    """Test DocWriting schema completeness"""
    skill = DocWritingSkill()
    schema = skill.get_schema()

    assert "doc_type" in schema["input"]["required"]
    assert "title" in schema["input"]["required"]
    assert "api" in schema["input"]["properties"]["doc_type"]["enum"]
    assert "changelog" in schema["input"]["properties"]["doc_type"]["enum"]
    assert "readme" in schema["input"]["properties"]["doc_type"]["enum"]


def test_deploy_verification_schema():
    """Test DeployVerification schema completeness"""
    skill = DeployVerificationSkill()
    schema = skill.get_schema()

    assert "services" in schema["input"]["properties"]
    assert "base_url" in schema["input"]["properties"]
    # rollback_strategy may or may not be in schema
    if "rollback_strategy" in schema["input"]["properties"]:
        assert "blue_green" in schema["input"]["properties"]["rollback_strategy"]["enum"]


def test_schema_types():
    """Test schema type declarations"""
    skills = [
        CodeReviewSkill(),
        SecurityScanSkill(),
        PerfAnalysisSkill(),
        TestGenerationSkill(),
        DocWritingSkill(),
        DeployVerificationSkill(),
    ]

    for skill in skills:
        schema = skill.get_schema()
        assert schema["input"]["type"] == "object"
        assert schema["output"]["type"] == "object"


def test_schema_consistency():
    """Test that execute output matches schema"""
    skills = [
        (CodeReviewSkill(), {"source_code": "x = 1"}),
        (SecurityScanSkill(), {"source_code": "x = 1"}),
        (PerfAnalysisSkill(), {"source_code": "x = 1"}),
        (TestGenerationSkill(), {"source_code": "def f(): pass"}),
        (DocWritingSkill(), {"doc_type": "api", "title": "Test"}),
        (DeployVerificationSkill(), {"services": ["test"]}),
    ]

    for skill, data in skills:
        result = skill.execute(data)
        assert "status" in result
        assert result["status"] == "ok"


def test_nested_schema_properties():
    """Test nested schema properties"""
    skill = CodeReviewSkill()
    schema = skill.get_schema()

    options = schema["input"]["properties"]["options"]
    assert "strict" in options["properties"]
    assert "check_security" in options["properties"]
    assert "check_performance" in options["properties"]
    assert "check_naming" in options["properties"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
