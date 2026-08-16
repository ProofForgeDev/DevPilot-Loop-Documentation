---
name: code-root-cause
version: 0.1.0
description: 根据结构化缺陷单定位代码根因，输出证据链与影响范围
author: DevPilot Loop Contributors
license: Apache-2.0
---

# CodeRootCause

## 用途
根据结构化缺陷单，在代码仓库中定位根因，输出证据链与影响范围。

## 输入
```json
{
  "defect_id": "",
  "severity": "",
  "evidence": [],
  "repo_ref": "",
  "recent_commits": []
}
```

## 输出
```json
{
  "root_cause": {
    "file": "string",
    "line_range": "string",
    "description": "string"
  },
  "impact_scope": ["string"],
  "evidence_chain": ["string"],
  "confidence": 0.0
}
```

## 执行步骤
1. 克隆或 checkout repo_ref 对应分支
2. 根据 evidence 关键词搜索相关代码文件
3. 结合 recent_commits 定位引入问题的最近变更
4. 使用 LLM 分析根因，生成 file + line_range + description
5. 梳理 impact_scope（受影响模块/接口/依赖）
6. 构建 evidence_chain（从报障到根因的推理链）
7. 评估 confidence（基于证据充分度与根因确定性）
8. 输出结构化根因报告

## 安全边界
- **只读**权限，不修改任何代码
- 所有外部调用经 Higress AI 网关转发
- 不缓存完整源代码到本地

## 失败处理
重试 3 次 → 扩大搜索范围（最近 50 commits）→ 仍失败则降级人工定位
