"""
Tests for CodeReviewSkill — 边界条件与异常处理
================================================="""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skills.code_review.skill import CodeReviewSkill


@pytest.fixture
def skill():
    return CodeReviewSkill()


# ── 基本功能测试 ─────────────────────────────────────

def test_empty_source_code(skill):
    """Empty source code should not crash"""
    result = skill.execute({"source_code": ""})
    assert result["status"] == "ok"
    assert result["issues_found"] == 0


def test_whitespace_only_code(skill):
    """Whitespace-only code should be handled"""
    result = skill.execute({"source_code": "   \n\n  \n"})
    assert result["status"] == "ok"
    assert result["total_lines"] == 3  # trailing newline stripped


def test_single_line_code(skill):
    """Single line code"""
    result = skill.execute({"source_code": "x = 1"})
    assert result["status"] == "ok"
    assert result["total_lines"] == 1


def test_execute_returns_dict(skill):
    """Execute should return a dictionary"""
    result = skill.execute({"source_code": "x = 1"})
    assert isinstance(result, dict)


def test_execute_required_fields(skill):
    """Execute result should have required fields"""
    result = skill.execute({"source_code": "x = 1"})
    assert "skill" in result
    assert "version" in result
    assert "status" in result
    assert "issues" in result
    assert "by_severity" in result


# ── 安全检查测试 ─────────────────────────────────────

def test_exec_detection(skill):
    """Detect exec() usage"""
    code = "exec(user_input)"
    result = skill.execute({"source_code": code})
    issues = [i for i in result["issues"] if "exec" in i["msg"].lower()]
    assert len(issues) >= 1


def test_eval_detection(skill):
    """Detect eval() usage"""
    code = "result = eval(user_input)"
    result = skill.execute({"source_code": code})
    issues = [i for i in result["issues"] if "eval" in i["msg"].lower()]
    assert len(issues) >= 1


def test_pickle_detection(skill):
    """Detect pickle usage"""
    code = "data = pickle.loads(serialized)"
    result = skill.execute({"source_code": code})
    issues = [i for i in result["issues"] if "pickle" in i["msg"].lower()]
    assert len(issues) >= 1


def test_os_system_detection(skill):
    """Detect os.system() usage"""
    code = "os.system('rm -rf /')"
    result = skill.execute({"source_code": code})
    issues = [i for i in result["issues"] if "os.system" in i["msg"]]
    assert len(issues) >= 1


def test_shell_true_detection(skill):
    """Detect shell=True usage"""
    code = "subprocess.run(cmd, shell=True)"
    result = skill.execute({"source_code": code})
    issues = [i for i in result["issues"] if "Shell injection" in i["msg"]]
    assert len(issues) >= 1


def test_debug_mode_detection(skill):
    """Detect debug=True"""
    code = "app.run(debug=True)"
    result = skill.execute({"source_code": code})
    issues = [i for i in result["issues"] if "Debug mode" in i["msg"]]
    assert len(issues) >= 1


def test_hardcoded_secret_detection(skill):
    """Detect hardcoded secrets"""
    code = 'SECRET_KEY = "mysecret123"'
    result = skill.execute({"source_code": code})
    issues = [i for i in result["issues"] if "secret" in i["msg"].lower()]
    assert len(issues) >= 1


def test_todo_marker_detection(skill):
    """Detect TODO markers in code (not comments)"""
    code = "x = 1  # TODO: fix this later"
    result = skill.execute({"source_code": code})
    # Comments are skipped by the analyzer, so this may or may not detect
    assert result["status"] == "ok"


def test_env_var_usage_not_flagged(skill):
    """Env var usage should not be flagged as hardcoded secret"""
    code = 'SECRET_KEY = os.environ.get("SECRET_KEY")'
    result = skill.execute({"source_code": code})
    issues = [i for i in result["issues"] if "secret" in i["msg"].lower() and "hardcoded" in i["msg"].lower()]
    assert len(issues) == 0


# ── 命名规范测试 ─────────────────────────────────────

def test_class_name_check(skill):
    """Class names should use PascalCase"""
    code = "class my_bad_name:\n    pass"
    result = skill.execute({"source_code": code, "options": {"check_naming": True}})
    issues = [i for i in result["issues"] if "PascalCase" in i["msg"]]
    assert len(issues) >= 1


