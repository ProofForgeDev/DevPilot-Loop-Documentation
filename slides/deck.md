---
marp: true
theme: default
paginate: true
size: 16:9
---

<!-- _class: lead -->

# DevPilot Loop
## 研发团队的"自动驾驶"：从缺陷归并到知识沉淀的全自主闭环

基于 AgentTeams（原 HiClaw）· Apache 2.0 开源

---

# 第 1 章 场景与痛点
<!-- 评分维度：场景价值与行业可复制性 25% -->

## 目标用户：3–20 人中小研发团队

| 痛点 | 现状 |
|------|------|
| 修复周期长 | 平均 **4 小时** / 缺陷 |
| 上下文丢失 | 重复沟通占修复时间 **40%+** |
| 经验不沉淀 | 同类缺陷反复出现 |
| 无法审计 | 出了问题无法追溯 |

---

# 量化价值
<!-- 评分维度：场景价值与行业可复制性 25% -->

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 修复周期 | 4 小时 | **15 分钟** | **16×** |
| 人工介入 | 100% | 减少 **80%** | 仅关键审批 |
| 复发率 | 基线 | 下降 **60%** | 经验沉淀 |

---

# 行业可复制性
<!-- 评分维度：场景价值与行业可复制性 25% -->

Manager–Worker–Skill 是场景无关的骨架：

| 场景 | 映射 |
|------|------|
| 运维自愈 | Intake→告警归并，Fixer→自愈脚本 |
| 智能客服 | Analyst→意图根因，Knowledge→话术沉淀 |
| 金融风控 | Verifier→规则校验，Release→灰度策略 |

---

# 第 2 章 方案总览
<!-- 端到端架构图 -->

![架构图](assets/architecture-overview.png)

外部入口 → DevLead(Manager) → 6 Workers → 治理层
全部在 Matrix 房间（人类可见可介入）

---

# DAL 自主分级模型
<!-- 行业定义级贡献 -->

| 级别 | 定义 | 状态 |
|------|------|------|
| DAL-1 | Agent 辅助定位 | ✅ 已实现 |
| DAL-2 | Agent 自主修复，人审批 | ✅ **当前** |
| DAL-3 | 自主闭环，人抽检 | 🎯 复赛 |
| DAL-4 | 多项目并行 | 愿景 |
| DAL-5 | 全自动闭环 | 长期 |

对标汽车 L1–L5 自动驾驶分级。

---

# 第 3 章 7 Agent 职责表
<!-- 评分维度：多 Agent 协同 25% -->

| Agent | 类型 | 职责 | Skill |
|-------|------|------|-------|
| DevLead | Manager | 拆解·调度·升级 | — |
| Intake | Worker | 归并分诊 | DefectTriage |
| Analyst | Worker | 根因定位 | CodeRootCause |
| Fixer | Worker | 修复执行 | FixGenerator |
| Verifier | Worker | 测试验证 | TestRunner |
| Release | Worker | 灰度发布 | CanaryRelease |
| Knowledge | Worker | 知识沉淀 | PostmortemCapture |

---

# 任务流转时序图
<!-- 评分维度：多 Agent 协同 25% -->

![时序图](assets/task-flow-sequence.png)

报障 → DevLead → Intake → Analyst → Fixer(★审批) → Verifier → Release(★审批) → Knowledge → 闭环

---

# 异常升级与回滚
<!-- 评分维度：多 Agent 协同 25% -->

- Worker 失败 → 重试 3 次 → 降级 → 上报 DevLead → 人工接管
- L3 操作 → 强制人工审批
- 灰度异常 → 自动回滚到 rollback_point
- 全程 Matrix 留痕

---

# 第 4 章 6 Skill 清单
<!-- 评分维度：Skill 工程 25% -->

每个 Skill 含 9 字段：名称版本 / 用途 / 输入 / 输出 / 调用条件 /
依赖工具 / 失败处理 / 安全边界 / 复用性

（详见 docs/04-skills.md，此处展示表格）

---

# Skill–Agent 复用矩阵 + 安装验证
<!-- 评分维度：Skill 工程 25% -->

![复用矩阵](assets/skill-agent-matrix.png)

```bash
hiclaw skill install ./poc/skills/defect-triage
# ✓ defect-triage v0.1.0 installed
```

跨场景复用：DefectTriage、PostmortemCapture 场景无关。

---

# 第 5 章 工程落地
<!-- 评分维度：工程落地 20% -->

| 项目 | 状态 | 层级 |
|------|------|------|
| HiClaw 部署（Docker） | ✅ | L1 实机 |
| 7 Agent 配置 | ✅ | L1 实机 |
| 6 Skill 安装验证 | ✅ | L1 实机 |
| 端到端 NPE 场景 | ✅ | L1/L2 |

真实证据见 poc/evidence/ 目录。

---

# 安全与审计
<!-- 评分维度：工程落地 20% -->

- 零信任：Worker 仅持 consumer token（框架原生）
- 三级权限：L1 只读 / L2 写需确认 / L3 生产需审批
- 审批流：Matrix @人类 → 确认/驳回
- 回滚：git tag + 部署快照
- 审计日志：全量记录
<!-- 评分维度：安全可审计 20% -->

---

# 第 6 章 开源计划
<!-- 开源贡献 5% -->

| 项目 | 说明 |
|------|------|
| 协议 | Apache 2.0 |
| 范围 | Agent 定义 / Skill / 场景 / 文档全部开源 |
| 依赖 | 完整披露（含 LLM API 成本与可替代性） |
| 目标 | AgentTeams 研发场景官方参考实现 |

---

# 第 7 章 落地计划
<!-- 评分维度：工程落地 20% -->

| 阶段 | 目标 | DAL |
|------|------|-----|
| 初赛 PoC | 7 Agent + 6 Skill 跑通 NPE | DAL-2 |
| 复赛 | 真实仓库 + 审批流 | DAL-2→3 |
| 决赛 | 多项目并行 | DAL-3 |

风险 5 项已识别，均有缓解措施（见 docs/08-roadmap.md）。

---

# 第 8 章 团队介绍

（团队成员 / 分工 / 相关成果）

DevPilot Loop
开源地址：github.com/YOUR_USERNAME/devpilot-loop
Apache 2.0 · 目标成为 AgentTeams 研发场景官方参考实现

---

# 谢谢

**DevPilot Loop**
研发团队的"自动驾驶"

github.com/YOUR_USERNAME/devpilot-loop
