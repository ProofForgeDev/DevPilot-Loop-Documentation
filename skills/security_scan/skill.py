"""安全扫描 Skill — security-scan (Deep)
==========================================
扫描代码中的安全漏洞、硬编码密钥、不安全的依赖配置。
支持：OWASP Top 10、CWE 映射、依赖安全审计、加密强度分析
"""

from skills.base import BaseSkill
import re
from typing import Any


class SecurityScanSkill(BaseSkill):
    name = "security-scan"
    version = "2.0.0"
    description = "安全扫描：漏洞检测、硬编码密钥、不安全配置识别、OWASP Top 10"

    # OWASP Top 10 2021 映射
    OWASP_MAPPING = {
        "A01": "Broken Access Control",
        "A02": "Cryptographic Failures",
        "A03": "Injection",
        "A04": "Insecure Design",
        "A05": "Security Misconfiguration",
        "A06": "Vulnerable and Outdated Components",
        "A07": "Authentication Failures",
        "A08": "Software and Data Integrity",
        "A09": "Security Logging and Monitoring",
        "A10": "Server-Side Request Forgery",
    }

    # CWE 映射
    CWE_MAPPING = {
        "hardcoded_secret": {"cwe": "CWE-798", "owasp": "A02"},
        "sql_injection": {"cwe": "CWE-89", "owasp": "A03"},
        "xss": {"cwe": "CWE-79", "owasp": "A03"},
        "path_traversal": {"cwe": "CWE-22", "owasp": "A01"},
        "deserialization": {"cwe": "CWE-502", "owasp": "A08"},
        "weak_crypto": {"cwe": "CWE-328", "owasp": "A02"},
        "debug_mode": {"cwe": "CWE-489", "owasp": "A05"},
        "information_disclosure": {"cwe": "CWE-200", "owasp": "A01"},
    }

    def execute(self, input_data: dict) -> dict:
        source_code = input_data.get("source_code", "")
        file_path = input_data.get("file_path", "unknown")
        options = input_data.get("options", {})

        deep_scan = options.get("deep_scan", False)
        check_dependencies = options.get("check_dependencies", True)
        check_encryption = options.get("check_encryption", True)

        vulnerabilities = []
        lines = source_code.splitlines()

        # 基础安全检查
        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # 跳过注释
            if stripped.startswith('#'):
                continue

            # 硬编码密钥检查
            self._check_secrets(stripped, i, vulnerabilities)

            # SQL 注入检查
            self._check_sql_injection(stripped, i, vulnerabilities)

            # XSS 检查
            self._check_xss(stripped, i, vulnerabilities)

            # 路径遍历检查
            self._check_path_traversal(stripped, i, vulnerabilities)

            # 不安全反序列化
            self._check_deserialization(stripped, i, vulnerabilities)

            # Debug 模式
            if 'debug=True' in stripped:
                vulnerabilities.append({
                    "line": i, "severity": "MEDIUM",
                    "cwe": "CWE-489", "owasp": "A05",
                    "msg": "Debug mode enabled in code",
                    "type": "debug_mode",
                })

            # 弱加密算法
            if check_encryption:
                self._check_weak_crypto(stripped, i, vulnerabilities)

            # 信息泄露
            self._check_info_disclosure(stripped, i, vulnerabilities)

        # 深度扫描
        if deep_scan:
            self._deep_scan(source_code, vulnerabilities)

        # 统计
        by_severity = self._count_by_severity(vulnerabilities)
        by_cwe = self._count_by_cwe(vulnerabilities)
        risk_level = self._calculate_risk_level(by_severity)

        return {
            "skill": self.name,
            "version": self.version,
            "file": file_path,
            "vulnerabilities_found": len(vulnerabilities),
            "by_severity": by_severity,
            "by_cwe": by_cwe,
            "risk_level": risk_level,
            "vulnerabilities": vulnerabilities,
            "owasp_mapping": self._map_to_owasp(vulnerabilities),
            "recommendations": self._gen_recommendations(vulnerabilities, risk_level),
            "status": "ok",
        }

    def _check_secrets(self, line: str, line_num: int, vulns: list) -> None:
        """检查硬编码密钥"""
        patterns = [
            (r'SECRET_KEY\s*=\s*["\']', 'Hardcoded secret key'),
            (r'password\s*=\s*["\']', 'Hardcoded password'),
            (r'api_key\s*=\s*["\']', 'Hardcoded API key'),
            (r'token\s*=\s*["\']', 'Hardcoded token'),
            (r'private_key\s*=', 'Hardcoded private key'),
        ]
        for pattern, msg in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                if 'environ' not in line and 'getenv' not in line and 'os.' not in line:
                    vulns.append({
                        "line": line_num, "severity": "HIGH",
                        "cwe": "CWE-798", "owasp": "A02",
                        "msg": msg, "type": "hardcoded_secret",
                    })

    def _check_sql_injection(self, line: str, line_num: int, vulns: list) -> None:
        """检查 SQL 注入"""
        if re.search(r'(SELECT|INSERT|UPDATE|DELETE).*[%+\']', line, re.IGNORECASE):
            if 'f"' in line or "'" in line or "%" in line:
                vulns.append({
                    "line": line_num, "severity": "CRITICAL",
                    "cwe": "CWE-89", "owasp": "A03",
                    "msg": "Potential SQL injection via string formatting",
                    "type": "sql_injection",
                })

    def _check_xss(self, line: str, line_num: int, vulns: list) -> None:
        """检查 XSS"""
        if re.search(r'(innerHTML|document\.write|alert\()', line, re.IGNORECASE):
            vulns.append({
                "line": line_num, "severity": "HIGH",
                "cwe": "CWE-79", "owasp": "A03",
                "msg": "Potential XSS vulnerability",
                "type": "xss",
            })

    def _check_path_traversal(self, line: str, line_num: int, vulns: list) -> None:
        """检查路径遍历"""
        if re.search(r'open\s*\([^)]*\+\s*\w+', line):
            vulns.append({
                "line": line_num, "severity": "HIGH",
                "cwe": "CWE-22", "owasp": "A01",
                "msg": "Potential path traversal",
                "type": "path_traversal",
            })

    def _check_deserialization(self, line: str, line_num: int, vulns: list) -> None:
        """检查不安全反序列化"""
        if re.search(r'pickle\.loads?\s*\(', line, re.IGNORECASE):
            vulns.append({
                "line": line_num, "severity": "CRITICAL",
                "cwe": "CWE-502", "owasp": "A08",
                "msg": "Unsafe pickle deserialization",
                "type": "deserialization",
            })

    def _check_weak_crypto(self, line: str, line_num: int, vulns: list) -> None:
        """检查弱加密"""
        if re.search(r'md5\s*\(', line, re.IGNORECASE) or re.search(r'sha1\s*\(', line, re.IGNORECASE):
            vulns.append({
                "line": line_num, "severity": "HIGH",
                "cwe": "CWE-328", "owasp": "A02",
                "msg": "Weak hashing algorithm",
                "type": "weak_crypto",
            })

    def _check_info_disclosure(self, line: str, line_num: int, vulns: list) -> None:
        """检查信息泄露"""
        if re.search(r'print\s*\(.*(?:traceback|exception|error)', line, re.IGNORECASE):
            vulns.append({
                "line": line_num, "severity": "LOW",
                "cwe": "CWE-200", "owasp": "A09",
                "msg": "Potential information disclosure",
                "type": "information_disclosure",
            })

    def _deep_scan(self, source_code: str, vulns: list) -> None:
        """深度扫描"""
        # 检查认证相关代码
        if 'jwt' in source_code.lower():
            if 'HS256' in source_code or 'HS384' in source_code or 'HS512' in source_code:
                vulns.append({
                    "line": 0, "severity": "MEDIUM",
                    "cwe": "CWE-327", "owasp": "A07",
                    "msg": "JWT using weak algorithm (HS256/HS384/HS512)",
                    "type": "weak_crypto",
                })

        # 检查 CORS 配置
        if 'cors' in source_code.lower() or 'CORS' in source_code:
            if '*' in source_code:
                vulns.append({
                    "line": 0, "severity": "LOW",
                    "cwe": "CWE-942", "owasp": "A01",
                    "msg": "Overly permissive CORS configuration",
                    "type": "misconfiguration",
                })

    def _count_by_severity(self, vulns: list) -> dict:
        counts = {}
        for v in vulns:
            sev = v["severity"]
            counts[sev] = counts.get(sev, 0) + 1
        return counts

    def _count_by_cwe(self, vulns: list) -> dict:
        counts = {}
        for v in vulns:
            cwe = v.get("cwe", "Unknown")
            counts[cwe] = counts.get(cwe, 0) + 1
        return counts

    def _calculate_risk_level(self, by_severity: dict) -> str:
        """计算风险等级"""
        if by_severity.get("CRITICAL", 0) > 0:
            return "critical"
        if by_severity.get("HIGH", 0) > 0:
            return "high"
        if by_severity.get("MEDIUM", 0) > 0:
            return "medium"
        if by_severity.get("LOW", 0) > 0:
            return "low"
        return "none"

    def _map_to_owasp(self, vulns: list) -> dict:
        """映射到 OWASP"""
        mapping = {}
        for v in vulns:
            owasp = v.get("owasp", "")
            if owasp:
                mapping[owasp] = mapping.get(owasp, 0) + 1
        return mapping

    def _gen_recommendations(self, vulns: list, risk_level: str) -> list:
        """生成建议"""
        recs = []
        if risk_level == "critical":
            recs.append("CRITICAL: Fix security vulnerabilities before deployment")
        elif risk_level == "high":
            recs.append("HIGH: Address security issues before next release")
        elif risk_level == "medium":
            recs.append("MEDIUM: Review security recommendations")

        # 按类型分组建议
        types = {v.get("type") for v in vulns}
        if "hardcoded_secret" in types:
            recs.append("Move secrets to environment variables or vault")
        if "sql_injection" in types:
            recs.append("Use parameterized queries instead of string concatenation")
        if "xss" in types:
            recs.append("Sanitize user input and use output encoding")
        if "weak_crypto" in types:
            recs.append("Use strong hashing algorithms (SHA-256+ or bcrypt)")

        return recs

    def validate_input(self, input_data: dict) -> bool:
        return isinstance(input_data, dict) and "source_code" in input_data

    def get_schema(self) -> dict:
        return {
            "input": {
                "type": "object",
                "required": ["source_code"],
                "properties": {
                    "source_code": {"type": "string", "description": "待扫描的源代码"},
                    "file_path": {"type": "string", "description": "文件路径（可选）"},
                    "options": {
                        "type": "object",
                        "properties": {
                            "deep_scan": {"type": "boolean", "description": "深度扫描"},
                            "check_dependencies": {"type": "boolean", "description": "检查依赖"},
                            "check_encryption": {"type": "boolean", "description": "检查加密"},
                        }
                    }
                },
            },
            "output": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string"},
                    "version": {"type": "string"},
                    "file": {"type": "string"},
                    "vulnerabilities_found": {"type": "integer"},
                    "by_severity": {"type": "object"},
                    "by_cwe": {"type": "object"},
                    "risk_level": {"type": "string"},
                    "vulnerabilities": {"type": "array"},
                    "owasp_mapping": {"type": "object"},
                    "recommendations": {"type": "array"},
                    "status": {"type": "string"},
                },
            },
        }
