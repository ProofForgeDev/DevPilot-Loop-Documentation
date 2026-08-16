#!/usr/bin/env python3
"""Verify every evidence file claimed in EVIDENCE-INDEX.md exists on disk."""
import os

# All files claimed in EVIDENCE-INDEX.md
files = [
    # L1a - Screenshots
    'devpilot-loop/evidence/screenshots/01-devlead-intake.png',
    'devpilot-loop/evidence/screenshots/02-intake-triage.png',
    'devpilot-loop/evidence/screenshots/03-analyst-rootcause.png',
    'devpilot-loop/evidence/screenshots/04-fixer-patch.png',
    'devpilot-loop/evidence/screenshots/05-fixer-approval.png',
    'devpilot-loop/evidence/screenshots/06-verifier-test.png',
    'devpilot-loop/evidence/screenshots/07-release-canary.png',
    'devpilot-loop/evidence/screenshots/08-knowledge-runbook.png',
    'devpilot-loop/evidence/screenshots/09-manager-health.png',
    'devpilot-loop/evidence/screenshots/10-task-dispatch.png',
    'devpilot-loop/evidence/screenshots/11-skill-execution.png',
    'devpilot-loop/evidence/screenshots/12-security-scan.png',
    'devpilot-loop/evidence/screenshots/13-evidence-matrix.png',
    'devpilot-loop/evidence/screenshots/14-ppt-generation.png',
    'devpilot-loop/evidence/screenshots/15-test-results.png',
    'devpilot-loop/evidence/screenshots/16-docker-status.png',
    # L1b - Logs
    'devpilot-loop/evidence/logs/service_startup.log',
    'devpilot-loop/evidence/logs/task_dispatch.log',
    'devpilot-loop/evidence/logs/error_recovery.log',
    'devpilot-loop/evidence/logs/security_events.log',
    'devpilot-loop/evidence/logs/observability_trace.log',
    'devpilot-loop/poc/evidence/logs/run-001.log',
    # L1c - Deploy
    'devpilot-loop/poc/deploy/evidence/L1_docker_compose_ps.txt',
    'devpilot-loop/poc/deploy/evidence/L1_docker_compose_logs.txt',
    'devpilot-loop/poc/deploy/agents/devlead/config.yaml',
    'devpilot-loop/poc/deploy/agents/orchestrator/config.yaml',
    # L2
    'devpilot-loop/evidence/api/api_spec.json',
    'devpilot-loop/evidence/api/api-reference.md',
    'devpilot-loop/evidence/config/config_evidence.json',
    'devpilot-loop/evidence/config/configuration-reference.md',
    'devpilot-loop/evidence/integrations/integration_evidence.json',
    'devpilot-loop/evidence/integrations/otel-trace-example.json',
    'devpilot-loop/evidence/scenarios/e2e-flow.md',
    'devpilot-loop/evidence/scenarios/scenario_evidence.json',
    'devpilot-loop/docs/03-agents.md',
    'devpilot-loop/docs/04-skills.md',
    'devpilot-loop/docs/adrs.md',
    'devpilot-loop/poc/deploy/evidence/L2_agent_comm_test.txt',
    'devpilot-loop/poc/deploy/evidence/L2_agent_configs.txt',
    # L3
    'devpilot-loop/evidence/performance/performance-baseline.md',
    'devpilot-loop/poc/evidence/scenario/L3_quantification.md',
    'devpilot-loop/poc/evidence/scenario/L3_timing_breakdown.txt',
    'devpilot-loop/poc/evidence/scenario/timing_breakdown.json',
    'devpilot-loop/poc/evidence/scenario/deliverables.json',
    'devpilot-loop/evidence/skills/skill_failure_security_report.md',
    # L4
    'devpilot-loop/evidence/l4/security_audit_report.md',
    'devpilot-loop/evidence/l4/benchmark_comparison.json',
    'devpilot-loop/evidence/l4/external_security_scan.json',
    'devpilot-loop/evidence/l4/code_quality_analysis.json',
    'devpilot-loop/poc/evidence/skills/L4_skill_registry_output.txt',
    # open-agent-audit
    'open-agent-audit/evidence/l3/call_graph.md',
    'open-agent-audit/evidence/l3/dal2_verification.md',
    'open-agent-audit/evidence/l3/threat_model.md',
]

found = []
missing = []
for f in files:
    if os.path.exists(f):
        found.append(f)
    else:
        missing.append(f)

print(f"Claimed: {len(files)}")
print(f"Found: {len(found)}")
print(f"Missing: {len(missing)}")
if missing:
    print("\nMissing files:")
    for m in missing:
        print(f"  ✗ {m}")

# Also check: are there OTHER evidence-like files not in the index?
extra = []
for root, dirs, fs in os.walk('devpilot-loop/evidence'):
    for f in fs:
        path = os.path.join(root, f)
        if path not in files and not path.endswith('.json') and not path.endswith('.md'):
            # skip meta-docs
            if f not in ['evidence_index.json', 'evidence_matrix_v2.md']:
                extra.append(path)
        elif path not in files and f not in ['evidence_index.json', 'evidence_matrix_v2.md']:
            extra.append(path)
if extra:
    print(f"\nExtra files not in index ({len(extra)}):")
    for e in sorted(extra):
        print(f"  + {e}")
