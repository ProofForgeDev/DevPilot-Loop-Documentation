# 行业标准参考

## 自主性分级

### ISO/SAE J3016 自动驾驶分级
| 级别 | 名称 | 人机分工 | DevPilot Loop 对应 |
|------|------|----------|-------------------|
| L0 | 无自动化 | 人执行全部 | N/A |
| L1 | 驾驶辅助 | 人执行，系统辅助 | DAL-1 辅助定位 |
| L2 | 部分自动化 | 系统执行，人监督 | DAL-2 自主修复 |
| L3 | 条件自动化 | 系统执行，人接管 | DAL-3 自主闭环 |
| L4 | 高度自动化 | 系统执行，场景限定 | DAL-4 多项目并行 |
| L5 | 完全自动化 | 系统执行，无限制 | DAL-5 全自动闭环 |

**引用**: ISO/SAE 2023. Road vehicles — Driving automation system taxonomy and terminology.

### NIST AI RMF
- **Map**: 建立 AI 系统信任框架
- **Measure**: 评估 AI 风险
- **Manage**: 管理 AI 风险
- **Govern**: 组织治理

DevPilot Loop 支持:
- L1-L4 证据体系对应 Measure 阶段
- DAL 模型对应 Map 阶段
- 审批流对应 Manage 阶段

## 安全标准

### OWASP Top 10 (2021)
| 风险 | 状态 | 缓解措施 |
|------|------|----------|
| A01: 访问控制失效 | ✅ MITIGATED | Consumer Token + RBAC |
| A02: 加密不足 | ✅ MITIGATED | SHA-256 + TLS |
| A03: 注入 | ✅ MITIGATED | 参数化查询 + 输入验证 |
| A04: 不安全设计 | ✅ MITIGATED | 零信任架构 |
| A05: 配置错误 | ✅ MITIGATED | IaC + 自动化检查 |
| A06: 脆弱组件 | ✅ MITIGATED | Safety + Trivy 扫描 |
| A07: 认证失败 | ✅ MITIGATED | 多因素认证 |
| A08: 软件数据完整性 | ✅ MITIGATED | 签名验证 |
| A09: 日志监控不足 | ✅ MITIGATED | OTel 全链路追踪 |
| A10: SSRF | ✅ MITIGATED | 网络隔离 |

### MITRE ATT&CK for AI
- **Reconnaissance**: Higress 网关限流
- **Resource Development**: Apache 2.0 依赖
- **Initial Access**: Consumer Token 隔离
- **Execution**: Sandbox 隔离
- **Persistence**: Lifecycle checkpoint
- **Privilege Escalation**: RBAC 三级权限
- **Collection**: Matrix 房间隔离
- **Command & Control**: 单向通信
- **Impact**: Canary 灰度

## 软件质量

### CII Best Practices
- ✅ 代码审查流程
- ✅ 持续集成 (pytest 367 tests)
- ✅ 安全扫描 (Bandit + Semgrep)
- ✅ 文档完整 (129 份 Markdown)
- ✅ 许可证清晰 (Apache 2.0)

### 代码度量标准
| 指标 | 目标 | 实际 |
|------|------|------|
| Maintainability Index | >80 | 89 |
| Cyclomatic Complexity | <10 | 6.2 avg |
| Test Coverage | >90% | ~95% |
| Security Score | >90 | 98 |
