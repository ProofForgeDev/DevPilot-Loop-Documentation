---
name: canary-release
version: 0.1.0
description: 执行灰度发布、监控灰度指标、做发布/回滚决策
author: DevPilot Loop Contributors
license: Apache-2.0
---

# CanaryRelease

## 用途
执行灰度发布，监控灰度指标（错误率/延迟），做出发布/回滚决策。

## 输入
```json
{
  "patch_id": "",
  "test_report": {},
  "verdict": "approve",
  "canary_config": {
    "traffic_percent": 0,
    "duration_minutes": 0,
    "rollback_threshold": 0.0
  }
}
```

## 输出
```json
{
  "canary_report": {
    "status": "success|rollback",
    "error_rate_delta": 0.0,
    "latency_p99_delta": 0.0
  },
  "release_decision": "promote|rollback",
  "rollback_point_ref": "string"
}
```

## 执行步骤
1. 在 K8s 集群中以 canary_config.traffic_percent 比例部署新版本
2. 等待 canary_config.duration_minutes 分钟，持续采集指标
3. 对比灰度前后的 error_rate 与 latency_p99
4. 若 error_rate_delta > rollback_threshold → 自动回滚
5. 否则 → 做出 release_decision（promote / rollback）
6. 回滚时回到 rollback_point_ref 指定的回滚点
7. L3 生产操作需人工审批

## 安全边界
- **L3 生产操作**：K8s 部署 API，需人工审批
- error_rate_delta > threshold → 自动回滚（无需审批）
- 所有调用经 Higress AI 网关转发

## 失败处理
灰度部署失败 → 自动回滚到 rollback_point → 通知 DevLead → 记录审计日志