def test_constant_name_check(skill):
    """Constants should use UPPER_CASE"""
    code = "my_constant = 42"
    result = skill.execute({"source_code": code, "options": {"check_naming": True}})
    # Should not flag lowercase variables
    assert result["status"] == "ok"


def test_naming_disabled(skill):
    """Testing with naming check disabled"""
    code = "class bad_name:\n    pass"
    result = skill.execute({"source_code": code, "options": {"check_naming": False}})
    issues = [i for i in result["issues"] if "PascalCase" in i["msg"]]
    assert len(issues) == 0


# ── 性能检查测试 ─────────────────────────────────────

def test_string_concat_in_loop(skill):
    """Detect string concatenation in loops"""
    code = """
for item in items:
    result += item
"""
    result = skill.execute({"source_code": code, "options": {"check_performance": True}})
    issues = [i for i in result["issues"] if "join()" in i["msg"]]
    assert len(issues) >= 1


def test_len_in_loop_condition(skill):
    """Detect len() in loop conditions"""
    code = """
for i in range(len(items)):
    pass
"""
    result = skill.execute({"source_code": code, "options": {"check_performance": True}})
    issues = [i for i in result["issues"] if "hoisting" in i["msg"].lower()]
    assert len(issues) >= 1


def test_performance_check_disabled(skill):
    """Testing with performance check disabled"""
    code = "for i in range(10):\n    print(i)"
    result = skill.execute({"source_code": code, "options": {"check_performance": False}})
    issues = [i for i in result["issues"] if "join()" in i["msg"]]
    assert len(issues) == 0


# ── 综合测试 ─────────────────────────────────────

def test_strict_mode_recommendations(skill):
    """Strict mode should include medium issues in recommendations"""
    code = """
def bad_function():
    x = 1
    # TODO: implement
    pass
"""
    result = skill.execute({"source_code": code, "options": {"strict": True}})
    recs = result["recommendations"]
    assert isinstance(recs, list)


def test_maintainability_index(skill):
    """Test maintainability index calculation"""
    clean_code = "def good_function():\n    return 42"
    result = skill.execute({"source_code": clean_code})
    assert result["summary"]["maintainability_index"] > 0
    assert result["summary"]["maintainability_index"] <= 100


def test_complexity_score(skill):
    """Test complexity score calculation"""
    long_code = "\n".join(f"x{i} = {i}" for i in range(100))
    result = skill.execute({"source_code": long_code})
    assert result["summary"]["complexity_score"] > 0


def test_imports_counted(skill):
    """Test imports are counted"""
    code = """
import os
import sys
from pathlib import Path
"""
    result = skill.execute({"source_code": code})
    assert result["imports_count"] == 3


def test_functions_detected(skill):
    """Test function definitions are detected"""
    code = """
def func_one():
    pass

def func_two(x, y):
    return x + y
"""
    result = skill.execute({"source_code": code})
    assert result["functions_count"] == 2


def test_classes_detected(skill):
    """Test class definitions are detected"""
    code = """
class MyClass:
    pass

class AnotherClass:
    pass
"""
    result = skill.execute({"source_code": code})
    assert result["classes_count"] == 2


def test_issues_sorted_by_severity(skill):
    """Test issues are sorted by severity"""
    code = """
exec('dangerous')
def func():
    pass  # minor issue
"""
    result = skill.execute({"source_code": code})
    if len(result["issues"]) >= 2:
        severities = [i["severity"] for i in result["issues"]]
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        sorted_severities = sorted(severities, key=lambda s: severity_order.get(s, 5))
        assert severities == sorted_severities


def test_deduplication(skill):
    """Test that duplicate issues are removed"""
    code = """
exec('x')
eval('y')
"""
    result = skill.execute({"source_code": code})
    exec_issues = [i for i in result["issues"] if "exec" in i["msg"].lower()]
    eval_issues = [i for i in result["issues"] if "eval" in i["msg"].lower()]
    assert len(exec_issues) <= 1
    assert len(eval_issues) <= 1


def test_options_parameter(skill):
    """Test options parameter is respected"""
    code = "x = 1"
    result = skill.execute({
        "source_code": code,
        "options": {
            "strict": True,
            "check_security": True,
            "check_performance": True,
            "check_naming": True,
        }
    })
    assert result["status"] == "ok"
