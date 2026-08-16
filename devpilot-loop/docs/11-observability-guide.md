"""
OpenTelemetry Integration Guide
================================
完整的可观测性集成文档
"""

import json
from datetime import datetime, timezone


# Span 命名规范
SPAN_CONVENTIONS = {
    "manager": {
        "dispatch": "devpilot.manager.dispatch_task",
        "approve": "devpilot.manager.approve_task",
        "reject": "devpilot.manager.reject_task",
    },
    "intake": {
        "receive": "devpilot.intake.receive_task",
        "triage": "devpilot.intake.triage",
        "submit_result": "devpilot.intake.submit_result",
    },
    "analyst": {
        "analyze": "devpilot.analyst.analyze",
        "root_cause": "devpilot.analyst.root_cause",
        "submit_result": "devpilot.analyst.submit_result",
    },
    "fixer": {
        "fix": "devpilot.fixer.fix",
        "patch": "devpilot.fixer.patch",
        "submit_result": "devpilot.fixer.submit_result",
    },
    "verifier": {
        "verify": "devpilot.verifier.verify",
        "test": "devpilot.verifier.test",
        "submit_result": "devpilot.verifier.submit_result",
    },
    "release": {
        "canary": "devpilot.release.canary",
        "deploy": "devpilot.release.deploy",
        "submit_result": "devpilot.release.submit_result",
    },
}


# Metric 命名规范
METRIC_CONVENTIONS = {
    "tasks_received": "devpilot.tasks.received",
    "tasks_dispatched": "devpilot.tasks.dispatched",
    "results_submitted": "devpilot.results.submitted",
    "errors": "devpilot.errors.count",
    "processing_time": "devpilot.processing.time_seconds",
}


# Log 级别规范
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
    "AUDIT": 55,
}


def generate_observability_report() -> dict:
    """生成可观测性配置报告"""
    return {
        "project": "DevPilot Loop",
        "tracing": {
            "provider": "OpenTelemetry",
            "fallback": "Console",
            "span_conventions": SPAN_CONVENTIONS,
        },
        "metrics": {
            "provider": "Prometheus",
            "conventions": METRIC_CONVENTIONS,
        },
        "logging": {
            "format": "JSON",
            "levels": LOG_LEVELS,
        },
    }


if __name__ == "__main__":
    report = generate_observability_report()
    print(json.dumps(report, indent=2))
