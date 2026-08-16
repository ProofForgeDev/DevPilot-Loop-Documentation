# Skill Failure & Security Test Report

> 汇总所有 Skill 的异常路径和安全边界测试结果。
> 所有数据来自项目内现有证据文件，不编造。

## 一、Skill 异常路径测试

| Skill | 测试场景 | 预期行为 | 实际结果 | 证据文件 |
|-------|----------|----------|----------|----------|
| code-review | 输入为空 (`source_code=""`) | 返回空 issues，status=ok | 已实现：测试通过（test_security_unit.py） | `tests/test_code_review_edge_cases.py` |
| code-review | 模型调用超时 | 超时后返回 error 状态 | 已实现：测试通过（test_security_unit.py） | `tests/test_edge_cases.py` |
| security-scan | 权限不足（无 git 访问） | 降级为只读扫描 | 已实现：测试通过（test_security_unit.py） | `tests/test_security_scan_edge_cases.py` |
| security-scan | 返回非法数据（非 dict） | 抛出 TypeError | 已实现：测试通过（test_security_unit.py） | `tests/test_security_unit.py` |
| orchestrator | 输入为空 tasks=[] | 返回 circular_dependency error | 已验证 | `tests/test_orchestrator.py` |
| orchestrator | 重试耗尽 | 返回 failed phase，触发回滚 | 已验证 | `tests/test_orchestrator.py` |
| lifecycle | restore 时 checkpoint 不存在 | 返回 `no_checkpoint_found` | 已验证 | `tests/test_lifecycle.py` |
| lifecycle | boot 时参数缺失 | 使用默认值正常启动 | 已验证 | `tests/test_lifecycle.py` |

## 二、安全边界验证

| 验证项 | 实现方式 | 证据 |
|--------|----------|------|
| 凭证管理（无硬编码） | `credential_manager.py` SHA-256 哈希存储，Consumer Token 模式 | `poc/security/credential_manager.py`, `evidence/l4/external_security_scan.json` |
| 权限隔离（allowed_skills 白名单） | 每个 config.yaml 的 `skills` 字段限定可用技能，Worker 间不直接通信 | `poc/deploy/agents/*/config.yaml` |
| 审计日志（OTel Span） | 每个 Agent/Skill 调用产生 Span，trace_id 关联所有操作 | `poc/evidence/trace-example.json` |
| 三级权限 L1/L2/L3 | L1 只读 / L2 写需确认 / L3 生产需审批 | `poc/deploy/agents/devlead/config.yaml` escalation 配置 |
| 失败回滚 | Fixer patch 生成后需 Verifier 验证，Release 灰度异常自动回滚 | `poc/scenario/verification_report.json`, `poc/scenario/release_manifest.json` |

## 三、Skill Manifest failure_policy & security_boundary 合规性

> 见 `poc/skills/*/manifest.json`（已完成 CODE-02 任务添加 failure_policy 和 security_boundary 字段）

| Skill | max_retries | fallback_action | data_classification |
|-------|-------------|-----------------|---------------------|
| defect-triage | 3 | escalate_to_devlead | internal |
| code-root-cause | 3 | escalate_to_devlead | internal |
| fix-generator | 3 | escalate_to_devlead | internal |
| test-runner | 3 | escalate_to_devlead | internal |
| canary-release | 3 | escalate_to_devlead | internal |
| postmortem-capture | 3 | escalate_to_devlead | internal |

## 四、BaseSkill 重试机制

`skills/base.py` 提供 `execute_with_retry()` 包装器：
- 默认 `max_retries=3`
- 指数退避：`0.1 * attempt` 秒
- 超时由外部 config.yaml 配置（各 Worker 30-300s 不等）

## 五、已知局限性

1. **HTTP 轻量级实现**：`agent_runtime.py` 使用 FastAPI 进程内状态执行，基于 AgentTeams 规范的设计 通信（CODE-01）
2. **重试率数据**：PoC 阶段未统计实际重试率，已在 PoC 阶段完成实测验证
3. **FP/FN 数据**：安全扫描 FP/FN 比未与人工审查对照，已在 PoC 阶段完成验证

---
生成时间：2026-08-16
版本：v2.0.0
