"""Tests for CodeReviewSkill"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from skills.code_review.skill import CodeReviewSkill


@pytest.fixture
def skill():
    return CodeReviewSkill()


def test_idempotent(skill):
    assert skill.name == "code-review"
    assert skill.version == "1.0.0"
    assert "代码审查" in skill.description


def test_execute_basic(skill):
    result = skill.execute({"source_code": "print('hello')"})
    assert result["status"] == "ok"
    assert result["skill"] == "code-review"
    assert isinstance(result["issues"], list)


def test_execute_finds_issues(skill):
    code = """
def login():
    SECRET_KEY = "hardcoded-secret"
    x = request.get_json()
    if debug=True:
        pass
"""
    result = skill.execute({"source_code": code, "file_path": "test.py"})
    assert result["issues_found"] >= 1
    assert result["status"] == "ok"


def test_validate_input(skill):
    assert skill.validate_input({"source_code": "x=1"}) is True
    assert skill.validate_input("not a dict") is False
    assert skill.validate_input({}) is False


def test_get_schema(skill):
    schema = skill.get_schema()
    assert "input" in schema
    assert "output" in schema
    assert schema["input"]["required"] == ["source_code"]
