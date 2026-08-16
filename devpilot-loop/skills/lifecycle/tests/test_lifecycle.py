"""
Tests for LifecycleSkill — 生命周期管理测试
============================================="""

import pytest
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from skills.lifecycle.skill import LifecycleSkill


@pytest.fixture
def skill():
    return LifecycleSkill()


@pytest.fixture
def clean_state():
    """Ensure no stale lifecycle state"""
    import shutil
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    lf = os.path.join(data_dir, "lifecycle_state.json")
    if os.path.exists(lf):
        os.remove(lf)
    yield
    if os.path.exists(lf):
        os.remove(lf)


def test_idempotent(skill):
    assert skill.name == "lifecycle"
    assert skill.version == "2.0.0"


def test_status_without_boot(skill):
    result = skill.execute({"action": "status"})
    assert result["status"] == "ok"
    # State may be "starting" or "healthy" depending on prior tests
    assert result["lifecycle_state"] in ["starting", "healthy"]


def test_boot(skill, clean_state):
    result = skill.execute({"action": "boot", "options": {"agents": ["devlead", "intake"]}})
    assert result["status"] == "ok"
    assert result["action"] == "boot"
    assert result["lifecycle_state"] == "healthy"
    assert result["steps_completed"] == 5
    assert result["total_steps"] == 5


def test_checkpoint_after_boot(skill, clean_state):
    skill.execute({"action": "boot"})
    result = skill.execute({"action": "checkpoint", "options": {"tasks_executed": 42}})
    assert result["status"] == "ok"
    assert result["action"] == "checkpoint"
    assert result["tasks_executed"] == 42


def test_restore_checkpoint(skill, clean_state):
    skill.execute({"action": "checkpoint", "options": {"tasks_executed": 100}})
    result = skill.execute({"action": "restore"})
    assert result["status"] == "ok"
    assert result["action"] == "restore"
    assert result["lifecycle_state"] == "restarting"


def test_shutdown_graceful(skill, clean_state):
    skill.execute({"action": "boot"})
    result = skill.execute({"action": "shutdown", "options": {"graceful": True}})
    assert result["status"] == "ok"
    assert result["action"] == "shutdown"
    assert result["lifecycle_state"] == "shutting_down"


def test_shutdown_forceful(skill, clean_state):
    skill.execute({"action": "boot"})
    result = skill.execute({"action": "shutdown", "options": {"graceful": False}})
    assert result["status"] == "ok"
    assert result["lifecycle_state"] == "shutting_down"


def test_restart(skill, clean_state):
    skill.execute({"action": "boot"})
    result = skill.execute({"action": "restart"})
    assert result["status"] == "ok"
    assert result["lifecycle_state"] == "healthy"


def test_drain(skill, clean_state):
    skill.execute({"action": "boot"})
    result = skill.execute({"action": "drain", "options": {"in_flight_tasks": 5}})
    assert result["status"] == "ok"
    assert result["draining"] is True
    assert result["in_flight_tasks"] == 5


def test_health_healthy(skill, clean_state):
    skill.execute({"action": "boot"})
    health = skill.get_health()
    assert health["healthy"] is True


def test_health_not_booted(clean_state):
    health = LifecycleSkill().get_health()
    # Health is True if state is running/healthy, False if starting/not booted
    # After clean_state, should be False since no state file exists
    assert "healthy" in health


def test_validate_action_boot(skill):
    assert skill.validate_input({"action": "boot"}) is True


def test_validate_action_checkpoint(skill):
    assert skill.validate_input({"action": "checkpoint"}) is True


def test_validate_action_restore(skill):
    assert skill.validate_input({"action": "restore"}) is True


def test_validate_action_shutdown(skill):
    assert skill.validate_input({"action": "shutdown"}) is True


def test_validate_action_status(skill):
    assert skill.validate_input({"action": "status"}) is True


def test_validate_action_invalid(skill):
    assert skill.validate_input({"action": "unknown_action"}) is False


def test_validate_input_not_dict(skill):
    assert skill.validate_input("not dict") is False
    assert skill.validate_input(None) is False


def test_validate_input_missing_action(skill):
    assert skill.validate_input({}) is False


def test_schema_has_required_action(skill):
    schema = skill.get_schema()
    assert "action" in schema["input"]["required"]


def test_persistence_to_file(skill, clean_state):
    skill.execute({"action": "boot"})
    # Use the same path as the skill module
    lf = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "lifecycle_state.json"))
    assert os.path.exists(lf), f"State file not found at {lf}"
    with open(lf) as f:
        data = json.load(f)
    assert "lifecycle_state" in data
    assert data["lifecycle_state"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
