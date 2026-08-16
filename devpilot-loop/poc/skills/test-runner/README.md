# TestRunner v2.0.0

沙箱测试执行 Skill。

## 安装

```bash
hiclaw skill install ./poc/skills/test-runner
```

## 使用

```bash
# 触发 Verifier Worker
hiclaw agent run verifier --input '{"patch_id": "", "patch_diff": "", "test_suite_ref": "", "sandbox_config": {}}'
```

## 依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| ci-api-mcp | MCP | CI/CD 测试触发接口 |
| llm-gateway | MCP | LLM 失败原因分析 |

## 权限

沙箱执行，不接触生产环境。
