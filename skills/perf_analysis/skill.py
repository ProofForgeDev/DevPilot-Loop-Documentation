"""性能分析 Skill — perf-analysis
==================================
分析代码性能瓶颈，检测潜在的 N+1 查询、内存泄漏、低效算法。
"""

from skills.base import BaseSkill


class PerfAnalysisSkill(BaseSkill):
    name = "perf-analysis"
    version = "1.0.0"
    description = "性能分析：瓶颈检测、N+1 查询识别、优化建议"

    def execute(self, input_data: dict) -> dict:
        source_code = input_data.get("source_code", "")
        file_path = input_data.get("file_path", "unknown")

        bottlenecks = []
        lines = source_code.splitlines()

        # 性能规则检查
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # 循环内数据库查询
            if stripped.startswith("for ") and i < len(lines):
                next_line = lines[i].strip()  # i is 1-based, lines is 0-based → lines[i] is next line
                if any(kw in next_line.lower() for kw in ["query", "select", "get(", "save(", "all()"]):
                    bottlenecks.append({
                        "line": i, "severity": "HIGH",
                        "type": "n_plus_one",
                        "msg": "Potential N+1 query inside loop",
                    })
            # 全表扫描
            if "objects.all()" in stripped or ".all()" in stripped:
                bottlenecks.append({
                    "line": i, "severity": "MEDIUM",
                    "type": "full_table_scan",
                    "msg": "Full table scan detected (no pagination)",
                })
            # 大对象加载
            if "read()" in stripped and "binary" not in stripped.lower():
                bottlenecks.append({
                    "line": i, "severity": "LOW",
                    "type": "memory",
                    "msg": "Potential large object loaded into memory",
                })
            # 缺少缓存标记
            if "cache" not in source_code.lower() and ("query" in source_code.lower() or "select" in source_code.lower()):
                if i == 1:
                    bottlenecks.append({
                        "line": 1, "severity": "INFO",
                        "type": "caching",
                        "msg": "No caching mechanism detected",
                    })

        return {
            "skill": self.name,
            "version": self.version,
            "file": file_path,
            "bottlenecks_found": len(bottlenecks),
            "bottlenecks": bottlenecks,
            "suggestions": self._gen_suggestions(bottlenecks),
            "status": "ok",
        }

    def _gen_suggestions(self, bottlenecks: list) -> list:
        suggestions = []
        types_found = {b["type"] for b in bottlenecks}
        if "n_plus_one" in types_found:
            suggestions.append("Use prefetch_related() or select_related() to reduce queries")
        if "full_table_scan" in types_found:
            suggestions.append("Add pagination or limiting to large querysets")
        if "caching" in types_found:
            suggestions.append("Consider adding Redis/cache layer for frequent queries")
        return suggestions

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
                },
            },
            "output": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string"},
                    "bottlenecks_found": {"type": "integer"},
                    "bottlenecks": {"type": "array"},
                    "suggestions": {"type": "array"},
                    "status": {"type": "string"},
                },
            },
        }
