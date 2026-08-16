import pytest
"""Tests for PerfAnalysisSkill"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from skills.perf_analysis.skill import PerfAnalysisSkill


@pytest.fixture
def skill():
    return PerfAnalysisSkill()


def test_idempotent(skill):
    assert skill.name == "perf-analysis"
    assert skill.version == "2.0.0"


def test_detects_n_plus_one(skill):
    code = """
for user in users:
    query = User.objects.get(id=user.id)
"""
    result = skill.execute({"source_code": code})
    assert result["bottlenecks_found"] >= 1
    assert any(b["type"] == "n_plus_one" for b in result["bottlenecks"])


def test_suggestions(skill):
    code = "for u in users:\n    db.query(u)"
    result = skill.execute({"source_code": code})
    assert isinstance(result["suggestions"], list)
    assert len(result["suggestions"]) >= 1


def test_validate_input(skill):
    assert skill.validate_input({"source_code": "x"}) is True
    assert skill.validate_input({}) is False


def test_get_schema(skill):
    schema = skill.get_schema()
    assert "bottlenecks_found" in schema["output"]["properties"]
