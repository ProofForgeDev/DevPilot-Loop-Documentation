# Agent Identity List

> 对应评分维度：**多 Agent 协同设计**，权重 **25%**
> 竞赛规则要求：提交包含 Agent 名称、类型、职责、能力的完整身份列表

---

## Agent 总览

| # | Agent 名称 | 类型 | 职责 | 挂载 Skill | 权限级别 |
|---|-----------|------|------|-----------|---------|
| 1 | devlead | Manager | 任务拆解、派发、升级决策 | 无（纯编排） | L3（全权限） |
| 2 | intake | Worker | 缺陷归并、分诊定级 | defect-triage | L1（只读） |
| 3 | analyst | Worker | 根因定位、代码分析 | code-root-cause | L1（只读） |
| 4 | fixer | Worker | 补丁生成、风险评估 | fix-generator | L2（写需确认） |
| 5 | verifier | Worker | 测试执行、质量验证 | test-runner | L2（写需确认） |
| 6 | release | Worker | 灰度发布、回滚决策 | canary-release | L3（需审批） |
| 7 | knowledge | Worker | 知识沉淀、Runbook 生成 | postmortem-capture | L1（只读） |
| 8 | orchestrator | Worker | 任务编排、依赖解析 | orchestrator | L2（写需确认） |
| 9 | lifecycle | Worker | 服务生命周期管理 | lifecycle | L1（只读） |

---

## Agent 详细定义

### Agent 1: devlead (Manager)

- **类型**: Manager
- **端口**: 8008
- **职责**: 
  - 接收外部任务（Issue/告警/CI 失败）
  - 拆解为结构化 plan（含步骤、Worker 分配、Skill 指定）
  - 派发任务给对应 Worker
  - 追踪每个 Worker 的执行状态
  - 决策升级：失败 ≥2 次上报人类；L3 操作强制人工审批
  - 汇总最终交付报告
- **约束**: 
  - 不直接改代码、不执行 Skill、不调用业务工具
  - 纯编排者，保持编排纯粹性
  - 所有通信在 Matrix 房间中，人类可见
- **升级策略**: 
  - Worker 无响应 >60s → 重试 3 次 → 熔断 → 人工接管
  - 同一子任务失败 ≥2 次 → 上报人类
  - L3 操作（push 主干/生产发布）→ 强制人工审批
- **配置文件**: `poc/deploy/agents/devlead/config.yaml`

### Agent 2: intake (Worker)

- **类型**: Worker
- **端口**: 8001
- **职责**: 
  - 接收原始报障（Issue/告警/CI 失败）
  - 归并去重：与已有缺陷对比，判断是否重复
  - 结构化：产出标准缺陷单
  - 定优先级：P0/P1/P2/P3
- **挂载 Skill**: defect-triage v2.0.0
- **权限级别**: L1（只读）
- **配置文件**: `poc/deploy/agents/intake/config.yaml`

### Agent 3: analyst (Worker)

- **类型**: Worker
- **端口**: 8002
- **职责**: 
  - 接收缺陷单
  - 分析代码定位根因
  - 生成根因报告
- **挂载 Skill**: code-root-cause v2.0.0
- **权限级别**: L1（只读）
- **配置文件**: `poc/deploy/agents/analyst/config.yaml`

### Agent 4: fixer (Worker)

- **类型**: Worker
- **端口**: 8003
- **职责**: 
  - 接收根因报告
  - 生成修复补丁
  - 创建回滚点
  - 提交人工审批
- **挂载 Skill**: fix-generator v2.0.0
- **权限级别**: L2（写需确认）
- **配置文件**: `poc/deploy/agents/fixer/config.yaml`

### Agent 5: verifier (Worker)

- **类型**: Worker
- **端口**: 8004
- **职责**: 
  - 接收补丁
  - 执行测试验证
  - 生成验证报告
- **挂载 Skill**: test-runner v2.0.0
- **权限级别**: L2（写需确认）
- **配置文件**: `poc/deploy/agents/verifier/config.yaml`

### Agent 6: release (Worker)

- **类型**: Worker
- **端口**: 8005
- **职责**: 
  - 接收验证通过的补丁
  - 执行灰度发布
  - 监控发布指标
  - 做发布/回滚决策
- **挂载 Skill**: canary-release v2.0.0
- **权限级别**: L3（需审批）
- **配置文件**: `poc/deploy/agents/release/config.yaml`

### Agent 7: knowledge (Worker)

- **类型**: Worker
- **端口**: 8006
- **职责**: 
  - 接收完整修复记录
  - 提取经验知识
  - 生成 Runbook
  - 更新知识库
- **挂载 Skill**: postmortem-capture v2.0.0
- **权限级别**: L1（只读）
- **配置文件**: `poc/deploy/agents/knowledge/config.yaml`

### Agent 8: orchestrator (Worker)

- **类型**: Worker
- **端口**: 8007
- **职责**: 
  - 多阶段任务编排
  - 依赖解析（拓扑排序）
  - 失败自动回滚
  - 指数退避重试
  - 进度实时追踪
- **挂载 Skill**: orchestrator v2.0.0
- **权限级别**: L2（写需确认）
- **配置文件**: `poc/deploy/agents/orchestrator/config.yaml`

### Agent 9: lifecycle (Worker)

- **类型**: Worker
- **端口**: 8009
- **职责**: 
  - 服务启动管理
  - 检查点保存
  - 状态恢复
  - 优雅关闭
  - 重启管理
- **挂载 Skill**: lifecycle v2.0.0
- **权限级别**: L1（只读）
- **配置文件**: `poc/deploy/agents/lifecycle/config.yaml`

---

## 通信矩阵

| Sender → Receiver | devlead | intake | analyst | fixer | verifier | release | knowledge | orchestrator | lifecycle |
|------------------|---------|--------|---------|-------|----------|---------|-----------|-------------|-----------|
| devlead | - | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| intake | ✅ | - | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| analyst | ✅ | ✅ | - | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| fixer | ✅ | ❌ | ✅ | - | ✅ | ❌ | ❌ | ❌ | ❌ |
| verifier | ✅ | ❌ | ✅ | ✅ | - | ✅ | ❌ | ❌ | ❌ |
| release | ✅ | ❌ | ❌ | ✅ | ✅ | - | ✅ | ❌ | ❌ |
| knowledge | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | - | ❌ | ❌ |
| orchestrator | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | - | ✅ |
| lifecycle | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | - |

---

**文档版本**: v2.2.0  
**最后更新**: 2026-08-16
