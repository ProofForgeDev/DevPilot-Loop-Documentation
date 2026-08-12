# FixGenerator v0.1.0

代码修复与 patch 生成 Skill。

## 安装

```bash
hiclaw skill install ./poc/skills/fix-generator
```

## 使用

```bash
# 触发 Fixer Worker
hiclaw agent run fixer --input '{"root_cause": {}, "impact_scope": [], "repo_ref": "", "branch_strategy": ""}'
```

## 依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| llm-gateway | MCP | LLM 推理网关 |
| git-api-mcp | MCP | Git 仓库读写接口 |

## 权限

L2 写操作：创建分支、生成 patch，需 Manager 确认。
L3 写操作：push 主干，需人工审批。
