"""
HiClaw Runtime — 生产级 Manager-Worker 通信框架
===============================================
HiClaw API 兼容的生产级运行时，支持：
  - 健康检查与指标暴露
  - 任务派发与结果提交
  - 结构化日志（JSON）
  - 审计追踪（trace_id 关联）
  - 权限分级（L1/L2/L3）
  - 指标收集（Prometheus 兼容）

每个容器通过 AGENT_NAME、AGENT_TYPE、SKILL_NAME 环境变量区分身份。
Manager (devlead) 运行在端口 8008，Workers 运行在端口 8001-8006。
"""

import json
import os
import sys
import uuid
import logging
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# ── 日志配置 ───────────────────────────────────────────────
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("devpilot.runtime")


# ── 全局状态（线程安全）────────────────────────────────────
_lock = threading.Lock()
_tasks: dict[str, dict[str, Any]] = {}
_results: list[dict[str, Any]] = []
_metrics: dict[str, Any] = {
    "tasks_received": 0,
    "tasks_dispatched": 0,
    "results_submitted": 0,
    "errors": 0,
    "start_time": _now_iso(),
}


# ── 数据模型 ──────────────────────────────────────────────
class TaskRequest(BaseModel):
    """任务请求模型"""
    task_id: str = Field(default_factory=lambda: f"TASK-{uuid.uuid4().hex[:8]}")
    source: str = Field(..., description="任务来源: issue/ci/alert/manual")
    raw_payload: dict[str, Any] = Field(..., description="原始负载数据")
    priority: str = Field("P2", pattern=r"^P[123]$", description="优先级: P1(紧急)/P2(正常)/P3(低)")
    trace_id: str = Field(default="", description="关联的 Trace ID")
    target_worker: str = Field(default="", description="目标 Worker（Manager 派发时必填）")
    approval_required: bool = Field(default=False, description="是否需要人工审批")
    metadata: dict[str, Any] = Field(default_factory=dict, description="附加元数据")


class ResultResponse(BaseModel):
    """结果响应模型"""
    task_id: str
    agent_name: str
    output: dict[str, Any]
    status: str = "ok"  # ok / failed / cancelled / pending_approval
    trace_id: str = ""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list, description="关联证据文件")
    approval_notes: str = Field(default="", description="审批意见")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    agent: str
    type: str
    uptime_seconds: float
    workers_active: int
    tasks_processed: int
    trace_id: str
    version: str = "2.0.0"
    dal_level: str = "DAL-2"
    metrics: dict[str, Any] = Field(default_factory=dict)


class MetricResponse(BaseModel):
    """指标响应"""
    tasks_received: int
    tasks_dispatched: int
    results_submitted: int
    errors: int
    uptime_seconds: float
    memory_usage_mb: Optional[float] = None


# ── 工具函数 ──────────────────────────────────────────────
def _now_iso() -> str:
    """返回 ISO 8601 UTC 时间戳"""
    return datetime.now(timezone.utc).isoformat()


def _generate_trace_id() -> str:
    """生成唯一 Trace ID"""
    return f"trace-{uuid.uuid4().hex[:16]}"


def _audit_event(event_type: str, agent: str, task_id: str, **kwargs) -> dict[str, Any]:
    """记录审计事件"""
    entry = {
        "ts": _now_iso(),
        "level": "AUDIT",
        "agent": agent,
        "type": "runtime",
        "event": event_type,
        "task_id": task_id,
        "trace_id": kwargs.get("trace_id", _generate_trace_id()),
        **kwargs,
    }
    with _lock:
        _results.append(entry)
    logger.info(f"[AUDIT] {event_type} agent={agent} task={task_id} trace={entry['trace_id']}")
    return entry


def _update_metric(key: str, delta: int = 1) -> None:
    """更新指标计数"""
    with _lock:
        _metrics[key] = _metrics.get(key, 0) + delta


