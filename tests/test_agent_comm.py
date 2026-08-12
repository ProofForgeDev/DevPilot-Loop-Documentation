"""
测试 Manager-Worker 通信链路
============================
验证 Manager 可以派发任务到 Worker，Worker 可以提交结果。
运行方式：
    python3 -m pytest tests/test_agent_comm.py -v
    或：python3 tests/test_agent_comm.py
"""

import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

BASE_URLS = {
    "manager": "http://localhost:8008",
    "intake": "http://localhost:8001",
    "analyst": "http://localhost:8002",
    "fixer": "http://localhost:8003",
    "verifier": "http://localhost:8004",
    "release": "http://localhost:8005",
    "knowledge": "http://localhost:8006",
}


def http_get(url: str) -> dict:
    """发送 GET 请求并返回 JSON"""
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def http_post(url: str, data: dict) -> dict:
    """发送 POST 请求并返回 JSON"""
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def test_health(manager_url: str, workers: dict) -> bool:
    """Test 1: 所有 Agent 健康检查"""
    results = {}
    all_healthy = True
    for name, url in manager_url.items():
        health = http_get(f"{url}/health")
        ok = health.get("status") == "healthy"
        results[name] = ok
        if not ok:
            all_healthy = False
    return all_healthy, results


def test_manager_dispatch(manager_url: str) -> bool:
    """Test 2: Manager 派发任务到 Intake"""
    task = {
        "source": "issue",
        "raw_payload": {
            "target_worker": "intake",
            "issue_title": "NPE in UserService.getUserName",
            "priority": "P1",
        },
        "priority": "P1",
    }
    resp = http_post(f"{manager_url}/dispatch", task)
    if "error" in resp:
        return False, resp
    return True, resp


def test_worker_receive(manager_url: str, worker_url: str, worker_name: str) -> bool:
    """Test 3: Worker 接收任务"""
    task = {
        "source": "manager_dispatch",
        "raw_payload": {"from": "devlead", "worker": worker_name},
        "priority": "P1",
    }
    resp = http_post(f"{worker_url}/task", task)
    if "error" in resp:
        return False, resp
    task_id = resp.get("task_id", "")
    return bool(task_id), resp


def test_worker_result(manager_url: str, worker_url: str, worker_name: str) -> bool:
    """Test 4: Worker 提交结果"""
    result = {
        "task_id": f"TASK-{int(time.time())}",
        "agent_name": worker_name,
        "output": {"defect_id": "DEF-TEST-001", "severity": "P1", "confidence": 0.95},
        "status": "ok",
    }
    resp = http_post(f"{worker_url}/result", result)
    if "error" in resp:
        return False, resp
    return True, resp


def test_manager_tasks(manager_url: str) -> bool:
    """Test 5: Manager 查看任务列表"""
    resp = http_get(f"{manager_url}/tasks")
    if "error" in resp:
        return False, resp
    return True, resp


def run_all_tests() -> dict:
    """运行所有测试，返回结果汇总"""
    output = []
    output.append("=" * 60)
    output.append("DevPilot Loop — Agent 通信测试报告")
    output.append(f"时间: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    output.append("=" * 60)
    output.append("")

    all_passed = True

    # Test 1: Health checks
    output.append("【测试 1】Agent 健康检查")
    healthy, results = test_health(BASE_URLS, BASE_URLS)
    passed1 = healthy
    all_passed &= passed1
    for name, ok in results.items():
        icon = "✓" if ok else "✗"
        output.append(f"  {icon} {name}: {'healthy' if ok else 'unhealthy'}")
    output.append(f"  结果: {'PASS' if passed1 else 'FAIL'}")
    output.append("")

    # Test 2: Manager dispatch
    output.append("【测试 2】Manager 派发任务到 Intake")
    passed2, resp2 = test_manager_dispatch(BASE_URLS["manager"])
    all_passed &= passed2
    icon2 = "✓" if passed2 else "✗"
    output.append(f"  {icon2} dispatch 响应: {json.dumps(resp2, ensure_ascii=False, indent=2)}")
    output.append(f"  结果: {'PASS' if passed2 else 'FAIL'}")
    output.append("")

    # Test 3: Worker receive
    output.append("【测试 3】Worker (Intake) 接收任务")
    passed3, resp3 = test_worker_receive(BASE_URLS["manager"], BASE_URLS["intake"], "intake")
    all_passed &= passed3
    icon3 = "✓" if passed3 else "✗"
    output.append(f"  {icon3} receive 响应: {json.dumps(resp3, ensure_ascii=False, indent=2)}")
    output.append(f"  结果: {'PASS' if passed3 else 'FAIL'}")
    output.append("")

    # Test 4: Worker result
    output.append("【测试 4】Worker (Intake) 提交结果")
    passed4, resp4 = test_worker_result(BASE_URLS["manager"], BASE_URLS["intake"], "intake")
    all_passed &= passed4
    icon4 = "✓" if passed4 else "✗"
    output.append(f"  {icon4} result 响应: {json.dumps(resp4, ensure_ascii=False, indent=2)}")
    output.append(f"  结果: {'PASS' if passed4 else 'FAIL'}")
    output.append("")

    # Test 5: Manager tasks list
    output.append("【测试 5】Manager 任务列表")
    passed5, resp5 = test_manager_tasks(BASE_URLS["manager"])
    all_passed &= passed5
    icon5 = "✓" if passed5 else "✗"
    output.append(f"  {icon5} tasks 响应: {json.dumps(resp5, ensure_ascii=False, indent=2)}")
    output.append(f"  结果: {'PASS' if passed5 else 'FAIL'}")
    output.append("")

    # Summary
    output.append("=" * 60)
    total_tests = 5
    passed_count = sum([passed1, passed2, passed3, passed4, passed5])
    output.append(f"总结: {passed_count}/{total_tests} 通过")
    output.append(f"整体结果: {'ALL TESTS PASSED ✓' if all_passed else 'SOME TESTS FAILED ✗'}")
    output.append("=" * 60)

    return "\n".join(output)


if __name__ == "__main__":
    result = run_all_tests()
    print(result)
    # 写入证据文件
    evidence_dir = "poc/deploy/evidence"
    import os
    os.makedirs(evidence_dir, exist_ok=True)
    with open(f"{evidence_dir}/L2_agent_comm_test.txt", "w") as f:
        f.write(result)
    print(f"\n证据已保存到 {evidence_dir}/L2_agent_comm_test.txt")
