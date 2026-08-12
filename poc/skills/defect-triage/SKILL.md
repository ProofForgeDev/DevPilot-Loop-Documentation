---
name: defect-triage
version: 0.1.0
description: 缺陷/需求归并去重、结构化为缺陷单、判定优先级
author: DevPilot Loop Contributors
license: Apache-2.0
---

# DefectTriage

## 用途
接收原始报障（Issue / 告警 / CI 失败），归并去重，结构化为标准缺陷单，判定优先级。

## 输入
```json
{
  "raw_issue": {},
  "logs": [],
  "existing_defects_ref": "",
  "source_channel": ""
}
```

## 输出
```json
{
  "defect_id": "string",
  "title": "string",
  "severity": "P0|P1|P2|P3",
  "dedup_of": "string|null",
  "evidence": ["string"],
  "triage_confidence": 0.0
}
```

## 执行步骤
1. 调用 Issue Tracker API 获取原始报障详情
2. 与 existing_defects_ref 中已有缺陷进行相似度比对（归并去重）
3. 使用 LLM 提取 title、生成 evidence 列表
4. 根据影响范围与紧急程度判定 severity（P0–P3）
5. 计算 triage_confidence（基于证据充分度）
6. 输出结构化缺陷单

## 安全边界
- **只读**权限，不修改任何生产数据
- 所有外部调用经 Higress AI 网关转发
- 不缓存敏感信息到本地

## 失败处理
重试 3 次（间隔 5s / 15s / 30s）→ 降级人工分诊 → 记录 trace
