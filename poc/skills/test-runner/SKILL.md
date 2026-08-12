---
name: test-runner
version: 0.1.0
description: 在沙箱环境执行单元测试与回归测试，输出测试报告
author: DevPilot Loop Contributors
license: Apache-2.0
---

# TestRunner

## 用途
在沙箱环境执行单元测试与回归测试，输出测试报告与通过/驳回判定。

## 输入
```json
{
  "patch_id": "",
  "patch_diff": "",
  "test_suite_ref": "",
  "sandbox_config": {}
}
```

## 输出
```json
{
  "test_report": {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0
  },
  "regression_result": "pass|fail",
  "verdict": "approve|reject",
  "failure_details": []
}
```

## 执行步骤
1. 在 sandbox_config 配置的沙箱环境中 checkout 代码
2. 应用 patch_diff 到沙箱环境
3. 触发 test_suite_ref 指向的测试套件
4. 收集测试结果，统计 total/passed/failed/skipped
5. 判断 regression_result（所有测试是否全部通过）
6. 给出 verdict（approve / reject）
7. 失败用例详细信息写入 failure_details

## 安全边界
- **沙箱执行**，不接触生产环境
- 所有外部调用经 Higress AI 网关转发
- 测试超时（>5min）自动终止

## 失败处理
测试超时 → 终止标记 timeout → 重试 1 次 → 降级人工
