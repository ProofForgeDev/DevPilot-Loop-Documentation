# MCP 等价契约文档（MCP Equivalent Contract）

> **说明**：本项目当前阶段以 FastAPI + JSON 执行 MCP 工具调用。本契约定义了与真实 MCP Server 对接的接口规范，
> 确保后续迁移到 AgentTeams 原生 MCP 仅需协议适配，无需重构调用链。

---

## 1. 协议规范

| 项目 | 规范 |
|------|------|
| 协议版本 | MCP 1.0 (2024-11-01) |
| 传输层 | HTTP / SSE（AgentTeams 推荐） |
| 编码 | JSON-RPC 2.0 |
| 认证 | Higress AI 网关 consumer token（零信任） |
| 错误码 | MCP 标准错误码（参考 [MCP Error Codes](https://modelcontextprotocol.io/specification/2024-11-05/common/errors)） |

### 迁移成本说明

| 组件 | 当前实现 | 迁移动作 | 预计改动量 |
|------|---------|---------|-----------|
| 工具调用入口 | FastAPI HTTP endpoint | 替换为 MCP Client SDK | < 50 行 |
| 凭证管理 | `credential_manager.py`（SHA-256 哈希） | 由 Higress 网关自动注入 | 0 行（网关层处理） |
| 参数序列化 | Pydantic v2 model | MCP `CallToolRequest` schema | < 100 行（schema 对齐） |
| 审计日志 | 结构化 JSON + trace_id | MCP `notifications/messages` 流式上报 | < 200 行 |
| **总计** | | | **< 350 行** |

---

## 2. 工具列表（Tools）

每个 Skill 挂载一个或多个 MCP Tool，以下是完整工具清单：

### 2.1 Issue Tracker MCP（Issue Tracker API）

| 属性 | 值 |
|------|---|
| 工具名 | `issue_tracker` |
| 描述 | 读取 Issue Tracker 中的缺陷、需求、告警 |
| 调用方 | Intake（只读） |
| 权限范围 | `read:issue-tracker` |
| 认证方式 | consumer token（Higress 网关注入） |

**输入 Schema**：
```json
{
  "tool_name": "issue_tracker",
  "arguments": {
    "action": "list|get|search",
    "project_id": "string",
    "filter": {
      "status": "open|closed|all",
      "priority": "P0|P1|P2|P3",
      "label": "string"
    },
    "limit": "int (default: 20)",
    "cursor": "string (pagination)"
  }
}
```

**输出 Schema**：
```json
{
  "content": [{
    "type": "text",
    "text": "string (JSON 格式的缺陷列表)"
  }],
  "isError": false
}
```

**失败重试**：3 次指数退避（5s / 15s / 30s）

**幂等性控制**：所有读操作天然幂等；写操作（若扩展）通过 `request_id` 去重

**审计日志**：每次调用记录 `trace_id + agent + tool + action + timestamp + result_status`

---

### 2.2 Git MCP（Git API）

| 属性 | 值 |
|------|---|
| 工具名 | `git` |
| 描述 | Git 仓库读写（只读权限为主，写操作需审批） |
| 调用方 | Analyst（只读）、Fixer（L2 写，需确认） |
| 权限范围 | `read:git-repo` / `write:git-repo`（L2） / `push:git-repo`（L3，人工审批） |
| 认证方式 | consumer token（Higress 网关注入） |

**输入 Schema**：
```json
{
  "tool_name": "git",
  "arguments": {
    "action": "diff|log|blame|show|branch|create_branch|commit|push",
    "repo_ref": "string (git URL or local path)",
    "ref": "string (branch/tag/commit)",
    "path": "string (file path in repo)",
    "limit": "int (default: 20, for log/diff)"
  }
}
```

**输出 Schema**：
```json
{
  "content": [{
    "type": "text",
    "text": "string (git command output or structured JSON)"
  }],
  "isError": false
}
```

**写操作审批链**：
- `create_branch` / `commit` → L2，需 Manager（DevLead）确认
- `push` → L3，需人工审批

**幂等性控制**：`create_branch` 通过分支名去重；`commit` 通过 `--amend` 提示

**审计日志**：同上，额外记录 `approval_status` 字段

---

### 2.3 LLM Gateway MCP（LLM API）

| 属性 | 值 |
|------|---|
| 工具名 | `llm_gateway` |
| 描述 | 统一 LLM 推理入口，所有 Agent/Skill 的 AI 调用经此网关 |
| 调用方 | 所有 Worker（Intake/Analyst/Fixer/Verifier/Release/Knowledge） |
| 权限范围 | `invoke:llm` |
| 认证方式 | consumer token（Higress 网关注入） |
| 支持模型 | OpenAI 兼容 API（可切换通义千问/DeepSeek/本地模型） |

**输入 Schema**：
```json
{
  "tool_name": "llm_gateway",
  "arguments": {
    "model": "string (default: gpt-4o)",
    "messages": [{
      "role": "system|user|assistant",
      "content": "string"
    }],
    "temperature": "float (default: 0.3)",
    "max_tokens": "int",
    "tools": ["array of MCP tool definitions (for function calling)"]
  }
}
```

**输出 Schema**：
```json
{
  "content": [{
    "type": "text",
    "text": "string (LLM response)"
  }],
  "isError": false,
  "usage": {
    "prompt_tokens": "int",
    "completion_tokens": "int",
    "total_tokens": "int"
  }
}
```

**成本估算**：单次缺陷修复约 5,000–15,000 tokens，按 $0.01/1K tokens 计约 $0.05–$0.15

**可替代性**：支持任意 OpenAI 兼容 API，切换 endpoint 仅需修改网关配置

**审计日志**：记录 `model + tokens + latency_ms + agent + skill`

---

### 2.4 CI/CD MCP（测试执行）

| 属性 | 值 |
|------|---|
| 工具名 | `ci_runner` |
| 描述 | 触发 CI 流水线、查询测试结果 |
| 调用方 | Verifier |
| 权限范围 | `execute:ci-pipeline` |
| 认证方式 | consumer token |

**输入 Schema**：
```json
{
  "tool_name": "ci_runner",
  "arguments": {
    "action": "trigger|status|logs",
    "pipeline_ref": "string",
    "branch": "string",
    "test_suite": "string"
  }
}
```

**输出 Schema**：
```json
{
  "content": [{
    "type": "text",
    "text": "string (CI result JSON or log output)"
  }],
  "isError": false
}
```

**超时控制**：CI 任务超时 >5min → 终止标记 timeout → 重试 1 次

---

### 2.5 K8s Deploy MCP（灰度发布）

| 属性 | 值 |
|------|---|
| 工具名 | `k8s_deploy` |
| 描述 | K8s 集群灰度发布、指标查询、回滚 |
| 调用方 | Release |
| 权限范围 | `deploy:k8s`（L3，人工审批） |
| 认证方式 | consumer token + 人工审批门禁 |

**输入 Schema**：
```json
{
  "tool_name": "k8s_deploy",
  "arguments": {
    "action": "canary|rollback|scale|metrics",
    "deployment_name": "string",
    "image_tag": "string",
    "traffic_percent": "int",
    "duration_minutes": "int",
    "rollback_threshold": "float"
  }
}
```

**输出 Schema**：
```json
{
  "content": [{
    "type": "text",
    "text": "string (deployment status or metrics JSON)"
  }],
  "isError": false
}
```

**自动回滚**：`error_rate_delta > rollback_threshold` → 立即回滚到 `rollback_point`

---

### 2.6 Knowledge Base MCP（知识库）

| 属性 | 值 |
|------|---|
| 工具名 | `knowledge_base` |
| 描述 | 读写知识库（Runbook、lessons_learned、Skill 模板） |
| 调用方 | Knowledge |
| 权限范围 | `read:knowledge-base` / `write:knowledge-base` |
| 认证方式 | consumer token |

**输入 Schema**：
```json
{
  "tool_name": "knowledge_base",
  "arguments": {
    "action": "read|write|search",
    "collection": "string (runbooks|lessons|templates)",
    "query": "string (for search)",
    "content": "object (for write)"
  }
}
```

**输出 Schema**：
```json
{
  "content": [{
    "type": "text",
    "text": "string (knowledge document or search results)"
  }],
  "isError": false
}
```

---

## 3. 认证与权限（对应 AgentTeams 零信任设计）

```
Worker (consumer token)
    │
    ▼
Higress AI 网关（凭证管理 + 路由 + 限流）
    │
    ▼
MCP Server（工具实现层）
```

- **Consumer Token**：每个 Agent 独立 token，网关层映射到真实 API 密钥
- **权限隔离**：MCP Server 层根据 token 决定可用工具集（而非 Agent 自行决定）
- **零信任原则**：即使 Worker 被攻陷，攻击者只能看到 consumer token，无法获取真实密钥
- **密钥轮换**：网关支持动态轮换，Worker 无感知

---

## 4. 错误处理与重试

| 错误类型 | 处理方式 | 重试策略 |
|---------|---------|---------|
| 网络超时 | 指数退避重试 | 3 次（5s/15s/30s） |
| 4xx（参数错误） | 直接报错，不重试 | 0 次 |
| 429（限流） | 等待后重试 | 2 次（30s/60s） |
| 5xx（服务端错误） | 指数退避重试 | 3 次（5s/15s/30s） |
| 工具不存在 | 直接报错，升级 DevLead | 0 次 |

所有重试均记录审计日志，包含 `attempt_count` 和 `backoff_ms`。

---

## 5. 审计日志格式

```json
{
  "timestamp": "ISO8601",
  "trace_id": "string (OpenTelemetry)",
  "agent": "string",
  "skill": "string",
  "tool_name": "string",
  "action": "string",
  "input_summary": "string (脱敏)",
  "output_summary": "string (脱敏)",
  "duration_ms": "int",
  "error_code": "string|null",
  "retry_count": "int",
  "approval_status": "none|manager_confirmed|human_approved|human_rejected"
}
```

---

## 6. 与 AgentTeams 原生 MCP 的兼容性

| 特性 | AgentTeams 原生 MCP | 本项目等价契约 | 兼容状态 |
|------|-------------------|--------------|---------|
| Tool 定义 | JSON Schema | 完全一致 | ✅ |
| 调用协议 | JSON-RPC 2.0 over SSE/HTTP | JSON-RPC 2.0 over HTTP | ✅ |
| 认证 | consumer token | consumer token | ✅ |
| 错误处理 | 标准错误码 | 完全一致 | ✅ |
| 审计 | trace_id 全链路 | trace_id 全链路 | ✅ |
| 迁移方式 | 替换 HTTP client 为 MCP Client SDK | < 350 行 | ✅ 低迁移成本 |

---

## 7. RAG 与上下文增强

本项目实现以下 3/4 项能力（超出最低要求 2/4）：

| 能力 | 实现状态 | 说明 |
|------|---------|------|
| Agent Memory Storage | ✅ | `data/lifecycle_state.json` 持久化 Agent 状态，Lifecycle Worker 管理 |
| Knowledge-Base RAG | ✅ | Knowledge Base MCP + PostmortemCapture Skill 支持知识库读写 |
| Shared State Management | ✅ | `task_manifest.json` + `lifecycle_state.json` 跨 Agent 共享状态 |
| Trajectory Observability | ✅ | OpenTelemetry Trace 全链路追踪 |

> **未实现**：向量数据库 RAG（复赛 DAL-3 目标，使用 PolarDB for PostgreSQL 向量搜索）

---

*文档版本：2.0.0 · 更新日期：2026-08-16*
