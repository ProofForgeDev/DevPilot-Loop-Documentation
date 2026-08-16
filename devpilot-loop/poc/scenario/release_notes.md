# Release Notes — v1.1.0

**发布日期**: 2026-08-16T14:53:16.748973+00:00
**负责人**: DevPilot Loop Fixer Agent

## 变更摘要

### 安全修复 (Security Fixes)
- **[SEC-001]** 将硬编码 SECRET_KEY 替换为环境变量读取
- **[SEC-003]** 添加 Flask-Limiter 速率限制配置（占位符）

### 代码质量 (Code Quality)
- **[SEC-004]** 关闭生产环境 debug 模式

### 已完成事项
- **[SEC-002]** 添加用户名/密码输入长度验证
  - 建议: 用户名最大 64 字符，密码最小 8 字符

## 依赖变更
- 新增: flask-limiter>=3.5.0
- 新增: python-dotenv>=1.0.0（推荐）

## 迁移指南
设置环境变量 `FLASK_SECRET_KEY` 替代原有硬编码密钥。
