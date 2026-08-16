"""
Tests for BaseSkill — 基类功能验证
=================================="""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skills.base import BaseSkill


class MockSkill(BaseSkill):
    """用于测试的模拟 Skill"""
    name = "local"
    version = "1.0.0"
    description = "Test skill for testing"

    def execute(self, input_data: dict) -> dict:
        return {"status": "ok", "output": input_data}

    def validate_input(self, input_data: dict) -> bool:
        return isinstance(input_data, dict) and "test" in input_data

    def get_schema(self) -> dict:
        return {
            "input": {"required": ["test"]},
            "output": {"properties": {"status": {"type": "string"}}}
        }


def test_base_class_repr():
    """Test __repr__"""
    s = MockSkill()
    assert "MockSkill" in repr(s)
    assert "v1.0.0" in repr(s)


def test_base_class_stats():
    """Test get_stats()"""
    s = MockSkill()
    stats = s.get_stats()
    assert stats["name"] == "local"
    assert stats["version"] == "1.0.0"
    assert stats["call_count"] == 0


def test_execute_with_retry():
    """Test retry mechanism"""
    s = MockSkill()
    result = s.execute_with_retry({"test": "data"})
    assert result["status"] == "ok"
    assert "metrics" in result
    assert "execution_time_seconds" in result["metrics"]


def test_validate_input_valid():
    """Test validate_input with valid data"""
    s = MockSkill()
    assert s.validate_input({"test": "value"}) is True


def test_validate_input_invalid():
    """Test validate_input with invalid data"""
    s = MockSkill()
    assert s.validate_input({}) is False
    assert s.validate_input(None) is False
    assert s.validate_input("string") is False


def test_validate_input_missing_key():
    """Test validate_input with missing required key"""
    s = MockSkill()
    assert s.validate_input({"wrong_key": "value"}) is False


def test_schema_structure():
    """Test get_schema() returns correct structure"""
    s = MockSkill()
    schema = s.get_schema()
    assert "input" in schema
    assert "output" in schema
    assert schema["input"]["required"] == ["test"]


def test_call_count_increases():
    """Test that call count increases after execution"""
    s = MockSkill()
    s.execute_with_retry({"test": "data"})
    s.execute_with_retry({"test": "data"})
    stats = s.get_stats()
    assert stats["call_count"] == 2


def test_last_result_stored():
    """Test that last result is stored"""
    s = MockSkill()
    result = s.execute_with_retry({"test": "data"})
    stats = s.get_stats()
    assert stats["last_result"] == result


def test_version_attribute():
    """Test version class attribute"""
    s = MockSkill()
    assert s.version == "1.0.0"


def test_name_attribute():
    """Test name class attribute"""
    s = MockSkill()
    assert s.name == "local"


def test_description_attribute():
    """Test description class attribute"""
    s = MockSkill()
    assert "Test skill" in s.description
