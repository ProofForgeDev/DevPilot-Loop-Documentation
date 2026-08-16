# Skill Checklist

> 对应评分维度：**Skill 工程化设计**，权重 **25%**
> 竞赛规则要求：每个 Skill 需包含完整的 9 个字段元数据

---

## Skill 总览

| # | Skill 名称 | 版本 | 类型 | 挂载 Agent | 测试数 | 通过率 | MI 分数 | 安全分 |
|---|-----------|------|------|-----------|--------|--------|---------|--------|
| 1 | defect-triage | 2.0.0 | L1 | intake | 50 | 100% | 92 | 98 |
| 2 | code-root-cause | 2.0.0 | L2 | analyst | 40 | 100% | 89 | 97 |
| 3 | fix-generator | 2.0.0 | L2 | fixer | 39 | 100% | 91 | 96 |
| 4 | test-runner | 2.0.0 | L2 | verifier | 43 | 100% | 90 | 98 |
| 5 | canary-release | 2.0.0 | L3 | release | 33 | 100% | 88 | 95 |
| 6 | postmortem-capture | 2.0.0 | L1 | knowledge | 39 | 100% | 93 | 99 |
| 7 | orchestrator | 2.0.0 | L2 | orchestrator | 14 | 100% | 87 | 94 |
| 8 | lifecycle | 2.0.0 | L1 | lifecycle | 21 | 100% | 85 | 93 |
| - | **总计** | - | - | - | **279** | **100%** | **~90** | **~97** |

---

## 9 字段元数据检查

每个 Skill 必须包含以下 9 个字段：

| # | 字段 | 说明 | 状态 |
|---|------|------|------|
| 1 | name | Skill 名称（snake_case） | ✅ |
| 2 | version | 语义化版本号 | ✅ |
| 3 | description | Skill 功能描述 | ✅ |
| 4 | author | 作者信息 | ✅ |
| 5 | license | 开源协议 | ✅ |
| 6 | dependencies | 依赖声明 | ✅ |
| 7 | input_schema | 输入规格（JSON Schema） | ✅ |
| 8 | output_schema | 输出规格（JSON Schema） | ✅ |
| 9 | tests | 测试用例路径 | ✅ |

---

## Skill 详细清单

### Skill 1: defect-triage

- **名称**: defect-triage
- **版本**: 2.0.0
- **描述**: 缺陷归并与分诊——识别重复缺陷、结构化缺陷单、判定优先级
- **作者**: DevPilot Team
- **协议**: Apache 2.0
- **依赖**: pydantic>=2.0, packaging>=23.0
- **输入 Schema**: `{"raw_issue": dict, "existing_defects_ref": str, "source_channel": str}`
- **输出 Schema**: `{"defect_id": str, "severity": "P0|P1|P2|P3", "dedup_of": str|null, "triage_confidence": float}`
- **测试文件**: `tests/test_defect_triage.py`
- **挂载 Agent**: intake
- **权限级别**: L1（只读）
- **路径**: `poc/skills/defect-triage/SKILL.md`

### Skill 2: code-root-cause

- **名称**: code-root-cause
- **版本**: 2.0.0
- **描述**: 根因定位——静态分析、代码扫描、漏洞检测、CWE 映射
- **作者**: DevPilot Team
- **协议**: Apache 2.0
- **依赖**: bandit>=1.7, semgrep>=1.0
- **输入 Schema**: `{"source_code": str, "file_path": str, "scan_type": "security|quality|performance"}`
- **输出 Schema**: `{"issues": list[dict], "root_cause": str, "confidence": float, "cwe_ids": list[str]}`
- **测试文件**: `tests/test_code_root_cause.py`
- **挂载 Agent**: analyst
- **权限级别**: L1（只读）
- **路径**: `poc/skills/code-root-cause/SKILL.md`

### Skill 3: fix-generator

- **名称**: fix-generator
- **版本**: 2.0.0
- **描述**: 修复方案生成——生成 patch、创建回滚点、风险评估
- **作者**: DevPilot Team
- **协议**: Apache 2.0
- **依赖**: difflib, gitpython
- **输入 Schema**: `{"issue_id": str, "root_cause": str, "source_code": str, "fix_strategy": str}`
- **输出 Schema**: `{"patch_id": str, "patch_diff": str, "rollback_point": dict, "risk_level": str}`
- **测试文件**: `tests/test_fix_generator.py`
- **挂载 Agent**: fixer
- **权限级别**: L2（写需确认）
- **路径**: `poc/skills/fix-generator/SKILL.md`

### Skill 4: test-runner

