# 第 4 章 Skill 工程体系 —— Skill Checklist

> 对应评分维度：**Skill 工程化设计**，权重 **25%**

共 **6 个 Skill**，均为标准 skill 包格式，可通过 `hiclaw skill install` 安装。

---

## Skill 1：DefectTriage v0.1.0

| # | 字段 | 内容 |
|---|------|------|
| 1 | 名称与版本 | defect-triage v0.1.0 |
| 2 | 用途 | 缺陷/需求归并去重、结构化为缺陷单、判定优先级（P0–P3） |
| 3 | 输入规格 | `{"raw_issue": "object", "logs": ["string"], "existing_defects_ref": "string", "source_channel": "string"}` |
| 4 | 输出规格 | `{"defect_id": "string", "title": "string", "severity": "P0|P1|P2|P3", "dedup_of": "string|null", "evidence": ["string"], "triage_confidence": "float"}` |
| 5 | 调用条件 | DevLead 派发 plan.step[0]；新 Issue / 告警 / CI 失败进入时 |
| 6 | 依赖工具 | Issue Tracker API（经 Higress AI 网关）、LLM API（经 Higress AI 网关） |
| 7 | 失败处理 | 重试 3 次（5s/15s/30s）→ 降级人工分诊 → 记录 trace |
| 8 | 安全边界 | **只读**权限，无写操作，无需审批 |
| 9 | 复用性 | Intake 专用。可平移到：运维告警归并、客服工单归并、安全事件分诊 |

---

## Skill 2：CodeRootCause v0.1.0

| # | 字段 | 内容 |
|---|------|------|
| 1 | 名称与版本 | code-root-cause v0.1.0 |
| 2 | 用途 | 根据结构化缺陷单，在代码仓库中定位根因，输出证据链与影响范围 |
| 3 | 输入规格 | `{"defect_id": "string", "severity": "string", "evidence": ["string"], "repo_ref": "string", "recent_commits": ["string"]}` |
| 4 | 输出规格 | `{"root_cause": {"file": "string", "line_range": "string", "description": "string"}, "impact_scope": ["string"], "evidence_chain": ["string"], "confidence": "float"}` |
| 5 | 调用条件 | Intake 产出 defect 后，DevLead 派发 plan.step[1] |
| 6 | 依赖工具 | Git API（读代码/commit history，经 Higress AI 网关）、LLM API（经 Higress AI 网关） |
| 7 | 失败处理 | 重试 3 次 → 扩大搜索范围（最近 50 commits）→ 仍失败则降级人工定位 |
| 8 | 安全边界 | **只读**权限，不修改代码，无需审批 |
| 9 | 复用性 | Analyst 专用。可平移到：客服意图根因分析、安全漏洞溯源 |

---

## Skill 3：FixGenerator v0.1.0

| # | 字段 | 内容 |
|---|------|------|
| 1 | 名称与版本 | fix-generator v0.1.0 |
| 2 | 用途 | 根据根因分析结果，生成修复方案与代码 patch，创建回滚点 |
| 3 | 输入规格 | `{"root_cause": "object", "impact_scope": ["string"], "repo_ref": "string", "branch_strategy": "string"}` |
| 4 | 输出规格 | `{"patch_id": "string", "patch_diff": "string", "rollback_point": {"git_tag": "string", "snapshot_id": "string"}, "fix_description": "string", "risk_level": "low|medium|high"}` |
| 5 | 调用条件 | Analyst 产出 root_cause 且 confidence ≥ 0.7 后，DevLead 派发 plan.step[2] |
| 6 | 依赖工具 | Git API（创建分支/生成 patch，经 Higress AI 网关）、LLM API（经 Higress AI 网关） |
| 7 | 失败处理 | 重试 3 次 → 降级为人工修复建议（输出候选方案供人选择） |
| 8 | 安全边界 | **写操作（L2）**：创建分支、生成 patch，需 Manager 确认。**push 主干（L3）**：需人工审批 |
| 9 | 复用性 | Fixer 专用。可平移到：运维自愈脚本生成、配置修复 |

---

## Skill 4：TestRunner v0.1.0

