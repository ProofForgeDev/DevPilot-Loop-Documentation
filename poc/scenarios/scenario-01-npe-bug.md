# 场景 01：空指针缺陷端到端修复

## 前置条件
- HiClaw 已部署（L1 实机）
- 7 个 Agent 已配置
- 6 个 Skill 已安装
- 最小 demo 仓库已创建（含 1 个 NPE 函数 + 1 个失败测试）

## Demo 仓库结构
```
demo-repo/
├── src/
│   └── UserService.java    # 含 NPE 的函数
├── test/
│   └── UserServiceTest.java  # 失败的测试
└── pom.xml
```

## NPE 函数示例
```java
public String getUserName(int userId) {
    User user = userRepository.findById(userId);  // 可能返回 null
    return user.getName();  // NPE！
}
```

## 执行步骤

### Step 1：人类提交报障
在 Matrix 房间输入：
"线上报障：/api/user/{id} 接口返回 500，错误日志显示 NullPointerException at UserService.getUserName:42。请团队处理。"

### Step 2：DevLead 拆解
DevLead 输出 plan，派发 Intake。

### Step 3：Intake 归并
Intake 调用 DefectTriage，输出：
```
defect_id: DEF-2026-001
severity: P1
dedup_of: null
triage_confidence: 0.95
```

### Step 4：Analyst 定位
Analyst 调用 CodeRootCause，输出：
```
root_cause: UserService.java:42, user 可能为 null
confidence: 0.93
evidence_chain: [stack_trace, git_blame, recent_commit]
```

### Step 5：Fixer 修复
Fixer 调用 FixGenerator，输出：
```
patch: 添加 null check
rollback_point: git tag rollback-DEF-2026-001
risk_level: low
```
此步展示 Manager 确认 + 人工审批对话。

### Step 6：Verifier 测试
Verifier 调用 TestRunner，输出：
```
total: 5, passed: 5, failed: 0
verdict: approve
```

### Step 7：Release 灰度
Release 调用 CanaryRelease，输出：
```
canary: 10% traffic, 5min
error_rate_delta: 0.0
release_decision: promote
```
此步展示人工审批对话。

### Step 8：Knowledge 沉淀
Knowledge 调用 PostmortemCapture，输出：
```
runbook: "NPE 防御编程检查清单"
lessons_learned: ["所有 findById 调用必须做 null check"]
```

## 证据收集清单

| 编号 | 文件 | 说明 |
|------|------|------|
| 1 | 截图 01-devlead-intake.png | DevLead 派发 |
| 2 | 截图 02-intake-triage.png | Intake 归并结果 |
| 3 | 截图 03-analyst-rootcause.png | Analyst 根因 |
| 4 | 截图 04-fixer-patch.png | Fixer patch |
| 5 | 截图 05-fixer-approval.png | 人工审批对话 |
| 6 | 截图 06-verifier-test.png | 测试报告 |
| 7 | 截图 07-release-canary.png | 灰度结果 |
| 8 | 截图 08-knowledge-runbook.png | Runbook |
| 9 | logs/run-001.log | 运行日志 |
| 10 | trace-example.json | OTel Trace |
| 11 | video/manager-dispatch-60s.mp4 | 60 秒录屏 |

## 真实性声明

| 内容 | 真实性级别 | 说明 |
|------|-----------|------|
| HiClaw 部署、Manager 调度、Matrix 通信 | L1 实机 | 100% 真实 |
| LLM 推理部分 | L2 半实机 | 链路真实，推理桩化 |
| DAL-3/4/5 演进 | L3 推演 | 明确标注为规划 |
