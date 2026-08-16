# DefectTriage v2.0.0

缺陷归并与分诊 Skill。

## 安装

```bash
hiclaw skill install ./poc/skills/defect-triage
```

## 使用

由 Intake Worker 自动调用，无需手动触发。

## 依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| issue-tracker-mcp | MCP | Issue Tracker 接口 |
| llm-gateway | MCP | LLM 推理网关（经 Higress AI 网关） |

## 权限

只读访问 Issue Tracker，不修改任何数据。

## 协议

Apache 2.0
