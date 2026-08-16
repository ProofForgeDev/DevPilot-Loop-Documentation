# 第 7 章 开源开放计划

> 对应评分维度：**开源贡献与生态复用**，权重 **5%**

---

## 7.1 开源协议

**Apache 2.0**。选型理由：
- 商业友好，允许企业自由使用与修改
- 包含专利授权条款，保护贡献者
- 与 AgentTeams / HiClaw 生态协议一致

## 7.2 开源范围

| 内容 | 是否开源 | 说明 |
|------|---------|------|
| Agent 定义文件（7 个） | ✅ | poc/hiclaw/ |
| Skill 包（6 个） | ✅ | poc/skills/ |
| MCP 适配器 | ✅ | 随 Skill 包 |
| 场景脚本 | ✅ | poc/scenarios/ |
| 全部文档 | ✅ | docs/ |
| PPT 生成脚本 | ✅ | slides/ |

## 7.3 第三方依赖披露

| 名称 | 用途 | 协议 | 是否商业 API |
|------|------|------|-------------|
| AgentTeams / HiClaw | 多 Agent 协作基座 | Apache 2.0 | 否 |
| Higress | AI 网关 / 凭证管理 | Apache 2.0 | 否 |
| Matrix / Synapse | Agent 通信 | Apache 2.0 | 否 |
| LLM API | 推理 | — | **是**（见 7.4） |
| Git 服务 | 代码管理 | — | 否 |
| CI/CD 平台 | 测试执行 | — | 否 |

## 7.4 LLM API 披露

- **调用链**：Worker → Higress AI 网关 → LLM Provider
- **成本估算**：单次缺陷修复约 5,000–15,000 tokens，按 $0.01/1K tokens 计约 $0.05–$0.15
- **可替代性**：可切换任意 OpenAI 兼容 API（通义千问、DeepSeek、本地模型等）

## 7.5 社区运营计划

- 版本迭代：每两周发布 Skill 模板库更新
- 贡献指南：见 CONTRIBUTING.md
- 目标：成为 AgentTeams 研发场景的**官方参考实现**

## 7.6 定位野心

> 本项目不只是一个参赛作品，而是以成为 **AgentTeams 研发场景官方参考实现**为目标设计。
> 仓库结构、Skill 格式、文档规范均按官方模板库候选标准编写。