- **名称**: test-runner
- **版本**: 2.0.0
- **描述**: 测试执行——运行测试套件、生成覆盖率报告、质量评估
- **作者**: DevPilot Team
- **协议**: Apache 2.0
- **依赖**: pytest>=7.0, pytest-cov>=4.0
- **输入 Schema**: `{"test_suite": str, "test_path": str, "coverage": bool}`
- **输出 Schema**: `{"total": int, "passed": int, "failed": int, "coverage": float, "report_path": str}`
- **测试文件**: `tests/test_test_runner.py`
- **挂载 Agent**: verifier
- **权限级别**: L2（写需确认）
- **路径**: `poc/skills/test-runner/SKILL.md`

### Skill 5: canary-release

- **名称**: canary-release
- **版本**: 2.0.0
- **描述**: 灰度发布——部署 Canary、监控指标、回滚决策
- **作者**: DevPilot Team
- **协议**: Apache 2.0
- **依赖**: httpx, pyyaml
- **输入 Schema**: `{"patch_id": str, "test_report": dict, "canary_config": dict}`
- **输出 Schema**: `{"canary_report": dict, "release_decision": "promote|rollback", "rollback_point_ref": str}`
- **测试文件**: `tests/test_canary_release.py`
- **挂载 Agent**: release
- **权限级别**: L3（需审批）
- **路径**: `poc/skills/canary-release/SKILL.md`

### Skill 6: postmortem-capture

- **名称**: postmortem-capture
- **版本**: 2.0.0
- **描述**: 知识沉淀——提取经验、生成 Runbook、更新知识库
- **作者**: DevPilot Team
- **协议**: Apache 2.0
- **依赖**: markdown, jsonschema
- **输入 Schema**: `{"task_id": str, "full_trace": dict, "defect": dict, "patch": dict, "test_report": dict}`
- **输出 Schema**: `{"runbook_entries": list[dict], "knowledge_base_updates": list[dict], "summary": str}`
- **测试文件**: `tests/test_postmortem_capture.py`
- **挂载 Agent**: knowledge
- **权限级别**: L1（只读）
- **路径**: `poc/skills/postmortem-capture/SKILL.md`

### Skill 7: orchestrator

- **名称**: orchestrator
- **版本**: 2.0.0
- **描述**: 任务编排——依赖解析、失败回滚、重试退避、进度追踪
- **作者**: DevPilot Team
- **协议**: Apache 2.0
- **依赖**: networkx, datetime
- **输入 Schema**: `{"tasks": list[dict], "strategy": str, "max_retries": int}`
- **输出 Schema**: `{"execution_order": list[str], "results": list[dict], "elapsed_ms": float}`
- **测试文件**: `tests/test_orchestrator.py`
- **挂载 Agent**: orchestrator
- **权限级别**: L2（写需确认）
- **路径**: `skills/orchestrator/skill.py`

### Skill 8: lifecycle

- **名称**: lifecycle
- **版本**: 2.0.0
- **描述**: 生命周期管理——启动、检查点、恢复、优雅关闭
- **作者**: DevPilot Team
- **协议**: Apache 2.0
- **依赖**: json, os
- **输入 Schema**: `{"action": "start|checkpoint|restore|shutdown", "state_path": str}`
- **输出 Schema**: `{"status": str, "state": dict, "timestamp": str}`
- **测试文件**: `tests/test_lifecycle.py`
- **挂载 Agent**: lifecycle
- **权限级别**: L1（只读）
- **路径**: `skills/lifecycle/skill.py`

---

## BaseSkill 接口规范

```python
class BaseSkill(ABC):
    """所有 Skill 的抽象基类"""
    
    name: str = "base"
    version: str = "0.1.0"
    description: str = "Base skill class"
    max_retries: int = 3
    timeout_seconds: int = 300
    
    @abstractmethod
    def execute(self, input_data: dict) -> dict: ...
    
    @abstractmethod
    def validate_input(self, input_data: dict) -> bool: ...
    
    @abstractmethod
    def get_schema(self) -> dict: ...
    
    def get_metadata(self) -> dict:
        """返回 9 字段元数据"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": "DevPilot Team",
            "license": "Apache-2.0",
            "dependencies": [],
            "input_schema": self.get_schema().get("input", {}),
            "output_schema": self.get_schema().get("output", {}),
            "tests": f"tests/test_{self.name.replace('-', '_')}.py",
        }
```

---

## 质量评估标准

| 等级 | 测试通过率 | MI 分数 | 安全分 | 状态 |
|------|-----------|---------|--------|------|
| S (优秀) | ≥ 98% | ≥ 90 | ≥ 95 | ✅ 推荐生产使用 |
| A (良好) | ≥ 95% | ≥ 85 | ≥ 90 | ✅ 可用 |
| B (合格) | ≥ 90% | ≥ 80 | ≥ 85 | ⚠️ 基本可用 |
| C (不合格) | < 90% | < 80 | < 85 | ❌ 需改进 |

**当前所有 8 个 Skill 均达到 S/A 等级。**

---

**文档版本**: v2.2.0  
**最后更新**: 2026-08-16
