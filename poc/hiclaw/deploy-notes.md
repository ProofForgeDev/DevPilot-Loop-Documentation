# HiClaw 部署记录

## 环境信息
- 日期：2026-08-13
- 操作系统：
- Docker 版本：
- 内存/CPU：
- HiClaw 版本：

## 部署步骤

### Step 1：环境检查
- [ ] Docker 已安装且运行
- [ ] 内存 ≥ 8GB（推荐 4C8GB）
- [ ] 端口 8008（Matrix Synapse）未被占用

### Step 2：安装 HiClaw
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/agentscope-ai/AgentTeams/main/install/agentteams-install.sh)
```

### Step 3：验证部署
```bash
# 检查 Docker 容器
docker ps  # 应看到 hiclaw-manager, synapse 等容器

# 检查 HiClaw 服务状态
hiclaw status

# 检查 Agent 列表
hiclaw agent list

# 检查 Skill 列表
hiclaw skill list

# 预期输出
# services: running (3/3)
# agents: devlead (active)
# skills: 0 installed
```

### Step 4：创建 Manager（DevLead）
命令：
```bash
hiclaw agent create --type manager --name devlead --config poc/hiclaw/manager/devlead.md
```
结果：

### Step 5：创建 6 个 Worker
命令：
```bash
for agent in intake analyst fixer verifier release knowledge; do
  hiclaw agent create --type worker --name $agent --config poc/hiclaw/workers/$agent.md
done
```
结果：

### Step 6：安装 Skill
命令：
```bash
for skill in defect-triage code-root-cause fix-generator test-runner canary-release postmortem-capture; do
  hiclaw skill install ./poc/skills/$skill
done
```
结果：

## 踩坑记录

| 问题 | 原因 | 解决方式 |
|------|------|---------|
| | | |

## 结果：
- 耗时：
- 遇到的问题：
- 解决方式：
