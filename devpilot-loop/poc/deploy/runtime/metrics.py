"""
Prometheus Metrics Endpoint
============================
暴露 /metrics 端点，兼容 Prometheus scrape 格式。
"""
import time
import threading
from datetime import datetime, timezone

_metrics_lock = threading.Lock()
_metrics = {
    "agent_dispatch_total": 0,
    "agent_dispatch_success": 0,
    "agent_dispatch_error": 0,
    "skill_execute_total": 0,
    "skill_execute_success": 0,
    "skill_execute_error": 0,
    "llm_calls_total": 0,
    "llm_calls_error": 0,
    "http_request_duration_seconds": {},
    "process_cpu_seconds_total": 0.0,
    "process_resident_memory_bytes": 0,
}

_metric_help = {
    "agent_dispatch_total": "Total number of agent task dispatches",
    "agent_dispatch_success": "Successful agent task dispatches",
    "agent_dispatch_error": "Failed agent task dispatches",
    "skill_execute_total": "Total number of skill executions",
    "skill_execute_success": "Successful skill executions",
    "skill_execute_error": "Failed skill executions",
    "llm_calls_total": "Total LLM API calls",
    "llm_calls_error": "Failed LLM API calls",
}


def inc(metric: str, value: int = 1):
    with _metrics_lock:
        _metrics[metric] = _metrics.get(metric, 0) + value


def set_metric(metric: str, value: float):
    with _metrics_lock:
        _metrics[metric] = value


def get_metrics_text() -> str:
    """返回 Prometheus 格式的 metrics"""
    lines = []
    lines.append("# HELP agent_dispatch_total Total agent task dispatches")
    lines.append("# TYPE agent_dispatch_total counter")
    lines.append(f'agent_dispatch_total {{}} {_metrics["agent_dispatch_total"]}')
    
    lines.append("# HELP agent_dispatch_success Successful dispatches")
    lines.append("# TYPE agent_dispatch_success counter")
    lines.append(f'agent_dispatch_success {{}} {_metrics["agent_dispatch_success"]}')
    
    lines.append("# HELP skill_execute_total Total skill executions")
    lines.append("# TYPE skill_execute_total counter")
    lines.append(f'skill_execute_total {{}} {_metrics["skill_execute_total"]}')
    
    lines.append("# HELP skill_execute_success Successful skill executions")
    lines.append("# TYPE skill_execute_success counter")
    lines.append(f'skill_execute_success {{}} {_metrics["skill_execute_success"]}')
    
    lines.append("# HELP llm_calls_total Total LLM calls")
    lines.append("# TYPE llm_calls_total counter")
    lines.append(f'llm_calls_total {{}} {_metrics["llm_calls_total"]}')
    
    lines.append("# HELP devpilot_uptime_seconds Agent uptime in seconds")
    lines.append("# TYPE devpilot_uptime_seconds gauge")
    lines.append(f'devpilot_uptime_seconds {{}} {time.time() - _START_TIME}')
    
    lines.append("")
    lines.append(f"# Generated at: {datetime.now(timezone.utc).isoformat()}")
    return "\n".join(lines)


_START_TIME = time.time()
