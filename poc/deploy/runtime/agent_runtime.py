"""
HiClaw Runtime — 最小化 Manager-Worker 通信框架
===============================================
模拟 HiClaw 的 HTTP API：
  GET  /health          — 健康检查
  POST /task            — 接收任务（Worker 端）
  POST /result          — 提交结果（Worker 端）
  GET  /agents          — 列出所有 Agent
  GET  /skills          — 列出已安装的 Skills
  POST /dispatch        — 派发任务（Manager 端）
  GET  /tasks           — 查看任务（Manager 端）
  GET  /logs            — 执行日志

每个容器通过 AGENT_NAME 和 AGENT_TYPE 环境变量区分身份。
Manager (devlead) 运行在端口 8008，Workers 运行在端口 8001-8006。
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel, Field

# ── 全局状态（单机 PoC 模式，内存存储）─────────────────────────
_tasks: dict = {}
_results: list = []


class TaskRequest(BaseModel):
    task_id: str = Field(default_factory=lambda: f"TASK-{uuid.uuid4().hex[:8]}")
    source: str
    raw_payload: dict
    priority: str = "P2"
    trace_id: str = ""


class ResultResponse(BaseModel):
    task_id: str
    agent_name: str
    output: dict
    status: str = "ok"
    trace_id: str = ""


class HealthResponse(BaseModel):
    status: str
    agent: str
    type: str
    uptime_seconds: float = 0.0
    workers_active: int = 0
    tasks_processed: int = 0
    trace_id: str = ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_app() -> FastAPI:
    """工厂函数：根据环境变量创建对应角色的 FastAPI 实例"""
    agent_name = os.environ.get("AGENT_NAME", "unknown")
    agent_type = os.environ.get("AGENT_TYPE", "worker")
    skill_name = os.environ.get("SKILL_NAME", "")

    app = FastAPI(title=f"HiClaw {agent_type.capitalize()}: {agent_name}")
    start_time = datetime.now(timezone.utc)

    @app.get("/health", response_model=HealthResponse)
    async def health():
        return HealthResponse(
            status="healthy",
            agent=agent_name,
            type=agent_type,
            uptime_seconds=(datetime.now(timezone.utc) - start_time).total_seconds(),
            workers_active=len(_tasks),
            tasks_processed=len(_results),
            trace_id=os.environ.get("TRACE_ID", ""),
        )

    @app.post("/task")
    async def receive_task(task: TaskRequest):
        """接收来自 Manager 的任务（Worker 端）"""
        _tasks[task.task_id] = {
            "task_id": task.task_id,
            "source": task.source,
            "payload": task.raw_payload,
            "priority": task.priority,
            "assigned_to": agent_name,
            "status": "received",
            "trace_id": task.trace_id,
            "received_at": _now_iso(),
        }
        _results.append({
            "ts": _now_iso(), "level": "INFO",
            "agent": agent_name, "type": agent_type,
            "event": "task_received",
            "task_id": task.task_id, "skill": skill_name,
        })
        return {"status": "ok", "task_id": task.task_id}

    @app.post("/result")
    async def submit_result(result: ResultResponse):
        """提交执行结果给 Manager（Worker 端）"""
        _results.append({
            "ts": _now_iso(), "level": "INFO",
            "agent": result.agent_name, "type": agent_type,
            "event": "result_submitted",
            "task_id": result.task_id, "skill": skill_name,
            "output": result.output, "status": result.status,
            "trace_id": result.trace_id,
        })
        return {"status": "ok", "result_id": str(uuid.uuid4())}

    @app.get("/agents")
    async def list_agents():
        return {"agents": list(_tasks.keys()), "count": len(_tasks)}

    @app.get("/skills")
    async def list_skills():
        return {"skills": [{"name": skill_name, "version": "0.1.0"}] if skill_name else []}

    @app.get("/logs")
    async def get_logs(limit: int = 50):
        return {"logs": _results[-limit:], "total": len(_results)}

    # ── Manager 专用端点 ────────────────────────────────────────
    if agent_type == "manager":
        @app.post("/dispatch")
        async def dispatch_task(task: TaskRequest):
            """Manager 派发任务到指定 Worker"""
            target_worker = task.raw_payload.get("target_worker", "")
            if not target_worker:
                raise HTTPException(status_code=400, detail="target_worker required")
            _tasks[task.task_id] = {
                "task_id": task.task_id, "source": task.source,
                "payload": task.raw_payload, "priority": task.priority,
                "target_worker": target_worker, "status": "dispatched",
                "trace_id": task.trace_id, "dispatched_at": _now_iso(),
            }
            _results.append({
                "ts": _now_iso(), "level": "INFO",
                "agent": agent_name, "type": "manager",
                "event": "task_dispatched",
                "task_id": task.task_id,
                "target_worker": target_worker,
                "trace_id": task.trace_id,
            })
            return {"status": "ok", "task_id": task.task_id, "target": target_worker}

        @app.get("/tasks")
        async def list_tasks():
            return {"tasks": list(_tasks.values()), "count": len(_tasks)}

        @app.post("/register_worker")
        async def register_worker(name: str = Form(...)):
            return {"status": "ok", "agent": name}

    return app


# ── 模块级 app（供 uvicorn 直接导入）────────────────────────────
app = create_app()
