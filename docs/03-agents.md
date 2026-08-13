# 第 3 章 多 Agent 协同设计 —— Agent Identity List (v2.0)

> 对应评分维度：**多 Agent 协同设计**，权重 **25%**
>
> **版本**: 2.0.0 · **Agent 总数**: 9（1 Manager + 8 Workers）· **状态**: DAL-2

系统基于 AgentTeams（原 HiClaw）Manager–Worker 架构，叠加 **Orchestrator** 与 **Lifecycle** 两个新增 Worker，形成完整的全自主闭环能力。

---

## Agent 1：DevLead（Manager）

| # | 字段 | 内容 |
|---|------|------|
| 1 | 名称与角色定位 | **DevLead**，研发总监，全局编排者 |
| 2 | 类型 | Manager |
| 3 | 职责边界 | **做**：接收外部任务、拆解子任务、派发 Worker、追踪进度、决策升级。**不做**：不直接改代码、不直接调用业务工具、不执行 Skill（保持编排纯粹性） |
| 4 | 输入 | `{"task_id": "string", "source": "issue|alert|ci_failure", "raw_payload": "object", "priority_hint": "string", "timestamp": "ISO8601"}` |
| 5 | 输出 | `{"plan": [...], "approval_required": ["int"], "trace_id": "string", "estimated_duration": "string"}` |
| 6 | 挂载 Skill | 无（纯编排） |
| 7 | 工具/MCP 权限 | **只读**：仅查询任务状态与 Worker 健康度，不写任何生产资源 |
| 8 | 升级策略 | 同一子任务失败 ≥2 次 → 上报人类；L3 操作 → 强制人工审批；Worker 无响应 >60s → 触发熔断 |
| 9 | 失败处理 | Worker 无响应：重试 3 次（5s/15s/30s）→ 降级为人工接管 → 记录熔断事件到审计日志 |
| 10 | 数据契约 | **上游**：外部系统（Issue Tracker / 告警平台 / CI）的原始任务。**下游**：结构化 plan → 所有 Worker；汇总各 Worker output → 最终交付报告 |

---

## Agent 2：Intake（Worker）

| # | 字段 | 内容 |
|---|------|------|
| 1 | 名称与角色定位 | **Intake**，缺陷归并与分诊员 |
| 2 | 类型 | Worker |
| 3 | 职责边界 | **做**：接收原始报障、归并去重、结构化为缺陷单、判定优先级。**不做**：不做根因分析、不改代码、不执行测试 |
| 4 | 输入 | `{"raw_issue": "object", "logs": ["string"], "existing_defects_ref": "string", "source_channel": "string"}` |
| 5 | 输出 | `{"defect_id": "string", "title": "string", "severity": "P0|P1|P2|P3", "dedup_of": "string|null", "evidence": ["string"], "triage_confidence": "float"}` |
| 6 | 挂载 Skill | DefectTriage v2.0.0 |
| 7 | 工具/MCP 权限 | **只读**：Issue Tracker API（经 Higress AI 网关） |
| 8 | 升级策略 | confidence < 0.6 → 上报 DevLead 请求人工分诊 |
| 9 | 失败处理 | 重试 3 次 → 降级为人工分诊 → 记录 trace |
| 10 | 数据契约 | **上游**：DevLead plan.step[0]。**下游**：结构化 defect → Analyst |

---

## Agent 3：Analyst（Worker）

| # | 字段 | 内容 |
|---|------|------|
| 1 | 名称与角色定位 | **Analyst**，代码根因定位专家 |
| 2 | 类型 | Worker |
| 3 | 职责边界 | **做**：分析缺陷单、定位代码根因、输出证据链与影响范围。**不做**：不生成修复代码、不执行测试、不做发布决策 |
| 4 | 输入 | `{"defect_id": "string", "severity": "string", "evidence": ["string"], "repo_ref": "string", "recent_commits": ["string"]}` |
| 5 | 输出 | `{"root_cause": {"file": "string", "line_range": "string", "description": "string"}, "impact_scope": ["string"], "evidence_chain": ["string"], "confidence": "float"}` |
| 6 | 挂载 Skill | CodeRootCause v2.0.0 |
| 7 | 工具/MCP 权限 | **只读**：Git 仓库（读代码、读 commit history）、LLM API（经 Higress AI 网关） |
| 8 | 升级策略 | confidence < 0.7 → 上报 DevLead 请求人工辅助定位 |
| 9 | 失败处理 | 重试 3 次 → 扩大搜索范围（最近 50 commits）→ 仍失败则降级人工 |
| 10 | 数据契约 | **上游**：Intake 的 defect。**下游**：root_cause + evidence_chain → Fixer |

