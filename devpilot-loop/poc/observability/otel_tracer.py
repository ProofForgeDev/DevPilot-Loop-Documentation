"""
OTel Tracer — OpenTelemetry 集成
================================
提供：
- Trace 生成与传播
- Span 命名规范
- 结构化日志
- Metrics 导出
"""

import os
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Callable
from contextlib import contextmanager

logger = logging.getLogger("devpilot.otel")

# 尝试导入 OTel，如果不可用则使用 fallback
try:
    from opentelemetry import trace, metrics
    from opentelemetry.trace import SpanKind
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
    USE_OTEL = True
except ImportError:
    USE_OTEL = False


class FallbackTracer:
    """OpenTelemetry 不可用时的 fallback 追踪器"""

    def start_span(self, name: str, **kwargs):
        return FallbackSpan(name, **kwargs)

    def get_tracer(self, name: str):
        return self

    @contextmanager
    def start_as_current_span(self, name: str, **kwargs):
        span = FallbackSpan(name, **kwargs)
        try:
            yield span
        finally:
            span.end()


class FallbackSpan:
    """Fallback span 实现"""

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.start_time = time.time()
        self.attributes: dict[str, Any] = kwargs
        self._ended = False

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def end(self) -> None:
        self._ended = True
        elapsed = time.time() - self.start_time
        log_entry = {
            "event": "span_end",
            "span_name": self.name,
            "duration_seconds": round(elapsed, 3),
            "attributes": self.attributes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        logger.info(json.dumps(log_entry, default=str))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.end()


# 初始化 tracer
if USE_OTEL:
    provider = TracerProvider()
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer("devpilot-loop")
else:
    tracer = FallbackTracer()


class TraceManager:
    """Trace 管理器 — 统一 trace/span 操作"""

    def __init__(self):
        self._traces: dict[str, dict] = {}

    def create_trace(self, trace_id: Optional[str] = None) -> str:
        """创建新 Trace"""
        tid = trace_id or f"trace-{uuid.uuid4().hex[:16]}"
        self._traces[tid] = {
            "trace_id": tid,
            "created_at": _now_iso(),
            "spans": [],
            "status": "active",
        }
        logger.info(f"Trace created: {tid}")
        return tid

    def get_trace(self, trace_id: str) -> Optional[dict]:
        """获取 Trace 信息"""
        return self._traces.get(trace_id)

    def add_span(self, trace_id: str, span_data: dict) -> None:
        """添加 Span 到 Trace"""
        if trace_id in self._traces:
            self._traces[trace_id]["spans"].append(span_data)

    def end_trace(self, trace_id: str, status: str = "completed") -> None:
        """结束 Trace"""
        if trace_id in self._traces:
            self._traces[trace_id]["status"] = status
            self._traces[trace_id]["ended_at"] = _now_iso()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# 全局单例
_trace_manager = TraceManager()


def get_trace_manager() -> TraceManager:
    return _trace_manager


def instrument_agent(agent_name: str, agent_type: str) -> Callable:
    """装饰器：自动为 Agent 方法添加 trace"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            trace_id = kwargs.get("trace_id") or _trace_manager.create_trace()
            span_name = f"agent.{agent_type}.{agent_name}.{func.__name__}"
            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("agent.name", agent_name)
                span.set_attribute("agent.type", agent_type)
                span.set_attribute("trace.id", trace_id)
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("result.status", "ok")
                    return result
                except Exception as e:
                    span.set_attribute("result.status", "error")
                    span.set_attribute("error.message", str(e))
                    raise
        return wrapper
    return decorator


# 快速验证
if __name__ == "__main__":
    tm = get_trace_manager()
    tid = tm.create_trace()
    print(f"Trace created: {tid}")
    print(f"Fallback tracer active: {not USE_OTEL}")
    print("OTel Module: OK")
