"""代码审查 Skill — code-review (Deep)
========================================
对 Python 代码进行静态分析，检查最佳实践、潜在 bug 和安全问题。
支持：代码规范、漏洞检测、性能警告、安全审计、依赖分析
"""

from skills.base import BaseSkill
import re
from typing import Any


class CodeReviewSkill(BaseSkill):
    name = "code-review"
    version = "2.0.0"
    description = "代码审查：静态分析、最佳实践检查、潜在缺陷检测、安全审计"

    # PEP 8 命名规范规则
    NAMING_PATTERNS = {
        "variable": r'^[a-z_][a-z0-9_]*$',
        "constant": r'^[A-Z_][A-Z0-9_]*$',
        "function": r'^[a-z_][a-z0-9_]*$',
        "class": r'^[A-Z][a-zA-Z0-9]*$',
        "module": r'^[a-z_][a-z0-9_]*$',
    }

    # 危险模式
    DANGEROUS_PATTERNS = [
        (r'exec\s*\(', 'Potential code injection via exec()', 'CRITICAL'),
        (r'eval\s*\(', 'Potential code injection via eval()', 'CRITICAL'),
        (r'pickle\.loads?\s*\(', 'Unsafe pickle deserialization', 'HIGH'),
        (r'subprocess\.(call|run|Popen)\s*\(', 'Unsafe subprocess usage', 'MEDIUM'),
        (r'os\.system\s*\(', 'Unsafe os.system() call', 'HIGH'),
        (r'shell\s*=\s*True', 'Shell injection risk', 'CRITICAL'),
        (r'asyncio\.ensure_future\s*\(', 'Legacy task creation', 'INFO'),
    ]

    # 反模式
    ANTI_PATTERNS = [
        (r'def\s+\w+\s*\(.*self.*,\s*self', 'Self passed as argument'),
        (r'class\s+\w+.*object\s*\)', 'Explicit object inheritance'),
        (r'import\s+(\w+)', 'Import analysis'),
        (r'except\s*\(', 'Bare except clause'),
        (r'pass\s*$', 'Pass statement'),
        (r'print\s*\(', 'Print statement (use logging)'),
    ]

    def execute(self, input_data: dict) -> dict:
        source_code = input_data.get("source_code", "")
        file_path = input_data.get("file_path", "unknown")
        options = input_data.get("options", {})

        strict_mode = options.get("strict", False)
        check_security = options.get("check_security", True)
        check_performance = options.get("check_performance", True)
        check_naming = options.get("check_naming", True)

        issues = []
        lines = source_code.splitlines()
        imports = []
        classes = []
        functions = []

        # 逐行分析
        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # 跳过空行和注释
            if not stripped or stripped.startswith('#'):
                continue

            # 收集导入
            match = re.match(r'^(?:from|import)\s+(\S+)', stripped)
            if match:
                imports.append(match.group(1))

            # 收集类和函数定义
            match = re.match(r'^class\s+(\w+)', stripped)
            if match:
                classes.append(match.group(1))
            match = re.match(r'^def\s+(\w+)', stripped)
            if match:
                functions.append(match.group(1))

            # 命名规范检查
            if check_naming:
                self._check_naming(stripped, i, issues)

            # 危险模式检查
            if check_security:
                self._check_dangerous_patterns(stripped, i, issues)

            # 基础安全检查
            if 'debug=True' in stripped:
                issues.append({"line": i, "severity": "MEDIUM", "msg": "Debug mode enabled"})
            if 'hardcoded' in stripped.lower() or ("=" in stripped and 'secret' in stripped.lower()):
                if not ('environ' in stripped or 'getenv' in stripped):
                    issues.append({"line": i, "severity": "HIGH", "msg": "Possible hardcoded secret"})
            if "except Exception" in stripped and "as e" not in stripped:
                issues.append({"line": i, "severity": "LOW", "msg": "Bare except clause"})
            if "TODO" in stripped or "FIXME" in stripped:
                issues.append({"line": i, "severity": "INFO", "msg": "TODO/FIXME marker found"})

            # 性能检查
            if check_performance:
                self._check_performance(stripped, i, lines, issues)

        # 去重和排序
        issues = self._deduplicate_issues(issues)
        issues.sort(key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}.get(x["severity"], 5))

        # 生成报告
        by_severity = self._count_by_severity(issues)
        summary = self._generate_summary(issues, imports, classes, functions, lines)

        return {
            "skill": self.name,
            "version": self.version,
            "file": file_path,
            "total_lines": len(lines),
            "imports_count": len(imports),
            "classes_count": len(classes),
            "functions_count": len(functions),
            "issues_found": len(issues),
            "by_severity": by_severity,
            "issues": issues,
            "summary": summary,
            "recommendations": self._gen_recommendations(issues, strict_mode),
            "status": "ok",
        }

    def _check_naming(self, line: str, line_num: int, issues: list) -> None:
        """检查命名规范"""
        # 常量检查
        if re.match(r'^[A-Z_][A-Z0-9_]*\s*=', line):
            match = re.match(r'^([A-Z_][A-Z0-9_]*)\s*=', line)
            if match:
                name = match.group(1)
                if '_' in name and not name.startswith('__'):
                    issues.append({
                        "line": line_num, "severity": "INFO",
                        "msg": f"Constant '{name}' uses snake_case, consider UPPER_CASE"
                    })

        # 类名检查
        match = re.match(r'class\s+(\w+)', line)
        if match:
            class_name = match.group(1)
            if '_' in class_name:
                issues.append({
                    "line": line_num, "severity": "LOW",
                    "msg": f"Class '{class_name}' should use PascalCase"
                })

    def _check_dangerous_patterns(self, line: str, line_num: int, issues: list) -> None:
        """检查危险模式"""
        for pattern, msg, severity in self.DANGEROUS_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append({"line": line_num, "severity": severity, "msg": msg})

    def _check_performance(self, line: str, line_num: int, all_lines: list, issues: list) -> None:
        """检查性能问题"""
        # 循环内字符串拼接
        if line.strip().startswith('for ') and line_num < len(all_lines):
            next_line = all_lines[line_num].strip()
            if '+=' in next_line or ('+' in next_line and 'str' not in next_line.lower()):
                issues.append({
                    "line": line_num + 1, "severity": "MEDIUM",
                    "msg": "String concatenation in loop - use join()"
                })

        # 重复计算
        if 'len(' in line and 'for' in line and 'in' in line:
            issues.append({
                "line": line_num, "severity": "INFO",
                "msg": "len() called in loop condition - consider hoisting"
            })

    def _deduplicate_issues(self, issues: list) -> list:
        """去重"""
        seen = set()
        unique = []
        for issue in issues:
            key = (issue["line"], issue["msg"])
            if key not in seen:
                seen.add(key)
                unique.append(issue)
        return unique

    def _count_by_severity(self, issues: list) -> dict:
        """按严重程度统计"""
        counts = {}
        for issue in issues:
            severity = issue["severity"]
            counts[severity] = counts.get(severity, 0) + 1
        return counts

    def _generate_summary(self, issues: list, imports: list, classes: list,
                          functions: list, lines: list) -> dict:
        """生成总结"""
        return {
            "complexity_score": min(len(lines) / 10, 10),
            "maintainability_index": max(100 - len(issues) * 5, 0),
            "import_analysis": {
                "total": len(imports),
                "stdlib": len([i for i in imports if not i.startswith('.') and '/' not in i]),
                "third_party": len([i for i in imports if i.startswith('.') or '/' in i]),
            },
            "structure": {
                "classes": classes,
                "functions": functions,
            }
        }

    def _gen_recommendations(self, issues: list, strict_mode: bool) -> list:
        """生成建议"""
        recommendations = []
        severities = {i["severity"] for i in issues}

        if "CRITICAL" in severities:
            recommendations.append("URGENT: Fix critical security issues before deployment")
        if "HIGH" in severities:
            recommendations.append("Address high-severity issues in next sprint")
        if strict_mode and "MEDIUM" in severities:
            recommendations.append("Strict mode: Review medium issues for consistency")

        if not issues:
            recommendations.append("Code looks clean! Consider adding more tests.")
        else:
            recommendations.append(f"Found {len(issues)} issues. Review and fix before merge.")

        return recommendations

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
                    "options": {
                        "type": "object",
                        "properties": {
                            "strict": {"type": "boolean", "description": "严格模式"},
                            "check_security": {"type": "boolean", "description": "检查安全"},
                            "check_performance": {"type": "boolean", "description": "检查性能"},
                            "check_naming": {"type": "boolean", "description": "检查命名"},
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
                    "total_lines": {"type": "integer"},
                    "issues_found": {"type": "integer"},
                    "by_severity": {"type": "object"},
                    "issues": {"type": "array"},
                    "summary": {"type": "object"},
                    "recommendations": {"type": "array"},
                    "status": {"type": "string"},
                },
            },
        }
