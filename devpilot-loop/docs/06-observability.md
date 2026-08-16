# 第 6 章 可观测性设计

---

## 6.1 Trace（OpenTelemetry GenAI 语义）

每个 Agent / Skill / MCP 调用产生一个 Span。

**Span 命名规范**：
- Agent 调用：`agent.{agent_name}`（如 `agent.devlead`、`agent.intake`）
- Skill 调用：`skill.{skill_name}`（如 `skill.defect-triage`）
- 工具调用：`mcp.{tool_name}`（如 `mcp.git-api`、`mcp.llm-gateway`）

完整 trace 示例见 `poc/evidence/trace-example.json`。

## 6.2 Log（结构化日志）

与 TraceId 关联。格式：

```json
{
  "ts": "2026-08-14T10:30:00.000Z",
  "level": "INFO",
  "trace_id": "abc123def456",
  "agent": "fixer",
  "skill": "fix-generator",
  "event": "patch_generated",
  "patch_id": "patch-001",
  "risk_level": "medium",
  "duration_ms": 3200
}
```
## 6.3 Metrics（6 项核心指标）

| 指标 | 说明 | 采集方式 |
|------|------|---------|
| 会话数 | 总任务处理数 | Manager 计数 |
| 端到端延迟 | 从任务进入到闭环完成 | Trace 首尾 Span 时间差 |
| Token 消耗 | LLM 调用总 Token 数 | Higress AI 网关上报 |
| 工具成功率 | Skill 调用成功/总数 | Skill 结果统计 |
| 修复成功率 | Verifier 通过率 | Verifier verdict 统计 |
| 人工介入率 | 审批事件数 / 总会话数 | 审批事件计数 |