| # | 字段 | 内容 |
|---|------|------|
| 1 | 名称与版本 | test-runner v0.1.0 |
| 2 | 用途 | 在沙箱环境执行单元测试与回归测试，输出测试报告与通过/驳回判定 |
| 3 | 输入规格 | `{"patch_id": "string", "patch_diff": "string", "test_suite_ref": "string", "sandbox_config": "object"}` |
| 4 | 输出规格 | `{"test_report": {"total": "int", "passed": "int", "failed": "int", "skipped": "int"}, "regression_result": "pass|fail", "verdict": "approve|reject", "failure_details": ["string"]}` |
| 5 | 调用条件 | Fixer 产出 patch 且经 Manager 确认后，DevLead 派发 plan.step[3] |
| 6 | 依赖工具 | CI API（触发测试，经 Higress AI 网关）、LLM API（分析失败原因，经 Higress AI 网关） |
| 7 | 失败处理 | 测试超时（>5min）→ 终止标记 timeout → 重试 1 次 → 降级人工 |
| 8 | 安全边界 | **沙箱执行**：不接触生产环境，无需审批 |
| 9 | 复用性 | Verifier 专用。可平移到：运维健康检查、风控规则校验 |

---

## Skill 5：CanaryRelease v0.1.0

| # | 字段 | 内容 |
|---|------|------|
| 1 | 名称与版本 | canary-release v0.1.0 |
| 2 | 用途 | 执行灰度发布、监控灰度指标（错误率/延迟）、做发布/回滚决策 |
| 3 | 输入规格 | `{"patch_id": "string", "test_report": "object", "verdict": "approve", "canary_config": {"traffic_percent": "int", "duration_minutes": "int", "rollback_threshold": "float"}}` |
| 4 | 输出规格 | `{"canary_report": {"status": "success|rollback", "error_rate_delta": "float", "latency_p99_delta": "float"}, "release_decision": "promote|rollback", "rollback_point_ref": "string"}` |
| 5 | 调用条件 | Verifier 产出 verdict = approve 后，DevLead 派发 plan.step[4] |
| 6 | 依赖工具 | K8s 部署 API（经 Higress AI 网关）、监控 API（经 Higress AI 网关） |
| 7 | 失败处理 | 灰度部署失败 → 自动回滚到 rollback_point → 通知 DevLead → 记录审计日志 |
| 8 | 安全边界 | **生产操作（L3）**：需人工审批。error_rate_delta > threshold → 自动回滚 |
| 9 | 复用性 | Release 专用。可平移到：运维变更灰度、金融策略灰度 |

---

## Skill 6：PostmortemCapture v0.1.0

| # | 字段 | 内容 |
|---|------|------|
| 1 | 名称与版本 | postmortem-capture v0.1.0 |
| 2 | 用途 | 汇总全流程 trace，生成复盘报告，沉淀 Runbook 与 Skill 模板更新建议 |
| 3 | 输入规格 | `{"trace_id": "string", "full_trace": "object", "defect": "object", "root_cause": "object", "patch": "object", "test_report": "object", "canary_report": "object"}` |
| 4 | 输出规格 | `{"runbook_id": "string", "runbook_content": "string", "skill_template_update": "object|null", "lessons_learned": ["string"], "knowledge_base_ref": "string"}` |
| 5 | 调用条件 | Release 产出 canary_report 后（无论 promote 或 rollback），DevLead 派发 plan.step[5] |
| 6 | 依赖工具 | 知识库 / Wiki API（经 Higress AI 网关）、LLM API（经 Higress AI 网关） |
| 7 | 失败处理 | 知识库写入失败 → 重试 3 次 → 降级为本地文件存储 → 标记待同步 |
| 8 | 安全边界 | **只写知识库**：不接触代码仓库与生产环境，无需审批 |
| 9 | 复用性 | Knowledge 专用。**场景无关**，可直接用于运维复盘、客服案例沉淀、安全事件复盘 |

---

## Skill–Agent 复用矩阵

| Skill ↓ \ Agent → | DevLead | Intake | Analyst | Fixer | Verifier | Release | Knowledge |
|--------------------|---------|--------|---------|-------|----------|---------|-----------|
| DefectTriage | | ● | | | | | |
| CodeRootCause | | | ● | | | | |
| FixGenerator | | | | ● | | | |
| TestRunner | | | | | ● | | |
| CanaryRelease | | | | | | ● | |
| PostmortemCapture | | | | | | | ● |

**跨场景复用**：DefectTriage、PostmortemCapture 为场景无关通用 Skill，
可直接用于运维 / 客服 / 风控场景。

---

## 安装验证

```bash
# 安装命令
hiclaw skill install ./poc/skills/defect-triage

# 预期输出
✓ defect-triage v0.1.0 installed

# 验证方式
hiclaw skill list
# 应显示 defect-triage v0.1.0
```

真实性声明：当前安装验证在本地 HiClaw 实例完成（L1 实机），
尚未发布到公共 skills.sh 仓库。
