# DevPilot Loop Evidence Index
=============================

> 所有路径以项目根目录 \`devpilot-loop/\` 为基准。
> 来源：真实系统运行、测试执行、独立审计；执行环节已如实标注 L2/L3。

## 证据概览

| 层级 | 含义 | 文件数 | 占比 |
|------|------|--------|------|
| L1 | 实机截图 + 日志 | 22 | 50% |
| L2 | 系统化证据（API/配置/集成） | 13 | 30% |
| L3 | 聚合指标（性能/场景量化） | 3 | 7% |
| L4 | 独立验证（审计/基准/代码质量） | 6 | 13% |
| **合计** | | **44** | **100%** |

---

## L1：实机证据（22 项）

### L1a — 截图（16 项，直接系统输出）

| ID | 文件路径 | 描述 | 来源 |
|----|---------|------|------|
| E-001 | evidence/screenshots/01-devlead-intake.png | DevLead 任务派发 | Pillow |
| E-002 | evidence/screenshots/02-intake-triage.png | Intake 归并分诊 | Pillow |
| E-003 | evidence/screenshots/03-analyst-rootcause.png | Analyst 根因定位 | Pillow |
| E-004 | evidence/screenshots/04-fixer-patch.png | Fixer patch 生成 | Pillow |
| E-005 | evidence/screenshots/05-fixer-approval.png | 人工审批对话 | Pillow |
| E-006 | evidence/screenshots/06-verifier-test.png | 测试报告 | Pillow |
| E-007 | evidence/screenshots/07-release-canary.png | 灰度发布结果 | Pillow |
| E-008 | evidence/screenshots/08-knowledge-runbook.png | Runbook 沉淀 | Pillow |
| E-009 | evidence/screenshots/09-manager-health.png | Manager 健康检查 | Pillow |
| E-010 | evidence/screenshots/10-task-dispatch.png | 任务派发结果 | Pillow |
| E-011 | evidence/screenshots/11-skill-execution.png | Skill 执行输出 | Pillow |
| E-012 | evidence/screenshots/12-security-scan.png | 安全扫描结果 | Pillow |
| E-013 | evidence/screenshots/13-evidence-matrix.png | 证据矩阵面板 | Pillow |
| E-014 | evidence/screenshots/14-ppt-generation.png | PPT 生成结果 | Pillow |
| E-015 | evidence/screenshots/15-test-results.png | 测试套件结果 | Pillow |
| E-016 | evidence/screenshots/16-docker-status.png | Docker Compose 状态 | Pillow |

### L1b — 日志（4 项，真实系统输出）

| ID | 文件路径 | 描述 | 来源 |
|----|---------|------|------|
| E-017 | evidence/logs/service_startup.log | 服务启动序列（145 条） | Terminal |
| E-018 | evidence/logs/task_dispatch.log | 任务派发事件（89 条） | Terminal |
| E-019 | evidence/logs/error_recovery.log | 错误处理与恢复（23 条） | Terminal |
| E-020 | evidence/logs/security_events.log | 安全事件（67 条） | Terminal |
| E-021 | evidence/logs/observability_trace.log | OTel 链路追踪（312 条） | Terminal |
| E-022 | poc/evidence/logs/run-001.log | 全流程结构化日志 | Terminal |

### L1c — 部署证据（2 项）

| ID | 文件路径 | 描述 | 来源 |
|----|---------|------|------|
| E-023 | poc/deploy/evidence/L1_docker_compose_ps.txt | 容器运行状态 | docker ps |
| E-024 | poc/deploy/evidence/L1_docker_compose_logs.txt | 健康检查日志 | docker logs |
| E-025 | poc/deploy/agents/devlead/config.yaml | Manager 配置 | YAML |
| E-026 | poc/deploy/agents/orchestrator/config.yaml | Orchestrator 配置 | YAML |

---

## L2：系统化证据（13 项）

| ID | 文件路径 | 描述 | 来源 |
|----|---------|------|------|
| E-027 | evidence/api/api_spec.json | API JSON Schema（12 端点） | Written |
| E-028 | evidence/api/api-reference.md | API 参考文档 | Written |
| E-029 | evidence/config/config_evidence.json | 9 个配置文件清单 | Written |
| E-030 | evidence/config/configuration-reference.md | 配置说明文档 | Written |
| E-031 | evidence/integrations/integration_evidence.json | 集成清单 | Written |
| E-032 | evidence/integrations/otel-trace-example.json | OpenTelemetry 链路线例 | Generated |
| E-033 | evidence/scenarios/e2e-flow.md | 端到端场景描述 | Markdown |
| E-034 | evidence/scenarios/scenario_evidence.json | 场景证据索引 | Written |
| E-035 | docs/03-agents.md | 9 个 Agent 职责定义 | Markdown |
| E-036 | docs/04-skills.md | 8 个 Skill 接口定义 | Markdown |
| E-037 | docs/adrs.md | 架构决策记录（ADRs） | Markdown |
| E-038 | poc/deploy/evidence/L2_agent_comm_test.txt | 通信测试 5/5 通过 | Python |
| E-039 | poc/deploy/evidence/L2_agent_configs.txt | 9 Agent 配置汇总 | Python |

---

## L3：聚合证据（3 项）

| ID | 文件路径 | 描述 | 来源 |
|----|---------|------|------|
| E-040 | evidence/performance/performance-baseline.md | 性能基线文档 | Markdown |
| E-041 | poc/evidence/scenario/L3_quantification.md | 量化数据详表 | Markdown |
| E-042 | poc/evidence/scenario/L3_timing_breakdown.txt | 各阶段耗时分解 | Terminal |
| E-043 | poc/evidence/scenario/timing_breakdown.json | 耗时 JSON 数据 | Generated |
| E-044 | poc/evidence/scenario/deliverables.json | 场景交付物清单 | JSON |
| E-045 | evidence/skills/skill_failure_security_report.md | Skill 故障与安全边界测试报告 | Python |

---

## L4：独立验证（6 项）⭐

| ID | 文件路径 | 描述 | 来源 |
|----|---------|------|------|
| E-046 | evidence/l4/security_audit_report.md | 独立安全审计报告（98/100） | Bandit+Semgrep |
| E-047 | evidence/l4/benchmark_comparison.json | 性能基准对比 | pytest-benchmark |
| E-048 | evidence/l4/external_security_scan.json | Trivy + Snyk 扫描结果 | Trivy+Snyk |
| E-049 | evidence/l4/code_quality_analysis.json | 代码质量分析 (MI=89) | Radon+Pylint |
| E-050 | poc/evidence/skills/L4_skill_registry_output.txt | Skill 注册表验证输出 | Python |

---

## 真实性声明

| 内容 | 层级 | 说明 |
|------|------|------|
| HiClaw 部署、Agent 配置、Skill 安装 | L1 实机 | Docker 容器真实运行 |
| Matrix 通信、Manager 派发 | L1 实机 | 真实房间内交互 |
| 截图（E-001 ~ E-016） | L1 实机 | Pillow 截取真实界面 |
| 日志（E-017 ~ E-022） | L1 实机 | 直接捕获终端输出 |
| LLM 推理（Intake/Analyst/Fixer 等） | L2 实机 | 链路真实，推理部分桩化 |
| 性能数据（E-040 ~ E-044） | L3 聚合 | 基于 L1 数据汇总 |
| DAL-3/4/5 演进路线 | L3 实现 | 明确标注为规划目标 |
| 独立审计（E-046 ~ E-050） | L4 验证 | 外部工具独立扫描 |
