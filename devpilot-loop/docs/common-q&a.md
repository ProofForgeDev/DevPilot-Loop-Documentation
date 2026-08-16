## 核心问答 (Q&A)

### Q1: DAL 模型的创新性在哪里？

**A**: DAL (DevPilot Autonomy Level) 是面向研发的特定动作纳入自主性评估，提供可量化的判定公式和验证方法。

**支撑证据**: `docs/innovation-dal-analysis.md`, `evidence/l4/security_audit_report.md`

---

### Q2: 9 个 Agent 和 8 个 Skill 是否必要？能否简化？

**A**: 每个 Agent/Skill 对应研发流程的一个关键环节，不可简化：
- Intake: 归并去重（解决重复报障问题）
- Analyst: 根因定位（减少人工调试时间）
- Fixer: 自动修复（提升效率）
- Verifier: 测试验证（保证质量）
- Release: 灰度发布（降低风险）
- Knowledge: 知识沉淀（防止复发）
- Orchestrator: 复杂任务编排（DAL-2→3 关键）
- Lifecycle: 服务生命周期管理（容错恢复）

**简化后果**: 失去端到端闭环能力，退回 DAL-1 级别。

---

### Q3: 如何证明安全性？

**A**: 三级安全保证：
1. **零信任架构**: Consumer Token + Higress 网关 + SHA-256 凭证存储
2. **独立安全审计**: Bandit + Safety + Trivy + Semgrep 全量扫描，评分 98/100
3. **合规映射**: OWASP Top 10 2021 全部 MITIGATED，CWE Top 25 全部覆盖

**支撑证据**: `evidence/l4/security_audit_report.md`, `evidence/l4/external_security_scan.json`

---

### Q4: 相比 Claude Code/AutoCodeRover，优势是什么？

**A**: 
| 指标 | DevPilot Loop | Claude Code | AutoCodeRover |
|------|--------------|-------------|---------------|
| 多 Agent 协作 | ✅ 9 Agents | ❌ 单 Agent | ❌ 单 Agent |
| 自主性分级 | ✅ DAL 5 级 | ❌ 无 | ❌ 无 |
| 知识沉淀 | ✅ Runbook 自动生成 | ❌ 无 | ❌ 无 |
| 安全审计 | ✅ L4 独立验证 | ❌ 无 | ❌ 无 |

**优势总结**: 多 Agent 协作场景下，通过任务分解和知识沉淀，修复质量优于单 Agent 方案（详见 evidence/scenarios/）

---

### Q5: 测试覆盖率 95%，剩下 5% 为什么没覆盖？

**A**: 未覆盖部分主要是：
- Gateway 路由层的边界条件（需要集成测试环境）
- Lifecycle 的状态转换异常路径（需要 local 文件系统）
- Orchestrator 的超时降级逻辑（需要长时间运行测试）

这些部分的覆盖需要在复赛阶段补充 DAST 测试和集成测试。

---

### Q6: 开源协议是什么？能否商用？

**A**: Apache 2.0 协议，完全商业友好。允许：
- 修改代码
- 分发衍生作品
- 商用

所有依赖均可替代，无商业锁定。

---

### Q7: 从 DAL-2 到 DAL-3 需要什么？

**A**: 
- 真实仓库接入（当前使用执行数据）
- 灰度发布自动化（当前需要人工确认）
- 自动回滚机制（已实现框架，待接入真实 K8s）
- 预计时间: 复赛阶段（2026-08-25 ~ 09-03）

---

### Q8: 为什么选择 AgentTeams (HiClaw) 作为基座？

**A**: 
1. **成熟的 Manager-Worker 架构**: 已验证的生产级实现
2. **标准化 Skill 接口**: BaseSkill 抽象类确保可扩展性
3. **社区支持**: Apache 2.0，活跃开发
4. **兼容性**: 与现有工具链（Higress, Matrix, OTel）无缝集成

---

### Q9: 如何保证 Agent 不会做出有害操作？

**A**: 多层防护：
1. **权限隔离**: L1 只读 → L2 写(需确认) → L3 生产(需审批)
2. **人工审批节点**: Fixer push / Release deploy 必须人工确认
3. **审计留痕**: 所有操作记录到 Matrix + OTel Trace
4. **熔断机制**: 60s 无响应触发熔断，人工接管
5. **回滚能力**: 每个操作都有 rollback_point

---

### Q10: 你们的独特价值主张是什么？

**A**: 
> "DevPilot Loop 是面向研发的闭环（9 Agents × 8 Skills）集成的开源多 Agent 系统。"


| 维度 | 自查项 | 状态 |
|------|--------|------|
| **技术创新** | DAL 模型创新性 | ✅ |
| **技术深度** | 9 Agents, 8 Skills, 12 ADRs | ✅ |
| **代码质量** | 367 测试, 95% 覆盖, MI=89 | ✅ |
| **安全性** | L4 独立审计, 98/100 分 | ✅ |
| **可观测性** | OTel + Matrix 全链路 | ✅ |
| **文档完整性** | 18 docs, 50 evidence files | ✅ |
| **开源贡献** | Apache 2.0, 全依赖开源 | ✅ |
| **竞赛准备** | PPT 50 slides, Defense Q&A | ✅ |

