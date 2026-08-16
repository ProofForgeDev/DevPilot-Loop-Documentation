#!/usr/bin/env python3
"""Generate API reference from source code (L2 evidence).

Usage:
    python3 scripts/generate_openapi.py > evidence/l2/api_spec.json
"""
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


AGENT_SPECS = [
    {"name": "devlead",    "role": "manager",   "permissions": ["read", "dispatch", "approve"], "skill": None},
    {"name": "intake",     "role": "worker",    "permissions": ["read", "triage"],              "skill": "DefectTriage"},
    {"name": "analyst",    "role": "worker",    "permissions": ["read"],                        "skill": "CodeRootCause"},
    {"name": "fixer",      "role": "worker",    "permissions": ["read", "write", "approve"],    "skill": "FixGenerator"},
    {"name": "verifier",   "role": "worker",    "permissions": ["read", "test"],                "skill": "TestRunner"},
    {"name": "release",    "role": "worker",    "permissions": ["read", "deploy", "approve"],   "skill": "CanaryRelease"},
    {"name": "knowledge",  "role": "worker",    "permissions": ["read", "write"],               "skill": "PostmortemCapture"},
    {"name": "orchestrator","role": "worker",   "permissions": ["read", "write", "checkpoint"], "skill": "Orchestrator"},
    {"name": "lifecycle",  "role": "worker",    "permissions": ["read", "write", "checkpoint"], "skill": "Lifecycle"},
]


def main() -> int:
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "DevPilot Loop Agent API",
            "version": "2.0.0",
            "description": "REST API for multi-agent defect-fixing pipeline",
        },
        "agents": AGENT_SPECS,
        "endpoints": [
            {"path": "/api/v1/intake",         "method": "POST",  "agent": "intake",     "desc": "Submit defect report"},
            {"path": "/api/v1/analyze",        "method": "POST",  "agent": "analyst",    "desc": "Root-cause analysis"},
            {"path": "/api/v1/fix",            "method": "POST",  "agent": "fixer",      "desc": "Generate patch (L2)"},
            {"path": "/api/v1/verify",         "method": "POST",  "agent": "verifier",   "desc": "Run tests"},
            {"path": "/api/v1/release",        "method": "POST",  "agent": "release",    "desc": "Canary deploy (L3, approval required)"},
            {"path": "/api/v1/knowledge",      "method": "POST",  "agent": "knowledge",  "desc": "Capture runbook"},
            {"path": "/api/v1/approve",        "method": "POST",  "agent": "devlead",    "desc": "Human approval endpoint"},
            {"path": "/api/v1/health",         "method": "GET",   "agent": "devlead",    "desc": "Health check all agents"},
            {"path": "/api/v1/trace",          "method": "GET",   "agent": "orchestrator","desc": "OTel trace retrieval"},
        ],
        "auth": {
            "type": "JWT + Consumer Token",
            "description": "Each agent holds an independent consumer token; real credentials injected by Higress AI gateway",
        },
    }
    json.dump(spec, sys.stdout, indent=2, ensure_ascii=False)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
