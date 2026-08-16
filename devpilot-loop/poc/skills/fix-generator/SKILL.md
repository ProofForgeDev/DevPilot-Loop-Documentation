---
name: fix-generator
version: 0.1.0
description: 根据根因分析结果生成修复方案与代码 patch，创建回滚点
author: DevPilot Loop Contributors
license: Apache-2.0
---

# FixGenerator

## 用途
根据根因分析结果，生成修复方案与代码 patch，创建回滚点。

## 输入
```json
{
  "root_cause": {},
  "impact_scope": [],
  "repo_ref": "",
  "branch_strategy": ""
}
```

## 输出
```json
{
  "patch_id": "string",
  "patch_diff": "string",
  "rollback_point": {
    "git_tag": "string",
    "snapshot_id": "string"
  },
  "fix_description": "string",
  "risk_level": "low|medium|high"
}
```

## 执行步骤
1. checkout 最新代码，按 branch_strategy 创建修复分支
2. 在 root_cause 指向的文件和行号处生成修复代码
3. 使用 LLM 辅助生成符合项目风格的 patch
4. 创建回滚点：git tag rollback-{patch_id}，记录 snapshot_id
5. 评估 risk_level（基于修改范围与影响面）
6. 输出 patch_diff 与 fix_description
7. L3 操作（push 主干）需人工审批，L2（创建分支）需 Manager 确认

## 安全边界
- **L2 写操作**：创建分支、生成 patch，需 Manager 确认
- **L3 写操作**：push 主干，需人工审批
- 所有操作经 Higress AI 网关转发

## 失败处理
重试 3 次 → 降级为人工修复建议（输出候选方案供人选择）
