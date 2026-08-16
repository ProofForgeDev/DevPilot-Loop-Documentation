# CanaryRelease v2.0.0

灰度发布与回滚决策 Skill。

## 安装

```bash
hiclaw skill install ./poc/skills/canary-release
```

## 使用

```bash
# 触发 Release Worker
hiclaw agent run release --input '{"patch_id": "", "test_report": {}, "verdict": "approve", "canary_config": {}}'
```

## 依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| k8s-api-mcp | MCP | K8s 部署接口 |
| monitoring-api-mcp | MCP | 监控指标采集接口 |

## 权限

L3 生产操作：需人工审批。
error_rate_delta > threshold → 自动回滚（无需审批）。
