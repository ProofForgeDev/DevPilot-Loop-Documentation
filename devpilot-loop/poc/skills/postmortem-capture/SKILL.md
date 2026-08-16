---
name: postmortem-capture
version: 0.1.0
description: 汇总全流程 trace，生成复盘报告，沉淀 Runbook 与 Skill 模板
author: DevPilot Loop Contributors
license: Apache-2.0
---

# PostmortemCapture

## 用途
汇总全流程 trace，生成复盘报告，沉淀 Runbook 与 Skill 模板更新建议。

## 输入
```json
{
  "trace_id": "",
  "full_trace": {},
  "defect": {},
  "root_cause": {},
  "patch": {},
  "test_report": {},
  "canary_report": {}
}
```

## 输出
```json
{
  "runbook_id": "string",
  "runbook_content": "string",
  "skill_template_update": {},
  "lessons_learned": [],
  "knowledge_base_ref": "string"
}
```

## 执行步骤
1. 拉取 full_trace 中所有 Agent 决策与 Skill 执行记录
2. 按照 defect → root_cause → patch → test → release 时序整理事件流
3. 使用 LLM 生成结构化复盘报告（Runbook）
4. 提炼 lessons_learned（可复用的经验与教训）
5. 识别可复用的 Skill 模板改进建议
6. 将 runbook 写入知识库，返回 runbook_id 与 knowledge_base_ref

## 安全边界
- **只写知识库**，不接触代码仓库与生产环境
- 所有调用经 Higress AI 网关转发
- 不存储任何敏感凭证或 PII

## 失败处理
知识库写入失败 → 重试 3 次 → 降级为本地文件存储 → 标记待同步
