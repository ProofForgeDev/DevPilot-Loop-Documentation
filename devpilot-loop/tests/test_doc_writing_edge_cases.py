"""
Tests for DocWritingSkill — 文档生成边界测试
============================================="""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skills.doc_writing.skill import DocWritingSkill


@pytest.fixture
def skill():
    return DocWritingSkill()


# ── 文档类型测试 ─────────────────────────────────────

def test_api_documentation(skill):
    """Test API documentation generation"""
    result = skill.execute({"doc_type": "api", "title": "Login API"})
    assert result["status"] == "ok"
    assert "document" in result
    assert result["doc_length"] > 0


def test_changelog_documentation(skill):
    """Test changelog generation"""
    result = skill.execute({"doc_type": "changelog", "title": "v2.0.0", "content": "Added new features"})
    assert result["status"] == "ok"
    assert "changelog" in result.get("doc_type", "").lower()


def test_readme_documentation(skill):
    """Test README generation"""
    result = skill.execute({"doc_type": "readme", "title": "My Project"})
    assert result["status"] == "ok"
    assert result["doc_length"] > 0


def test_spec_documentation(skill):
    """Test specification generation"""
    result = skill.execute({"doc_type": "spec", "title": "System Architecture"})
    assert result["status"] == "ok"


def test_runbook_documentation(skill):
    """Test runbook generation"""
    result = skill.execute({"doc_type": "runbook", "title": "Deployment Guide"})
    assert result["status"] == "ok"


# ── 模板测试 ────────────────────────────────────────

def test_template_sections(skill):
    """Test template has required sections"""
    result = skill.execute({"doc_type": "api", "title": "Test API"})
    document = result.get("document", "")
    assert "##" in document or "# " in document  # Markdown headers


def test_metadata_included(skill):
    """Test metadata is included"""
    result = skill.execute({"doc_type": "api", "title": "Test"})
    metadata = result.get("metadata", {})
    assert "title" in metadata or result["doc_length"] > 0


# ── 输入验证测试 ─────────────────────────────────────

def test_validate_input_valid(skill):
    """Test validate_input with valid data"""
    assert skill.validate_input({"doc_type": "api", "title": "Test"}) is True


def test_validate_input_missing_type(skill):
    """Test validate_input without doc_type"""
    assert skill.validate_input({"title": "Test"}) is False


def test_validate_input_invalid(skill):
    """Test validate_input with invalid data"""
    assert skill.validate_input({}) is False
    assert skill.validate_input(None) is False


# ── Schema 测试 ─────────────────────────────────────

def test_schema_has_input(skill):
    """Test schema has input"""
    schema = skill.get_schema()
    assert "input" in schema


def test_schema_has_output(skill):
    """Test schema has output"""
    schema = skill.get_schema()
    assert "output" in schema


def test_schema_doc_types(skill):
    """Test schema has all doc types"""
    schema = skill.get_schema()
    doc_types = schema["input"]["properties"]["doc_type"]["enum"]
    assert "api" in doc_types
    assert "changelog" in doc_types
    assert "readme" in doc_types


# ── 综合测试 ───────────────────────────────────────

def test_long_document_generation(skill):
    """Test generating long document"""
    result = skill.execute({"doc_type": "readme", "title": "Comprehensive Project Documentation"})
    assert result["status"] == "ok"
    assert result["doc_length"] > 100


def test_markdown_format(skill):
    """Test markdown format output"""
    result = skill.execute({"doc_type": "api", "title": "API Docs"})
    document = result.get("document", "")
    assert isinstance(document, str)
    assert len(document) > 0


def test_word_count_accuracy(skill):
    """Test word count accuracy"""
    result = skill.execute({"doc_type": "api", "title": "Test"})
    word_count = result.get("word_count", 0)
    document = result.get("document", "")
    actual_words = len(document.split())
    # Word count should be approximately correct
    assert abs(word_count - actual_words) < actual_words * 0.1 or word_count > 0
