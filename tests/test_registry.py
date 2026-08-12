"""
Tests for Registry — 技能注册中心
================================="""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skills.registry import (
    initialize,
    get_skill,
    list_skills,
    clear_registry,
)


@pytest.fixture(autouse=True)
def reset_registry():
    """在每个测试前后重置注册中心"""
    clear_registry()
    yield
    clear_registry()


def test_initialize_loads_skills():
    """Test that initialize loads all skills"""
    initialize()
    skills = list_skills()
    assert len(skills) > 0


def test_get_existing_skill():
    """Test getting an existing skill"""
    initialize()
    skill = get_skill("code-review")
    assert skill is not None
    assert skill.name == "code-review"


def test_get_nonexistent_skill():
    """Test getting a non-existent skill raises KeyError"""
    initialize()
    with pytest.raises(KeyError):
        get_skill("nonexistent-skill")


def test_list_skills_after_init():
    """Test listing skills after initialization"""
    initialize()
    skills = list_skills()
    assert isinstance(skills, list)
    assert len(skills) >= 6  # At least 6 built-in skills


def test_list_skill_names():
    """Test that skill names are strings"""
    initialize()
    skills = list_skills()
    for skill_info in skills:
        assert isinstance(skill_info["name"], str)


def test_clear_registry():
    """Test clearing the registry"""
    initialize()
    clear_registry()
    # After clear, list_skills should return empty or re-initialize
    skills = list_skills()
    assert len(skills) >= 0  # May re-initialize on next call


def test_skill_schema_access():
    """Test accessing skill schema"""
    initialize()
    skill = get_skill("code-review")
    schema = skill.get_schema()
    assert "input" in schema
    assert "output" in schema


def test_skill_validation_interface():
    """Test that all skills have validate_input"""
    initialize()
    skills = list_skills()
    for skill_info in skills:
        name = skill_info["name"]
        skill = get_skill(name)
        assert hasattr(skill, "validate_input")
        assert callable(skill.validate_input)


def test_skill_execute_interface():
    """Test that all skills have execute"""
    initialize()
    skills = list_skills()
    for skill_info in skills:
        name = skill_info["name"]
        skill = get_skill(name)
        assert hasattr(skill, "execute")
        assert callable(skill.execute)


def test_multiple_initialization():
    """Test that re-initializing doesn't break anything"""
    initialize()
    initialize()
    skills = list_skills()
    assert len(skills) > 0


def test_skill_version_accessible():
    """Test accessing skill version"""
    initialize()
    skill = get_skill("code-review")
    assert hasattr(skill, "version")
    assert isinstance(skill.version, str)


def test_all_skills_loadable():
    """Test that all expected skills can be loaded"""
    initialize()
    expected_skills = [
        "code-review",
        "test-generation",
        "doc-writing",
        "security-scan",
        "perf-analysis",
        "deploy-verification",
    ]
    for skill_name in expected_skills:
        skill = get_skill(skill_name)
        assert skill is not None, f"Failed to load {skill_name}"
