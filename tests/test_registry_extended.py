"""
Registry and Discovery Tests — 注册中心测试
==========================================="""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skills.registry import initialize, get_skill, list_skills, clear_registry


@pytest.fixture(autouse=True)
def setup_registry():
    """Auto-setup registry before each test"""
    clear_registry()
    initialize()
    yield
    clear_registry()


def test_skill_count():
    """Test correct number of skills loaded"""
    skills = list_skills()
    assert len(skills) >= 6


def test_all_expected_skills_present():
    """Test all expected skills are present"""
    skills = list_skills()
    skill_names = {s["name"] for s in skills}
    expected = {
        "code-review",
        "security-scan",
        "perf-analysis",
        "test-generation",
        "doc-writing",
        "deploy-verification",
    }
    assert expected.issubset(skill_names)


def test_skill_names_unique():
    """Test all skill names are unique"""
    skills = list_skills()
    names = [s["name"] for s in skills]
    assert len(names) == len(set(names))


def test_skill_retrieval():
    """Test retrieving skills by name"""
    for skill_info in list_skills():
        name = skill_info["name"]
        skill = get_skill(name)
        assert skill is not None
        assert skill.name == name


def test_get_nonexistent_skill():
    """Test getting non-existent skill raises KeyError"""
    with pytest.raises(KeyError):
        get_skill("nonexistent-skill-name")


def test_skill_attribute_access():
    """Test accessing skill attributes"""
    skill = get_skill("code-review")
    assert hasattr(skill, "name")
    assert hasattr(skill, "version")
    assert hasattr(skill, "description")
    assert hasattr(skill, "execute")
    assert hasattr(skill, "validate_input")
    assert hasattr(skill, "get_schema")


def test_skill_version_format():
    """Test skill versions follow semver-like format"""
    for skill_info in list_skills():
        skill = get_skill(skill_info["name"])
        version = skill.version
        assert isinstance(version, str)
        # Version should have at least one dot
        assert "." in version


def test_skill_description_not_empty():
    """Test all skills have descriptions"""
    for skill_info in list_skills():
        skill = get_skill(skill_info["name"])
        assert len(skill.description) > 0


def test_list_skills_is_sorted():
    """Test that skill list is deterministic"""
    skills1 = list_skills()
    skills2 = list_skills()
    assert skills1 == skills2


def test_registry_isolation():
    """Test that registry state is isolated between calls"""
    skills1 = list_skills()
    clear_registry()
    initialize()
    skills2 = list_skills()
    assert skills1 == skills2


def test_multiple_initialization():
    """Test multiple initialization calls don't break registry"""
    initialize()
    initialize()
    initialize()
    skills = list_skills()
    assert len(skills) >= 6


def test_skill_interface_compliance():
    """Test all skills implement required interface"""
    for skill_info in list_skills():
        name = skill_info["name"]
        skill = get_skill(name)
        # Must be callable
        assert callable(skill.execute)
        assert callable(skill.validate_input)
        assert callable(skill.get_schema)

        # Must return correct types
        schema = skill.get_schema()
        assert isinstance(schema, dict)


def test_skill_execute_returns_dict():
    """Test all skills return dict from execute"""
    test_inputs = [
        ("code-review", {"source_code": "x = 1"}),
        ("security-scan", {"source_code": "x = 1"}),
        ("perf-analysis", {"source_code": "x = 1"}),
        ("test-generation", {"source_code": "def f(): pass"}),
        ("doc-writing", {"doc_type": "api", "title": "Test"}),
        ("deploy-verification", {"services": ["test"]}),
    ]

    for name, data in test_inputs:
        skill = get_skill(name)
        result = skill.execute(data)
        assert isinstance(result, dict), f"{name} did not return dict"
        assert result.get("status") == "ok", f"{name} returned non-ok status"
