"""安全扫描 Skill — security-scan
==================================
扫描代码中的安全漏洞、硬编码密钥、不安全的依赖配置。
"""

from skills.base import BaseSkill


class SecurityScanSkill(BaseSkill):
    name = "security-scan"
    version = "1.0.0"
    description = "安全扫描：漏洞检测、硬编码密钥、不安全配置识别"

    def execute(self, input_data: dict) -> dict:
        source_code = input_data.get("source_code", "")
        file_path = input_data.get("file_path", "unknown")

        vulnerabilities = []
        lines = source_code.splitlines()

        # 安全规则检查
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # 硬编码密钥
            patterns_secret = [
                ('SECRET_KEY', 'Hardcoded secret key'),
                ('password = ', 'Hardcoded password assignment'),
                ('api_key = ', 'Hardcoded API key'),
                ('token = "', 'Hardcoded token value'),
            ]
            for pattern, msg in patterns_secret:
                if pattern.lower() in stripped.lower() and '=' in stripped and not stripped.startswith('#'):
                    if 'environ' not in stripped and 'getenv' not in stripped and 'os.' not in stripped:
                        vulnerabilities.append({
                            "line": i, "severity": "HIGH",
                            "cwe": "CWE-798", "msg": msg,
                        })

            # 不安全的密码哈希
            if 'md5(' in stripped.lower() or 'sha1(' in stripped.lower():
                vulnerabilities.append({
                    "line": i, "severity": "HIGH",
                    "cwe": "CWE-328", "msg": "Weak hashing algorithm",
                })

            # SQL 注入风险
            if ('SELECT' in stripped or 'INSERT' in stripped) and ('%' in stripped or '+' in stripped or 'f"' in stripped):
                vulnerabilities.append({
                    "line": i, "severity": "CRITICAL",
                    "cwe": "CWE-89", "msg": "Potential SQL injection",
                })

            # debug 模式
            if 'debug=True' in stripped:
                vulnerabilities.append({
                    "line": i, "severity": "MEDIUM",
                    "cwe": "CWE-489", "msg": "Debug mode enabled in code",
                })

        # 统计
        by_severity = {}
        for v in vulnerabilities:
            by_severity[v["severity"]] = by_severity.get(v["severity"], 0) + 1

        return {
            "skill": self.name,
            "version": self.version,
            "file": file_path,
            "vulnerabilities_found": len(vulnerabilities),
            "by_severity": by_severity,
            "vulnerabilities": vulnerabilities,
            "status": "ok",
        }

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
                },
            },
            "output": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string"},
                    "vulnerabilities_found": {"type": "integer"},
                    "by_severity": {"type": "object"},
                    "vulnerabilities": {"type": "array"},
                    "status": {"type": "string"},
                },
            },
        }
