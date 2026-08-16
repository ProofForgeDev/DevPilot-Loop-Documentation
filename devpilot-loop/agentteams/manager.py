"""AgentManager — 任务编排核心"""
import logging
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger("devpilot.agentteams")

class AgentManager:
    """AgentTeams 兼容的 Manager 实现"""
    
    def __init__(self, name: str, workers: List['AgentWorker'] = None):
        self.name = name
        self.workers = workers or []
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._trace_id = str(uuid.uuid4())[:16]
    
    def dispatch(self, task: Dict[str, Any]) -> str:
        """派发任务到 Worker"""
        task_id = f"TASK-{uuid.uuid4().hex[:8]}"
        self._tasks[task_id] = {
            "task_id": task_id,
            "plan": task.get("plan", []),
            "status": "dispatched",
            "trace_id": self._trace_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        logger.info(f"Manager {self.name} dispatched {task_id}")
        return task_id
    
    def get_status(self, task_id: str) -> Optional[Dict]:
        return self._tasks.get(task_id)
    
    def get_all_tasks(self) -> Dict[str, Dict]:
        return self._tasks
