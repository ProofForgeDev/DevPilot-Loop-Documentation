# DevPilot Loop

> 基于 **AgentTeams（原 HiClaw）** 的软件研发全生命周期多 Agent 自主闭环系统。
>
> **本项目目标是成为 AgentTeams 研发场景的官方参考实现。**

---

## 它解决什么

中小研发团队（3–20 人）的缺陷修复长期依赖人工串联：报障、定位、改码、测试、发布
各自割裂。平均一个缺陷修复周期约 **4 小时**，上下文在人与人之间反复丢失，
修复经验无法沉淀复用。

**DevPilot Loop** 用 **1 Manager + 6 Workers + 6 Skills** 把这条链路变成
可审计、可回放、可复用的自主闭环。

---

## 架构

Human（研发负责人）
Matrix 客户端全程监督介入
│
┌─────────┴─────────┐
│ DevLead (Manager) │
│ 任务拆解·调度·升级 │
└─────────┬─────────┘
┌──────┬──────┬─────┴───┬──────┬──────┐
▼ ▼ ▼ ▼ ▼ ▼
Intake Analyst Fixer Verifier Release Knowledge
│ │ │ │ │ │
Defect Code Fix Test Canary Postmortem
Triage Root Gen Runner Release Capture
Cause
└──────┴──────┴────────┴───────┴──────┘
│
┌─────────┴─────────┐
│ Higress AI 网关 │
│ 凭证集中管理 │
│ Worker 零真实密钥 │
│ skills.sh · MCP │
└───────────────────┘

---

## 核心能力

| 能力 | 说明 |
|------|------|
| **多 Agent 协同** | 1 Manager + 6 Workers，职责清晰、上下文结构化传递 |
| **Skill 工程化** | 6 个 Skill 均为标准 skill 包，一条命令可安装到任意 HiClaw 实例 |
| **安全可审计** | 继承 HiClaw 零信任设计，叠加审批流与回滚点，全程 Matrix 留痕 |
| **自主分级** | 提出 DAL（DevPilot Autonomy Level）DAL-1 ~ DAL-5 分级模型 |
| **可观测** | OpenTelemetry GenAI 语义 Trace + 结构化 Log + 6 项 Metrics |

---

## 量化收益

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 缺陷修复周期 | 4 小时 | 15 分钟 | 16× |
| 人工介入 | 基线 100% | 减少 80% | 仅关键节点审批 |
| 同类缺陷复发率 | 基线 | 下降 60% | 经验自动沉淀 |

---

## 目录结构

| 目录 | 内容 |
|------|------|
| `docs/` | 设计与方案文档（00–09），含 500 字简介 |
| `poc/` | HiClaw 部署、Agent/Skill 定义、场景模拟与证据 |
| `slides/` | 初赛方案 PPT（Marp 源 + python-pptx 生成脚本） |
| `checklists/` | 提交前质量清单 |

---

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/devpilot-loop.git
cd devpilot-loop

# 2. 部署 HiClaw（需 Docker，推荐 4C8GB）
bash <(curl -fsSL https://raw.githubusercontent.com/agentscope-ai/AgentTeams/main/install/agentteams-install.sh)

# 3. 安装 Skill
hiclaw skill install ./poc/skills/defect-triage
hiclaw skill install ./poc/skills/code-root-cause
hiclaw skill install ./poc/skills/fix-generator
hiclaw skill install ./poc/skills/test-runner
hiclaw skill install ./poc/skills/canary-release
hiclaw skill install ./poc/skills/postmortem-capture

# 4. 验证
hiclaw skill list
```

---

## 开源协议

Apache 2.0。第三方依赖与商业 API 披露见 `docs/07-opensource-plan.md`。

---

## 致谢

- **AgentTeams / HiClaw**：多 Agent 协作基座
- **Higress**：AI 网关与凭证管理
- **Matrix**：Agent 通信协议
- **skills.sh**：Skill 生态
