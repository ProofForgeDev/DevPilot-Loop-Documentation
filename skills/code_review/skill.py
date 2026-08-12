"""代码审查 Skill — code-review
================================
对 Python 代码进行静态分析，检查最佳实践、潜在 bug 和安全问题。
"""

from skills.base import BaseSkill


class CodeReviewSkill(BaseSkill):
    name = "code-review"
    version = "1.0.0"
    description = "代码审查：静态分析、最佳实践检查、潜在缺陷检测"

    def execute(self, input_data: dict) -> dict:
        source_code = input_data.get("source_code", "")
        file_path = input_data.get("file_path", "unknown")

        issues = []
        lines = source_code.splitlines()

        # 规则检查
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if "debug=True" in stripped:
                issues.append({"line": i, "severity": "MEDIUM", "msg": "Debug mode enabled"})
            if "hardcoded" in stripped.lower() or ("=" in stripped and 'secret' in stripped.lower()):
                issues.append({"line": i, "severity": "HIGH", "msg": "Possible hardcoded secret"})
            if stripped.startswith("import ") and "os" in stripped:
                pass  # normal import
            if "except Exception" in stripped and "as e" not in stripped:
                issues.append({"line": i, "severity": "LOW", "msg": "Bare except clause"})
            if "TODO" in stripped or "FIXME" in stripped:
                issues.append({"line": i, "severity": "INFO", "msg": "TODO/FIXME marker found"})

        return {
            "skill": self.name,
            "version": self.version,
            "file": file_path,
            "total_lines": len(lines),
            "issues_found": len(issues),
            "issues": issues,
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
                    "source_code": {"type": "string", "description": "待审查的源代码"},
                    "file_path": {"type": "string", "description": "文件路径（可选）"},
                },
            },
            "output": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string"},
                    "file": {"type": "string"},
                    "total_lines": {"type": "integer"},
                    "issues_found": {"type": "integer"},
                    "issues": {"type": "array", "items": {"type": "object"}},
                    "status": {"type": "string"},
                },
            },
        }