# ── 应用工厂 ──────────────────────────────────────────────
def create_app() -> FastAPI:
    """工厂函数：根据环境变量创建对应角色的 FastAPI 实例"""
    agent_name = os.environ.get("AGENT_NAME", "unknown")
    agent_type = os.environ.get("AGENT_TYPE", "worker")
    skill_name = os.environ.get("SKILL_NAME", "")
    permission_level = os.environ.get("PERMISSION_LEVEL", "L1")
    trace_id = os.environ.get("TRACE_ID", _generate_trace_id())

    app = FastAPI(
        title=f"HiClaw {agent_type.capitalize()}: {agent_name}",
        description=f"DevPilot Loop Agent Runtime — {agent_name} ({agent_type})",
        version="2.0.0",
    )
    start_time = datetime.now(timezone.utc)

    # ── 中间件：请求日志 ───────────────────────────────────
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """请求日志中间件"""
        req_id = str(uuid.uuid4())[:8]
        logger.debug(f"[{req_id}] {request.method} {request.url.path}")
        response = await call_next(request)
        logger.debug(f"[{req_id}] → {response.status_code}")
        return response

    # ── 健康检查 ───────────────────────────────────────────
    @app.get("/health", response_model=HealthResponse)
    async def health():
        """服务健康检查端点"""
        return HealthResponse(
            status="healthy",
            agent=agent_name,
            type=agent_type,
            uptime_seconds=(datetime.now(timezone.utc) - start_time).total_seconds(),
            workers_active=len(_tasks),
            tasks_processed=len(_results),
            trace_id=trace_id,
            version="2.0.0",
            dal_level="DAL-2",
            metrics={
                "tasks_received": _metrics.get("tasks_received", 0),
                "tasks_dispatched": _metrics.get("tasks_dispatched", 0),
                "results_submitted": _metrics.get("results_submitted", 0),
                "errors": _metrics.get("errors", 0),
            },
        )

    @app.get("/metrics", response_model=MetricResponse)
    async def metrics():
        """Prometheus 兼容指标端点"""
        try:
            import psutil
            mem = psutil.Process(os.getpid()).memory_info()
        except ImportError:
            mem = None
        return MetricResponse(
            tasks_received=_metrics.get("tasks_received", 0),
            tasks_dispatched=_metrics.get("tasks_dispatched", 0),
            results_submitted=_metrics.get("results_submitted", 0),
            errors=_metrics.get("errors", 0),
            uptime_seconds=(datetime.now(timezone.utc) - start_time).total_seconds(),
            memory_usage_mb=round(mem.rss / 1024 / 1024, 2),
        )

    # ── Worker 端点 ─────────────────────────────────────────
    @app.post("/task")
    async def receive_task(task: TaskRequest):
        """接收来自 Manager 的任务（Worker 端）"""
        try:
            with _lock:
                _tasks[task.task_id] = {
                    "task_id": task.task_id,
                    "source": task.source,
                    "payload": task.raw_payload,
                    "priority": task.priority,
                    "assigned_to": agent_name,
                    "skill": skill_name,
                    "permission_level": permission_level,
                    "status": "received",
                    "trace_id": task.trace_id or _generate_trace_id(),
                    "received_at": _now_iso(),
                }
            _audit_event("task_received", agent_name, task.task_id, skill=skill_name)
            _update_metric("tasks_received")
            return {"status": "ok", "task_id": task.task_id, "trace_id": _tasks[task.task_id]["trace_id"]}
        except Exception as e:
            logger.error(f"Error receiving task: {e}")
            _update_metric("errors")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/result")
    async def submit_result(result: ResultResponse):
        """提交执行结果给 Manager（Worker 端）"""
        try:
            entry = {
                "ts": _now_iso(),
                "level": "INFO",
                "agent": result.agent_name,
                "type": agent_type,
                "event": "result_submitted",
                "task_id": result.task_id,
                "skill": skill_name,
                "output": result.output,
                "status": result.status,
                "trace_id": result.trace_id or _generate_trace_id(),
                "confidence": result.confidence,
                "evidence": result.evidence,
            }
            with _lock:
                _results.append(entry)
            _audit_event("result_submitted", result.agent_name, result.task_id)
            _update_metric("results_submitted")
            return {"status": "ok", "result_id": str(uuid.uuid4()), "trace_id": entry["trace_id"]}
        except Exception as e:
            logger.error(f"Error submitting result: {e}")
            _update_metric("errors")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agents")
    async def list_agents():
        """列出当前 Agent 的任务"""
        my_tasks = [t for t in _tasks.values() if t.get("assigned_to") == agent_name]
        return {"agents": my_tasks, "count": len(my_tasks), "agent": agent_name}

    @app.get("/skills")
    async def list_skills():
        """列出已安装的 Skills"""
        skills = []
        if skill_name:
            skills.append({"name": skill_name, "version": "1.0.0", "agent": agent_name})
        return {"skills": skills, "count": len(skills)}

    @app.get("/logs")
    async def get_logs(limit: int = 50, level: Optional[str] = None):
        """获取执行日志"""
        with _lock:
            logs = _results[-limit:] if limit > 0 else list(_results)
        if level:
            logs = [l for l in logs if l.get("level") == level.upper()]
        return {"logs": logs, "total": len(_results), "filtered": len(logs)}

    # ── Manager 专用端点 ────────────────────────────────────
    if agent_type == "manager":
        @app.post("/dispatch")
        async def dispatch_task(task: TaskRequest):
            """Manager 派发任务到指定 Worker"""
            target_worker = task.target_worker or task.raw_payload.get("target_worker", "")
            if not target_worker:
                raise HTTPException(status_code=400, detail="target_worker required in payload")
            try:
                trace = task.trace_id or _generate_trace_id()
                with _lock:
                    _tasks[task.task_id] = {
                        "task_id": task.task_id,
                        "source": task.source,
                        "payload": task.raw_payload,
                        "priority": task.priority,
                        "target_worker": target_worker,
                        "permission_level": task.raw_payload.get("permission_level", "L1"),
                        "approval_required": task.approval_required,
                        "status": "dispatched",
                        "trace_id": trace,
                        "dispatched_at": _now_iso(),
                        "metadata": task.metadata,
                    }
                _audit_event("task_dispatched", agent_name, task.task_id, target=target_worker, trace=trace)
                _update_metric("tasks_dispatched")
                return {
                    "status": "ok",
                    "task_id": task.task_id,
                    "target": target_worker,
                    "trace_id": trace,
                }
            except Exception as e:
                logger.error(f"Error dispatching task: {e}")
                _update_metric("errors")
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/tasks")
        async def list_tasks(status: Optional[str] = None):
            """查看所有任务"""
            with _lock:
                all_tasks = list(_tasks.values())
            if status:
                all_tasks = [t for t in all_tasks if t.get("status") == status]
            return {"tasks": all_tasks, "count": len(all_tasks)}

        @app.post("/register_worker")
        async def register_worker(name: str = Form(...), worker_type: str = Form("worker")):
            """注册 Worker Agent"""
            _audit_event("worker_registered", agent_name, "", worker=name, type=worker_type)
            return {"status": "ok", "agent": name, "type": worker_type}

        @app.get("/approval")
        async def get_pending_approvals():
            """获取待审批任务"""
            pending = [t for t in _tasks.values() if t.get("approval_required") and t.get("status") == "dispatched"]
            return {"pending": pending, "count": len(pending)}

        @app.post("/approve/{task_id}")
        async def approve_task(task_id: str, notes: str = Form("")):
            """审批任务"""
            with _lock:
                if task_id not in _tasks:
                    raise HTTPException(status_code=404, detail="Task not found")
                _tasks[task_id]["status"] = "approved"
                _tasks[task_id]["approval_notes"] = notes
                _tasks[task_id]["approved_at"] = _now_iso()
            _audit_event("task_approved", agent_name, task_id, notes=notes)
            return {"status": "ok", "task_id": task_id}

        @app.post("/reject/{task_id}")
        async def reject_task(task_id: str, notes: str = Form("")):
            """拒绝任务"""
            with _lock:
                if task_id not in _tasks:
                    raise HTTPException(status_code=404, detail="Task not found")
                _tasks[task_id]["status"] = "rejected"
                _tasks[task_id]["rejection_notes"] = notes
                _tasks[task_id]["rejected_at"] = _now_iso()
            _audit_event("task_rejected", agent_name, task_id, notes=notes)
            return {"status": "ok", "task_id": task_id}

    return app


# ── 模块级 app（供 uvicorn 直接导入）────────────────────────
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8001)))
