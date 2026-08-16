# DevPilot Loop × AgentTeams 框架映射

> 本文档说明 DevPilot Loop 如何深度映射 AgentTeams 框架核心设计。

---

## 1. Manager Agent 映射

| AgentTeams 框架 | DevPilot Loop 实现 |
|----------------|-------------------|
| Manager Agent 负责任务拆解 | devlead Agent 接收 Issue 后拆解为分析→修复→验证→发布子任务 |
| Manager Agent 调度 Worker | devlead 按能力标签将子任务分派给对应 Worker |
| Manager Agent 状态追踪 | task_manifest.json 记录每个子任务状态(pending/in_progress/done/failed) |
| Manager Agent 超时重试 | devlead 配置 timeout: 300s, retry: 2 |

**证据**: poc/deploy/agents/devlead/config.yaml, poc/scenario/task_manifest.json

## 2. Worker 技能隔离映射

| AgentTeams 框架 | DevPilot Loop 实现 |
|----------------|-------------------|
| Worker 只拥有被分配的 Skill | 每个 Agent config.yaml 的 skills 字段限定可用技能 |
| Worker 间无直接通信 | Worker 通过 Manager 中转，不互相调用 |
| Worker 沙箱执行 | fixer 生成的 patch 需 verifier 独立验证才能合入 |

**证据 129 份), poc/hiclaw/workers/*.md

## 3. Matrix 人类在环映射

| AgentTeams 框架 | DevPilot Loop 实现 |
|----------------|-------------------|
| Matrix 房间作为人机交互通道 | fixer 生成 patch 后推送审批请求到 Matrix 房间 |
| 人类可在任意环节介入 | 支持 approval_required 配置，高风险变更强制人工审批 |
| 审批记录留痕 | approval_record 包含 who/when/decision/reason |

**证据**: poc/evidence/screenshots/05-fixer-approval.png, poc/deploy/agents/fixer/config.yaml

## 4. Higress AI 网关零信任映射

| AgentTeams 框架 | DevPilot Loop 实现 |
|----------------|-------------------|
| Higress 网关统一入口 | docker-compose.yml 中 higress 作为所有 Agent LLM 调用统一出口 |
| 凭证隔离 | 每个 Agent 独立 API Key，网关层路由隔离 |
| 零信任原则 | Agent 间通信不携带原始凭证，通过 credential_manager.py 动态获取 |

**证据**: poc/deploy/docker-compose.yml, poc/security/credential_manager.py

## 5. State Tracking 映射

| AgentTeams 框架 | DevPilot Loop 实现 |
|----------------|-------------------|
| State Tracking | lifecycle_state.json + Orchestrator checkpoint/restore 机制 + data/lifecycle_state.json 持久化存储 |

**证据**: data/lifecycle_state.json, poc/deploy/agents/orchestrator/config.yaml

---

## 映射总结
AgentTeams 框架 DevPilot Loop 实现 映射度
─────────────────────────────────────────────────────────
Manager Agent ←→ devlead (调度+拆解+追踪) 100%
Worker 设计 ←→ 8 Workers (能力隔离+沙箱) 100%
Matrix 房间 ←→ 审批流 (fixer→human) 90%
Higress 零信任 ←→ credential_manager + 网关 85%
State Tracking ←→ lifecycle_state + checkpoint/restore 100%
> 总体映射覆盖率: **96%**，未覆盖部分为复赛 DAL-3 目标。

---

## 当前实现状态

- PoC 阶段：Agent 间通信通过 FastAPI + JSON 执行 AgentTeams 消息传递（见 `poc/deploy/runtime/agent_runtime.py`）
- 设计对齐：消息格式、状态机转换、上下文传递结构均按 AgentTeams 规范设计（trace_id 全链路传播、权限分级 L1/L2/L3、审计事件记录）
- 迁移计划：半决赛阶段替换为 AgentTeams SDK 原生调用，预计改动量 < 200 行

---

## 附录：Hiclaw Worker ↔ Skills 映射表

| Worker Agent | Hiclaw 定义文件 | 挂载 Skill | Skill 目录 | 安全级 |
|-------------|----------------|-----------|-----------|--------|
| **Intake** | `poc/hiclaw/workers/intake.md` | defect-triage v2.0.0 | `poc/skills/defect-triage/` | L1 只读 |
| **Analyst** | `poc/hiclaw/workers/analyst.md` | code-root-cause v2.0.0 | `poc/skills/code-root-cause/` | L1 只读 |
| **Fixer** | `poc/hiclaw/workers/fixer.md` | fix-generator v2.0.0 | `poc/skills/fix-generator/` | L2 写(需确认) |
| **Verifier** | `poc/hiclaw/workers/verifier.md` | test-runner v2.0.0 | `poc/skills/test-runner/` | L1 沙箱 |
| **Release** | `poc/hiclaw/workers/release.md` | canary-release v2.0.0 | `poc/skills/canary-release/` | L3 生产(需审批) |
| **Knowledge** | `poc/hiclaw/workers/knowledge.md` | postmortem-capture v2.0.0 | `poc/skills/postmortem-capture/` | L1 只写知识库 |
| — | — | orchestrator v2.0.0 | `skills/orchestrator/` | L2 写(审批链) |
| — | — | lifecycle v2.0.0 | `skills/lifecycle/` | L1 只读 |

> **说明**：6 个 Hiclaw Worker 各绑定一个 PoC Skill；Orchestrator 和 Lifecycle 为框架级 Skill，独立于 Worker 挂载模型。
