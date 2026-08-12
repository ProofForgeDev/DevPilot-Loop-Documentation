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

### Step 5: Approval
- **Agent:** manager
- **Action:** Requests approval for high-severity fix
- **Output:** Approval granted (auto-approved for P1 bugs)

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
