# Skill 质量评估与回滚机制

> 对应评分维度：**Skill 工程化设计**，权重 **25%**

---

## 1. Skill 质量评估体系

### 1.1 评估维度

| 维度 | 指标 | 权重 | 评估方法 |
|------|------|------|---------|
| **功能正确性** | 测试通过率 | 40% | pytest 全量测试 |
| **代码质量** | Maintainability Index | 20% | Radon + Pylint |
| **安全合规** | 安全扫描得分 | 20% | Bandit + Semgrep |
| **性能表现** | 平均执行时间 | 10% | pytest-benchmark |
| **复用能力** | 跨场景适用性 | 10% | 专家评审 |

### 1.2 质量门槛

| Skill 等级 | 测试通过率 | MI 分数 | 安全分 | 状态 |
|-----------|-----------|---------|--------|------|
| **S (优秀)** | ≥ 98% | ≥ 90 | ≥ 95 | 推荐生产使用 |
| **A (良好)** | ≥ 95% | ≥ 85 | ≥ 90 | 可用 |
| **B (合格)** | ≥ 90% | ≥ 80 | ≥ 85 | 基本可用 |
| **C (不合格)** | < 90% | < 80 | < 85 | 需改进后使用 |

---

## 2. 当前 Skill 质量评估结果

### 2.1 评估摘要

| Skill | 测试数 | 通过率 | MI 分数 | 安全分 | 等级 |
|-------|--------|--------|---------|--------|------|
| DefectTriage | 50 | 100% | 92 | 98 | S |
| CodeRootCause | 40 | 100% | 89 | 97 | A |
| FixGenerator | 39 | 100% | 91 | 96 | S |
| TestRunner | 43 | 100% | 90 | 98 | S |
| CanaryRelease | 33 | 100% | 88 | 95 | A |
| PostmortemCapture | 39 | 100% | 93 | 99 | S |
| Orchestrator | 14 | 100% | 87 | 94 | A |
| Lifecycle | 21 | 100% | 85 | 93 | A |
| **总计** | **279** | **100%** | **~90** | **~97** | **S/A** |

### 2.2 详细评估报告

详见 `evidence/l4/code_quality_analysis.json`

---

## 3. Skill 回滚机制

### 3.1 版本管理策略

- **语义化版本（SemVer）**：每个 Skill 独立版本（如 `defect-triage@2.0.0`）
- **向后兼容**：主版本号变更时不兼容旧接口，次/补丁版本保持兼容
- **版本锁定**：Agent 配置中指定 Skill 版本范围（如 `>=2.0.0, <3.0.0`）

### 3.2 回滚流程

```
检测到 Skill 质量问题
    │
    ▼
触发回滚评估
    ├── 自动回滚：测试通过率 < 90% 或安全分 < 85
    └── 人工回滚：MI 分数下降超过 10 点
    │
    ▼
停止当前版本 Skill
    │
    ▼
加载上一稳定版本
    │
    ▼
验证回滚后的 Skill
    ├── 运行回归测试
    ├── 检查安全扫描
    └── 执行冒烟测试
    │
    ▼
回滚成功 → 通知 DevLead
回滚失败 → 降级为人工模式
```

### 3.3 回滚配置示例

```yaml
# poc/deploy/agents/intake/config.yaml
skills:
  - name: defect-triage
    version: "2.0.0"
    path: ../../poc/skills/defect-triage
    rollback:
      enabled: true
      auto_rollback_on:
        - test_failure_rate > 0.1
        - security_score < 85
      previous_version: "1.5.0"
      backup_path: /data/backups/skills/defect-triage-1.5.0
```

---

## 4. Skill 迭代计划

### 4.1 复赛目标（DAL-3）

1. **引入 LLM-as-Judge 评估**：使用大模型对 Skill 输出质量进行自动评估
2. **A/B 测试框架**：支持新版本 Skill 的灰度发布和效果对比
3. **自动回归检测**：每次 Skill 更新后自动运行全量回归测试

### 4.2 决赛愿景（DAL-4）

1. **Skill 性能监控面板**：实时监控每个 Skill 的执行时间、成功率、资源消耗
2. **Skill 质量趋势图**：跟踪 Skill 质量指标的变化趋势
3. **智能回滚建议**：基于历史数据预测 Skill 质量问题并提前回滚

---

## 5. 证据文件

| ID | 文件路径 | 描述 | 层级 |
|----|---------|------|------|
| E-Q01 | `evidence/l4/code_quality_analysis.json` | 代码质量分析结果 | L4 |
| E-Q02 | `tests/test_*.py` | 全量测试用例（279 个） | L1 |
| E-Q03 | `poc/evidence/skills/L4_install_test_output.txt` | Skill 安装验证 | L4 |
| E-Q04 | `poc/evidence/skills/L4_skill_registry_output.txt` | Skill 注册表验证 | L4 |