---

## Agent 4：Fixer（Worker）

| # | 字段 | 内容 |
|---|------|------|
| 1 | 名称与角色定位 | **Fixer**，修复执行工程师 |
| 2 | 类型 | Worker |
| 3 | 职责边界 | **做**：根据根因生成修复方案、产出 patch、创建回滚点。**不做**：不执行测试（交给 Verifier）、不做发布决策、不直接 push 主干 |
| 4 | 输入 | `{"root_cause": "object", "impact_scope": ["string"], "repo_ref": "string", "branch_strategy": "string"}` |
| 5 | 输出 | `{"patch_id": "string", "patch_diff": "string", "rollback_point": {"git_tag": "string", "snapshot_id": "string"}, "fix_description": "string", "risk_level": "low|medium|high"}` |
| 6 | 挂载 Skill | FixGenerator v2.0.0 |
| 7 | 工具/MCP 权限 | **写操作（L2）**：创建分支、生成 patch，需 Manager 确认。**push 主干（L3）**：需人工审批 |
| 8 | 升级策略 | risk_level = high → 强制人工审批；patch 生成失败 → 上报 DevLead |
| 9 | 失败处理 | 重试 3 次 → 降级为人工修复建议（输出候选方案供人选择） |
| 10 | 数据契约 | **上游**：Analyst 的 root_cause。**下游**：patch + rollback_point → Verifier |

---

## Agent 5：Verifier（Worker）

| # | 字段 | 内容 |
|---|------|------|
| 1 | 名称与角色定位 | **Verifier**，测试验证工程师 |
| 2 | 类型 | Worker |
| 3 | 职责边界 | **做**：在沙箱环境执行测试、运行回归测试、输出测试报告。**不做**：不修改代码、不做发布决策、不修改测试用例（除非明确授权） |
| 4 | 输入 | `{"patch_id": "string", "patch_diff": "string", "test_suite_ref": "string", "sandbox_config": "object"}` |
| 5 | 输出 | `{"test_report": {"total": "int", "passed": "int", "failed": "int", "skipped": "int"}, "regression_result": "pass|fail", "verdict": "approve|reject", "failure_details": ["string"]}` |
| 6 | 挂载 Skill | TestRunner v2.0.0 |
| 7 | 工具/MCP 权限 | **沙箱执行**：CI API（触发测试）、LLM API（分析失败原因）。不接触生产环境 |
| 8 | 升级策略 | regression_result = fail → 驳回 patch，通知 Fixer 重新修复；连续 2 次 fail → 上报 DevLead |
| 9 | 失败处理 | 测试超时（>5min）→ 终止标记 timeout → 重试 1 次 → 降级人工 |
| 10 | 数据契约 | **上游**：Fixer 的 patch。**下游**：test_report + verdict → Release |

---

## Agent 6：Release（Worker）

| # | 字段 | 内容 |
|---|------|------|
| 1 | 名称与角色定位 | **Release**，灰度发布工程师 |
| 2 | 类型 | Worker |
| 3 | 职责边界 | **做**：执行灰度发布、监控灰度指标、做发布/回滚决策。**不做**：不修改代码、不执行测试、不做根因分析 |
| 4 | 输入 | `{"patch_id": "string", "test_report": "object", "verdict": "approve", "canary_config": {...}}` |
| 5 | 输出 | `{"canary_report": {...}, "release_decision": "promote|rollback", "rollback_point_ref": "string"}` |
| 6 | 挂载 Skill | CanaryRelease v2.0.0 |
| 7 | 工具/MCP 权限 | **生产操作（L3）**：K8s 部署 API、监控 API。需人工审批 |
| 8 | 升级策略 | 所有生产操作 → 强制人工审批；error_rate_delta > threshold → 自动回滚 + 通知 DevLead |
| 9 | 失败处理 | 灰度部署失败 → 自动回滚到 rollback_point → 通知 DevLead → 记录审计日志 |
| 10 | 数据契约 | **上游**：Verifier 的 test_report。**下游**：canary_report → Knowledge |

---

## Agent 7：Knowledge（Worker）

