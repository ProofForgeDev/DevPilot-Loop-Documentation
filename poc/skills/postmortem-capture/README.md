# PostmortemCapture v0.1.0

复盘报告与知识沉淀 Skill。

## 安装

```bash
hiclaw skill install ./poc/skills/postmortem-capture
```

## 使用

```bash
# 触发 Knowledge Worker
hiclaw agent run knowledge --input '{"trace_id": "", "full_trace": {}, "defect": {}, "root_cause": {}, "patch": {}, "test_report": {}, "canary_report": {}}'
```

## 依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| llm-gateway | MCP | LLM 复盘报告生成 |
| knowledge-base-mcp | MCP | 知识库写入接口 |

## 权限

只写知识库，不接触代码仓库与生产环境。
