# DevPilot Loop —— 软件研发全生命周期多 Agent 自主闭环系统

**场景与用户**：面向 3–20 人中小研发团队。缺陷修复依赖人工串联，平均 4 小时/个，上下文丢失严重，经验无法沉淀。

**方案**：基于 AgentTeams（原 HiClaw）构建"1 Manager + 8 Worker"协同闭环。Manager（DevLead）负责拆解与调度；Intake、Analyst、Fixer、Verifier、Release、Knowledge 六 Worker 分别承担归并、根因定位、修复执行、测试验证、灰度发布、知识沉淀。全流程由 8 个 Skill 驱动，协作发生在可审计的 Matrix 房间中。

**量化收益**：缺陷修复周期 4 小时→15 分钟；人工介入减少 80%；复发率下降 60%。

**可复制性**：Manager–Worker–Skill 模式可平移至运维自愈、智能客服、金融风控等场景。

项目 Apache 2.0 开源，目标是成为 AgentTeams 研发场景官方参考实现。
