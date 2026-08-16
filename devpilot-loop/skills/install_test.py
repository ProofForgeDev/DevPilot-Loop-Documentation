#!/usr/bin/env python3
"""
DevPilot Loop — Skill 安装验证脚本（Python 版）
==============================================
对每个 skill 执行 import + execute() 测试，并运行 pytest。
"""

import sys
import os
import json
import subprocess
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
EVIDENCE_DIR = os.path.join(BASE_DIR, "poc", "evidence", "skills")
PYTHON = os.path.join(BASE_DIR, ".venv", "bin", "python")

PASS = 0
FAIL = 0
LINES = []

def log(msg):
    print(msg)
    LINES.append(msg)

def run_python(code: str) -> str:
    result = subprocess.run([PYTHON, "-c", code], capture_output=True, text=True, cwd=BASE_DIR)
    return result.stdout + result.stderr, result.returncode


# ── Part 1: Import & execute each skill ─────────────────────────
SKILLS = {
    "code-review":     {"dir": "code_review",     "cls": "CodeReviewSkill",     "input": {"source_code": "x = 1"}},
    "test-generation": {"dir": "test_generation", "cls": "TestGenerationSkill", "input": {"source_code": "def foo(): pass"}},
    "doc-writing":     {"dir": "doc_writing",     "cls": "DocWritingSkill",     "input": {"doc_type": "api", "title": "Test"}},
    "security-scan":   {"dir": "security_scan",   "cls": "SecurityScanSkill",   "input": {"source_code": "SECRET_KEY = os.environ.get('X')"}},
    "perf-analysis":   {"dir": "perf_analysis",   "cls": "PerfAnalysisSkill",   "input": {"source_code": "for u in users:\n    q = db.query(u)"}},
    "deploy-verification": {"dir": "deploy_verification", "cls": "DeployVerificationSkill", "input": {"services": ["manager"]}},
    "orchestrator":        {"dir": "orchestrator",        "cls": "OrchestratorSkill",        "input": {"tasks": [{"id": "t1", "skill": "code_review"}]}},
    "lifecycle":           {"dir": "lifecycle",           "cls": "LifecycleSkill",           "input": {"action": "status"}},
}

log("=" * 60)
log(f"  DevPilot Loop — Skill 安装验证")
log(f"  时间: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
log("=" * 60)
log("")

log("【Part 1】各 Skill execute() 测试")
for name, info in SKILLS.items():
    log(f"── {name} ──")
    code = f'''
import sys
sys.path.insert(0, r"{SKILLS_DIR}")
from skills.{info["dir"]}.skill import {info["cls"]}
s = {info["cls"]}()
r = s.execute({json.dumps(info["input"])})
assert r["status"] == "ok", f"status={{r[\"status\"]}}"
print(f"execute OK — name={{s.name}} status={{r[\"status\"]}}")
'''
    out, rc = run_python(code)
    if rc == 0 and "execute OK" in out:
        log(f"  ✓ {out.strip()}")
        PASS += 1
    else:
        log(f"  ✗ {out.strip()}")
        FAIL += 1
    log("")

# ── Part 2: Registry ────────────────────────────────────────────
log("【Part 2】Registry 注册中心")
registry_code = f'''
import sys
sys.path.insert(0, r"{SKILLS_DIR}")
from skills.registry import list_skills, get_skill, get_skill_count
count = get_skill_count()
print(f"registry count: {{count}}")
assert count == 8, f"expected 8, got {{count}}"
for s in list_skills():
    inst = get_skill(s["name"])
    print(f"  found: {{s[\"name\"]}} v{{s[\"version\"]}}")
print("registry OK")
'''
out, rc = run_python(registry_code)
if rc == 0 and "registry OK" in out:
    log(f"  ✓ Registry 发现全部 {out.count('found:')} 个 Skill")
    for line in out.strip().split("\n"):
        log(f"    {line}")
    PASS += 1
else:
    log(f"  ✗ Registry 失败: {out.strip()}")
    FAIL += 1
log("")

# ── Part 3: Pytest ──────────────────────────────────────────────
log("【Part 3】Pytest 测试套件")
result = subprocess.run(
    [PYTHON, "-m", "pytest", SKILLS_DIR, "-v", "--tb=short"],
    capture_output=True, text=True, cwd=BASE_DIR
)
pytest_out = result.stdout + result.stderr
log(pytest_out)
if result.returncode == 0:
    log("  ✓ Pytest 全部通过")
    PASS += 1
else:
    log("  ✗ 部分测试失败")
    FAIL += 1
log("")

# ── Summary ─────────────────────────────────────────────────────
log("=" * 60)
log(f"  结果: {PASS} passed, {FAIL} failed")
log("=" * 60)

# Save evidence
install_output_path = os.path.join(EVIDENCE_DIR, "L4_install_test_output.txt")
with open(install_output_path, "w") as f:
    f.write("\n".join(LINES))

log(f"\n证据已保存: {install_output_path}")

sys.exit(0 if FAIL == 0 else 1)
