import pytest
"""Tests for DocWritingSkill"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from skills.doc_writing.skill import DocWritingSkill


@pytest.fixture
def skill():
    return DocWritingSkill()


def test_idempotent(skill):
    assert skill.name == "doc-writing"
    assert skill.version == "2.0.0"


def test_execute_changelog(skill):
    result = skill.execute({"doc_type": "changelog", "title": "v1.0", "content": "fix bug"})
    assert result["status"] == "ok"
    assert "changelog" in result["doc_type"]
    assert result["doc_length"] > 0


def test_execute_api(skill):
    result = skill.execute({"doc_type": "api", "title": "API Docs"})
    assert result["status"] == "ok"
    assert "API Documentation" in result["document"]


def test_validate_input(skill):
    assert skill.validate_input({"doc_type": "api", "title": "x"}) is True
    assert skill.validate_input({}) is False


def test_get_schema(skill):
    schema = skill.get_schema()
    assert "api" in schema["input"]["properties"]["doc_type"]["enum"]
