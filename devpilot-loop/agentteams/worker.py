"""AgentWorker — Worker Agent 实现"""
import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger("devpilot.worker")

class AgentWorker:
    """AgentTeams 兼容的 Worker 实现"""
    
    def __init__(self, name: str, skill=None, port: int = 8001):
        self.name = name
        self.skill = skill
        self.port = port
        self._results: Dict[str, Dict] = {}
    
    def receive(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """接收并执行任务"""
        start = time.perf_counter()
        try:
            output = self.skill.execute(task.get("payload", {})) if self.skill else {"status": "ok", "result": "noop"}
            elapsed = (time.perf_counter() - start) * 1000
            result = {
                "task_id": task.get("task_id", ""),
                "agent": self.name,
                "status": output.get("status", "ok"),
                "output": output,
                "elapsed_ms": round(elapsed, 2),
            }
            self._results[task.get("task_id", "")] = result
            logger.info(f"Worker {self.name} completed in {elapsed:.1f}ms")
            return result
        except Exception as e:
            logger.error(f"Worker {self.name} failed: {e}")
            return {"task_id": task.get("task_id", ""), "status": "error", "error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        return {"agent": self.name, "status": "healthy", "port": self.port}
