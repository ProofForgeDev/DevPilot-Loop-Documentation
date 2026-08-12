# 贡献指南

感谢你对 DevPilot Loop 的关注！本项目目标是成为 AgentTeams 研发场景的官方参考实现，
我们欢迎任何形式的贡献。

## 贡献方式

### 1. 提交 Skill
最受欢迎的贡献方式。每个 Skill 是一个独立目录，包含：
- `manifest.json`：元数据（名称、版本、描述、依赖、入口）
- `SKILL.md`：按 AgentTeams 官方 Skill 模板编写
- `README.md`：安装与使用说明

版本号遵循 [semver](https://semver.org/)，新 Skill 从 `v0.1.0` 起步。

### 2. 改进 Agent 定义
修改 `poc/hiclaw/workers/` 下的 Agent 定义文件。请确保：
- 10 个 Identity 字段完整（见 docs/03-agents.md）
- 职责边界包含"做什么"和"不做什么"
- 失败处理包含重试、降级、熔断三级

### 3. 补充场景
在 `poc/scenarios/` 下添加新的端到端场景脚本。

### 4. 文档改进
修正错别字、补充说明、翻译等。

## 开发流程

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-skill-name`
3. 提交变更：`git commit -m "feat: add your-skill-name skill"`
4. 推送并创建 Pull Request

## Commit 规范

使用 [Conventional Commits](https://www.conventionalcommits.org/)：
- `feat:` 新功能
- `fix:` 修复
- `docs:` 文档
- `refactor:` 重构
- `test:` 测试
- `chore:` 杂项

## 行为准则

- 尊重所有贡献者
- 不允许虚假陈述（模拟必须标注）
- 不允许购买 Star 或任何形式的刷量行为

## 许可

提交贡献即表示你同意以 Apache 2.0 协议授权你的贡献。
