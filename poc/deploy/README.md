# DevPilot Loop — HiClaw 部署指南

> 基于 **AgentTeams（原 HiClaw）** 的本地部署方案，用于初赛 PoC 验证。
>
> **框架仓库**: [agentscope-ai/AgentTeams](https://github.com/agentscope-ai/AgentTeams)（5377+ Stars）
>
> **DAL 等级**: DAL-2（当前实现级别）

---

## 前置条件

| 项目 | 要求 | 验证命令 |
|------|------|---------|
| Docker | ≥ 24.0 | `docker --version` |
| Docker Compose | ≥ 2.20 | `docker compose version` |
| 内存 | ≥ 8 GB | `docker info --format '{{.MemTotal}}'` |
| CPU | ≥ 4 核 | `docker info --format '{{.NCPU}}'` |
| 端口 8008 | 未被占用 | `lsof -i :8008` |

---

## Step 1：安装 AgentTeams CLI

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/agentscope-ai/AgentTeams/main/install/agentteams-install.sh)
```

安装后验证：

```bash
hiclaw --version
# 预期输出：hiclaw version x.x.x
```

---

## Step 2：启动基础设施（可选）

如需本地完整运行（Matrix + MinIO + Synapse），使用以下 compose 文件：

```bash
cd poc/deploy
docker compose up -d
```

**注意**：正式部署需对接真实 Higress AI 网关和 Matrix Synapse 服务器。
本 compose 仅为 PoC 阶段本地测试使用，生产环境请参照 [AgentTeams 官方文档](https://agentscope-ai.github.io/)。

---

## Step 3：创建 Manager Agent（DevLead）

```bash
hiclaw agent create \
  --type manager \
  --name devlead \
  --config poc/deploy/agents/devlead/config.yaml
```

验证：

```bash
hiclaw agent list
# 预期输出：devlead (active, manager)
```

---

## Step 4：创建 6 个 Worker Agent

```bash
for agent in intake analyst fixer verifier release knowledge; do
  hiclaw agent create \
    --type worker \
    --name $agent \
    --config poc/deploy/agents/$agent/config.yaml
done
```

验证：

```bash
hiclaw agent list
# 预期输出：
# devlead   (active, manager)
# intake    (active, worker)
# analyst   (active, worker)
# fixer     (active, worker)
# verifier  (active, worker)
# release   (active, worker)
# knowledge (active, worker)
```

---

## Step 5：安装 6 个 Skill

```bash
for skill in defect-triage code-root-cause fix-generator test-runner canary-release postmortem-capture; do
  hiclaw skill install ./poc/skills/$skill
done
```

验证：

```bash
hiclaw skill list
# 预期输出：
# defect-triage       v0.1.0  ✓ installed
# code-root-cause     v0.1.0  ✓ installed
# fix-generator       v0.1.0  ✓ installed
# test-runner         v0.1.0  ✓ installed
# canary-release      v0.1.0  ✓ installed
# postmortem-capture  v0.1.0  ✓ installed
```

---

## Step 6：运行端到端场景验证

```bash
# 触发 NPE 缺陷修复场景
hiclaw run scenario poc/scenarios/scenario-01-npe-bug.md
```

预期结果：
- 7 个 Agent 按序执行
- 全流程约 15 秒完成
- 结构化日志写入 `poc/evidence/logs/run-001.log`
- OTel trace 写入 `poc/evidence/trace-example.json`

---

## 架构图（部署视图）

```
┌─────────────────────────────────────────────────────────┐
│                    Host / Docker                        │
│                                                         │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐            │
│  │ Manager  │   │ Worker   │   │ Worker   │  ...       │
│  │ :8008    │──▶│ intake   │   │ analyst  │            │
│  │ (devlead)│   │ :8001    │   │ :8002    │            │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘            │
│       │              │              │                   │
│       ▼              ▼              ▼                   │
│  ┌──────────────────────────────────────────┐          │
│  │         Shared Network                   │          │
│  │       devpilot-network                   │          │
│  │   (Matrix 房间 + AgentTeams IPC)         │          │
│  └──────────────────────────────────────────┘          │
│              │                              │           │
│              ▼                              ▼           │
│  ┌─────────────────┐       ┌─────────────────────┐     │
│  │ Higress AI 网关  │       │  MinIO (对象存储)    │     │
│  │ ·凭证集中管理    │       │  ·Agent 配置持久化   │     │
│  │ ·LLM 路由       │       │  ·Skill 包存储       │     │
│  │ ·零信任认证     │       │  ·Trace 数据         │     │
│  └─────────────────┘       └─────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## 端口分配

| 服务 | 端口 | 说明 |
|------|------|------|
| Manager (DevLead) | 8008 | 主管理入口 |
| Worker: intake | 8001 | 缺陷归并 |
| Worker: analyst | 8002 | 根因定位 |
| Worker: fixer | 8003 | 修复执行 |
| Worker: verifier | 8004 | 测试验证 |
| Worker: release | 8005 | 灰度发布 |
| Worker: knowledge | 8006 | 知识沉淀 |

---

## 踩坑记录

| # | 问题 | 原因 | 解决方式 |
|---|------|------|---------|
| 1 | `hiclaw: command not found` | AgentTeams 未加入 PATH | 重新运行安装脚本或手动 export PATH |
| 2 | Skill 安装失败：manifest 格式错误 | manifest.json 缺少 required 字段 | 检查 manifest 格式，参考 poc/skills/defect-triage/manifest.json |
| 3 | Worker 无响应超时 | Manager 与 Worker 网络不通 | 检查 docker compose network 配置 |
| 4 | Matrix 房间无法创建 | Synapse 未就绪 | 先启动基础设施：`docker compose up -d` |
| 5 | LLM API 限流 | Higress 网关配置了速率限制 | 使用 L2 半实机桩替代，如实标注证据层级 |

---

## 结果记录

- **部署日期**：2026-08-12
- **HiClaw 版本**：AgentTeams main（参考仓库 commits 截至 2026-08-12）
- **Docker 版本**：$(docker version --format '{{.Server.Version}}' 2>/dev/null || echo "待填写")
- **环境**：macOS Darwin 25.5.0 / 4C8GB
- **遇到的问题**：见踩坑记录表
- **解决方式**：已记录在 README 和文档中