| # | 字段 | 内容 |
|---|------|------|
| 1 | 名称与角色定位 | **Knowledge**，知识沉淀工程师 |
| 2 | 类型 | Worker |
| 3 | 职责边界 | **做**：汇总全流程 trace、生成复盘报告、沉淀 Runbook 与 Skill 模板更新建议。**不做**：不修改代码、不执行测试、不做发布操作 |
| 4 | 输入 | `{"trace_id": "string", "full_trace": "object", "defect": "object", "root_cause": "object", "patch": "object", "test_report": "object", "canary_report": "object"}` |
| 5 | 输出 | `{"runbook_id": "string", "runbook_content": "string", "skill_template_update": "object|null", "lessons_learned": ["string"], "knowledge_base_ref": "string"}` |
| 6 | 挂载 Skill | PostmortemCapture v2.0.0 |
| 7 | 工具/MCP 权限 | **只写知识库**：Wiki / 知识库 API。不接触代码仓库与生产环境 |
| 8 | 升级策略 | 发现系统性问题（同类缺陷 ≥3 次）→ 上报 DevLead 建议流程改进 |
| 9 | 失败处理 | 知识库写入失败 → 重试 3 次 → 降级为本地文件存储 → 标记待同步 |
| 10 | 数据契约 | **上游**：Release 的 canary_report + 全流程 trace。**下游**：runbook 到知识库，闭环完成 |

---

## Agent 8：Orchestrator（Worker）— v2.0 新增

| # | 字段 | 内容 |
|---|------|------|
| 1 | 名称与角色定位 | **Orchestrator**，任务编排管理器 |
| 2 | 类型 | Worker |
| 3 | 职责边界 | **做**：多阶段任务编排、依赖解析（拓扑排序）、失败自动回滚、重试退避、进度实时追踪。**不做**：不替代 DevLead 的全局决策，专注于复杂任务的局部编排 |
| 4 | 输入 | `{"tasks": [{"id": "string", "skill": "string", "input": "object", "depends_on": ["string"]}], "strategy": "parallel|sequential|pipeline", "timeout": "int (seconds)", "max_retries": "int"}` |
| 5 | 输出 | `{"total_tasks": "int", "completed_tasks": "int", "failed_tasks": "int", "elapsed_ms": "int", "results": [...], "dependency_resolved": "bool", "rollback_triggered": "bool", "summary": "string"}` |
| 6 | 挂载 Skill | Orchestrator v2.0.0 |
| 7 | 工具/MCP 权限 | **写操作（L2）**：可调用其他 Worker API，需审批链确认 |
| 8 | 升级策略 | 依赖解析失败 → 降级为顺序执行；total_duration > timeout → 部分完成返回中间结果 |
| 9 | 失败处理 | 指数退避重试（5s→15s→30s）；全部失败则触发回滚已完成的步骤 |
| 10 | 数据契约 | **上游**：任意需要多步编排的任务。**下游**：结构化编排结果，供 DevLead 汇总 |

**核心价值**：实现 DAL-2→DAL-3 的关键基础设施。允许跨 Agent 的灵活任务编排，无需硬编码固定流水线。

---

## Agent 9：Lifecycle（Worker）— v2.0 新增

| # | 字段 | 内容 |
|---|------|------|
| 1 | 名称与角色定位 | **Lifecycle**，生命周期管家 |
| 2 | 类型 | Worker |
| 3 | 职责边界 | **做**：服务启动、检查点保存、状态恢复、优雅关闭、重启管理、状态查询。**不做**：不参与业务逻辑，专注系统级生命周期控制 |
| 4 | 输入 | `{"action": "boot|checkpoint|restore|shutdown|restart|drain|status"}` |
| 5 | 输出 | `{"action": "string", "status": "string", "state": "object|null", "timestamp": "string"}` |
| 6 | 挂载 Skill | Lifecycle v2.0.0 |
| 7 | 工具/MCP 权限 | **只读**：读取 JSON 状态文件，无外部写入权限（除自身状态文件） |
| 8 | 升级策略 | checkpoint 保存失败 → 降级为内存状态（短期可用） |
| 9 | 失败处理 | restore 失败 → 从最新 checkpoint 重建 → 标记为 warm start |
| 10 | 数据契约 | **上游**：系统级事件（启动/崩溃/升级）。**下游**：持久化状态文件 `data/lifecycle_state.json` |

**核心价值**：支持服务级别的容错与快速恢复，是 DAL-3 自主闭环的必要基础设施。

---

## 完整 Agent 对比表

