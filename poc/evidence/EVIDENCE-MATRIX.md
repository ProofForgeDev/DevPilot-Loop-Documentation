# 证据矩阵

## 第 5 章 工程落地

| # | 项目 | 状态 | 证据层级 |
|---|------|------|---------|
| 1 | HiClaw 实机部署（Docker，4C8GB） | ✅ 完成 | L1 实机 |
| 2 | 7 Agent 配置完成 | ✅ 完成 | L1 实机 |
| 3 | 6 Skill 安装验证通过 | ✅ 完成 | L1 实机 |
| 4 | 端到端场景跑通（NPE 缺陷） | ✅ 完成 | L1/L2 |
| 5 | 真实证据 | ✅ 见下表 | — |

### 证据文件清单

| 编号 | 文件路径 | 类型 | 证明了什么 | 真实性 |
|------|---------|------|-----------|--------|
| 1 | evidence/screenshots/01-devlead-intake.png | 截图 | DevLead 任务派发 | L1 实机 |
| 2 | evidence/screenshots/02-intake-triage.png | 截图 | Intake 归并分诊 | L1 实机 |
| 3 | evidence/screenshots/03-analyst-rootcause.png | 截图 | Analyst 根因定位 | L2 半实机 |
| 4 | evidence/screenshots/04-fixer-patch.png | 截图 | Fixer patch 生成 | L2 半实机 |
| 5 | evidence/screenshots/05-fixer-approval.png | 截图 | 人工审批对话 | L1 实机 |
| 6 | evidence/screenshots/06-verifier-test.png | 截图 | 测试报告 | L2 半实机 |
| 7 | evidence/screenshots/07-release-canary.png | 截图 | 灰度发布结果 | L2 半实机 |
| 8 | evidence/screenshots/08-knowledge-runbook.png | 截图 | Runbook 沉淀 | L2 半实机 |
| 9 | evidence/logs/run-001.log | 日志 | 全流程结构化日志 | L1 实机 |
| 10 | evidence/trace-example.json | Trace | OTel GenAI 全链路 trace | L1 实机 |
| 11 | evidence/video/manager-dispatch-60s.mp4 | 录屏 | Manager 调度全过程 | L1 实机 |

### 真实性声明

| 内容 | 层级 | 说明 |
|------|------|------|
| HiClaw 部署、Agent 配置、Skill 安装 | L1 实机 | Docker 容器真实运行 |
| Matrix 通信、Manager 派发 | L1 实机 | 真实房间内交互 |
| LLM 推理（Intake/Analyst/Fixer 等） | L2 半实机 | 链路真实，推理部分桩化 |
| DAL-3/4/5 演进路线 | L3 推演 | 明确标注为规划目标 |
