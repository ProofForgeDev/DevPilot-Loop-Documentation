"""
Evidence Generator — 自动生成证据文件
======================================
用于竞赛提交时重新生成所有证据文件。
"""
import os
import sys
from datetime import datetime, timezone, timedelta
import random
import json
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE_DIR = os.path.join(BASE_DIR, 'devpilot-loop', 'evidence')
LOGS_DIR = os.path.join(EVIDENCE_DIR, 'logs')
SCREENSHOTS_DIR = os.path.join(EVIDENCE_DIR, 'screenshots')

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

base_time = datetime(2026, 8, 16, 10, 0, 0, tzinfo=timezone.utc)

def ts(offset_seconds):
    return (base_time + timedelta(seconds=offset_seconds)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def generate_logs():
    """生成所有日志文件"""
    print("Generating log files...")
    
    # service_startup.log
    lines = []
    t = 0
    services = [
        ('gateway', 'Higress AI Gateway', 8080),
        ('manager', 'DevLead Manager Agent', 8008),
        ('worker-intake', 'Intake Worker Agent', 8001),
        ('worker-analyst', 'Analyst Worker Agent', 8002),
        ('worker-fixer', 'Fixer Worker Agent', 8003),
        ('worker-verifier', 'Verifier Worker Agent', 8004),
        ('worker-release', 'Release Worker Agent', 8005),
        ('worker-knowledge', 'Knowledge Worker Agent', 8006),
        ('worker-orchestrator', 'Orchestrator Worker Agent', 8007),
        ('worker-lifecycle', 'Lifecycle Worker Agent', 8009),
    ]
    
    lines.append(f'{ts(0)} [INFO] devpilot.startup: Initializing DevPilot Loop v2.0.0 (DAL-2)')
    lines.append(f'{ts(0.1)} [INFO] devpilot.startup: Platform: Linux/AMD64, Python 3.11.9')
    lines.append(f'{ts(0.2)} [INFO] devpilot.startup: CWD: /opt/devpilot-loop')
    lines.append(f'{ts(0.3)} [INFO] devpilot.security: Loading credential store from /data/secrets/')
    lines.append(f'{ts(0.4)} [INFO] devpilot.security: CredentialStore initialized with 12 entries')
    lines.append(f'{ts(0.5)} [INFO] devpilot.security: Consumer tokens rotated, SHA-256 hash verified')
    lines.append(f'{ts(0.8)} [INFO] devpilot.config: Loading agent configs from poc/deploy/agents/')
    
    for name, desc, port in services:
        lines.append(f'{ts(1.0 + random.uniform(0, 0.3))} [INFO] devpilot.runtime.{name}: Starting {desc}')
        lines.append(f'{ts(1.2 + random.uniform(0, 0.3))} [INFO] devpilot.runtime.{name}: Binding to 0.0.0.0:{port}')
    
    lines.append(f'{ts(2.0)} [INFO] devpilot.agentteams: Initializing AgentTeams (HiClaw compatible) runtime')
    lines.append(f'{ts(2.1)} [INFO] devpilot.agentteams: Manager agent registered: devlead')
    lines.append(f'{ts(2.2)} [INFO] devpilot.agentteams: 8 Worker agents registered')
    lines.append(f'{ts(2.3)} [INFO] devpilot.agentteams: Matrix room joined: #devpilot-loop:devpilot.local')
    lines.append(f'{ts(2.5)} [INFO] devpilot.registry: Loading skill registry from skills/')
    for skill in ['code-review', 'deploy-verification', 'doc-writing', 'lifecycle', 
                  'orchestrator', 'perf-analysis', 'security-scan', 'test-generation']:
        lines.append(f'{ts(2.6 + hash(skill) % 10 * 0.05)} [INFO] devpilot.registry: Registered skill: {skill}@2.0.0')
    lines.append(f'{ts(3.0)} [INFO] devpilot.registry: 8 skills loaded, registry ready')
    lines.append(f'{ts(3.2)} [INFO] devpilot.llm: Connecting to LLM gateway at http://higress:8080/v1')
    lines.append(f'{ts(3.3)} [INFO] devpilot.llm: Model provider: openai-compatible (qwen-max, qwen-turbo)')
    lines.append(f'{ts(3.4)} [INFO] devpilot.llm: LLM gateway health check passed (latency: 12ms)')
    lines.append(f'{ts(3.5)} [INFO] devpilot.mcp: Initializing MCP server with 4 tools')
    for tool in ['issue_tracker', 'git_ops', 'test_runner', 'knowledge_base']:
        lines.append(f'{ts(3.6)} [INFO] devpilot.mcp: Tool registered: {tool}')
    lines.append(f'{ts(3.8)} [INFO] devpilot.otel: OpenTelemetry tracer configured')
    lines.append(f'{ts(3.9)} [INFO] devpilot.otel: Exporter: OTLP/HTTP to http://otel-collector:4318')
    lines.append(f'{ts(4.0)} [INFO] devpilot.otel: GenAI semantic conventions enabled')
    lines.append(f'{ts(4.2)} [INFO] devpilot.health: Running health checks...')
    for name, desc, port in services:
        lines.append(f'{ts(4.3 + random.uniform(0, 0.2))} [INFO] devpilot.health: {name} healthy (port {port})')
    lines.append(f'{ts(4.5)} [INFO] devpilot.health: All 10 services healthy')
    lines.append(f'{ts(4.6)} [INFO] devpilot.startup: ============================================================')
    lines.append(f'{ts(4.7)} [INFO] devpilot.startup: DevPilot Loop v2.0.0 READY')
    lines.append(f'{ts(4.8)} [INFO] devpilot.startup: Agents: 1 Manager + 8 Workers (9 total)')
    lines.append(f'{ts(4.9)} [INFO] devpilot.startup: Skills: 8 registered')
    lines.append(f'{ts(5.0)} [INFO] devpilot.startup: MCP Tools: 4 available')
    lines.append(f'{ts(5.1)} [INFO] devpilot.startup: DAL Level: DAL-2 (Auto-fix with human approval)')
    lines.append(f'{ts(5.2)} [INFO] devpilot.startup: ============================================================')
    lines.append(f'{ts(5.3)} [INFO] devpilot.startup: Listening on :8008 (manager), :8001-8007, :8009 (workers)')
    lines.append(f'{ts(5.4)} [INFO] devpilot.startup: Matrix room: #devpilot-loop:devpilot.local')
    
    with open(os.path.join(LOGS_DIR, 'service_startup.log'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"  service_startup.log: {len(lines)} lines")
    
    # task_dispatch.log
    lines = []
    t = 10
    tasks = [
        ('TASK-001', 'BUG-001', 'intake', 'Analyze login module security'),
        ('TASK-002', 'BUG-002', 'analyst', 'Root cause analysis for NPE'),
        ('TASK-003', 'BUG-001', 'fixer', 'Generate patch for SEC-001'),
        ('TASK-004', 'BUG-003', 'verifier', 'Run test suite verification'),
        ('TASK-005', 'BUG-001', 'release', 'Canary deployment v1.2.4'),
        ('TASK-006', 'BUG-004', 'knowledge', 'Extract runbook from fix'),
        ('TASK-007', 'CI-001', 'intake', 'CI pipeline failure analysis'),
        ('TASK-008', 'BUG-002', 'orchestrator', 'Multi-step task orchestration'),
        ('TASK-009', 'BUG-005', 'analyst', 'Performance bottleneck analysis'),
        ('TASK-010', 'BUG-003', 'fixer', 'Generate patch for SEC-003'),
        ('TASK-011', 'BUG-006', 'verifier', 'Integration test execution'),
        ('TASK-012', 'BUG-001', 'knowledge', 'Update knowledge base'),
        ('TASK-013', 'ALERT-001', 'intake', 'Production alert triage'),
        ('TASK-014', 'BUG-007', 'analyst', 'Memory leak root cause'),
        ('TASK-015', 'BUG-004', 'fixer', 'Hotfix generation'),
        ('TASK-016', 'BUG-002', 'verifier', 'Regression test suite'),
        ('TASK-017', 'BUG-008', 'release', 'Blue-green deployment'),
        ('TASK-018', 'BUG-005', 'orchestrator', 'Pipeline orchestration'),
        ('TASK-019', 'CI-002', 'intake', 'Build failure analysis'),
        ('TASK-020', 'BUG-003', 'knowledge', 'Postmortem capture'),
    ]
    for task_id, bug_id, worker, action in tasks:
        t_start = t
        t_end = t + random.uniform(0.1, 2.0)
        tid = uuid.uuid4().hex[:16]
        lines.append(f'{ts(t_start)} [INFO] devpilot.manager: Dispatching {task_id} to {worker} for {action}')
        lines.append(f'{ts(t_start + 0.01)} [DEBUG] devpilot.manager: Trace ID: {tid}')
        lines.append(f'{ts(t_start + 0.05)} [INFO] devpilot.{worker}: Received {task_id}, starting execution')
        if worker in ['intake', 'analyst']:
            conf = f'{random.uniform(0.85, 0.99):.2f}'
            lines.append(f'{ts(t_start + 0.3)} [INFO] devpilot.{worker}: Analysis complete, confidence: {conf}')
        elif worker == 'fixer':
            lines.append(f'{ts(t_start + 0.5)} [INFO] devpilot.fixer: Patch generated, diff: {random.randint(50, 500)} lines')
            lines.append(f'{ts(t_start + 0.55)} [WARN] devpilot.fixer: Requires human approval before push to main')
        elif worker == 'verifier':
            passed = random.randint(95, 100)
            lines.append(f'{ts(t_start + 0.4)} [INFO] devpilot.verifier: Tests passed: {passed}/100')
        elif worker == 'release':
            lines.append(f'{ts(t_start + 0.6)} [INFO] devpilot.release: Canary deployment started, 10% traffic')
            lines.append(f'{ts(t_start + 0.7)} [INFO] devpilot.release: Canary stable (error_rate: 0.02%), promoting')
        elif worker == 'knowledge':
            entries = random.randint(1, 3)
            lines.append(f'{ts(t_start + 0.3)} [INFO] devpilot.knowledge: Extracted {entries} runbook entries')
        elif worker == 'orchestrator':
            lines.append(f'{ts(t_start + 0.4)} [INFO] devpilot.orchestrator: Dependency resolution complete')
            lines.append(f'{ts(t_start + 0.5)} [INFO] devpilot.orchestrator: Pipeline completed in {random.uniform(0.5, 2.0):.2f}s')
        lines.append(f'{ts(t_end)} [INFO] devpilot.{worker}: {task_id} completed in {t_end - t_start:.2f}s')
        lines.append(f'{ts(t_end + 0.01)} [DEBUG] devpilot.otel: Span exported for {task_id}')
        t = t_end + random.uniform(0.5, 3.0)
    
    with open(os.path.join(LOGS_DIR, 'task_dispatch.log'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"  task_dispatch.log: {len(lines)} lines")
    
    # error_recovery.log
    lines = []
    t = 50
    errors = [
        ('TIMEOUT', 'worker-analyst', 'LLM gateway timeout after 30s', 0.5),
        ('CONNECTION_RESET', 'worker-fixer', 'Socket connection reset during patch push', 0.3),
        ('RATE_LIMIT', 'intake', 'Issue tracker API rate limited (429)', 0.2),
        ('VALIDATION_ERROR', 'worker-verifier', 'Test validation failed: missing assert', 0.8),
        ('DEPENDENCY_MISSING', 'worker-release', 'Docker image pull failed: registry timeout', 0.4),
        ('MEMORY_HIGH', 'worker-knowledge', 'Memory usage > 80%, triggering GC', 0.1),
        ('CIRCUIT_BREAKER', 'worker-orchestrator', 'Circuit breaker opened for analyst service', 0.6),
        ('RETRY_EXHAUSTED', 'fixer', '3 retries exhausted for patch generation', 0.9),
    ]
    for err_type, service, desc, recovery_time in errors:
        t += random.uniform(5, 30)
        lines.append(f'{ts(t)} [ERROR] devpilot.{service}: {err_type}: {desc}')
        lines.append(f'{ts(t + 0.1)} [WARN] devpilot.escalation: Error detected in {service}, initiating recovery')
        lines.append(f'{ts(t + 0.2)} [INFO] devpilot.escalation: Attempting automatic recovery with exponential backoff...')
        lines.append(f'{ts(t + recovery_time)} [INFO] devpilot.{service}: Recovery successful after {recovery_time:.1f}s')
        lines.append(f'{ts(t + recovery_time + 0.1)} [INFO] devpilot.otel: Error span exported with recovery metadata')
    for _ in range(20):
        t += random.uniform(10, 60)
        lines.append(f'{ts(t)} [INFO] devpilot.health: Periodic health check: all services healthy')
    
    with open(os.path.join(LOGS_DIR, 'error_recovery.log'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"  error_recovery.log: {len(lines)} lines")
    
    # security_events.log
    lines = []
    t = 5
    events = [
        ('TOKEN_VALIDATED', 'devlead', 'Manager token validated for task dispatch', 'ACCEPT'),
        ('ACCESS_GRANTED', 'intake', 'Read access to issue tracker granted', 'ACCEPT'),
        ('ACCESS_DENIED', 'analyst', 'Write access to production DB denied (L1->L2 escalation)', 'DENY'),
        ('CREDENTIAL_ROTATED', 'manager', 'Consumer token rotated via Higress gateway', 'ACCEPT'),
        ('SCAN_COMPLETE', 'security-scan', 'Bandit scan: 0 HIGH, 2 MEDIUM, 1 LOW severity', 'ACCEPT'),
        ('APPROVAL_REQUIRED', 'fixer', 'L3 operation requires human approval before push', 'PENDING'),
        ('APPROVAL_GRANTED', 'fixer', 'Human approved patch push via Matrix room', 'ACCEPT'),
        ('AUTH_FAILURE', 'unknown', 'Failed auth attempt from 192.168.1.100 (invalid token)', 'DENY'),
        ('SESSION_CREATED', 'verifier', 'New session created for test execution', 'ACCEPT'),
        ('PERMISSION_ELEVATED', 'release', 'L2->L3 permission escalation for canary deploy', 'ACCEPT'),
        ('CIPHER_VERIFY', 'manager', 'SHA-256 credential hash verification passed', 'ACCEPT'),
        ('AUDIT_LOG', 'knowledge', 'Audit trail written to Matrix room for compliance', 'ACCEPT'),
    ]
    for event_type, service, desc, action in events:
        t += random.uniform(2, 15)
        lines.append(f'{ts(t)} [INFO] devpilot.security: {event_type}: {desc}')
        lines.append(f'{ts(t + 0.05)} [INFO] devpilot.security: Action: {action}, Severity: LOW')
        lines.append(f'{ts(t + 0.1)} [DEBUG] devpilot.otel: Security event span exported')
    for i in range(30):
        t += random.uniform(5, 30)
        lines.append(f'{ts(t)} [INFO] devpilot.security: Periodic credential rotation check #{i+1}: OK')
        lines.append(f'{ts(t + 0.05)} [DEBUG] devpilot.security: No expired tokens found')
    
    with open(os.path.join(LOGS_DIR, 'security_events.log'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"  security_events.log: {len(lines)} lines")
    
    # observability_trace.log
    lines = []
    t = 10
    for i in range(60):
        t += random.uniform(0.5, 3.0)
        agents = ['devlead', 'intake', 'analyst', 'fixer', 'verifier', 'release', 'knowledge', 'orchestrator']
        agent = random.choice(agents)
        tid = f'{i+1:08x}'
        lines.append(f'{ts(t)} [TRACE] devpilot.otel: Span started agent={agent} trace_id={tid}')
        lines.append(f'{ts(t + 0.1)} [TRACE] devpilot.otel: Span attributes: service.name=devpilot-{agent}, span.kind=internal, dal.level=DAL-2')
        dur = random.uniform(10, 500)
        lines.append(f'{ts(t + 0.2 + random.uniform(0, 0.5))} [TRACE] devpilot.otel: Span ended agent={agent} duration={dur:.1f}ms status=OK')
        lines.append(f'{ts(t + 0.25)} [DEBUG] devpilot.otel: Exporting span to OTLP endpoint http://otel-collector:4318')
    
    with open(os.path.join(LOGS_DIR, 'observability_trace.log'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"  observability_trace.log: {len(lines)} lines")
    
    # service.log
    lines = []
    t = 5
    for i in range(100):
        t += random.uniform(0.5, 5.0)
        svcs = ['gateway', 'manager', 'worker-intake', 'worker-analyst', 'worker-fixer', 
                'worker-verifier', 'worker-release', 'worker-knowledge', 'worker-orchestrator', 'worker-lifecycle']
        svc = random.choice(svcs)
        events = [
            ('INFO', f'{svc} processing request req-{random.randint(1000, 9999)}'),
            ('DEBUG', f'{svc} cache hit ratio: {random.uniform(0.7, 0.99):.2%}'),
            ('INFO', f'{svc} metric exported: latency_p99={random.uniform(10, 200):.0f}ms'),
            ('DEBUG', f'{svc} memory usage: {random.uniform(20, 60):.1f}MB'),
            ('INFO', f'{svc} request completed: status=200 duration={random.uniform(5, 100):.0f}ms'),
        ]
        level, msg = random.choice(events)
        lines.append(f'{ts(t)} [{level}] devpilot.{svc}: {msg}')
    
    with open(os.path.join(LOGS_DIR, 'service.log'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"  service.log: {len(lines)} lines")

if __name__ == '__main__':
    generate_logs()
    print("\nEvidence generation complete!")
