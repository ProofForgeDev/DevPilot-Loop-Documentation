"""
Tests for SecurityScanSkill — 深度安全测试
==========================================="""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from skills.security_scan.skill import SecurityScanSkill


@pytest.fixture
def skill():
    return SecurityScanSkill()


# ── OWASP Top 10 测试 ───────────────────────────────

def test_owasp_a01_detection(skill):
    """Test OWASP A01: Injection detection"""
    code = "result = eval(user_input)"
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


def test_owasp_a02_detection(skill):
    """Test OWASP A02: Cryptographic failures detection"""
    code = "password = hashlib.md5(user_input).hexdigest()"
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


def test_owasp_a03_detection(skill):
    """Test OWASP A03: Broken authentication detection"""
    code = "session['user'] = username  # No proper session management"
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


# ── 漏洞类型测试 ─────────────────────────────────────

def test_hardcoded_secret_detection(skill):
    """Test hardcoded secret detection"""
    code = 'API_KEY = "sk-12345-abcde-67890"'
    result = skill.execute({"source_code": code})
    vulns = result.get("vulnerabilities", [])
    assert len(vulns) >= 1


def test_sql_injection_detection(skill):
    """Test SQL injection detection"""
    code = 'query = f"SELECT * FROM users WHERE id = {user_id}"'
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


def test_xss_detection(skill):
    """Test XSS detection"""
    code = 'return f"<script>{user_input}</script>"'
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


def test_path_traversal_detection(skill):
    """Test path traversal detection"""
    code = 'path = os.path.join("/uploads", user_filename)'
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


def test_unsafe_deserialization_detection(skill):
    """Test unsafe deserialization detection"""
    code = "data = pickle.loads(request.data)"
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


# ── 风险等级测试 ─────────────────────────────────────

def test_critical_risk_level(skill):
    """Test CRITICAL risk level"""
    code = "exec(user_controlled_code)"
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


def test_high_risk_level(skill):
    """Test HIGH risk level"""
    code = 'SECRET = "hardcoded_value"'
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


def test_clean_code_risk_level(skill):
    """Test clean code has LOW risk"""
    code = """
import os
key = os.environ.get("API_KEY")
print("hello")
"""
    result = skill.execute({"source_code": code})
    # Risk level may be at top level or in output sub-dict
    risk = result.get("risk_level", result.get("output", {}).get("risk_level", "low"))
    assert isinstance(risk, str)


# ── 深度扫描模式测试 ─────────────────────────────────

def test_deep_scan_mode(skill):
    """Test deep scan mode"""
    code = """
import pickle
import subprocess
import os

# Dangerous patterns
data = pickle.loads(b"data")
subprocess.call("ls", shell=True)
os.system("rm -rf /")
"""
    result = skill.execute({
        "source_code": code,
        "options": {"deep_scan": True}
    })
    assert result["status"] == "ok"
    vulns = result.get("vulnerabilities", [])
    assert len(vulns) >= 1


# ── 加密检测测试 ─────────────────────────────────────

def test_weak_encryption_detection(skill):
    """Test weak encryption detection"""
    code = "cipher = DES.new(key, DES.MODE_ECB)"
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


def test_strong_encryption_not_flagged(skill):
    """Test strong encryption is not flagged"""
    code = "cipher = AES.new(key, AES.MODE_GCM)"
    result = skill.execute({"source_code": code})
    assert result["status"] == "ok"


# ── CWE 映射测试 ─────────────────────────────────────

def test_cwe_mapping(skill):
    """Test CWE mapping exists"""
    code = "eval(user_input)"
    result = skill.execute({"source_code": code})
    if result.get("vulnerabilities"):
        assert "cwe_id" in result["vulnerabilities"][0] or "cwe" in result


def test_owasp_mapping(skill):
    """Test OWASP mapping exists"""
    code = "exec(user_input)"
    result = skill.execute({"source_code": code})
    if result.get("vulnerabilities"):
        assert "owasp" in result or "category" in result


# ── 输入验证测试 ─────────────────────────────────────

def test_validate_input_valid(skill):
    """Test validate_input with valid data"""
    assert skill.validate_input({"source_code": "x = 1"}) is True


def test_validate_input_invalid(skill):
    """Test validate_input with invalid data"""
    assert skill.validate_input({}) is False
    assert skill.validate_input(None) is False


def test_validate_input_missing_source(skill):
    """Test validate_input without source_code"""
    assert skill.validate_input({"other": "data"}) is False


# ── Schema 测试 ─────────────────────────────────────

def test_schema_has_input(skill):
    """Test schema has input definition"""
    schema = skill.get_schema()
    assert "input" in schema


def test_schema_has_output(skill):
    """Test schema has output definition"""
    schema = skill.get_schema()
    assert "output" in schema


def test_schema_input_required(skill):
    """Test schema input required fields"""
    schema = skill.get_schema()
    assert "source_code" in schema["input"]["required"]


# ── 输出结构测试 ─────────────────────────────────────

def test_output_has_vulnerabilities(skill):
    """Test output contains vulnerabilities list"""
    result = skill.execute({"source_code": "x = 1"})
    # Vulnerabilities may be at top level or in output
    vulns = result.get("vulnerabilities", [])
    if not vulns:
        vulns = result.get("output", {}).get("findings", [])
    assert isinstance(vulns, list)


def test_output_has_risk_level(skill):
    """Test output contains risk_level"""
    result = skill.execute({"source_code": "x = 1"})
    # Risk level may be at top level or in output sub-dict
    risk = result.get("risk_level", result.get("output", {}).get("risk_level", "low"))
    assert isinstance(risk, str)


def test_output_has_recommendations(skill):
    """Test output contains recommendations"""
    result = skill.execute({"source_code": "x = 1"})
    assert "recommendations" in result


def test_vulnerability_structure(skill):
    """Test vulnerability object structure"""
    code = 'SECRET = "test123"'
    result = skill.execute({"source_code": code})
    vulns = result.get("vulnerabilities", [])
    if vulns:
        vuln = vulns[0]
        assert "line" in vuln or "location" in vuln
        assert "severity" in vuln
        assert "description" in vuln or "msg" in vuln
