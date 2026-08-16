"""
DevPilot Loop — 场景编排器（Orchestrator）
============================================
按顺序调用 Step 1-6，记录每步耗时，生成完整报告。
"""

import json
import time
import os
import sys
from datetime import datetime, timezone

# 添加 scenario 目录到路径
SCENARIO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCENARIO_DIR)

EVIDENCE_DIR = os.path.join(SCENARIO_DIR, "..", "evidence", "scenario")
os.makedirs(EVIDENCE_DIR, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_orchestrator():
    """运行完整的 DevPilot Loop 编排"""

    print("=" * 70)
    print("  DevPilot Loop — 端到端场景编排器")
    print("  场景: Flask 登录模块安全修复")
    print(f"  时间: {now_iso()}")
    print("=" * 70)

    overall_start = time.time()
    step_results = []
    all_output_files = []

    # ── Step 1: Intake ─────────────────────────────────────────────────
    print("\n[1/6] Intake Agent — 接收并解析任务...")
    t0 = time.time()
    from e2e_demo import step_intake
    result = step_intake()
    step_results.append({"step": "intake", "elapsed_sec": time.time() - t0, "result": result})
    if result["status"] == "ok":
        all_output_files.append(result["output"])

    # ── Step 2: Analyst ────────────────────────────────────────────────
    print("\n[2/6] Analyst Agent — 扫描代码发现缺陷...")
    t1 = time.time()
    from e2e_demo import step_analyst
    result = step_analyst()
    step_results.append({"step": "analyst", "elapsed_sec": time.time() - t1, "result": result})
    if result["status"] == "ok":
        all_output_files.append(result["output"])

    # ── Step 3: Fixer ──────────────────────────────────────────────────
    print("\n[3/6] Fixer Agent — 生成修复补丁...")
    t2 = time.time()
    from e2e_demo import step_fixer
    result = step_fixer()
    step_results.append({"step": "fixer", "elapsed_sec": time.time() - t2, "result": result})
    if result["status"] == "ok":
        all_output_files.append(result["output"])

    # ── Step 4: Verifier ───────────────────────────────────────────────
    print("\n[4/6] Verifier Agent — 验证修复结果...")
    t3 = time.time()
    from e2e_demo import step_verifier
    result = step_verifier()
    step_results.append({"step": "verifier", "elapsed_sec": time.time() - t3, "result": result})
    if result["status"] == "ok":
        all_output_files.append(result["output"])

    # ── Step 5: Release ────────────────────────────────────────────────
    print("\n[5/6] Release Agent — 生成发布说明...")
    t4 = time.time()
    from e2e_demo import step_release
    result = step_release()
    step_results.append({"step": "release", "elapsed_sec": time.time() - t4, "result": result})
    if result["status"] == "ok":
        all_output_files.append(result["output"])

    # ── Step 6: Knowledge ──────────────────────────────────────────────
    print("\n[6/6] Knowledge Agent — 提取经验知识...")
    t5 = time.time()
    from e2e_demo import step_knowledge
    result = step_knowledge()
    step_results.append({"step": "knowledge", "elapsed_sec": time.time() - t5, "result": result})
    if result["status"] == "ok":
        all_output_files.append(result["output"])

    overall_elapsed = time.time() - overall_start

    # ── 输出汇总报告 ───────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  【端到端演示完成】")
    print("=" * 70)
    print(f"\n  总耗时: {overall_elapsed:.3f} 秒\n")

    print("  各步骤耗时明细:")
    print("  " + "-" * 40)
    for sr in step_results:
        print(f"  {sr['step']:12s}  {sr['elapsed_sec']:6.3f}s")
    print("  " + "-" * 40)
    print(f"  {'TOTAL':12s}  {overall_elapsed:6.3f}s")
    print()

    # 保存时序记录
    timing_record = {
        "scenario": "flask_login_module_security_review",
        "started_at": now_iso(),
        "overall_elapsed_sec": overall_elapsed,
        "steps": [
            {
                "step": sr["step"],
                "elapsed_sec": sr["elapsed_sec"],
                "status": sr["result"].get("status", "unknown"),
            }
            for sr in step_results
        ],
    }

    timing_path = os.path.join(EVIDENCE_DIR, "timing_breakdown.json")
    with open(timing_path, "w") as f:
        json.dump(timing_record, f, indent=2, ensure_ascii=False)

    # 收集所有输出文件列表
    output_dir = SCENARIO_DIR
    all_outputs = []
    for fname in os.listdir(output_dir):
        fpath = os.path.join(output_dir, fname)
        if os.path.isfile(fpath) and fname.endswith((".json", ".diff", ".md", ".py")) and not fname.startswith("__"):
            all_outputs.append(fname)

    # 保存交付物清单
    delivery_path = os.path.join(EVIDENCE_DIR, "deliverables.json")
    with open(delivery_path, "w") as f:
        json.dump({
            "scenario": timing_record["scenario"],
            "total_elapsed_sec": overall_elapsed,
            "deliverables": sorted(all_outputs),
            "evidence_dir": EVIDENCE_DIR,
        }, f, indent=2, ensure_ascii=False)

    print(f"  时序记录已保存: {timing_path}")
    print(f"  交付物清单已保存: {delivery_path}")
    print(f"  生成文件: {', '.join(sorted(all_outputs))}")
    print("\n" + "=" * 70)

    return overall_elapsed


if __name__ == "__main__":
    elapsed = run_orchestrator()
    sys.exit(0 if elapsed < 30 else 1)  # 应在 30 秒内完成
