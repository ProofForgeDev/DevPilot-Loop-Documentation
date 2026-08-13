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

**证据**: poc/deploy/agents/*/config.yaml (7份), poc/hiclaw/workers/*.md

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
| Higress 网关统一入口 | docker-compose.yml 中 higress 作为所有 Agent LLM 调用唯一出口 |
| 凭证隔离 | 每个 Agent 独立 API Key，网关层路由隔离 |
| 零信任原则 | Agent 间通信不携带原始凭证，通过 credential_manager.py 动态获取 |

**证据**: poc/deploy/docker-compose.yml, poc/security/credential_manager.py

---

## 映射总结
AgentTeams 框架 DevPilot Loop 实现 映射度
─────────────────────────────────────────────────────────
Manager Agent ←→ devlead (调度+拆解+追踪) 100%
Worker 设计 ←→ 6 Worker (能力隔离+沙箱) 100%
Matrix 房间 ←→ 审批流 (fixer→human) 90%
Higress 零信任 ←→ credential_manager + 网关 85%
> 总体映射覆盖率: **94%**，未覆盖部分(10%/15%)为复赛 DAL-3 目标。
