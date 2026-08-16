# DevPilot Loop — 快速启动指南
# ============================
# 本目录包含 PoC 阶段的演示代码和部署配置。
# 完整系统基于 AgentTeams（HiClaw）框架构建。

## 环境要求
- Python ≥ 3.10
- Docker ≥ 24.0（可选，用于容器化部署）
- Docker Compose ≥ 2.20（可选）

## 一键启动（Docker）
```bash
cd devpilot-loop/poc/deploy
docker compose up -d
```
启动后访问 http://localhost:8080 查看网关状态。

## 本地运行（无需 Docker）
```bash
cd devpilot-loop
python3 -m pytest tests/ -v --tb=short
```
运行所有测试用例（367 个），验证 Agent 通信、Skill 注册、安全扫描等核心功能。

## 运行端到端场景演示
```bash
cd devpilot-loop/poc/scenario
python3 orchestrator_run.py
```
执行完整的缺陷修复流程：Intake → Analyst → Fixer → Verifier → Release → Knowledge。

## 停止服务
```bash
cd devpilot-loop/poc/deploy
docker compose down
```

## 目录说明
- `deploy/` — Docker Compose 配置 + Agent 配置文件
- `scenario/` — 端到端场景演示脚本
- `skills/` — 8 个可安装 Skill 模块（defect-triage, code-root-cause, fix-generator 等）
- `security/` — 零信任凭证管理模块
- `observability/` — OpenTelemetry 链路追踪
- `evidence/` — L1-L4 证据文件（截图、日志、审计报告）
