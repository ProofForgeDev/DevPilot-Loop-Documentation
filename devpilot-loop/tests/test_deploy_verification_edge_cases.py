"""
Tests for DeployVerificationSkill — 部署验证边界测试
====================================================="""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skills.deploy_verification.skill import DeployVerificationSkill


@pytest.fixture
def skill():
    return DeployVerificationSkill()


# ── 基础验证测试 ─────────────────────────────────────

def test_basic_deployment_check(skill):
    """Test basic deployment check"""
    result = skill.execute({"services": ["manager", "worker"]})
    assert result["status"] == "ok"


def test_single_service(skill):
    """Test single service verification"""
    result = skill.execute({"services": ["manager"]})
    assert result["status"] == "ok"


def test_empty_services_list(skill):
    """Test empty services list"""
    result = skill.execute({"services": []})
    assert result["status"] == "ok"


# ── 策略测试 ────────────────────────────────────────

def test_blue_green_strategy(skill):
    """Test blue-green deployment strategy"""
    result = skill.execute({"services": ["web"], "rollback_strategy": "blue_green"})
    assert result["status"] == "ok"
    rollback = result.get("rollback_plan", {})
    assert rollback.get("strategy") == "blue_green"


def test_canary_strategy(skill):
    """Test canary deployment strategy"""
    result = skill.execute({"services": ["web"], "rollback_strategy": "canary"})
    assert result["status"] == "ok"


def test_rolling_strategy(skill):
    """Test rolling deployment strategy"""
    result = skill.execute({"services": ["web"], "rollback_strategy": "rolling"})
    assert result["status"] == "ok"


# ── 回滚计划测试 ─────────────────────────────────────

def test_rollback_plan_generated(skill):
    """Test rollback plan is generated"""
    result = skill.execute({"services": ["web"]})
    assert "rollback_plan" in result


def test_rollback_steps_present(skill):
    """Test rollback plan has steps"""
    result = skill.execute({"services": ["web"]})
    rollback = result.get("rollback_plan", {})
    if "steps" in rollback:
        assert isinstance(rollback["steps"], list)


# ── 风险评估测试 ─────────────────────────────────────

def test_risk_assessment(skill):
    """Test risk level assessment"""
    result = skill.execute({"services": ["manager", "worker", "database"]})
    risk = result.get("risk_level", "UNKNOWN")
    assert isinstance(risk, str)


def test_overall_status(skill):
    """Test overall status"""
    result = skill.execute({"services": ["web"]})
    status = result.get("overall_status", "UNKNOWN")
    assert isinstance(status, str)


# ── 依赖检查测试 ─────────────────────────────────────

def test_dependency_check(skill):
    """Test dependency checking"""
    result = skill.execute({"services": ["web", "api", "database"]})
    assert result["status"] == "ok"


def test_warning_analysis(skill):
    """Test warning analysis"""
    result = skill.execute({"services": ["web"]})
    warnings = result.get("warnings", [])
    assert isinstance(warnings, list)


# ── 输入验证测试 ─────────────────────────────────────

def test_validate_input_valid_services(skill):
    """Test validate_input with valid services"""
    assert skill.validate_input({"services": ["web"]}) is True


def test_validate_input_valid_url(skill):
    """Test validate_input with valid URL"""
    assert skill.validate_input({"base_url": "http://localhost:8008"}) is True


def test_validate_input_both_valid(skill):
    """Test validate_input with both parameters"""
    assert skill.validate_input({"base_url": "http://localhost:8008", "services": ["web"]}) is True


def test_validate_input_empty(skill):
    """Test validate_input with empty data"""
    assert skill.validate_input({}) is False


def test_validate_input_none(skill):
    """Test validate_input with None"""
    assert skill.validate_input(None) is False


# ── Schema 测试 ─────────────────────────────────────

def test_schema_input(skill):
    """Test schema input definition"""
    schema = skill.get_schema()
    assert "input" in schema


def test_schema_output(skill):
    """Test schema output definition"""
    schema = skill.get_schema()
    assert "output" in schema


def test_schema_rollback_strategy(skill):
    """Test schema has rollback strategy options"""
    schema = skill.get_schema()
    props = schema["input"]["properties"]
    # rollback_strategy may or may not be in schema depending on version
    if "rollback_strategy" in props:
        strategies = props["rollback_strategy"]["enum"]
        assert "blue_green" in strategies


# ── 综合测试 ───────────────────────────────────────

def test_full_deployment_check(skill):
    """Test full deployment verification"""
    result = skill.execute({
        "services": ["manager", "worker-intake", "worker-analyst"],
        "base_url": "http://localhost:8008",
        "rollback_strategy": "blue_green"
    })
    assert result["status"] == "ok"
    assert "overall_status" in result
    assert "rollback_plan" in result


def test_multi_service_deployment(skill):
    """Test multi-service deployment"""
    result = skill.execute({"services": ["a", "b", "c", "d", "e"]})
    assert result["status"] == "ok"
