# 上下文增强与 RAG 设计

> 对应评分维度：**Skill 工程化设计** 和 **工程落地与安全可审计**

---

## 1. 上下文增强策略

本项目采用**混合上下文增强策略**，结合以下四种能力：

### 1.1 Agent Memory Storage（Agent 记忆存储）✅ 已实现

- **实现方式**：每个 Agent 维护独立的会话历史缓冲区
- **存储位置**：内存中（PoC 阶段）→ Redis/PolarDB（复赛阶段）
- **查询方式**：时间窗口 + 语义检索
- **证据文件**：`data/lifecycle_state.json`, `poc/evidence/trace-example.json`

### 1.2 Knowledge Base RAG（知识库 RAG）🎯 复赛目标

- **设计目标**：使用向量数据库存储 Runbook、FAQ、历史缺陷记录
- **检索方式**：语义相似度检索（embedding-based）
- **集成点**：Knowledge Agent 在生成 Runbook 时检索相似历史案例
- **实现计划**：复赛阶段接入 PostgreSQL + pgvector

### 1.3 Shared State Management（共享状态管理）✅ 已实现

- **实现方式**：通过 Manager (DevLead) 维护全局任务状态机
- **数据模型**：`task_manifest.json` 记录所有子任务的状态转换
- **一致性保障**：乐观锁 + 版本号机制
- **证据文件**：`poc/scenario/task_manifest.json`

### 1.4 Trace Observability（轨迹可观测性）✅ 已实现

- **实现方式**：OpenTelemetry 全链路追踪
- **数据持久化**：所有 Span 写入结构化日志
- **检索方式**：按 trace_id 关联所有操作
- **证据文件**：`poc/evidence/trace-example.json`, `evidence/logs/observability_trace.log`

---

## 2. RAG vs 替代方案选择

### 当前选择：使用 Shared State + Trace Observability

**原因**：
1. 研发场景的上下文主要是**任务状态和执行轨迹**，而非外部文档检索
2. 共享状态管理已能支持多 Agent 间的一致上下文传递
3. 轨迹可观测性提供了完整的执行证据链

### 复赛演进：引入 Knowledge Base RAG

**触发条件**：
- 当知识库规模超过 1000 条 Runbook/FAQ 时
- 当需要跨项目检索相似缺陷模式时
- 当 Knowledge Agent 的 Runbook 生成准确率下降到 80% 以下时

**技术方案**：
- 向量数据库：PostgreSQL + pgvector
- Embedding 模型：text-embedding-3-small（OpenAI）或 bge-large-zh（本地）
- 检索策略：Hybrid Search（关键词 + 语义）

---

## 3. 上下文传递机制

### 3.1 任务级上下文传递

```
Intake 输出 → Analyst 输入
{
  "defect_id": "BUG-001",
  "title": "Login NPE",
  "severity": "P1",
  "evidence": ["log_line_42", "stack_trace"],
  "triage_confidence": 0.92
}
```

### 3.2 执行级上下文传递

```
Fixer 输出 → Verifier 输入
{
  "patch_id": "patch-001",
  "patch_diff": "diff内容",
  "rollback_point": {"git_tag": "v1.2.3"},
  "risk_level": "medium"
}
```

### 3.3 全局上下文传递

```
全链路 Trace → Knowledge 输入
{
  "trace_id": "abc123",
  "full_trace": [...],  // 所有 Span 列表
  "defect": {...},
  "root_cause": {...},
  "patch": {...},
  "test_report": {...},
  "canary_report": {...}
}
```

---

## 4. 证据文件

| ID | 文件路径 | 描述 | 层级 |
|----|---------|------|------|
| E-C01 | `data/lifecycle_state.json` | Agent 状态持久化示例 | L1 |
| E-C02 | `poc/scenario/task_manifest.json` | 共享状态管理示例 | L2 |
| E-C03 | `poc/evidence/trace-example.json` | Trace 可观测性示例 | L1 |
| E-C04 | `docs/context-enhancement.md` | 本文档 | L1 |
