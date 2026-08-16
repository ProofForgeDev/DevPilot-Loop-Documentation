"""性能分析 Skill — perf-analysis (Deep)
==========================================
分析代码性能瓶颈，检测潜在的 N+1 查询、内存泄漏、低效算法。
支持：时间复杂度分析、内存使用检测、数据库查询优化、缓存策略建议
"""

from skills.base import BaseSkill
import re
import logging
from typing import Any

logger = logging.getLogger("devpilot.skills")


class PerfAnalysisSkill(BaseSkill):
    name = "perf-analysis"
    version = "2.0.0"
    description = "性能分析：瓶颈检测、N+1 查询识别、优化建议、复杂度分析"

    # 性能规则库
    PERFORMANCE_RULES = {
        "n_plus_one": {
            "pattern": r'for\s+\w+\s+in\s+\w+:.*(?:query|select|get\(|save\(|all\()',
            "severity": "HIGH",
            "msg": "Potential N+1 query pattern detected",
            "fix": "Use prefetch_related() or select_related()",
        },
        "full_table_scan": {
            "pattern": r'\.all\(\)|objects\.all\(\)',
            "severity": "MEDIUM",
            "msg": "Full table scan without pagination",
            "fix": "Add pagination or limiting",
        },
        "string_concat_in_loop": {
            "pattern": r'\w+\s*\+=\s*["\']',
            "severity": "MEDIUM",
            "msg": "String concatenation in loop",
            "fix": "Use list comprehension and join()",
        },
        "expensive_function_in_loop": {
            "pattern": r'for\s+.*:.*(?:len\(|sorted\(|reversed\()',
            "severity": "LOW",
            "msg": "Expensive function call inside loop",
            "fix": "Hoist outside loop",
        },
        "missing_cache": {
            "pattern": r'(?:query|select).*without.*cache',
            "severity": "INFO",
            "msg": "Query without caching",
            "fix": "Consider adding Redis/cache layer",
        },
        "inefficient_algorithm": {
            "pattern": r'(?:for.*for|nested.*loop)',
            "severity": "HIGH",
            "msg": "Potential O(n²) algorithm",
            "fix": "Use hash-based lookup or sorting",
        },
        "large_object_load": {
            "pattern": r'read\(\)|\.load\(\)',
            "severity": "MEDIUM",
            "msg": "Large object loaded into memory",
            "fix": "Use streaming or pagination",
        },
    }

    def execute(self, input_data: dict) -> dict:
        try:
            if not self.validate_input(input_data):
                logger.error("perf-analysis: invalid input")
                return {"status": "error", "error": "invalid_input", "skill": self.name, "version": self.version}

            source_code = input_data.get("source_code", "")
            file_path = input_data.get("file_path", "unknown")
            options = input_data.get("options", {})

            strict_mode = options.get("strict", False)
            analyze_complexity = options.get("analyze_complexity", True)
            check_memory = options.get("check_memory", True)
            check_queries = options.get("check_queries", True)

            bottlenecks = []
            lines = source_code.splitlines()
            complexity_analysis = {}

            # 逐行分析
            for i, line in enumerate(lines, 1):
                stripped = line.strip()

                # 跳过注释
                if stripped.startswith('#'):
                    continue

                # 规则匹配
                for rule_name, rule in self.PERFORMANCE_RULES.items():
                    if re.search(rule["pattern"], stripped, re.IGNORECASE):
                        bottlenecks.append({
                            "line": i,
                            "severity": rule["severity"],
                            "type": rule_name,
                            "msg": rule["msg"],
                            "fix": rule["fix"],
                        })

                # 循环复杂度检测
                if analyze_complexity:
                    self._analyze_loop_complexity(stripped, i, lines, bottlenecks)

                # 内存检查
                if check_memory:
                    self._check_memory_usage(stripped, i, bottlenecks)

                # 查询优化检查
                if check_queries:
                    self._check_query_optimization(stripped, i, source_code, bottlenecks)

            # 去重
            bottlenecks = self._deduplicate(bottlenecks)

            # 排序
            severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
            bottlenecks.sort(key=lambda x: severity_order.get(x["severity"], 5))

            # 计算复杂度指标
            if analyze_complexity:
                complexity_analysis = self._analyze_complexity(lines)

            # 统计
            by_severity = self._count_by_severity(bottlenecks)
            total_issues = sum(by_severity.values())

            # 计算性能分数
            perf_score = self._calculate_performance_score(bottlenecks, total_issues)

            return {
                "skill": self.name,
                "version": self.version,
                "file": file_path,
                "total_lines": len(lines),
                "bottlenecks_found": len(bottlenecks),
                "by_severity": by_severity,
                "performance_score": perf_score,
                "complexity_analysis": complexity_analysis,
                "bottlenecks": bottlenecks,
                "suggestions": self._gen_suggestions(bottlenecks),
                "optimization_plan": self._gen_optimization_plan(bottlenecks, strict_mode),
                "status": "ok",
            }
        except Exception as e:
            logger.error(f"perf-analysis: execution failed: {e}")
            return {"status": "error", "error": str(e), "skill": self.name, "version": self.version}

    def _analyze_loop_complexity(self, line: str, line_num: int, all_lines: list, bottlenecks: list) -> None:
        """分析循环复杂度"""
        # 嵌套循环检测
        if line.strip().startswith('for ') or line.strip().startswith('while '):
            indent = len(line) - len(line.lstrip())
            for j, next_line in enumerate(all_lines[line_num:], line_num + 1):
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent <= indent and next_line.strip():
                    break
                # 发现嵌套循环
                if next_line.strip().startswith('for ') or next_line.strip().startswith('while '):
                    bottlenecks.append({
                        "line": j, "severity": "HIGH",
                        "type": "nested_loop",
                        "msg": f"Nested loop detected at line {j}",
                        "fix": "Consider using hash-based lookup or sorting",
                    })

    def _check_memory_usage(self, line: str, line_num: int, bottlenecks: list) -> None:
        """检查内存使用"""
        # 大对象加载
        if re.search(r'read\(\)|\.load\(\)', line):
            if 'binary' not in line.lower() and 'stream' not in line.lower():
                bottlenecks.append({
                    "line": line_num, "severity": "MEDIUM",
                    "type": "memory",
                    "msg": "Potential large object loaded into memory",
                    "fix": "Use streaming or chunked reading",
                })

        # 列表推导式 vs 生成器
        if re.search(r'\[\w+\s+for\s+\w+\s+in\s+\w+\]', line):
            if len(line) > 100:  # 长列表推导式
                bottlenecks.append({
                    "line": line_num, "severity": "INFO",
                    "type": "memory",
                    "msg": "Large list comprehension - consider generator",
                    "fix": "Use generator expression (parentheses instead of brackets)",
                })

    def _check_query_optimization(self, line: str, line_num: int, source: str, bottlenecks: list) -> None:
        """检查查询优化"""
        # N+1 检测
        if 'for ' in line and 'in ' in line:
            # 检查后续行是否有查询操作
            lines = source.splitlines()
            for j in range(line_num, min(line_num + 10, len(lines))):
                next_line = lines[j].strip()
                if any(kw in next_line.lower() for kw in ['query', 'select', 'get(', 'save(', 'all()']):
                    bottlenecks.append({
                        "line": line_num, "severity": "HIGH",
                        "type": "n_plus_one",
                        "msg": "Potential N+1 query inside loop",
                        "fix": "Use prefetch_related() or select_related()",
                    })
                    break

        # 缺少缓存
        if ('query' in source.lower() or 'select' in source.lower()):
            if 'cache' not in source.lower() and '@cache' not in source:
                if line_num == 1:
                    bottlenecks.append({
                        "line": 1, "severity": "INFO",
                        "type": "caching",
                        "msg": "No caching mechanism detected",
                        "fix": "Consider adding Redis/cache layer for frequent queries",
                    })

    def _analyze_complexity(self, lines: list) -> dict:
        """分析复杂度"""
        loops = sum(1 for l in lines if l.strip().startswith('for ') or l.strip().startswith('while '))
        conditionals = sum(1 for l in lines if l.strip().startswith('if ') or l.strip().startswith('elif '))
        returns = sum(1 for l in lines if l.strip().startswith('return '))

        return {
            "loop_count": loops,
            "conditional_count": conditionals,
            "return_count": returns,
            "cyclomatic_complexity": conditionals + loops + 1,
            "lines_of_code": len(lines),
        }

    def _count_by_severity(self, bottlenecks: list) -> dict:
        counts = {}
        for b in bottlenecks:
            sev = b["severity"]
            counts[sev] = counts.get(sev, 0) + 1
        return counts

    def _calculate_performance_score(self, bottlenecks: list, total: int) -> float:
        """计算性能分数 (0-100)"""
        if total == 0:
            return 100.0
        penalties = {
            "CRITICAL": 30,
            "HIGH": 15,
            "MEDIUM": 8,
            "LOW": 3,
            "INFO": 1,
        }
        penalty = sum(penalties.get(b["severity"], 0) for b in bottlenecks)
        return max(0, 100 - penalty)

    def _deduplicate(self, bottlenecks: list) -> list:
        seen = set()
        unique = []
        for b in bottlenecks:
            key = (b["line"], b["type"])
            if key not in seen:
                seen.add(key)
                unique.append(b)
        return unique

    def _gen_suggestions(self, bottlenecks: list) -> list:
        """生成优化建议"""
        suggestions = []
        types_found = {b["type"] for b in bottlenecks}

        if "n_plus_one" in types_found:
            suggestions.append("Use prefetch_related() or select_related() to reduce queries")
        if "full_table_scan" in types_found:
            suggestions.append("Add pagination or limiting to large querysets")
        if "caching" in types_found:
            suggestions.append("Consider adding Redis/cache layer for frequent queries")
        if "nested_loop" in types_found:
            suggestions.append("Replace nested loops with hash-based lookup")
        if "string_concat_in_loop" in types_found:
            suggestions.append("Use join() instead of += for string concatenation")
        if "memory" in types_found:
            suggestions.append("Consider using generators for large datasets")

        return suggestions

    def _gen_optimization_plan(self, bottlenecks: list, strict_mode: bool) -> list:
        """生成优化计划"""
        plan = []
        by_severity = self._count_by_severity(bottlenecks)

        if by_severity.get("CRITICAL", 0) > 0:
            plan.append({"phase": "Critical", "items": "Fix all critical performance issues", "effort": "1-2 days"})
        if by_severity.get("HIGH", 0) > 0:
            plan.append({"phase": "High Priority", "items": "Address high-severity bottlenecks", "effort": "2-3 days"})
        if by_severity.get("MEDIUM", 0) > 0:
            plan.append({"phase": "Medium Priority", "items": "Review medium-severity issues", "effort": "1 day"})
        if strict_mode and by_severity.get("LOW", 0) > 0:
            plan.append({"phase": "Low Priority", "items": "Review low-severity optimizations", "effort": "Optional"})

        if not plan:
            plan.append({"phase": "Optimal", "items": "Code is well-optimized", "effort": "None"})

        return plan

    def validate_input(self, input_data: dict) -> bool:
        return isinstance(input_data, dict) and "source_code" in input_data

    def get_schema(self) -> dict:
        return {
            "input": {
                "type": "object",
                "required": ["source_code"],
                "properties": {
                    "source_code": {"type": "string", "description": "待分析的源代码"},
                    "file_path": {"type": "string", "description": "文件路径（可选）"},
                    "options": {
                        "type": "object",
                        "properties": {
                            "strict": {"type": "boolean", "description": "严格模式"},
                            "analyze_complexity": {"type": "boolean", "description": "分析复杂度"},
                            "check_memory": {"type": "boolean", "description": "检查内存"},
                            "check_queries": {"type": "boolean", "description": "检查查询"},
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
                    "bottlenecks_found": {"type": "integer"},
                    "by_severity": {"type": "object"},
                    "performance_score": {"type": "number"},
                    "complexity_analysis": {"type": "object"},
                    "bottlenecks": {"type": "array"},
                    "suggestions": {"type": "array"},
                    "optimization_plan": {"type": "array"},
                    "status": {"type": "string"},
                },
            },
        }