| Agent | 类型 | Skill | 安全级 | 核心能力 | 新增? |
|-------|------|-------|--------|----------|-------|
| **DevLead** | Manager | — | L1 只读 | 全局编排、调度、升级决策 | |
| **Intake** | Worker | DefectTriage | L1 只读 | 归并去重、优先级排序 | |
| **Analyst** | Worker | CodeRootCause | L1 只读 | 根因定位、证据链生成 | |
| **Fixer** | Worker | FixGenerator | L2 写(需确认) | Patch 生成、回滚点创建 | |
| **Verifier** | Worker | TestRunner | L1 沙箱 | 沙箱测试、覆盖率报告 | |
| **Release** | Worker | CanaryRelease | L3 生产(需审批) | 灰度发布、自动回滚 | |
| **Knowledge** | Worker | PostmortemCapture | L1 只写 | Runbook 生成、经验提取 | |
| **Orchestrator** | Worker | Orchestrator | L2 写(审批链) | 依赖解析、失败回滚 | ✨ NEW |
| **Lifecycle** | Worker | Lifecycle | L1 只读 | 启动/检查点/恢复 | ✨ NEW |

---

## 任务流转序列表（一个缺陷的完整旅程）

| 步 | 触发条件 | Agent | Skill | 输入 | 输出 | Manager 决策 | 人工节点 |
|----|---------|-------|-------|------|------|-------------|---------|
| 1 | 外部报障进入 | DevLead | — | raw_payload | plan（7 步） | 拆解派发 | — |
| 2 | plan.step[0] | Intake | DefectTriage | raw_issue + logs | defect（结构化缺陷单） | — | — |
| 3 | defect 产出 | Analyst | CodeRootCause | defect + repo | root_cause + evidence_chain | — | — |
| 4 | root_cause 产出 | Fixer | FixGenerator | root_cause + repo | patch + rollback_point | 确认 patch | ★审批 push |
| 5 | patch 产出 | Verifier | TestRunner | patch + test_suite | test_report + verdict | — | — |
| 6 | verdict = approve | Release | CanaryRelease | patch + test_report | canary_report | 确认发布 | ★审批发布 |
| 7 | 流程结束 | Knowledge | PostmortemCapture | full_trace | runbook + lessons | — | — |
| 8 | runbook 产出 | DevLead | — | 全部输出 | 最终交付报告 | 汇总关闭 | — |
| 9 | 复杂任务 | Orchestrator | Orchestrator | tasks + strategy | structured_results | 可选介入 | — |
| 10 | 系统事件 | Lifecycle | Lifecycle | action | state_change | 可选介入 | — |

---

## 异常升级路径

```
Worker 执行失败
├─ 重试 3 次（5s / 15s / 30s 指数退避）
│ ├─ 成功 → 继续
│ └─ 仍失败
│ ├─ 降级路径可用 → 降级执行（如人工分诊）
│ └─ 降级路径不可用
│   ├─ 上报 DevLead
│   │ ├─ DevLead 可解决 → 重新调度
│   │ └─ DevLead 无法解决 → 触发人工介入
│   └─ 记录熔断事件 → 审计日志
└─ 超时（>60s 无响应）
└─ 触发熔断 → 人工接管

Orchestrator 异常
├─ 依赖解析失败 → 降级为顺序执行
├─ 单任务失败 → 触发回滚已完成步骤
├─ total_duration > timeout → 返回部分结果
└─ 全部失败 → 通知 DevLead

Lifecycle 异常
├─ checkpoint 保存失败 → 降级为内存状态
└─ restore 失败 → 从最新 checkpoint 重建（warm start）
```

---

## 安全权限矩阵

| Agent | Read | Write | L2_Confirm | L3_Approve | Sandbox |
|-------|------|-------|------------|------------|---------|
| DevLead | ✅ | ❌ | — | — | — |
| Intake | ✅ | ❌ | — | — | — |
| Analyst | ✅ | ❌ | — | — | — |
| Fixer | ✅ | ✅ | ✅ | ❌ | — |
| Verifier | ✅ | ✅ | — | — | ✅ |
| Release | ✅ | ✅ | — | ✅ | ❌ |
| Knowledge | ✅ | ✅ | — | — | — |
| Orchestrator | ✅ | ✅ | ✅ | ✅ | — |
| Lifecycle | ✅ | ✅ | — | — | — |

> **L1** = 只读，**L2** = 写操作需 Manager 确认，**L3** = 生产操作需人工审批，**Sandbox** = 隔离环境执行

---

## 关键指标

- **总 Agent 数**: 9（1 Manager + 8 Workers）
- **手动审批节点**: 2（Fixer push / Release deploy）
- **自动重试上限**: 3 次（指数退避）
- **熔断阈值**: 60s 无响应
- **证据链完整度**: 100%（L1-L4 全覆盖）
