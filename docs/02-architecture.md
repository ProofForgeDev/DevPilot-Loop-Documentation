# 第 2 章 方案总览

---

## 2.1 端到端主流程

```
外部入口                  DevLead              8 Workers              治理层
(Issue/告警/CI失败) →   (Manager)      →   (流水线)       →   (证据/审计)
│                                      │
│ raw_payload                          │ plan
├──────────────────→  ├────────────────────→ │ → defect → root_cause
│                     │                    │        → patch → test_report
│                     │                    │        → canary_report
│                     │                    │        → runbook
│                     │                    │
└────────────────────┴────────────────────┴────────────────────────────┘

全部发生在 Matrix 房间（人类可见可介入）
```

## 2.2 分层架构

| 层 | 职责 | 对应 AgentTeams 能力 | 本项目实现 |
|----|------|---------------------|-----------|
| 编排层 | 任务拆解 / 调度 / 状态追踪 | Manager Agent | DevLead |
| 协同层 | 7 Agent 协作、上下文传递 | Matrix 房间 | 8 Workers |
| 能力层 | 8 Skill 执行 | skills.sh 生态 | 6 个标准 skill 包 |
| 连接层 | Git / CI / K8s / LLM 工具 | MCP + Higress AI 网关 | 适配器 |
| 治理层 | 审批 / 回滚 / 审计 / 可观测 | 零信任凭证 + 留痕 | 审批流 + OTel |

## 2.3 与 AgentTeams 框架的映射关系

| AgentTeams 原生能力 | 本项目映射 | 评分维度 |
|--------------------|-----------|---------|
| Manager Agent 任务拆解与调度 | DevLead 拆解 plan → 派发 Worker | 多 Agent 协同 25% |
| Worker 技能隔离 | 每个 Worker 只挂载 1 个 Skill | 多 Agent 协同 25% |
| Matrix 房间全程可见 | 人类在 Matrix 客户端监督全部协作 | 安全可审计 20% |
| 零信任凭证（consumer token） | Worker 不持真实密钥，Higress 网关管理 | 安全可审计 20% |
| skills.sh 生态 | 8 个 Skill 按标准格式打包，可安装 | Skill 工程 25% |

## 2.4 DAL 自主分级模型（入口）

本项目提出 **DAL（DevPilot Autonomy Level）** 分级模型，
为研发 Agent 自主性定义行业标准。当前 PoC 达到 **DAL-2**。

详见 [docs/09-dal-model.md](09-dal-model.md)。
