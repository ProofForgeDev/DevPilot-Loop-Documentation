import pytest
"""Tests for TestGenerationSkill"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from skills.test_generation.skill import TestGenerationSkill


@pytest.fixture
def skill():
    return TestGenerationSkill()


def test_idempotent(skill):
    assert skill.name == "test-generation"
    assert skill.version == "2.0.0"


def test_execute_generates_tests(skill):
    code = "def login_user(): pass\nclass AuthHandler: pass"
    result = skill.execute({"source_code": code, "file_path": "app.py"})
    assert result["status"] == "ok"
    assert result["tests_generated"] >= 1


def test_validate_input(skill):
    assert skill.validate_input({"source_code": "x"}) is True
    assert skill.validate_input({}) is False


def test_get_schema(skill):
    schema = skill.get_schema()
    assert "unit" in schema["input"]["properties"]["test_type"]["enum"]
