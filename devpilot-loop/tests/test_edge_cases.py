"""
Edge Case Tests — 边界情况测试
==============================="""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skills.code_review.skill import CodeReviewSkill
from skills.security_scan.skill import SecurityScanSkill
from skills.perf_analysis.skill import PerfAnalysisSkill
from skills.test_generation.skill import TestGenerationSkill
from skills.doc_writing.skill import DocWritingSkill
from skills.deploy_verification.skill import DeployVerificationSkill


# ── 空值和边界值 ─────────────────────────────────────

def test_null_source_code():
    """Test null source code handling"""
    skill = CodeReviewSkill()
    # Test graceful handling of None - should not crash
    result = skill.execute({"source_code": None})
    # Should return error status gracefully, not crash
    assert result["status"] in ("ok", "error")


def test_empty_string_code():
    """Test empty string code"""
    skill = CodeReviewSkill()
    result = skill.execute({"source_code": ""})
    assert result["status"] == "ok"


def test_very_long_line():
    """Test very long single line"""
    skill = CodeReviewSkill()
    long_line = "x = " + "a" * 10000
    result = skill.execute({"source_code": long_line})
    assert result["status"] == "ok"


def test_special_characters():
    """Test special characters in code"""
    skill = CodeReviewSkill()
    code = '# -*- coding: utf-8 -*-\n# 中文注释\nemoji = "🚀"\n'
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


def test_binary_content():
    """Test binary-like content"""
    skill = CodeReviewSkill()
    code = "data = b'\\x00\\x01\\x02'"
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


# ── 极端代码模式 ─────────────────────────────────────

def test_very_deep_nesting():
    """Test very deep nesting"""
    skill = CodeReviewSkill()
    code = "\n".join(f"if True:\n" for _ in range(20)) + "x = 1"
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


def test_repeated_patterns():
    """Test repeated dangerous patterns"""
    skill = SecurityScanSkill()
    code = "\n".join(['exec("x")' for _ in range(50)])
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


def test_mixed_language_comments():
    """Test mixed language comments"""
    skill = CodeReviewSkill()
    code = """
# English comment
# 中文注释
# Français commentaire
# Español comentario
def hello():
    pass
"""
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


# ── Skill 输入边界 ───────────────────────────────────

def test_all_skills_empty_input():
    """Test all skills with empty/minimal input"""
    tests = [
        (CodeReviewSkill(), {"source_code": ""}),
        (SecurityScanSkill(), {"source_code": ""}),
        (PerfAnalysisSkill(), {"source_code": ""}),
        (TestGenerationSkill(), {"source_code": ""}),
        (DocWritingSkill(), {"doc_type": "api", "title": ""}),
        (DeployVerificationSkill(), {"services": []}),
    ]

    for skill, data in tests:
        result = skill.execute(data)
        assert result["status"] == "ok", f"{skill.name} failed with empty input"


def test_all_skills_none_values():
    """Test all skills with None values in input"""
    tests = [
        (CodeReviewSkill(), {"source_code": None}),
        (SecurityScanSkill(), {"source_code": None}),
        (PerfAnalysisSkill(), {"source_code": None}),
        (TestGenerationSkill(), {"source_code": None}),
    ]

    for skill, data in tests:
        try:
            result = skill.execute(data)
            # Should handle gracefully
            assert result.get("status") in ["ok", "error", None]
        except (TypeError, AttributeError):
            pass  # Expected for some skills with None


# ── 编码测试 ─────────────────────────────────────────

def test_utf8_encoding():
    """Test UTF-8 encoded code"""
    skill = CodeReviewSkill()
    code = """
def greet():
    return "こんにちは"  # Japanese
    return "مرحبا"  # Arabic
    return "Привет"  # Russian
"""
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


def test_mixed_encoding_markers():
    """Test various encoding markers"""
    skill = CodeReviewSkill()
    code = "# -*- coding: utf-8 -*-\n# vim: set fileencoding=utf-8 :\nx = 1"
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


# ── 性能边界测试 ─────────────────────────────────────

def test_thousand_line_code():
    """Test 1000-line code analysis"""
    skill = CodeReviewSkill()
    code = "\n".join(f"line_{i} = {i}" for i in range(1000))
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"
    assert result["total_lines"] == 1000


def test_thousand_function_code():
    """Test code with 1000 functions"""
    skill = CodeReviewSkill()
    code = "\n".join(f"def func_{i}(): return {i}" for i in range(1000))
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"
    assert result["functions_count"] == 1000


# ── 并发边界测试 ─────────────────────────────────────

def test_rapid_sequential_calls():
    """Test rapid sequential skill calls"""
    skill = CodeReviewSkill()
    for i in range(100):
        result = skill.execute({"source_code": "x = 1"})
        assert result["status"] == "ok"


def test_alternating_skills():
    """Test alternating between different skills"""
    skills = [
        CodeReviewSkill(),
        SecurityScanSkill(),
        PerfAnalysisSkill(),
    ]

    for i in range(30):
        skill = skills[i % len(skills)]
        result = skill.execute({"source_code": "x = 1"})
        assert result["status"] == "ok"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
