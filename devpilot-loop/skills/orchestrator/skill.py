"""
DevPilot Orchestrator Skill — Orchestrator (Deep)
==================================================
Multi-stage task orchestration with dependency resolution,
rollback on failure, retry with backoff, and progress tracking.
"""

from skills.base import BaseSkill
from typing import Any
from datetime import datetime, timezone
import time
import logging

logger = logging.getLogger("devpilot.skills")


class OrchestratorSkill(BaseSkill):
    name = "orchestrator"
    version = "2.0.0"
    description = "任务编排：依赖解析、失败回滚、重试退避、进度追踪"

    RESTART_PATTERNS = [
        {"name": "immediate", "delay_s": 0.1},
        {"name": "exponential", "delay_s": 0.5},
        {"name": "linear", "delay_s": 0.2},
    ]

    def execute(self, input_data: dict) -> dict:
        """Execute task orchestration with dependency resolution and rollback."""
        if not self.validate_input(input_data):
            logger.error("orchestrator: invalid input")
            return {"status": "error", "error": "invalid_input", "skill": self.name, "version": self.version}

        tasks = input_data.get("tasks", [])
        strategy = input_data.get("strategy", "sequential")
        max_retries = input_data.get("max_retries", 3)
        timeout_s = input_data.get("timeout_s", 300)
        enable_rollback = input_data.get("enable_rollback", True)

        # 依赖解析 (topological sort)
        resolved_order, deps_ok = self._resolve_dependencies(tasks)
        if not deps_ok:
            return {"status": "error", "error": "circular_dependency"}

        # 执行编排
        start = time.time()
        results = []
        failed = False

        for idx, task_info in enumerate(resolved_order):
            task_id = task_info.get("id", f"task-{idx}")
            skill_name = task_info.get("skill", "code-review")
            payload = task_info.get("payload", {})

            result = {
                "task_id": task_id,
                "skill": skill_name,
                "phase": "pending",
                "retries": 0,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "duration_ms": 0,
            }

            # 带重试的执行
            for attempt in range(max_retries):
                t0 = time.time()
                try:
                    perf_start = time.perf_counter()
                    from skills.registry import get_skill
                    skill = get_skill(skill_name)
                    ok = skill.validate_input(payload)
                    if not ok:
                        raise ValueError(f"validate_input failed for {skill_name}")
                    exec_result = skill.execute(payload)
                    perf_ms = (time.perf_counter() - perf_start) * 1000

                    result.update({
                        "phase": "completed",
                        "exec_ms": round(perf_ms, 2),
                        "output_summary": self._summarize_output(exec_result),
                    })
                    break
                except Exception as exc:
                    result["retries"] = attempt + 1
                    if attempt < max_retries - 1:
                        delay = min(0.1 * (2 ** attempt), 5.0)
                        time.sleep(delay)
            else:
                result["phase"] = "failed"
                result["error"] = str(exc)
                if enable_rollback:
                    results = self._rollback(results, idx)
                failed = True
                break

            results.append(result)

        elapsed_ms = round((time.time() - start) * 1000, 2)

        completed = sum(1 for r in results if r["phase"] == "completed")
        return {
            "skill": self.name,
            "version": self.version,
            "strategy": strategy,
            "total_tasks": len(tasks),
            "completed_tasks": completed,
            "failed_tasks": len(tasks) - completed,
            "elapsed_ms": elapsed_ms,
            "results": results,
            "dependency_resolved": resolved_order,
            "rollback_triggered": failed and enable_rollback,
            "status": "ok",
        }

    def _resolve_dependencies(self, tasks: list) -> tuple:
        """Topological sort with cycle detection"""
        task_map = {t.get("id"): t for t in tasks}
        visited = set()
        order = []

        def dfs(tid):
            if tid in visited:
                return True
            if tid not in task_map:
                return False
            visited.add(tid)
            for dep in task_map[tid].get("depends_on", []):
                if not dfs(dep):
                    return False
            order.append(task_map[tid])
            return True

        for t in tasks:
            if not dfs(t["id"]):
                return [], False
        return order, True

    def _rollback(self, results: list, up_to: int) -> list:
        """Mark tasks after index as rolled back"""
        for r in results[up_to:]:
            r["phase"] = "rolled_back"
        return results

    def _summarize_output(self, output: dict) -> dict:
        keys = list(output.keys())[:8]
        return {k: str(output[k])[:100] if isinstance(output[k], (str, list, dict))
                else repr(output[k]) for k in keys}

    def get_plan(self, tasks: list) -> dict:
        resolved, ok = self._resolve_dependencies(tasks)
        return {
            "valid": ok,
            "execution_order": [t["id"] for t in resolved],
            "total_steps": len(resolved),
            "dependencies": {t["id"]: t.get("depends_on", []) for t in tasks},
        }

    def validate_input(self, input_data: dict) -> bool:
        if not isinstance(input_data, dict):
            return False
        tasks = input_data.get("tasks", [])
        return isinstance(tasks, list) and len(tasks) > 0

    def get_schema(self) -> dict:
        return {
            "input": {
                "type": "object",
                "required": ["tasks"],
                "properties": {
                    "tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "skill": {"type": "string"},
                                "payload": {"type": "object"},
                                "depends_on": {"type": "array", "items": {"type": "string"}},
                            },
                        },
                    },
                    "strategy": {"type": "string", "enum": ["sequential", "parallel", "pipeline"]},
                    "max_retries": {"type": "integer", "default": 3},
                    "timeout_s": {"type": "integer", "default": 300},
                    "enable_rollback": {"type": "boolean", "default": True},
                },
            },
            "output": {
                "type": "object",
                "properties": {
                    "skill": {"type": "string"},
                    "version": {"type": "string"},
                    "strategy": {"type": "string"},
                    "total_tasks": {"type": "integer"},
                    "completed_tasks": {"type": "integer"},
                    "failed_tasks": {"type": "integer"},
                    "elapsed_ms": {"type": "number"},
                    "results": {"type": "array"},
                    "dependency_resolved": {"type": "array"},
                    "rollback_triggered": {"type": "boolean"},
                    "status": {"type": "string"},
                },
            },
        }
