# CodeRootCause v0.1.0

代码根因定位 Skill。

## 安装

```bash
hiclaw skill install ./poc/skills/code-root-cause
```

## 使用

```bash
# 触发 Analyst Worker
hiclaw agent run analyst --input '{"defect_id": "", "severity": "", "evidence": [], "repo_ref": "", "recent_commits": []}'
```

## 依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| llm-gateway | MCP | LLM 推理网关 |
| git-api-mcp | MCP | Git 仓库读写接口 |

## 权限

只读访问代码仓库，不修改任何代码。
