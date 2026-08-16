"""
tests/conftest.py — 共享测试 fixtures
=====================================
提供所有测试共用的 fixtures：
- manager_url / worker_urls: Agent URL 映射
- sample_task: 示例任务数据
- sample_payload: 示例 payloads 用于各 skill
"""

import pytest
import sys
import os

# 确保 skills 目录在 path 中
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
if SKILLS_DIR not in sys.path:
    sys.path.insert(0, SKILLS_DIR)


# ── Agent URL fixtures ──────────────────────────────────────
BASE_URLS = {
    "manager": "http://localhost:8008",
    "intake": "http://localhost:8001",
    "analyst": "http://localhost:8002",
    "fixer": "http://localhost:8003",
    "verifier": "http://localhost:8004",
    "release": "http://localhost:8005",
    "knowledge": "http://localhost:8006",
    "gateway": "http://localhost:8080",
}


@pytest.fixture
def manager_url():
    """Manager agent URL"""
    return BASE_URLS["manager"]


@pytest.fixture
def worker_urls():
    """所有 Worker URL 映射"""
    return {k: v for k, v in BASE_URLS.items() if k != "manager"}


@pytest.fixture
def all_urls():
    """所有 Agent URL 映射"""
    return BASE_URLS


# ── Sample data fixtures ────────────────────────────────────
@pytest.fixture
def sample_task():
    """示例任务数据"""
    return {
        "task_id": "TEST-TASK-001",
        "source": "manual",
        "raw_payload": {"issue": "login bug", "repo": "test-repo"},
        "priority": "P1",
        "trace_id": "trace-test-001",
    }


@pytest.fixture
def sample_payloads():
    """各 Skill 的示例输入"""
    return {
        "code-review": {"source_code": "x = 1"},
        "test-generation": {"source_code": "def foo(): pass"},
        "doc-writing": {"doc_type": "api", "title": "Test"},
        "security-scan": {"source_code": "SECRET_KEY = os.environ.get('X')"},
        "perf-analysis": {"source_code": "for u in users:\n    q = db.query(u)"},
        "deploy-verification": {"services": ["manager"]},
    }


# ── HTTP helper fixtures ────────────────────────────────────
@pytest.fixture
def http_client():
    """HTTP 请求辅助函数"""
    import urllib.request
    import json

    def get(url: str, timeout: int = 5) -> dict:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {"error": str(e)}

    def post(url: str, data: dict, timeout: int = 10) -> dict:
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {"error": str(e)}

    return {"get": get, "post": post}
