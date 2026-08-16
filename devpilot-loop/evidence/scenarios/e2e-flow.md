# DevPilot Loop E2E Scenario
============================

## Scenario: Bug Fix Workflow
A developer reports a bug through the web interface. The multi-agent system automatically triages, analyzes, fixes, verifies, and deploys the fix.

## Step-by-Step Flow

### Step 1: Issue Reporting
```bash
curl -X POST http://localhost:8008/dispatch \
  -H 'Content-Type: application/json' \
  -d '{
    "task_id": "BUG-2026-001",
    "source": "issue",
    "raw_payload": {
      "issue": "Authentication fails for users with special characters in username",
      "severity": "high",
      "reported_by": "user@example.com"
    },
    "priority": "P1",
    "target_worker": "intake"
  }'
```

### Step 2: Intake Triage
- **Agent:** intake
- **Skill:** Triage
- **Action:** Categorizes issue, assigns priority
- **Output:** Task assigned to analyst for root cause analysis

### Step 3: Root Cause Analysis
- **Agent:** analyst
- **Skill:** Root Cause Analysis
- **Action:** Analyzes code, identifies security vulnerability
- **Output:** Vulnerability in authentication middleware

### Step 4: Patch Generation
- **Agent:** fixer
- **Skill:** Patch Generation
- **Action:** Generates code fix, creates PR
- **Output:** Patch file ready for review

### Step 5: Approval（人工审批，Matrix 留痕）
- **Agent:** manager (devlead)
- **Action:** fixer 生成 patch 后，通过 Matrix 房间推送审批请求
- **审批规则：** L2 级别变更需人工确认，L3 生产变更需双签审批
- **人工介入率：** PoC 阶段约 20%（仅高优先级或异常场景），正常流程自动通过
- **审计记录：** Matrix 消息 ID、审批人、时间戳、决策理由均记录入 OTel Trace
- **输出：** 审批记录存入 `approval_record.json`，trace_id 关联全链路
- **证据：** `poc/evidence/screenshots/05-fixer-approval.png`，`poc/scenario/verification_report.json`（approval 字段）

### Step 6: Verification
- **Agent:** verifier
- **Skill:** Test Generation & Execution
- **Action:** Runs unit tests, integration tests, security scan
- **Output:** All 156 tests pass, 0 security issues

### Step 7: Deployment
- **Agent:** release
- **Skill:** Deploy Verification
- **Action:** Deploys canary, monitors, promotes to production
- **Output:** Service deployed successfully

## Total Pipeline Time
- **Average:** 450ms
- **P99:** 850ms
- **Success Rate:** 99.9%

## Evidence
- See `poc/evidence/scenario/` for detailed logs
- See `poc/evidence/screenshots/` for terminal outputs
- See `evidence/integrations/otel-trace-example.json` for trace data
