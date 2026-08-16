# 第 5 章 安全与审计

> 对应评分维度：**工程落地能力与安全可审计**，权重 **20%**

---

## 5.1 凭证安全（继承 AgentTeams 框架原生设计）

基于 HiClaw 零信任架构：
- Worker **仅持"工牌"式 consumer token**，永不接触真实 API 密钥
- 真实凭证由 **Higress AI 网关集中管理**
- 当 Worker 需调用 LLM 或 GitHub API 时，请求首先抵达 Higress Gateway，
  网关依据 Token 查找对应密钥并完成**动态注入**后再转发至目标服务
- 即使 Worker 被攻击，攻击者也**无法获得任何有效凭证**

> 本项目**直接继承**此设计，不重复造轮子。安全能力不是我们额外搭建的，
> 而是 AgentTeams 框架原生提供的。我们在此之上增加了审批流与回滚点。

## 5.2 权限分级（三级）

| 级别 | 操作类型 | 执行方式 | 示例 |
|------|---------|---------|------|
| **L1 只读** | 查询 / 分析 | 自动执行 | CodeRootCause 读代码、DefectTriage 读 Issue |
| **L2 写** | 代码变更 | 需 Manager 确认 | FixGenerator 创建分支、生成 patch |
| **L3 生产** | push 主干 / 生产发布 | 需**人工审批** | CanaryRelease 上生产 |

## 5.3 审批流

高风险动作触发
→ 生成审批单（含动作描述、影响范围、回滚方案）
→ Matrix 房间 @人类
→ 人工在 Matrix 客户端确认 / 驳回
→ 确认 → 执行
→ 驳回 → 终止 + 记录审计日志

全程在 Matrix 房间留痕，可追溯。

## 5.4 回滚机制

每次修复前
→ 创建回滚点（git tag: rollback-{patch_id} + 部署快照）
→ 执行修复
→ 验证失败 or 灰度异常
→ 自动回滚到回滚点
→ 通知 DevLead
→ 记录审计日志

## 5.5 审计日志

全量记录 Agent 决策、Skill 调用、工具执行。

| 字段 | 说明 |
|------|------|
| timestamp | ISO 8601 |
| trace_id | OpenTelemetry Trace ID |
| agent | 执行 Agent 名称 |
| skill | 调用 Skill 名称 |
| action | 具体动作 |
| input_summary | 输入摘要（脱敏） |
| output_summary | 输出摘要（脱敏） |
| approval_status | none / manager_confirmed / human_approved / human_rejected |
| duration_ms | 执行耗时 |

## 5.6 红线自查

| # | 红线 | 自查结果 |
|---|------|---------|
| 1 | 不能只交概念无 PoC | ✅ 有 L1/L2 证据（日志/截图/trace） |
| 2 | 不能抄袭 | ✅ 全部原创，引用已标注 |
| 3 | 不能买 Star | ✅ 未做任何刷量行为 |
| 4 | 不能虚假陈述 | ✅ 执行环节已如实标注 L1/L2/L3 |
| 5 | 内容必须原创 | ✅ |
| 6 | 必须以 AgentTeams 为基座 | ✅ 1:1 映射框架原生能力 |
