# HiClaw 部署验证截图取证指南

## 截图清单

以下截图用于 PPT 证据和提交材料，每个截图需包含：
- **真实性声明**：L1 实机 / L2 半实机 / L3 推演
- **时间戳**：2026-08-12 或实际运行时间
- **Trace ID**：与 poc/evidence/trace-example.json 对齐

---

## Screenshot 1：docker compose ps（7 服务全绿）

**路径**: `poc/deploy/evidence/deployment/screenshot-01-docker-compose-ps.png`

**验证命令**:
```bash
cd poc/deploy
docker compose ps
```

**预期输出**:
```
NAME                     STATUS        PORTS
devpilot-synapse         Up 2 minutes  0.0.0.0:8008->8008/tcp
devpilot-minio           Up 2 minutes  0.0.0.0:9000-9001->9000-9001/tcp
devpilot-manager         Up 1 minute   0.0.0.0:8008->8008/tcp
devpilot-worker-intake   Up 30 seconds 0.0.0.0:8001->8001/tcp
devpilot-worker-analyst  Up 30 seconds 0.0.0.0:8002->8002/tcp
devpilot-worker-fixer    Up 30 seconds 0.0.0.0:8003->8003/tcp
devpilot-worker-verifier Up 30 seconds 0.0.0.0:8004->8004/tcp
devpilot-worker-release  Up 30 seconds 0.0.0.0:8005->8005/tcp
devpilot-worker-knowledge Up 30 seconds 0.0.0.0:8006->8006/tcp
```

**真实性声明**: L1 实机（如真实部署）/ L2 半实机（模拟环境）

---

## Screenshot 2：Manager Health Check

**路径**: `poc/deploy/evidence/deployment/screenshot-02-manager-health.png`

**验证命令**:
```bash
curl -s http://localhost:8008/health | jq .
```

**预期输出**:
```json
{
  "status": "healthy",
  "agent": "devlead",
  "type": "manager",
  "workers_active": 6,
  "uptime_seconds": 45,
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"
}
```

**真实性声明**: L1 实机（如真实部署）/ L2 半实机（模拟环境）

---

## Screenshot 3：Worker 日志（以 Intake 为例）

**路径**: `poc/deploy/evidence/deployment/screenshot-03-worker-intake-logs.png`

**验证命令**:
```bash
docker logs devpilot-worker-intake --tail 20
```

**预期输出**:
```
[2026-08-14T10:00:02.500Z] INFO  intake agent started
[2026-08-14T10:00:02.600Z] INFO  loading skill: defect-triage v0.1.0
[2026-08-14T10:00:03.000Z] INFO  connected to matrix room: #devpilot-loop:devpilot.local
[2026-08-14T10:00:05.200Z] INFO  task received: raw_issue=DEF-2026-001
[2026-08-14T10:00:05.200Z] INFO  skill.defect-triage executed, confidence=0.95, severity=P1
```

**真实性声明**: L2 半实机（桩化日志）

---

## Screenshot 4：Skill 安装验证

**路径**: `poc/deploy/evidence/deployment/screenshot-04-skill-list.png`

**验证命令**:
```bash
hiclaw skill list
```

**预期输出**:
```
✓ defect-triage       v0.1.0  installed
✓ code-root-cause     v0.1.0  installed
✓ fix-generator       v0.1.0  installed
✓ test-runner         v0.1.0  installed
✓ canary-release      v0.1.0  installed
✓ postmortem-capture  v0.1.0  installed
```

**真实性声明**: L1 实机（如已在本地 HiClaw 实例安装）/ L2 半实机（模拟输出）

---

## Screenshot 5：Agent 列表验证

**路径**: `poc/deploy/evidence/deployment/screenshot-05-agent-list.png`

**验证命令**:
```bash
hiclaw agent list
```

**预期输出**:
```
NAME        TYPE     STATUS
devlead     manager  active
intake      worker   active
analyst     worker   active
fixer       worker   active
verifier    worker   active
release     worker   active
knowledge   worker   active
```

**真实性声明**: L1 实机（如已在本地 HiClaw 实例配置）/ L2 半实机（模拟输出）

---

## Screenshot 6：端到端场景运行结果

**路径**: `poc/deploy/evidence/deployment/screenshot-06-scenario-run.png`

**验证命令**:
```bash
hiclaw run scenario poc/scenarios/scenario-01-npe-bug.md
```

**预期输出**:
```
[INFO] 启动场景: scenario-01-npe-bug
[INFO] Trace ID: 4bf92f3577b34da6a3ce929d0e0e4736
[INFO] Step 1/8: DevLead 派发 plan（7 步）
[INFO] Step 2/8: Intake 归并分诊 → defect_id=DEF-2026-001, severity=P1
[INFO] Step 3/8: Analyst 根因定位 → UserService.java:42, confidence=0.93
[INFO] Step 4/8: Fixer 生成 patch → patch_id=PATCH-001, risk_level=low
[INFO] Step 5/8: Verifier 测试通过 → 5/5 passed, verdict=approve
[INFO] Step 6/8: Release 灰度发布 → status=success, decision=promote
[INFO] Step 7/8: Knowledge 沉淀 Runbook → runbook_id=RB-2026-001
[INFO] Step 8/8: DevLead 汇总报告 → 全流程 28s
[OK] 场景完成，输出日志: poc/evidence/logs/run-001.log
```

**真实性声明**: L2 半实机（桩化链路）

---

## Screenshot 7：Trace 可视化（可选）

**路径**: `poc/deploy/evidence/deployment/screenshot-07-trace-visual.png`

**验证方式**: 使用 Jaeger / Tempo UI 查看 OTel trace

**预期内容**: 11 个 Span 的全链路视图（agent.devlead → agent.intake → ... → agent.knowledge）

**真实性声明**: L2 半实机（基于 trace-example.json 生成模拟数据）

---

## Screenshot 8：Matrix 房间截图（可选）

**路径**: `poc/deploy/evidence/deployment/screenshot-08-matrix-room.png`

**说明**: Matrix 客户端（Element Web）中 #devpilot-loop 房间的全部消息记录

**真实性声明**: L1 实机（如已部署真实 Matrix）/ L3 推演（无真实部署时标注）

---

## 取证说明

| # | 截图 | 真实性 | 用途 |
|---|------|--------|------|
| 1 | docker compose ps | L1/L2 | 证明 7 服务运行 |
| 2 | Manager health | L1/L2 | 证明 Manager 就绪 |
| 3 | Worker 日志 | L2 | 证明 Worker 执行 |
| 4 | Skill list | L1/L2 | 证明 6 Skill 安装 |
| 5 | Agent list | L1/L2 | 证明 7 Agent 配置 |
| 6 | 场景运行 | L2 | 证明端到端跑通 |
| 7 | Trace 可视化 | L2 | 证明可观测性 |
| 8 | Matrix 房间 | L1/L3 | 证明协作可见 |

**总真实性声明**: 本 PoC 使用 HiClaw 官方框架（L1 部署）+ 桩化推理（L2 模拟），如实标注。
