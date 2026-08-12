"""
Base Skill Class Tests — 扩展基类测试
====================================="""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skills.base import BaseSkill


class TestableSkill(BaseSkill):
    """Testable implementation of BaseSkill"""
    name = "testable"
    version = "2.0.0"
    description = "Test skill"
    max_retries = 2

    def execute(self, input_data: dict) -> dict:
        if input_data.get("fail"):
            raise ValueError("Intentional failure")
        return {"status": "ok", "data": input_data}

    def validate_input(self, input_data: dict) -> bool:
        return isinstance(input_data, dict)

    def get_schema(self) -> dict:
        return {"input": {}, "output": {}}


def test_retry_mechanism():
    """Test retry on failure"""
    skill = TestableSkill()
    # Should succeed on second attempt after exponential backoff
    result = skill.execute({"fail": False})
    assert result["status"] == "ok"


def test_retry_with_transient_failure():
    """Test retry handles transient failures"""
    call_count = 0

    class FlakySkill(BaseSkill):
        name = "flaky"
        version = "1.0.0"

        def execute(self, input_data: dict) -> dict:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Transient error")
            return {"status": "ok"}

        def validate_input(self, input_data: dict) -> bool:
            return True

        def get_schema(self) -> dict:
            return {"input": {}, "output": {}}

    skill = FlakySkill()
    result = skill.execute_with_retry({})
    assert result["status"] == "ok"
    assert call_count == 2


def test_retry_exhaustion():
    """Test retry exhaustion raises error"""
    call_count = 0

    class AlwaysFailSkill(BaseSkill):
        name = "always-fail"
        version = "1.0.0"
        max_retries = 1

        def execute(self, input_data: dict) -> dict:
            nonlocal call_count
            call_count += 1
            raise RuntimeError("Permanent failure")

        def validate_input(self, input_data: dict) -> bool:
            return True

        def get_schema(self) -> dict:
            return {"input": {}, "output": {}}

    skill = AlwaysFailSkill()
    with pytest.raises(RuntimeError):
        skill.execute_with_retry({})
    assert call_count == 1


def test_skill_stats():
    """Test skill statistics tracking"""
    skill = TestableSkill()

    skill.execute_with_retry({})
    skill.execute_with_retry({})

    stats = skill.get_stats()
    assert stats["call_count"] == 2
    assert stats["name"] == "testable"
    assert stats["last_result"] is not None


def test_skill_repr():
    """Test skill string representation"""
    skill = TestableSkill()
    rep = repr(skill)
    assert "TestableSkill" in rep
    assert "testable" in rep


def test_base_class_attributes():
    """Test base class default attributes"""
    class DefaultSkill(BaseSkill):
        name = "default"
        version = "0.1.0"

        def execute(self, input_data: dict) -> dict:
            return {}

        def validate_input(self, input_data: dict) -> bool:
            return True

        def get_schema(self) -> dict:
            return {"input": {}, "output": {}}

    skill = DefaultSkill()
    assert skill.max_retries == 3
    assert skill.timeout_seconds == 300
