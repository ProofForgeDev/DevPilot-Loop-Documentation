import pytest
"""Tests for DeployVerificationSkill"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from skills.deploy_verification.skill import DeployVerificationSkill


@pytest.fixture
def skill():
    return DeployVerificationSkill()


def test_idempotent(skill):
    assert skill.name == "deploy-verification"
    assert skill.version == "1.0.0"


def test_execute_without_url(skill):
    result = skill.execute({"services": ["manager", "worker-intake"]})
    assert result["status"] == "ok"
    assert result["overall_status"] == "NEEDS_CHECK"


def test_rollback_plan(skill):
    result = skill.execute({"services": ["a"]})
    assert "rollback_plan" in result
    assert result["rollback_plan"]["strategy"] == "blue_green"


def test_validate_input(skill):
    assert skill.validate_input({"base_url": "http://localhost:8008"}) is True
    assert skill.validate_input({"services": ["a"]}) is True
    assert skill.validate_input({}) is False


def test_get_schema(skill):
    schema = skill.get_schema()
    assert "blue_green" in schema["input"]["properties"]["rollback_strategy"]["enum"]
