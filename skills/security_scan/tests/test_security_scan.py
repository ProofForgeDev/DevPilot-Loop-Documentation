import pytest
"""Tests for SecurityScanSkill"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from skills.security_scan.skill import SecurityScanSkill


@pytest.fixture
def skill():
    return SecurityScanSkill()


def test_idempotent(skill):
    assert skill.name == "security-scan"
    assert skill.version == "2.0.0"


def test_finds_hardcoded_secret(skill):
    code = 'SECRET_KEY = "my-secret-key-12345"'
    result = skill.execute({"source_code": code})
    assert result["vulnerabilities_found"] >= 1
    assert any(v["severity"] == "HIGH" for v in result["vulnerabilities"])


def test_clean_code(skill):
    code = 'SECRET_KEY = os.environ.get("SECRET_KEY")\nprint("hello")'
    result = skill.execute({"source_code": code})
    # Should not flag env var usage
    assert result["status"] == "ok"


def test_validate_input(skill):
    assert skill.validate_input({"source_code": "x"}) is True
    assert skill.validate_input({}) is False


def test_get_schema(skill):
    schema = skill.get_schema()
    assert schema["input"]["required"] == ["source_code"]
